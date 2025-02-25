# HA OpenDNS Updater

**HA OpenDNS Updater** HA OpenDNS Updater is an add-on for Home Assistant that automatically updates your public IP address on OpenDNS to keep your network filtering settings up to date. It uses MQTT to publish the update status (valid or invalid) and the date of the last update using MQTT Discovery, allowing Home Assistant to automatically detect the sensor. 
**New features:**  
-   Updates your public IP address on OpenDNS.
-   Publishes the status (valid or invalid) via MQTT.
-   Includes a last_update attribute to display the date of the last update.
-   Uses MQTT Discovery for automatic integration into Home Assistant.

---

## Prerequisites
-   Home Assistant installed with the MQTT broker configured.
-   An OpenDNS account with a network label configured.
-   Access to your Home Assistant instance via Supervisor to install the add-on.

## Installation

1. **Add this repository** to Home Assistant as an Add-on repository:  
   - Go to **Settings** → **Add-ons** → **Add-on Store** → the three dots menu (**⋮**) → **Repositories** → enter this repo's URL.  
   - Or click the button below:

   [![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FFrazou1%2Fhaopendnsupdater)

2. **Install** the add-on named **HA OpenDNS Updater** from your local add-ons list.
3. **Configure** the add-on with the following options:
   - **Username:** The username of opendns account.
   - **Password:** The password of opendns account.
   - **Network_label:** The network label of opendns account.
   - **Update interval:** How frequently (in seconds) the site is re-checked.
   - **MQTT settings:** MQTT host, port, username, and password.

4. **Start** the add-on and check the logs. You should see  publishing MQTT sensor data, and (if configured) creating sensor in HA.

---

## Configuration Options

| Key                  | Description                                                                                      | Default                         |
|----------------------|--------------------------------------------------------------------------------------------------|---------------------------------|
| `username`           | The username of opendns account.                                                                 | `"aaa@bbb.com"`                 |
| `password`           | The password of opendns account.                                                                 | `password`                      |
| `network_label       | The network label of opendns account.                                                            | `home_lan`                      |
| `check_interval      | How frequently (in seconds) to re-check                                                          | `300"` 5min                     |
| `mqtt_host`          | The MQTT broker hostname                                                                         | `"core-mosquitto"`              |
| `mqtt_port`          | The MQTT broker port                                                                             | `1883`                          |
| `mqtt_username`      | Username for MQTT (if any)                                                                       | `""`                            |
| `mqtt_password`      | Password for MQTT (if any)                                                                       | `""`                            |


---

## Automation Example

```yaml
alias: Notification OpenDns Updater à échoué
description: ""
triggers:
  - trigger: state
    entity_id:
      - sensor.opendns_updater_opendns_status
    to: invalide
conditions: []
actions:
  - action: notify.mobile_app_iphone
    metadata: {}
    data:
      title: OpenDNS - Mise à jour échouée
      message: >-
        La mise à jour de l'IP publique sur OpenDNS a échoué. Vérifiez vos identifiants ou votre connexion internet.
      data:
        actions:
          - action: "URI"
            title: "Vérifier OpenDNS"
            uri: "https://dashboard.opendns.com/" 
  - action: persistent_notification.create
    metadata: {}
    data:
      title: OpenDNS Status
      message: La mise à jour OpenDNS a échoué. Vérifiez l'add-on.
mode: single


```



## Architectures

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

---

## Community & Support

- [Home Assistant Community](https://community.home-assistant.io/) – For questions, setup tips, or to share configurations.
- [Ville de Québec Info-Collecte](https://www.ville.quebec.qc.ca/services/info-collecte/) – Official site with waste collection schedules.

---

<!--
Notes for developers or advanced instructions can remain hidden here as comments if desired.
-->

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
