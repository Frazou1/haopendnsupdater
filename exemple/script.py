from datetime import datetime
import json
import requests
import sys
import paho.mqtt.client as mqtt

# Obtenir l'adresse IP publique
def get_public_ip():
    try:
        response = requests.get("http://icanhazip.com")
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération de l'IP publique : {e}")
        return None

# Mise à jour de l'IP sur OpenDNS
def update_opendns(username, password, network_label, ip):
    url = f"https://updates.opendns.com/nic/update?hostname={network_label}&myip={ip}"
    try:
        response = requests.get(url, auth=(username, password))
        response.raise_for_status()
        print(f"Réponse d'OpenDNS : {response.text}")
        if "good" in response.text or "nochg" in response.text:
            return True
        else:
            return False
    except requests.RequestException as e:
        print(f"Erreur lors de la mise à jour sur OpenDNS : {e}")
        return False

# Publication MQTT
def publish_mqtt(mqtt_host, mqtt_port, mqtt_username, mqtt_password, status, last_update):
    client = mqtt.Client("opendns_updater")
    client.username_pw_set(mqtt_username, mqtt_password)
    
    try:
        client.connect(mqtt_host, int(mqtt_port), 60)
        client.loop_start()

        # Publier le statut du sensor
        client.publish("homeassistant/sensor/opendns_updater/state", status, retain=True)

        # Publier l'attribut de date de mise à jour
        attributes = {
            "last_update": last_update
        }
        client.publish("homeassistant/sensor/opendns_updater/attributes", json.dumps(attributes), retain=True)
        
        client.loop_stop()
        client.disconnect()

        print("Publication MQTT réussie.")
    except Exception as e:
        print(f"Erreur lors de la publication MQTT : {e}")

# Fonction principale
def main():
    if len(sys.argv) != 8:
        print("Usage: script.py <username> <password> <network_label> <mqtt_host> <mqtt_port> <mqtt_username> <mqtt_password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    network_label = sys.argv[3]
    mqtt_host = sys.argv[4]
    mqtt_port = sys.argv[5]
    mqtt_username = sys.argv[6]
    mqtt_password = sys.argv[7]

    # Vérification de l'IP publique
    current_ip = get_public_ip()
    if not current_ip:
        print("Impossible de récupérer l'adresse IP publique.")
        publish_mqtt(mqtt_host, mqtt_port, mqtt_username, mqtt_password, "invalide", datetime.now().isoformat())
        return

    print(f"Adresse IP publique actuelle : {current_ip}")

    # Mise à jour sur OpenDNS
    status = update_opendns(username, password, network_label, current_ip)

    # Définir le statut et la date
    status_text = "valide" if status else "invalide"
    last_update = datetime.now().isoformat()

    # Publier le statut et la date via MQTT
    publish_mqtt(mqtt_host, mqtt_port, mqtt_username, mqtt_password, status_text, last_update)

if __name__ == "__main__":
    main()
