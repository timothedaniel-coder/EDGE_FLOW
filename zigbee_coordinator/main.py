import serial
import threading
import time
import zstack.handlers as handlers
import zstack.commands as commands
import zstack.protocol as protocol

def ecoute_reseau(ser):
    """Tourne en boucle en arrière-plan pour lire les messages Zigbee."""
    while True:
        try:
            # 1. Attente du Start of Frame (0xFE)
            octet = ser.read(1)
            if not octet or octet[0] != 0xFE:
                continue
            
            # 2. Lecture de la longueur (1 octet)
            longueur = ser.read(1)[0]
            
            # 3. Lecture des commandes (Cmd0 et Cmd1)
            cmd0 = ser.read(1)[0]
            cmd1 = ser.read(1)[0]
            
            # 4. Lecture des données utiles
            data = list(ser.read(longueur))
            
            # 5. Lecture du Checksum (FCS)
            fcs = ser.read(1)[0]
            
            # 6. Assemblage et envoi à l'aiguilleur
            frame = (cmd0, cmd1, data)
            handlers.handle_frame(ser, frame)
            
        except Exception:
            # Si le port se déconnecte ou s'il y a un timeout, on ignore
            # pour ne pas faire crasher le thread d'écoute en arrière-plan.
            pass

def main():
    ser = None
    try:
        # Remplace par /dev/ttyACM0 si ta clé change de nom
        ser = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=0.1)
        
        # 1. On lance l'écouteur Zigbee en arrière-plan
        thread_ecoute = threading.Thread(target=ecoute_reseau, args=(ser,), daemon=True)
        thread_ecoute.start()
        
        # 2. Réveil de la clé pour déclencher la cascade d'initialisation
        print("Initialisation de la clé USB...")
        commands.send_command(ser, *protocol.SYS_RESET_REQ, [0x00])
        
        # On laisse 2 secondes à la clé pour redémarrer et s'auto-configurer
        time.sleep(2) 
        
        print("Coordinateur Zigbee lancé avec succès !")
        print("Tapez 'HELP' pour voir les commandes disponibles.")
        
        # 3. La boucle de commandes interactives
        while True:
            cmd = input("\n[Zigbee CMD] > ").strip().upper()
            
            if cmd == "QUIT":
                break
                
            elif cmd == "PAIR":
                commands.permit_join(ser, 60)
                
            elif cmd == "ON":
                if handlers.prise_connectee:
                    commands.set_plug_state(ser, handlers.prise_connectee, 0x01)
                    print("--> Ordre d'allumage envoyé.")
                else:
                    print("[!] Aucune prise détectée. Tapez PAIR pour l'appairer.")
                    
            elif cmd == "OFF":
                if handlers.prise_connectee:
                    commands.set_plug_state(ser, handlers.prise_connectee, 0x00)
                    print("--> Ordre d'extinction envoyé.")
                else:
                    print("[!] Aucune prise détectée. Tapez PAIR pour l'appairer.")
                
            elif cmd == "TOGGLE":
                if handlers.prise_connectee:
                    commands.set_plug_state(ser, handlers.prise_connectee, 0x02)
                    print("--> Ordre de bascule envoyé.")
                else:
                    print("[!] Aucune prise détectée. Tapez PAIR pour l'appairer.")
                    
            elif cmd == "HELP":
                print("\nCommandes disponibles :")
                print("  PAIR   : Ouvre le réseau pendant 60s pour associer une prise")
                print("  ON     : Allume la prise")
                print("  OFF    : Éteint la prise")
                print("  TOGGLE : Alterne l'état de la prise")
                print("  QUIT   : Ferme le programme")
            
            elif cmd != "":
                print("Commande inconnue. Tapez HELP.")
                
    except KeyboardInterrupt:
        print("\nArrêt manuel (Ctrl+C).")
    except Exception as e:
        print(f"\n[ERREUR FATALE] {e}")
    finally:
        # Fermeture sécurisée du port série
        if ser is not None and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()