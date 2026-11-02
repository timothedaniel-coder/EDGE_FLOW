import zstack.protocol as protocol
import zstack.commands as commands

# Variable globale pour stocker l'adresse de la prise et l'utiliser dans le menu
prise_connectee = None

# Garde tes fonctions on_reset, on_config_response, on_state_change, on_rpc_error ici...

def on_startup_response(data):
    if data and data[0] == 0x00:
        print("[INFO] Lancement du réseau en cours, patientez...")
    else:
        print("[ERREUR] Échec du lancement du réseau")

def on_device_joined(ser, data):
    if len(data) < 12: return
    nwk_addr = (data[3] << 8) | data[2]
    mac_bytes = data[4:12]
    mac_hex = ":".join(f"{b:02x}" for b in reversed(mac_bytes))

    print("\n[+] NOUVEL APPAREIL CONNECTÉ !")
    print(f"    Adresse réseau (ID) : {hex(nwk_addr)}")
    print(f"    Adresse MAC (IEEE)  : {mac_hex}")
    print("    [>] Interrogation de l'appareil pour découvrir ses capacités...")
    
    commands.request_active_endpoints(ser, nwk_addr)

def on_active_ep_rsp(ser, data):
    if data[2] == 0x00:
        nwk_addr = (data[4] << 8) | data[3]
        nb_endpoints = data[5]
        endpoints = data[6:6+nb_endpoints]
        print(f"    [INFO] L'appareil {hex(nwk_addr)} possède {nb_endpoints} endpoint(s) : {endpoints}")
        
        if nb_endpoints > 0:
            commands.request_simple_descriptor(ser, nwk_addr, endpoints[0])

def on_simple_desc_rsp(data):
    global prise_connectee
    if data[2] == 0x00:
        nwk_addr = (data[4] << 8) | data[3]
        endpoint = data[6]
        device_id = (data[10] << 8) | data[9]
        
        print(f"\n[SUCCESS] Identification terminée pour {hex(nwk_addr)} (Endpoint {endpoint}) :")
        
        if device_id in [0x0009, 0x0051, 0x0100]:
            print("    [!] AUTO-DÉTECTION : C'est une Prise connectée ou une Ampoule (On/Off) !")
            prise_connectee = nwk_addr  # On sauvegarde l'adresse pour le menu principal

def handle_frame(ser, frame):
    """Aiguille une trame reçue vers la bonne fonction."""
    cmd0, cmd1, data = frame
    commande = (cmd0, cmd1)

    if commande == protocol.SYS_RESET_IND:
        pass # Appelle ton on_reset(ser, data)
    elif commande == protocol.SYS_OSAL_NV_WRITE_SRSP:
        pass # Appelle ton on_config_response(ser, data)
    elif commande == protocol.ZDO_STATE_CHANGE_IND:
        pass # Appelle ton on_state_change(ser, data)
    elif commande == protocol.ZDO_STARTUP_FROM_APP_SRSP:
        on_startup_response(data)
    elif commande == protocol.ZDO_END_DEVICE_ANNCE_IND:
        on_device_joined(ser, data)
    elif commande == protocol.ZDO_ACTIVE_EP_RSP:
        on_active_ep_rsp(ser, data)
    elif commande == protocol.ZDO_SIMPLE_DESC_RSP:
        on_simple_desc_rsp(data)
    elif commande == protocol.MT_RPC_ERROR:
        pass # Appelle ton on_rpc_error(data)