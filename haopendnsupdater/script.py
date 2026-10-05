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

# Explication des codes de réponse OpenDNS (protocole DynDNS) : (anglais, français)
# OpenDNS response codes explained (DynDNS protocol): (English, French)
OPENDNS_MESSAGES = {
    "good": ("Public IP updated on OpenDNS.",
             "IP publique mise à jour sur OpenDNS."),
    "nochg": ("OpenDNS already had this IP, nothing to change.",
              "OpenDNS avait déjà cette IP, rien à changer."),
    "badauth": ("Wrong OpenDNS username or password. Check the add-on configuration.",
                "Utilisateur ou mot de passe OpenDNS incorrect. Vérifiez la configuration de l'add-on."),
    "nohost": ("Network label not found in this OpenDNS account. Check network_label (case-sensitive) in the OpenDNS dashboard.",
               "Libellé de réseau introuvable dans ce compte OpenDNS. Vérifiez network_label (majuscules comprises) dans le tableau de bord OpenDNS."),
    "notfqdn": ("Invalid network label. Check network_label.",
                "Libellé de réseau invalide. Vérifiez network_label."),
    "!yours": ("This network belongs to another OpenDNS account.",
               "Ce réseau appartient à un autre compte OpenDNS."),
    "numhost": ("Too many networks match this label in the OpenDNS account.",
                "Trop de réseaux correspondent à ce libellé dans le compte OpenDNS."),
    "abuse": ("Updates blocked by OpenDNS (too many requests). Wait, then restart the add-on.",
              "Mises à jour bloquées par OpenDNS (trop de requêtes). Attendez, puis redémarrez l'add-on."),
    "badagent": ("Request refused by OpenDNS (client blocked).",
                 "Requête refusée par OpenDNS (client bloqué)."),
    "dnserr": ("OpenDNS server error. Will retry at the next check.",
               "Erreur du serveur OpenDNS. Nouvel essai à la prochaine vérification."),
    "911": ("OpenDNS server error. Will retry at the next check.",
            "Erreur du serveur OpenDNS. Nouvel essai à la prochaine vérification."),
}


def log(message):
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {message}", flush=True)


def now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def network_error_message(err, target):
    """Message clair pour une erreur réseau : (anglais, français).

    Clear message for a network error: (English, French).
    """
    if isinstance(err, requests.Timeout):
        return (f"{target} did not answer within {HTTP_TIMEOUT} s.",
                f"{target} n'a pas répondu en moins de {HTTP_TIMEOUT} s.")
    if isinstance(err, requests.ConnectionError):
        return (f"Cannot reach {target}. Is the Internet connection down?",
                f"Impossible de joindre {target}. La connexion Internet est-elle coupée ?")
    return (f"Network error with {target}: {err}",
            f"Erreur réseau avec {target} : {err}")


def get_public_ip():
    """Retourne (IP ou None, message en, message fr) / Returns (IP or None, en message, fr message)."""
    try:
        response = requests.get("https://icanhazip.com", timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        return response.text.strip(), None, None
    except requests.RequestException as err:
        en, fr = network_error_message(err, "icanhazip.com")
        return None, f"Could not determine the public IP. {en}", f"Impossible d'obtenir l'IP publique. {fr}"


def update_opendns(username, password, network_label, ip):
    """Retourne (succès, réponse brute, message en, message fr).

    Returns (success, raw response, en message, fr message).
    """
    try:
        response = requests.get(
            "https://updates.opendns.com/nic/update",
            params={"hostname": network_label, "myip": ip},
            auth=(username, password),
            timeout=HTTP_TIMEOUT,
        )
    except requests.RequestException as err:
        en, fr = network_error_message(err, "OpenDNS")
        return False, type(err).__name__, en, fr

    # Pas de raise_for_status() : OpenDNS renvoie « badauth » avec un HTTP 401
    # No raise_for_status(): OpenDNS sends "badauth" with an HTTP 401
    answer = response.text.strip()
    code = answer.split(" ", 1)[0].lower() if answer else ""
    if response.status_code == 401 and code not in OPENDNS_MESSAGES:
        code = "badauth"
    if code in OPENDNS_MESSAGES:
        en, fr = OPENDNS_MESSAGES[code]
    else:
        en = f"Unexpected OpenDNS response (HTTP {response.status_code}): {answer or '(empty)'}"
        fr = f"Réponse inattendue d'OpenDNS (HTTP {response.status_code}) : {answer or '(vide)'}"
    return code in ("good", "nochg"), answer or f"HTTP {response.status_code}", en, fr


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

    def report(ok, en, fr):
        # Journal bilingue + attributs message / message_fr pour les notifications
        # Bilingual log + message / message_fr attributes for notifications
        status = STATUS_OK if ok else STATUS_FAILED
        prefix = "OK" if ok else "ERROR"
        log(f"{prefix} [{status}] {en}")
        log(f"{' ' * len(prefix)} [{status}] {fr}")
        attributes.update(message=en, message_fr=fr, last_check=now_iso())
        publisher.publish(status, dict(attributes))

    while True:
        ip, en, fr = get_public_ip()
        if not ip:
            report(False, en, fr)
        elif ip != last_ip or time.monotonic() - last_success > FORCE_UPDATE_SECONDS:
            # On ne contacte OpenDNS que si l'IP a changé (ou une fois par jour)
            # Only contact OpenDNS when the IP changed (or once a day)
            log(f"Public IP {ip}: updating OpenDNS network '{options['network_label']}'")
            ok, answer, en, fr = update_opendns(options["username"], options["password"], options["network_label"], ip)
            if ok:
                last_ip = ip
                last_success = time.monotonic()
            attributes.update(public_ip=ip, opendns_response=answer, last_update=now_iso())
            report(ok, f"{en} (OpenDNS: {answer})", f"{fr} (OpenDNS : {answer})")
        else:
            report(True, f"Public IP unchanged ({ip}), OpenDNS is up to date.",
                   f"IP publique inchangée ({ip}), OpenDNS est à jour.")

        time.sleep(interval)


if __name__ == "__main__":
    main()
