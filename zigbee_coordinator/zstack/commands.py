"""Commandes que l'on peut envoyer au dongle (une fonction = une commande)."""

from zstack import protocol
from zstack.serial_link import send_command

# Remarque : send_command(ser, *protocol.SYS_PING) équivaut à
# send_command(ser, 0x21, 0x01). Le * "déballe" le tuple (cmd0, cmd1).


def send_ping(ser):
    """SYS_PING : le dongle répond avec ses capacités."""
    send_command(ser, *protocol.SYS_PING)


def reset_dongle(ser):
    """SYS_RESET_REQ : redémarre le dongle (0x00 = reset matériel)."""
    send_command(ser, *protocol.SYS_RESET_REQ, [0x00])


def configure_coordinator(ser):
    """Configure la puce en mode Coordinateur avec l'API OSAL (Z-Stack 3.0+)."""
    # Structure attendue par SYS_OSAL_NV_WRITE : 
    # [ID LSB, ID MSB, Offset, Longueur, Valeur]
    # 0x87, 0x00 -> ID mémoire 0x0087 (ZCD_NV_LOGICAL_TYPE)
    # 0x00 -> Offset (aucun décalage)
    # 0x01 -> On écrit 1 seul octet
    # 0x00 -> La valeur (0x00 = Coordinateur)
    donnees = [protocol.ZCD_NV_LOGICAL_TYPE, 0x00, 0x00, 0x01, protocol.LOGICAL_TYPE_COORDINATOR]
    
    send_command(ser, *protocol.SYS_OSAL_NV_WRITE, donnees)

def start_network(ser):
    """ZDO_STARTUP_FROM_APP : démarre le réseau (0x00 = sans délai)."""
    send_command(ser, *protocol.ZDO_STARTUP_FROM_APP, [0x00])


def permit_join(ser, duree_secondes=60):
    """ZDO_MGMT_PERMIT_JOIN_REQ : autorise l'appairage de nouveaux capteurs."""
    if not 0 <= duree_secondes <= 255:
        raise ValueError("La durée doit être comprise entre 0 et 255 secondes")

    print(f"\n[!] Ouverture du réseau pour {duree_secondes} secondes...")
    # Données : [mode d'adresse 0x0F = broadcast,
    #            adresse de destination 0xFFFC (tous les routeurs) en little-endian,
    #            durée, TCSignificance]
    send_command(ser, *protocol.ZDO_MGMT_PERMIT_JOIN_REQ,
                 [0x0F, 0xFC, 0xFF, duree_secondes, 0x00])

def request_active_endpoints(ser, nwk_addr):
    """Demande à l'appareil la liste de ses Endpoints actifs."""
    addr_lsb = nwk_addr & 0xFF 
    addr_msb = (nwk_addr >> 8) & 0xFF
    
    # Données: Adresse cible (2 octets) + Adresse d'intérêt (2 octets)
    donnees = [addr_lsb, addr_msb, addr_lsb, addr_msb]
    send_command(ser, *protocol.ZDO_ACTIVE_EP_REQ, donnees)

def request_simple_descriptor(ser, nwk_addr, endpoint):
    """Demande la carte d'identité d'un Endpoint spécifique."""
    addr_lsb = nwk_addr & 0xFF
    addr_msb = (nwk_addr >> 8) & 0xFF
    
    # Données: Adresse cible (2) + Adresse d'intérêt (2) + Endpoint (1)
    donnees = [addr_lsb, addr_msb, addr_lsb, addr_msb, endpoint]
    send_command(ser, *protocol.ZDO_SIMPLE_DESC_REQ, donnees)

def request_active_endpoints(ser, nwk_addr):
    """Demande à l'appareil la liste de ses Endpoints actifs."""
    addr_lsb = nwk_addr & 0xFF
    addr_msb = (nwk_addr >> 8) & 0xFF
    donnees = [addr_lsb, addr_msb, addr_lsb, addr_msb]
    send_command(ser, *protocol.ZDO_ACTIVE_EP_REQ, donnees)

def request_simple_descriptor(ser, nwk_addr, endpoint):
    """Demande la carte d'identité d'un Endpoint spécifique."""
    addr_lsb = nwk_addr & 0xFF
    addr_msb = (nwk_addr >> 8) & 0xFF
    donnees = [addr_lsb, addr_msb, addr_lsb, addr_msb, endpoint]
    send_command(ser, *protocol.ZDO_SIMPLE_DESC_REQ, donnees)

def set_plug_state(ser, nwk_addr, state):
    """
    Allume, éteint ou bascule l'état de la prise.
    state : 0x00 (Off), 0x01 (On), 0x02 (Toggle)
    """
    zcl_payload = [0x11, 0x01, state]

    addr_lsb = nwk_addr & 0xFF
    addr_msb = (nwk_addr >> 8) & 0xFF

    donnees = [
        addr_lsb, addr_msb, # 1. Adresse de destination
        0x01,               # 2. Endpoint cible
        0x01,               # 3. Endpoint source
        0x06, 0x00,         # 4. Cluster 0x0006 (On/Off) en Little-Endian
        0x00,               # 5. Transaction ID
        0x00,               # 6. Options
        0x0F,               # 7. Rayon
        len(zcl_payload)    # 8. Taille payload
    ] + zcl_payload
    
    send_command(ser, *protocol.AF_DATA_REQUEST, donnees)

def permit_join(ser, duree=60):
    """Ouvre le réseau pour permettre l'appairage de nouveaux appareils."""
    # 0xFC 0xFF (0xFFFC) = adresse de diffusion à tous les routeurs
    donnees = [0x0F, 0xFC, 0xFF, duree, 0x00]
    send_command(ser, *protocol.ZDO_MGMT_PERMIT_JOIN_REQ, donnees)
    print(f"\n[!] Ouverture du réseau Zigbee pour {duree} secondes...")