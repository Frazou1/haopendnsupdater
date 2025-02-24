from datetime import datetime
import json
import os
import requests
import sys

def get_public_ip():
    """Récupère l'IP publique en utilisant le service icanhazip.com"""
    try:
        response = requests.get("http://icanhazip.com")
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération de l'IP publique : {e}")
        return None

def update_ha_sensor(status, last_update):
    """Met à jour le sensor dans Home Assistant via un fichier JSON."""
    sensor_data = {
        "status": status,
        "last_update": last_update
    }
    # Écriture des données dans le fichier de statut
    with open('/data/sensor_status.json', 'w') as f:
        json.dump(sensor_data, f)
    print(f"Statut du capteur mis à jour : {sensor_data}")

def update_opendns(username, password, network_label, ip):
    """Met à jour l'adresse IP sur OpenDNS."""
    url = f"https://updates.opendns.com/nic/update?hostname={network_label}&myip={ip}"
    try:
        response = requests.get(url, auth=(username, password))
        response.raise_for_status()
        print(f"Réponse d'OpenDNS : {response.text}")
        update_ha_sensor(
            status="success",
            last_update=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    except requests.RequestException as e:
        print(f"Erreur lors de la mise à jour sur OpenDNS : {e}")
        update_ha_sensor(
            status="failure",
            last_update=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

def main():
    """Point d'entrée principal du script."""
    if len(sys.argv) != 4:
        print("Usage: script.py <username> <password> <network_label>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    network_label = sys.argv[3]

    # Vérification de l'IP publique
    current_ip = get_public_ip()
    if not current_ip:
        print("Impossible de récupérer l'adresse IP publique.")
        return

    print(f"Adresse IP publique actuelle : {current_ip}")

    # Mise à jour sur OpenDNS
    update_opendns(username, password, network_label, current_ip)

if __name__ == "__main__":
    main()
