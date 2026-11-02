"""Communication bas niveau avec le dongle : ouverture du port, envoi et lecture de trames."""

import time

import serial

import config
from zstack import protocol
from zstack.display import format_bytes

def open_port():
    """Ouvre le port série et le prépare. Peut lever serial.SerialException."""
    ser = serial.Serial(config.PORT, config.BAUD_RATE, timeout=config.TIMEOUT)
    time.sleep(config.BOOT_DELAY)
    ser.reset_input_buffer()
    return ser


def send_command(ser, cmd0, cmd1, data=None):
    """Construit et envoie une trame Z-Stack."""
    if data is None:
        data = []
    frame = protocol.build_frame(cmd0, cmd1, data)

    print(f"--> Envoi : cmd0=0x{cmd0:02x} cmd1=0x{cmd1:02x} data=[{format_bytes(data)}]")
    ser.write(frame)


def read_frame(ser):
    """
    Lit une trame. Retourne (cmd0, cmd1, data) ou None si rien de valide
    n'a été reçu (timeout, trame coupée ou checksum faux).
    """
    # 1. On cherche l'octet de début (0xFE), un octet à la fois.
    #    Si le timeout expire, read(1) renvoie b'' : on abandonne.
    while True:
        octet = ser.read(1)
        if not octet:
            return None          # Rien reçu pendant le timeout
        if octet[0] == protocol.SOF:
            break

    # 2. En-tête : longueur + cmd0 + cmd1
    header = ser.read(3)
    if len(header) != 3:
        return None              # Trame coupée
    length, cmd0, cmd1 = header

    # Une longueur impossible veut dire que ce 0xFE n'était pas un vrai début
    if length > protocol.MAX_DATA_LEN:
        print("[!] Longueur invalide, trame ignorée")
        return None

    # 3a. Données
    data_bytes = ser.read(length)
    if len(data_bytes) != length:
        return None              # Trame coupée pendant les données

    # 3b. Checksum
    checksum_bytes = ser.read(1)
    if not checksum_bytes:
        return None              # Trame coupée juste avant le checksum
    checksum = checksum_bytes[0]  # Convertit b'\x61' en entier 97
    data = list(data_bytes)

    # 4. Vérification du checksum
    payload = list(header) + data
    if protocol.calculate_fcs(payload) != checksum:
        print("[!] Trame corrompue (erreur de checksum)")
        return None

    return cmd0, cmd1, data
