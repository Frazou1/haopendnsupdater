#!/usr/bin/env bash
set -e

OPTIONS_FILE="/data/options.json"

USERNAME="$(jq -r '.username' $OPTIONS_FILE)"
PASSWORD="$(jq -r '.password' $OPTIONS_FILE)"
NETWORK_LABEL="$(jq -r '.network_label' $OPTIONS_FILE)"
INTERVAL="$(jq -r '.check_interval' $OPTIONS_FILE)"


echo "[INFO] Démarrage de l'add-on HA OpenDNS Updater"

while true; do
    echo "Vérification de l'adresse IP publique..."
    python3 /script.py "$USERNAME" "$PASSWORD" "$NETWORK_LABEL" 
    
    echo "Attente de $INTERVAL secondes avant la prochaine vérification."
    sleep $INTERVAL
done
