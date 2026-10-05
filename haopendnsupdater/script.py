"""HA OpenDNS Updater.

Met à jour l'IP publique du réseau OpenDNS et publie le statut via MQTT Discovery.
Updates the OpenDNS network's public IP and publishes the status via MQTT Discovery.
"""

import json
import signal
import sys
import time
from datetime import datetime

import paho.mqtt.client as mqtt
import requests

OPTIONS_FILE = "/data/options.json"

BASE_TOPIC = "homeassistant/sensor/opendns_updater"
DISCOVERY_TOPIC = f"{BASE_TOPIC}/config"
STATE_TOPIC = f"{BASE_TOPIC}/state"
ATTR_TOPIC = f"{BASE_TOPIC}/attributes"
AVAILABILITY_TOPIC = f"{BASE_TOPIC}/availability"

HTTP_TIMEOUT = 15
# Mise à jour forcée au moins une fois par jour, même si l'IP n'a pas changé
# Forced update at least once a day, even if the IP did not change
FORCE_UPDATE_SECONDS = 24 * 3600

# Valeurs d'état gardées en français pour ne pas casser les automatisations existantes
# State values kept in French so existing automations keep working
STATUS_OK = "valide"
STATUS_FAILED = "invalide"


def log(message):
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {message}", flush=True)


def now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def get_public_ip():
    try:
        response = requests.get("https://icanhazip.com", timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as err:
        log(f"ERROR: could not get the public IP: {err}")
        return None


def update_opendns(username, password, network_label, ip):
    """Retourne (succès, réponse d'OpenDNS) / Returns (success, OpenDNS response)."""
    try:
        response = requests.get(
            "https://updates.opendns.com/nic/update",
            params={"hostname": network_label, "myip": ip},
            auth=(username, password),
            timeout=HTTP_TIMEOUT,
        )
        response.raise_for_status()
        answer = response.text.strip()
        log(f"OpenDNS response: {answer}")
        # good / nochg = succès ; badauth, nohost, abuse... = échec
        # good / nochg = success; badauth, nohost, abuse... = failure
        return answer.startswith(("good", "nochg")), answer
    except requests.RequestException as err:
        log(f"ERROR: OpenDNS update failed: {err}")
        return False, str(err)


class Publisher:
    """Connexion MQTT persistante, avec reconnexion automatique.

    Persistent MQTT connection, with automatic reconnection.
    """

    def __init__(self, options):
        self.state = None
        self.attributes = {}
        self.client = mqtt.Client("opendns_updater")
        if options.get("mqtt_username"):
            self.client.username_pw_set(options["mqtt_username"], options.get("mqtt_password") or None)
        # Le broker marque le capteur indisponible si l'add-on s'arrête
        # The broker marks the sensor unavailable if the add-on stops
        self.client.will_set(AVAILABILITY_TOPIC, "offline", retain=True)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.connect_async(options["mqtt_host"], int(options["mqtt_port"]), 60)
        self.client.loop_start()

    def _on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            log(f"ERROR: MQTT connection refused ({mqtt.connack_string(rc)})")
            return
        log("Connected to MQTT")
        client.publish(DISCOVERY_TOPIC, json.dumps(self._discovery_payload()), retain=True)
        client.publish(AVAILABILITY_TOPIC, "online", retain=True)
        # Republie le dernier état après une reconnexion / Republish the last state after a reconnect
        if self.state is not None:
            self._publish_state()

    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            log("WARNING: MQTT connection lost, reconnecting...")

    @staticmethod
    def _discovery_payload():
        return {
            "name": "OpenDNS Status",
            "state_topic": STATE_TOPIC,
            "json_attributes_topic": ATTR_TOPIC,
            "availability_topic": AVAILABILITY_TOPIC,
            "icon": "mdi:cloud-check",
            "unique_id": "opendns_updater",
            "device": {
                "identifiers": ["opendns_updater"],
                "name": "OpenDNS Updater",
                "model": "HA OpenDNS Updater",
                "manufacturer": "Custom",
            },
        }

    def publish(self, state, attributes):
        self.state = state
        self.attributes = attributes
        if self.client.is_connected():
            self._publish_state()
        else:
            log("WARNING: MQTT not connected, status will be sent on reconnect")

    def _publish_state(self):
        self.client.publish(STATE_TOPIC, self.state, retain=True)
        self.client.publish(ATTR_TOPIC, json.dumps(self.attributes), retain=True)

    def stop(self):
        if self.client.is_connected():
            self.client.publish(AVAILABILITY_TOPIC, "offline", retain=True).wait_for_publish(5)
        self.client.disconnect()
        self.client.loop_stop()


def main():
    with open(OPTIONS_FILE, encoding="utf-8") as file:
        options = json.load(file)

    interval = max(60, int(options.get("check_interval", 300)))
    log(f"Starting HA OpenDNS Updater (network: {options['network_label']}, every {interval} s)")
    log(f"MQTT = {options['mqtt_host']}:{options['mqtt_port']}")

    publisher = Publisher(options)

    # Arrêt propre quand le Supervisor arrête l'add-on / Clean shutdown when the Supervisor stops the add-on
    def shutdown(signum, frame):
        log("Stopping")
        publisher.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    last_ip = None
    last_success = 0.0
    attributes = {}

    while True:
        ip = get_public_ip()
        if not ip:
            attributes.update(last_check=now_iso())
            publisher.publish(STATUS_FAILED, dict(attributes))
        elif ip != last_ip or time.monotonic() - last_success > FORCE_UPDATE_SECONDS:
            # On ne contacte OpenDNS que si l'IP a changé (ou une fois par jour)
            # Only contact OpenDNS when the IP changed (or once a day)
            log(f"Public IP: {ip}, updating OpenDNS")
            ok, answer = update_opendns(options["username"], options["password"], options["network_label"], ip)
            if ok:
                last_ip = ip
                last_success = time.monotonic()
            attributes.update(public_ip=ip, opendns_response=answer, last_update=now_iso(), last_check=now_iso())
            publisher.publish(STATUS_OK if ok else STATUS_FAILED, dict(attributes))
        else:
            log(f"Public IP unchanged ({ip})")
            attributes.update(last_check=now_iso())
            publisher.publish(STATUS_OK, dict(attributes))

        time.sleep(interval)


if __name__ == "__main__":
    main()
