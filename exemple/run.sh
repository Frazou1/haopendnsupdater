#!/usr/bin/env bash
set -e

OPTIONS_FILE="/data/options.json"

USERNAME="$(jq -r '.username' $OPTIONS_FILE)"
PASSWORD="$(jq -r '.password' $OPTIONS_FILE)"
NETWORK_LABEL="$(jq -r '.network_label' $OPTIONS_FILE)"
INTERVAL="$(jq -r '.check_interval' $OPTIONS_FILE)"
MQTT_HOST="$(jq -r '.mqtt_host' $OPTIONS_FILE)"
MQTT_PORT="$(jq -r '.mqtt_port' $OPTIONS_FILE)"
MQTT_USERNAME="$(jq -r '.mqtt_username' $OPTIONS_FILE)"
MQTT_PASSWORD="$(jq -r '.mqtt_password' $OPTIONS_FILE)"

echo "[INFO] Démarrage de l'add-on HA OpenDNS Updater"
echo "[INFO] 📡 MQTT = $MQTT_HOST:$MQTT_PORT (utilisateur: $MQTT_USERNAME)"

while true; do
    echo "Vérification de l'adresse IP publique..."
    python3 /script.py \
    "$USERNAME" \
    "$PASSWORD" \
    "$NETWORK_LABEL" \
    "$MQTT_HOST" \
    "$MQTT_PORT" \
    "$MQTT_USERNAME" \
    "$MQTT_PASSWORD"
    
    echo "Attente de $INTERVAL secondes avant la prochaine vérification."
    sleep $INTERVAL
done
