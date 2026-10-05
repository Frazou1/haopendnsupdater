<!-- https://developers.home-assistant.io/docs/add-ons/presentation#keeping-a-changelog -->

## 1.2.0

- The OpenDNS password is now hidden in the configuration screen / Le mot de passe OpenDNS est maintenant masqué dans l'écran de configuration
- OpenDNS is only contacted when the public IP changes (or once a day) / OpenDNS n'est contacté que si l'IP publique change (ou une fois par jour)
- The sensor becomes unavailable when the add-on stops / Le capteur devient indisponible quand l'add-on s'arrête
- New attributes `public_ip`, `opendns_response`, `last_check` / Nouveaux attributs `public_ip`, `opendns_response`, `last_check`
- Persistent MQTT connection with automatic reconnection; the add-on no longer stops on an error / Connexion MQTT persistante avec reconnexion automatique ; l'add-on ne s'arrête plus sur une erreur
- Network timeouts, and a much smaller Docker image / Délais d'attente réseau, et image Docker beaucoup plus légère
- MQTT username/password are optional; default broker `core-mosquitto` / Utilisateur et mot de passe MQTT optionnels ; broker par défaut `core-mosquitto`
- Configuration screen translated (English, French) / Écran de configuration traduit (anglais, français)

## 1.1.6

- Version before the changelog / Version antérieure au journal des modifications
