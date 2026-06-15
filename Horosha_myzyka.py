import argparse
import os

def attack(mac_address:str): 
    try:
        print(f"*** Proceeding with attacking {mac_address}")
    except Exception as e:
        print(f"[-] Failed to attack: {e}")


def configure_audio_routing(mode: str):
    try:
        # MODE 1: Bridge / Relay Mode
        if mode == 'bridge':
            print("*** Routing Matrix: Bridging Input directly to Output ...")
            
            # Use Android's native command line utilities to force SCO / Communication routing
            os.system("adb shell cmd audio set-mode 3") # MODE_IN_COMMUNICATION is 3
            os.system("adb shell cmd audio set-sco-on true")
            
            print("[+] Audio bridge active! Wait for pohana myzyka.")

        # MODE 2: Local Audio Priority Mode
        elif mode == 'priority':
            print("*** Routing Matrix: Severing external input to favor local apps...")
            
            # Reset system audio state back to normal media playback via shell
            os.system("adb shell cmd audio set-sco-on false")
            os.system("adb shell cmd audio set-mode 0") # MODE_NORMAL is 0
            
            print("[+] Audio matrix reset. Local music apps will now rule the device! Save the day!!!")

    except Exception as e:
        print(f"[-] Failed to configure audio routing via system utilities: {e}")


def doppleganger(new_name: str, mode: str):
    try:
        print(f"[*] Requesting Bluetooth name update to: {new_name}")
        
        # Bypassing the broken local package entirely via your working ADB intent bridge
        adb_cmd = f"adb shell am broadcast -a com.termux.api.execute --es api_method BluetoothSetName --es name '{new_name}' --user 0"
        
        result = os.system(adb_cmd)
        if result != 0:
            raise Exception("ADB intent broadcast rejected by system daemon.")
            
        print(f"[+] Successfully changed Bluetooth name to: {new_name}")
        
        # Trigger the audio routing changes based on your mode selection
        configure_audio_routing(mode)
        
    except Exception as e:
        print(f"[-] Hardware layer rejected name change or audio configuration: {e}")
        return
    
    print("*** Press Ctrl+C to stop the doppleganger.")
    import time
    try:
        while True:
            time.sleep(1) 
    except KeyboardInterrupt:
        print("\n*** Looks like day was saved so stopping doppleganger and cleaning up...")
        # Clean up the audio matrix automatically when you exit!
        configure_audio_routing('priority')

def main():
    parser = argparse.ArgumentParser(
        description='''Operation "Save the day", script for scanning, creating doppleganger and saving the day from the pohana myzyka. 
        To use: python [file_name].py -[command] -[argument](if needed)''', add_help=False)
    
    parser.add_argument("-h", "--help", action="help", help="Show list of commands with description")
    parser.add_argument("-scan", action="store_true", help="List devices and exit (ignored)")
    parser.add_argument("-attack", help="Turning off speaker")
    parser.add_argument("-mac", help="Targeting some address (with -attack)")
    parser.add_argument("-dopple", action="store_true", help="Creates a doppleganger of device which relays or streams audio," 
    " by default relay(bridge)")

    parser.add_argument("-name", type=str, default=None, help="Preferred device name (with -dopple)")
    parser.add_argument("-mode", type=str, choices=["bridge","priority"], default="bridge",
                         help="Changes mode of doppleganger function(bridge or priority) (with -dopple)")
    

    arg = parser.parse_args()

    if arg.scan:
        print("*** Scan is ignored in this version.")
        return

    if arg.attack:
       attack(arg.mac)

    if arg.dopple:
        target_name = arg.name or "POMINAY IMYA"
        doppleganger(target_name, arg.mode)
        return

    print('''*** Welcome to the operation "SAVE THE DAY". No action specified. Use -scan to start or -help for info. ''')

if __name__ == '__main__':
    main()




