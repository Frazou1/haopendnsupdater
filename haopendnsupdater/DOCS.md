# HA OpenDNS Updater

[English](#english) · [Français](#français)

---

## English

This add-on keeps your OpenDNS network's public IP address up to date, so your OpenDNS filtering keeps applying when your ISP changes your IP. The status is published to Home Assistant over MQTT (MQTT Discovery: the sensor appears automatically).

### Prerequisites

- An MQTT broker in Home Assistant (e.g. the **Mosquitto broker** add-on) and the MQTT integration.
- An OpenDNS account with a labelled network.

### Configuration

| Option | Description | Default |
|---|---|---|
| `username` | OpenDNS account username (email) | |
| `password` | OpenDNS account password | |
| `network_label` | Network label, as shown in the OpenDNS dashboard | |
| `check_interval` | Seconds between public IP checks (minimum 60) | `300` |
| `mqtt_host` | MQTT broker hostname | `core-mosquitto` |
| `mqtt_port` | MQTT broker port | `1883` |
| `mqtt_username` | MQTT username (optional) | |
| `mqtt_password` | MQTT password (optional) | |

OpenDNS is only contacted when the public IP changes, plus once a day as a safety net.

### Sensor

`sensor.opendns_updater_opendns_status`

| State | Meaning |
|---|---|
| `valide` | Last update accepted by OpenDNS |
| `invalide` | Update failed (bad credentials, unknown network label, no Internet…) |
| `unavailable` | The add-on is stopped |

The state values stay in French for compatibility with existing automations.

| Attribute | Description |
|---|---|
| `public_ip` | Public IP sent to OpenDNS |
| `opendns_response` | Raw OpenDNS answer (`good`, `nochg`, `badauth`, `nohost`…) |
| `last_update` | Date of the last OpenDNS update |
| `last_check` | Date of the last public IP check |

### Automation example

```yaml
alias: OpenDNS Updater failed
triggers:
  - trigger: state
    entity_id: sensor.opendns_updater_opendns_status
    to: invalide
actions:
  - action: persistent_notification.create
    data:
      title: OpenDNS
      message: >-
        The OpenDNS public IP update failed
        ({{ state_attr('sensor.opendns_updater_opendns_status', 'opendns_response') }}).
        Check your credentials and the add-on logs.
mode: single
```

---

## Français

Cet add-on garde à jour l'adresse IP publique de votre réseau OpenDNS, pour que le filtrage OpenDNS continue de s'appliquer quand votre fournisseur Internet change votre IP. Le statut est publié dans Home Assistant via MQTT (MQTT Discovery : le capteur apparaît automatiquement).

### Prérequis

- Un broker MQTT dans Home Assistant (ex. l'add-on **Mosquitto broker**) et l'intégration MQTT.
- Un compte OpenDNS avec un réseau doté d'un libellé.

### Configuration

| Option | Description | Défaut |
|---|---|---|
| `username` | Utilisateur du compte OpenDNS (courriel) | |
| `password` | Mot de passe du compte OpenDNS | |
| `network_label` | Libellé du réseau, tel qu'affiché dans le tableau de bord OpenDNS | |
| `check_interval` | Secondes entre deux vérifications de l'IP publique (minimum 60) | `300` |
| `mqtt_host` | Nom d'hôte du broker MQTT | `core-mosquitto` |
| `mqtt_port` | Port du broker MQTT | `1883` |
| `mqtt_username` | Utilisateur MQTT (optionnel) | |
| `mqtt_password` | Mot de passe MQTT (optionnel) | |

OpenDNS n'est contacté que si l'IP publique change, plus une fois par jour par précaution.

### Capteur

`sensor.opendns_updater_opendns_status`

| État | Signification |
|---|---|
| `valide` | Dernière mise à jour acceptée par OpenDNS |
| `invalide` | Mise à jour échouée (identifiants, libellé de réseau inconnu, pas d'Internet…) |
| `unavailable` | L'add-on est arrêté |

| Attribut | Description |
|---|---|
| `public_ip` | IP publique envoyée à OpenDNS |
| `opendns_response` | Réponse brute d'OpenDNS (`good`, `nochg`, `badauth`, `nohost`…) |
| `last_update` | Date de la dernière mise à jour OpenDNS |
| `last_check` | Date de la dernière vérification de l'IP publique |

### Exemple d'automatisation

```yaml
alias: Échec OpenDNS Updater
triggers:
  - trigger: state
    entity_id: sensor.opendns_updater_opendns_status
    to: invalide
actions:
  - action: persistent_notification.create
    data:
      title: OpenDNS
      message: >-
        La mise à jour de l'IP publique sur OpenDNS a échoué
        ({{ state_attr('sensor.opendns_updater_opendns_status', 'opendns_response') }}).
        Vérifiez vos identifiants et le journal de l'add-on.
mode: single
```
