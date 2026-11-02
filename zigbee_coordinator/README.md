# Coordinateur Zigbee – Sonoff Dongle Plus (Z-Stack MT)

Programme Python qui dialogue directement avec un dongle Zigbee **Sonoff Zigbee 3.0 USB Dongle Plus**
(modèle **P**, puce CC2652P, firmware Z-Stack) grâce au protocole **MT** (Monitor and Test) de Texas Instruments.

Il démarre le dongle en **Coordinateur**, ouvre le réseau pendant 60 s et affiche
l'adresse réseau et l'adresse MAC de chaque appareil qui s'appaire.

## Arborescence

```
zigbee_coordinator/
├── main.py              Point d'entrée : boucle de lecture
├── config.py            Port, vitesse, délais, durée d'ouverture du réseau
├── requirements.txt     Dépendances Python
├── README.md
├── zstack/              Le "moteur" du projet
│   ├── protocol.py      Constantes MT, calcul du checksum, construction d'une trame
│   ├── serial_link.py   Port série : ouverture, send_command, read_frame
│   ├── commands.py      Commandes envoyées : ping, reset, configuration, démarrage, permit_join
│   ├── handlers.py      Réactions aux trames reçues (machine à états du démarrage)
│   └── display.py       Affichage lisible des trames
└── tests/
    └── test_zstack.py   Tests automatiques (sans dongle)
```

## Installation

```bash
pip install -r requirements.txt
```

Adapte `PORT` dans `config.py` si ton dongle a un autre chemin (`ls /dev/serial/by-id/`).

## Lancement

```bash
python3 main.py
```

Si tu as une erreur de permission, soit lance avec `sudo`, soit ajoute-toi au groupe `dialout`
(`sudo usermod -aG dialout $USER`, puis reconnecte ta session).

**Important :** arrête Zigbee2MQTT, ZHA ou tout autre programme qui utilise le dongle avant de lancer le script.

## Tests

```bash
python3 -m unittest -v
```

## Déroulement du programme

Chaque étape est déclenchée par la **réponse du dongle** à l'étape précédente
(on n'utilise pas de `sleep` pour "deviner" quand il est prêt) :

| Étape | Le programme envoie | Le dongle répond |
|-------|---------------------|------------------|
| 1 | `SYS_RESET_REQ` | `SYS_RESET_IND` (redémarrage terminé) |
| 2 | `ZB_WRITE_CONFIGURATION` (rôle Coordinateur) | SRSP avec statut `00` (OK) |
| 3 | `ZDO_STARTUP_FROM_APP` | `ZDO_STATE_CHANGE_IND` … jusqu'à l'état `0x09` (Coordinateur prêt) |
| 4 | `ZDO_MGMT_PERMIT_JOIN_REQ` | Les appareils peuvent s'appairer |
| 5 | – | `ZDO_END_DEVICE_ANNCE_IND` à chaque nouvel appareil |

## Dépannage

- **Aucune réponse du dongle** : vérifie le modèle. Le Dongle Plus **E** (puce EFR32) utilise le protocole EZSP
  et ne comprend pas les trames MT.
- **`[ERREUR] ... commande invalide`** : le firmware du dongle n'accepte pas cette commande
  (certains firmwares n'activent pas toute l'interface MT).
- **`Impossible d'ouvrir ...`** : dongle débranché, mauvais chemin, ou port déjà utilisé par un autre programme.
