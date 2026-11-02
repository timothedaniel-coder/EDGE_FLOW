"""Paramètres modifiables du projet."""

# Port série du dongle (le chemin /dev/serial/by-id reste stable après un rebranchement)
PORT = '/dev/serial/by-id/usb-ITead_Sonoff_Zigbee_3.0_USB_Dongle_Plus_52421b7df89def119e1fcba661ce3355-if00-port0'
BAUD_RATE = 115200

TIMEOUT = 1                  # secondes : attente maximale lors d'une lecture
BOOT_DELAY = 1               # secondes : temps laissé au dongle après l'ouverture du port
PERMIT_JOIN_DURATION = 60    # secondes : durée pendant laquelle le réseau accepte de nouveaux appareils
