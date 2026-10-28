# HA OpenDNS Updater (module complémentaire Home Assistant / Home Assistant add-on)

[Français](#français) | [English](#english)

---

## Français

### Description

Module complémentaire (add-on) Home Assistant qui garde à jour l'adresse IP publique de votre **réseau OpenDNS**. OpenDNS applique votre filtrage (catégories bloquées, statistiques…) selon l'IP publique de votre réseau ; quand votre fournisseur Internet change cette IP, OpenDNS ne vous reconnaît plus. L'add-on règle ce problème, comme le ferait le logiciel « OpenDNS Updater » sur un ordinateur.

Fonctionnement :

1. À chaque vérification, l'add-on obtient l'IP publique auprès de `https://icanhazip.com`.
2. Si l'IP a changé (ou si la dernière mise à jour réussie date de plus de 24 h), il l'envoie à OpenDNS par `https://updates.opendns.com/nic/update` (protocole de type DynDNS, authentification HTTP Basic avec votre compte OpenDNS, paramètre `hostname` = libellé du réseau).
3. Le résultat est publié dans Home Assistant par **MQTT** (le capteur apparaît tout seul grâce à MQTT Discovery).

### Fonctionnalités

- Mise à jour de l'IP publique sur OpenDNS, seulement quand elle change, plus une fois par jour par précaution.
- Capteur de statut `valide` / `invalide`, « indisponible » quand l'add-on est arrêté.
- Attributs : IP publique, réponse brute d'OpenDNS, explication claire en anglais (`message`) et en français (`message_fr`), dates de dernière mise à jour et de dernière vérification.
- Journal clair, en anglais puis en français, avec la marche à suivre.
- Connexion MQTT persistante avec reconnexion automatique ; l'add-on ne s'arrête pas sur une erreur.

### Installation

**Prérequis :**

- un broker MQTT (ex. le module complémentaire **Mosquitto broker**) et l'intégration **MQTT** configurée dans Home Assistant ;
- un compte OpenDNS (ex. OpenDNS Home) avec un réseau enregistré (voir ci-dessous).

1. Allez dans **Paramètres → Modules complémentaires → Boutique des modules complémentaires → ⋮ (en haut à droite) → Dépôts** et ajoutez `https://github.com/Frazou1/haopendnsupdater`.
2. Rafraîchissez la boutique, puis installez **HA OpenDNS Updater**.
3. Remplissez l'onglet **Configuration** (`username`, `password`, `network_label`).
4. Démarrez l'add-on et consultez l'onglet **Journal**.

#### Préparer le compte OpenDNS

1. Connectez-vous au tableau de bord OpenDNS (`https://dashboard.opendns.com`) avec votre compte.
2. Onglet **Settings** : si votre réseau n'existe pas encore, ajoutez-le (OpenDNS propose l'IP publique actuelle) et donnez-lui un **libellé** (nom). Ce libellé est la valeur de `network_label` ; copiez-le exactement, **majuscules comprises**.
3. Ouvrez ce réseau, section **Advanced Settings**, et cochez l'option de **mise à jour dynamique de l'IP** (« Dynamic IP Update »), puis enregistrez. Sans elle, OpenDNS peut refuser les mises à jour.
4. `username` = l'**adresse courriel** de connexion du compte OpenDNS ; `password` = son mot de passe.

Les intitulés exacts de l'interface OpenDNS peuvent varier légèrement.

### Configuration

| Option | Type | Défaut | Rôle |
|---|---|---|---|
| `username` | texte (requis) | *(vide)* | Courriel de connexion du compte OpenDNS. |
| `password` | mot de passe (requis) | *(vide)* | Mot de passe du compte OpenDNS (masqué). |
| `network_label` | texte (requis) | *(vide)* | Libellé du réseau, tel qu'affiché dans le tableau de bord OpenDNS (sensible à la casse). |
| `check_interval` | entier (secondes, minimum 60) | `300` | Délai entre deux vérifications de l'IP publique. OpenDNS n'est contacté que si l'IP change, ou une fois par jour. |
| `mqtt_host` | texte | `core-mosquitto` | Nom d'hôte du broker MQTT. `core-mosquitto` = add-on Mosquitto. |
| `mqtt_port` | port | `1883` | Port du broker MQTT. |
| `mqtt_username` | texte (optionnel) | *(vide)* | Utilisateur MQTT ; vide si le broker n'exige pas d'authentification. |
| `mqtt_password` | mot de passe (optionnel) | *(vide)* | Mot de passe MQTT (masqué). |

Exemple (valeurs fictives) :

```yaml
username: "vous@example.com"
password: "votre-mot-de-passe-opendns"
network_label: "Maison"
check_interval: 300
mqtt_host: core-mosquitto
mqtt_port: 1883
mqtt_username: ""
mqtt_password: ""
```

L'add-on n'utilise **pas** l'API de Home Assistant : tout passe par MQTT.

### Entités créées

Un capteur, rattaché à l'appareil MQTT **OpenDNS Updater** (modèle « HA OpenDNS Updater ») :

`sensor.opendns_updater_opendns_status` (nom « OpenDNS Status », identifiant unique `opendns_updater`). L'identifiant d'entité exact dépend de votre version de Home Assistant et de vos renommages : vérifiez-le dans **Paramètres → Appareils et services → Entités** (recherche « OpenDNS »).

| État | Signification |
|---|---|
| `valide` | Dernière vérification réussie : OpenDNS a accepté l'IP (`good`, `nochg`) ou l'IP n'a pas changé depuis. |
| `invalide` | Échec : identifiants, libellé de réseau, IP publique introuvable, OpenDNS injoignable… |
| `unavailable` | L'add-on est arrêté. |

Les états restent en français (`valide` / `invalide`) pour ne pas briser les automatisations existantes.

| Attribut | Description |
|---|---|
| `message` | Explication du dernier résultat, en anglais. |
| `message_fr` | Même explication, en français. |
| `public_ip` | Dernière IP publique envoyée à OpenDNS. |
| `opendns_response` | Réponse brute d'OpenDNS (`good …`, `nochg …`, `badauth`, `nohost`…). |
| `last_update` | Date et heure du dernier envoi à OpenDNS. |
| `last_check` | Date et heure de la dernière vérification. |

### Exemples d'utilisation

Carte Lovelace :

```yaml
type: entities
title: OpenDNS
entities:
  - entity: sensor.opendns_updater_opendns_status
    name: Statut
  - type: attribute
    entity: sensor.opendns_updater_opendns_status
    attribute: public_ip
    name: IP publique
  - type: attribute
    entity: sensor.opendns_updater_opendns_status
    attribute: last_update
    name: Dernière mise à jour
```

Notification en cas d'échec :

```yaml
alias: OpenDNS - échec de mise à jour
triggers:
  - trigger: state
    entity_id: sensor.opendns_updater_opendns_status
    to: invalide
actions:
  - action: persistent_notification.create
    data:
      title: OpenDNS
      message: "{{ state_attr('sensor.opendns_updater_opendns_status', 'message_fr') }}"
mode: single
```

### Dépannage

Consultez l'onglet **Journal** de l'add-on. Chaque vérification écrit deux lignes horodatées, en anglais puis en français, par exemple :

```
OK [valide] Public IP updated on OpenDNS. (OpenDNS: good <votre IP>)
   [valide] IP publique mise à jour sur OpenDNS. (OpenDNS : good <votre IP>)
ERROR [invalide] Wrong OpenDNS username or password. Check the add-on configuration. (OpenDNS: badauth)
      [invalide] Utilisateur ou mot de passe OpenDNS incorrect. Vérifiez la configuration de l'add-on. (OpenDNS : badauth)
```

| Réponse OpenDNS / message | Signification / quoi faire |
|---|---|
| `good`, `nochg` | Tout va bien. |
| `badauth` (ou HTTP 401) | Courriel ou mot de passe OpenDNS incorrect. |
| `nohost`, `notfqdn` | `network_label` ne correspond à aucun réseau du compte (vérifier l'orthographe et les majuscules). |
| `!yours` | Le réseau appartient à un autre compte OpenDNS. |
| `numhost` | Plusieurs réseaux du compte portent ce libellé : donnez-leur des libellés uniques. |
| `abuse` | Mises à jour bloquées par OpenDNS (trop de requêtes) : attendez, puis redémarrez l'add-on. |
| `badagent` | Requête refusée par OpenDNS (client bloqué). |
| `dnserr`, `911` | Erreur du serveur OpenDNS ; nouvel essai à la prochaine vérification. |
| `Could not determine the public IP…` | `icanhazip.com` injoignable (Internet coupé ?) ; nouvel essai à la prochaine vérification. |
| `ERROR: MQTT connection refused (…)` | Mauvais hôte, port, utilisateur ou mot de passe MQTT. |
| `WARNING: MQTT not connected, status will be sent on reconnect` | Broker MQTT indisponible ; le statut sera envoyé à la reconnexion. |

Important : tant qu'une mise à jour échoue, l'add-on recontacte OpenDNS à **chaque** vérification. En cas de `badauth` ou de `nohost`, corrigez la configuration rapidement (ou arrêtez l'add-on) pour éviter un blocage `abuse`.

### Limites connues

- L'IP publique est obtenue auprès d'un service externe (`icanhazip.com`) ; s'il est indisponible, aucune mise à jour n'est faite.
- La dernière IP connue est gardée en mémoire seulement : après un redémarrage de l'add-on, OpenDNS est recontacté une fois.
- Un seul réseau OpenDNS par instance de l'add-on.

### Revenir à une version précédente

Le dépôt ne publie pas d'étiquettes (tags) de version. Pour revenir en arrière, cochez l'option de sauvegarde au moment de la mise à jour de l'add-on, puis restaurez cette sauvegarde dans **Paramètres → Système → Sauvegardes**. L'historique des changements est dans [CHANGELOG.md](https://github.com/Frazou1/haopendnsupdater/blob/main/haopendnsupdater/CHANGELOG.md).

### Licence

Apache License 2.0 — voir [LICENSE](https://github.com/Frazou1/haopendnsupdater/blob/main/LICENSE).

---

## English

### Description

Home Assistant add-on that keeps your **OpenDNS network**'s public IP address up to date. OpenDNS applies your filtering (blocked categories, statistics…) based on your network's public IP; when your ISP changes that IP, OpenDNS no longer recognises you. The add-on fixes that, like the "OpenDNS Updater" software would on a computer.

How it works:

1. At each check, the add-on gets the public IP from `https://icanhazip.com`.
2. If the IP changed (or the last successful update is more than 24 h old), it sends it to OpenDNS through `https://updates.opendns.com/nic/update` (DynDNS-style protocol, HTTP Basic authentication with your OpenDNS account, `hostname` parameter = network label).
3. The result is published to Home Assistant over **MQTT** (the sensor appears automatically through MQTT Discovery).

### Features

- Updates the public IP on OpenDNS, only when it changes, plus once a day as a safety net.
- Status sensor `valide` / `invalide` (valid / invalid), unavailable when the add-on is stopped.
- Attributes: public IP, raw OpenDNS answer, clear explanation in English (`message`) and French (`message_fr`), last update and last check times.
- Clear log, in English then French, telling you what to do.
- Persistent MQTT connection with automatic reconnection; the add-on does not stop on an error.

### Installation

**Prerequisites:**

- an MQTT broker (e.g. the **Mosquitto broker** add-on) and the **MQTT** integration set up in Home Assistant;
- an OpenDNS account (e.g. OpenDNS Home) with a registered network (see below).

1. Go to **Settings → Add-ons → Add-on Store → ⋮ (top right) → Repositories** and add `https://github.com/Frazou1/haopendnsupdater`.
2. Refresh the store, then install **HA OpenDNS Updater**.
3. Fill in the **Configuration** tab (`username`, `password`, `network_label`).
4. Start the add-on and check the **Log** tab.

#### Preparing the OpenDNS account

1. Sign in to the OpenDNS dashboard (`https://dashboard.opendns.com`) with your account.
2. **Settings** tab: if your network does not exist yet, add it (OpenDNS suggests your current public IP) and give it a **label** (name). That label is the `network_label` value; copy it exactly, **including upper/lower case**.
3. Open that network, **Advanced Settings** section, tick the **Dynamic IP Update** option and save. Without it, OpenDNS may refuse updates.
4. `username` = the sign-in **email address** of the OpenDNS account; `password` = its password.

The exact labels of the OpenDNS interface may vary slightly.

### Configuration

| Option | Type | Default | Purpose |
|---|---|---|---|
| `username` | text (required) | *(empty)* | Sign-in email of the OpenDNS account. |
| `password` | password (required) | *(empty)* | OpenDNS account password (hidden). |
| `network_label` | text (required) | *(empty)* | Network label, as shown in the OpenDNS dashboard (case-sensitive). |
| `check_interval` | integer (seconds, minimum 60) | `300` | Delay between two public IP checks. OpenDNS is only contacted when the IP changes, or once a day. |
| `mqtt_host` | text | `core-mosquitto` | MQTT broker hostname. `core-mosquitto` = Mosquitto add-on. |
| `mqtt_port` | port | `1883` | MQTT broker port. |
| `mqtt_username` | text (optional) | *(empty)* | MQTT username; empty if the broker requires no authentication. |
| `mqtt_password` | password (optional) | *(empty)* | MQTT password (hidden). |

Example (dummy values):

```yaml
username: "you@example.com"
password: "your-opendns-password"
network_label: "Home"
check_interval: 300
mqtt_host: core-mosquitto
mqtt_port: 1883
mqtt_username: ""
mqtt_password: ""
```

The add-on does **not** use the Home Assistant API: everything goes through MQTT.

### Created entities

One sensor, attached to the **OpenDNS Updater** MQTT device (model "HA OpenDNS Updater"):

`sensor.opendns_updater_opendns_status` (name "OpenDNS Status", unique ID `opendns_updater`). The exact entity ID depends on your Home Assistant version and any renaming: check it in **Settings → Devices & services → Entities** (search for "OpenDNS").

| State | Meaning |
|---|---|
| `valide` | Last check succeeded: OpenDNS accepted the IP (`good`, `nochg`) or the IP has not changed since. |
| `invalide` | Failure: credentials, network label, public IP not found, OpenDNS unreachable… |
| `unavailable` | The add-on is stopped. |

The states stay in French (`valide` / `invalide`) so existing automations keep working.

| Attribute | Description |
|---|---|
| `message` | Explanation of the last result, in English. |
| `message_fr` | Same explanation, in French. |
| `public_ip` | Last public IP sent to OpenDNS. |
| `opendns_response` | Raw OpenDNS answer (`good …`, `nochg …`, `badauth`, `nohost`…). |
| `last_update` | Date and time of the last call to OpenDNS. |
| `last_check` | Date and time of the last check. |

### Usage examples

Lovelace card:

```yaml
type: entities
title: OpenDNS
entities:
  - entity: sensor.opendns_updater_opendns_status
    name: Status
  - type: attribute
    entity: sensor.opendns_updater_opendns_status
    attribute: public_ip
    name: Public IP
  - type: attribute
    entity: sensor.opendns_updater_opendns_status
    attribute: last_update
    name: Last update
```

Notification on failure:

```yaml
alias: OpenDNS - update failed
triggers:
  - trigger: state
    entity_id: sensor.opendns_updater_opendns_status
    to: invalide
actions:
  - action: persistent_notification.create
    data:
      title: OpenDNS
      message: "{{ state_attr('sensor.opendns_updater_opendns_status', 'message') }}"
mode: single
```

### Troubleshooting

Check the add-on's **Log** tab. Each check writes two timestamped lines, in English then French, for example:

```
OK [valide] Public IP updated on OpenDNS. (OpenDNS: good <your IP>)
   [valide] IP publique mise à jour sur OpenDNS. (OpenDNS : good <your IP>)
ERROR [invalide] Wrong OpenDNS username or password. Check the add-on configuration. (OpenDNS: badauth)
      [invalide] Utilisateur ou mot de passe OpenDNS incorrect. Vérifiez la configuration de l'add-on. (OpenDNS : badauth)
```

| OpenDNS answer / message | Meaning / what to do |
|---|---|
| `good`, `nochg` | Everything is fine. |
| `badauth` (or HTTP 401) | Wrong OpenDNS email or password. |
| `nohost`, `notfqdn` | `network_label` does not match any network of the account (check spelling and case). |
| `!yours` | The network belongs to another OpenDNS account. |
| `numhost` | Several networks of the account share this label: give them unique labels. |
| `abuse` | Updates blocked by OpenDNS (too many requests): wait, then restart the add-on. |
| `badagent` | Request refused by OpenDNS (client blocked). |
| `dnserr`, `911` | OpenDNS server error; retried at the next check. |
| `Could not determine the public IP…` | `icanhazip.com` unreachable (Internet down?); retried at the next check. |
| `ERROR: MQTT connection refused (…)` | Wrong MQTT host, port, username or password. |
| `WARNING: MQTT not connected, status will be sent on reconnect` | MQTT broker unavailable; the status is sent on reconnect. |

Important: as long as an update fails, the add-on contacts OpenDNS again at **every** check. On `badauth` or `nohost`, fix the configuration quickly (or stop the add-on) to avoid an `abuse` block.

### Known limitations

- The public IP comes from an external service (`icanhazip.com`); if it is down, no update is made.
- The last known IP is kept in memory only: after an add-on restart, OpenDNS is contacted once again.
- One OpenDNS network per add-on instance.

### Rolling back to a previous version

The repository does not publish version tags. To roll back, tick the backup option when updating the add-on, then restore that backup in **Settings → System → Backups**. The change history is in [CHANGELOG.md](https://github.com/Frazou1/haopendnsupdater/blob/main/haopendnsupdater/CHANGELOG.md).

### License

Apache License 2.0 — see [LICENSE](https://github.com/Frazou1/haopendnsupdater/blob/main/LICENSE).

