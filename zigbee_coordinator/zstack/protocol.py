"""
Constantes et fonctions de base du protocole MT (Monitor and Test).

Format d'une trame MT :
    SOF | LEN | CMD0 | CMD1 | DATA (LEN octets) | FCS
    0xFE|  1  |   1  |   1  |        ...        |  1

FCS = XOR de tous les octets entre SOF et FCS (LEN, CMD0, CMD1, DATA).
"""

from functools import reduce
import operator

SOF = 0xFE            # Octet de début de trame
MAX_DATA_LEN = 250    # Taille maximale des données d'une trame MT

# Les 3 bits de poids fort de CMD0 donnent le type de commande
TYPES = {1: "SREQ", 2: "AREQ", 3: "SRSP"}

# --- SYSTÈME ---
SYS_PING = (0x21, 0x01)                      # Test de connexion
SYS_RESET_REQ = (0x41, 0x00)                 # Redémarrage du dongle
SYS_RESET_IND = (0x41, 0x80)                 # Le dongle a redémarré
SYS_OSAL_NV_WRITE = (0x21, 0x09)             # Écriture mémoire
SYS_OSAL_NV_WRITE_SRSP = (0x61, 0x09)        # Confirmation d'écriture

# --- RÉSEAU (ZDO) ---
ZDO_STARTUP_FROM_APP = (0x25, 0x40)          # Démarrage antenne
ZDO_STARTUP_FROM_APP_SRSP = (0x65, 0x40)     # Accusé de démarrage
ZDO_MGMT_PERMIT_JOIN_REQ = (0x25, 0x36)      # Ouverture du réseau
ZDO_STATE_CHANGE_IND = (0x45, 0xC0)          # Changement d'état (Coordinateur prêt)
ZDO_END_DEVICE_ANNCE_IND = (0x45, 0xC1)      # Un appareil a rejoint le réseau

# --- AUTO-DÉTECTION (Nouveau) ---
ZDO_ACTIVE_EP_REQ = (0x25, 0x05)             # Demande des Endpoints
ZDO_ACTIVE_EP_RSP = (0x45, 0x85)             # Réponse Endpoints
ZDO_SIMPLE_DESC_REQ = (0x25, 0x04)           # Demande de la fiche technique
ZDO_SIMPLE_DESC_RSP = (0x45, 0x84)           # Réponse fiche technique

# --- COMMANDES D'ACTION (Nouveau) ---
AF_DATA_REQUEST = (0x24, 0x01)               # Envoi d'un ordre standard (Allumer/Éteindre)
MT_RPC_ERROR = (0x60, 0x00)                  # Le dongle refuse la commande

# États du dongle dans le réseau (ZDO_STATE_CHANGE_IND)
STATE_COORDINATOR = 0x09
ZDO_STATES = {
    0x00: "DEV_HOLD",
    0x01: "DEV_INIT",
    0x02: "DEV_NWK_DISC",
    0x03: "DEV_NWK_JOINING",
    0x04: "DEV_NWK_REJOIN",
    0x05: "DEV_END_DEVICE_UNAUTH",
    0x06: "DEV_END_DEVICE",
    0x07: "DEV_ROUTER",
    0x08: "DEV_COORD_STARTING",
    0x09: "DEV_ZB_COORD",
    0x0A: "DEV_NWK_ORPHAN",
}

# Codes d'erreur renvoyés avec MT_RPC_ERROR
RPC_ERRORS = {
    0x01: "sous-système invalide",
    0x02: "commande invalide",
    0x03: "paramètre invalide",
    0x04: "longueur invalide",
}


def calculate_fcs(payload):
    """Calcule le checksum (XOR de tous les octets) d'une trame Z-Stack."""
    return reduce(operator.xor, payload, 0)


def build_frame(cmd0, cmd1, data=None):
    """Construit une trame complète sous forme de bytes, prête à être envoyée."""
    # On évite data=[] dans la signature : une liste par défaut est partagée
    # entre tous les appels de la fonction, ce qui cause des bugs subtils.
    if data is None:
        data = []
    if len(data) > MAX_DATA_LEN:
        raise ValueError(f"Trop de données : {len(data)} octets (maximum {MAX_DATA_LEN})")

    payload = [len(data), cmd0, cmd1] + list(data)   # LEN, CMD0, CMD1, DATA
    return bytes([SOF] + payload + [calculate_fcs(payload)])
