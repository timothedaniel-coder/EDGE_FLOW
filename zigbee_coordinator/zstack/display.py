"""Fonctions d'affichage (rien d'autre que des print)."""

from zstack import protocol


def format_bytes(octets):
    """Affiche une liste d'octets en hexadécimal : [0x79, 0x7] -> '79 07'."""
    return " ".join(f"{b:02x}" for b in octets)


def print_frame(cmd0, cmd1, data):
    """Affiche une trame reçue de façon lisible."""
    type_cmd = protocol.TYPES.get(cmd0 >> 5, "?")   # bits 7-5 : type de commande
    subsystem = cmd0 & 0x1F                         # bits 4-0 : sous-système
    print(f"<-- {type_cmd} sous-système=0x{subsystem:02x} cmd0=0x{cmd0:02x} cmd1=0x{cmd1:02x} data=[{format_bytes(data)}]")