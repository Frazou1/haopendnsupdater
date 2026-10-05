# HA OpenDNS Updater

[English](#english) · [Français](#français)

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FFrazou1%2Fhaopendnsupdater)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

---

## English

Home Assistant add-on that keeps your OpenDNS network's public IP address up to date, so your OpenDNS filtering keeps applying when your ISP changes your IP.

- Updates the public IP on OpenDNS (only when it changes, plus once a day)
- Publishes a status sensor through MQTT Discovery (`valide` / `invalide`, unavailable when the add-on is stopped)
- Attributes: public IP, OpenDNS answer, last update, last check

### Installation

1. Click the button above, or go to **Settings → Add-ons → Add-on Store → ⋮ → Repositories** and add `https://github.com/Frazou1/haopendnsupdater`.
2. Install **HA OpenDNS Updater**.
3. Fill in the **Configuration** tab (OpenDNS account, network label, MQTT broker).
4. Start the add-on and check its logs.

Full documentation: [haopendnsupdater/DOCS.md](haopendnsupdater/DOCS.md) (also shown in the add-on's **Documentation** tab).

---

## Français

Add-on Home Assistant qui garde à jour l'adresse IP publique de votre réseau OpenDNS, pour que le filtrage OpenDNS continue de s'appliquer quand votre fournisseur Internet change votre IP.

- Met à jour l'IP publique sur OpenDNS (seulement quand elle change, plus une fois par jour)
- Publie un capteur de statut via MQTT Discovery (`valide` / `invalide`, indisponible quand l'add-on est arrêté)
- Attributs : IP publique, réponse d'OpenDNS, dernière mise à jour, dernière vérification

### Installation

1. Cliquez sur le bouton ci-dessus, ou allez dans **Paramètres → Modules complémentaires → Boutique → ⋮ → Dépôts** et ajoutez `https://github.com/Frazou1/haopendnsupdater`.
2. Installez **HA OpenDNS Updater**.
3. Remplissez l'onglet **Configuration** (compte OpenDNS, libellé du réseau, broker MQTT).
4. Démarrez l'add-on et consultez son journal.

Documentation complète : [haopendnsupdater/DOCS.md](haopendnsupdater/DOCS.md) (aussi affichée dans l'onglet **Documentation** de l'add-on).

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
