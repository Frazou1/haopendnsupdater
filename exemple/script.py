from datetime import datetime
import json
import os
import requests
import sys
import time

def get_public_ip():
    """Récupère l'adresse IP publique actuelle."""
    try:
        response = requests.get("http://icanhazip.com")
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération de l'IP publique : {e}")
        return None

def update_ha_sensor(status, last_update):
    """Met à jour le sensor dans Home Assistant en écrivant dans un fichier JSON."""
    sensor_data = {
        "status": status,
        "last_update": last_update
    }
    
    # Écriture des données dans le fichier de statut
    with open('/data/sensor_status.json', 'w') as f:
        json.dump(sensor_data, f)

    print(f"Statut du sensor mis à jour : {sensor_data}")

def update_opendns(username, password, network_label, ip):
    """Met à jour l'adresse IP sur OpenDNS via l'API dynamique."""
    url = f"https://updates.opendns.com/nic/update?hostname={network_label}&myip={ip}"
    try:
        response = requests.get(url, auth=(username, password))
        response.raise_for_status()
        print(f"Réponse d'OpenDNS : {response.text}")

        # Si la mise à jour est réussie, on met à jour le sensor
        update_ha_sensor(
            status="success",
            last_update=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    except requests.RequestException as e:
        print(f"Erreur lors de la mise à jour sur OpenDNS : {e}")

        # Si la mise à jour échoue, on met à jour le sensor avec un statut d'échec
        update_ha_sensor(
            status="failure",
            last_update=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

def main():
    # Vérification des arguments
    if len(sys.argv) != 5:
        print("Usage: script.py <username> <password> <network_label> <check_interval>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    network_label = sys.argv[3]
    check_interval = int(sys.argv[4])

    # Variable pour stocker la dernière IP connue
    last_ip = None

    while True:
        # Récupération de l'IP publique actuelle
        current_ip = get_public_ip()
        if not current_ip:
            print("Impossible de récupérer l'adresse IP publique.")
            update_ha_sensor(
                status="error",
                last_update=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        else:
            print(f"Adresse IP publique actuelle : {current_ip}")

            # Si l'IP a changé, mise à jour sur OpenDNS
            if current_ip != last_ip:
                print("Nouvelle IP détectée. Mise à jour sur OpenDNS...")
                update_opendns(username, password, network_label, current_ip)
                last_ip = current_ip
            else:
                print("Aucune modification de l'IP détectée.")
                
                # Mise à jour du sensor même si l'IP n'a pas changé
                update_ha_sensor(
                    status="no_change",
                    last_update=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
        
        # Attente avant la prochaine vérification
        time.sleep(check_interval)

if __name__ == "__main__":
    main()
