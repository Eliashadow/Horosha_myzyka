import argparse
from jnius import autoclass, PythonJavaClass, java_method

BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
BluetoothProfile = autoclass('android.bluetooth.BluetoothProfile')

def attack(mac_address:str): 
    try:
        print(f"*** Proceeding with attacking {mac_address}")
    except Exception as e:
        print(f"[-] Failed to attack: {e}")

class ProfileListener(PythonJavaClass):
  
    __javainterfaces__ = ['android/bluetooth/BluetoothProfile$ServiceListener']

    def __init__(self, mode: str = "bridge"):
        super(ProfileListener, self).__init__()
        self.a2dp_sink = None
        self.a2dp_source = None
        self.mode = mode

    def configure_audio_routing(self):
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Context = autoclass('android.content.Context')
            AudioManager = autoclass('android.media.AudioManager')

            activity = PythonActivity.mActivity
            audio_manager = activity.getSystemService(Context.AUDIO_SERVICE)

            # MODE 1: Bridge / Relay Mode
            if self.mode == 'bridge':
                print("*** Routing Matrix: Bridging Input directly to Output ...")
                # Force routing through SCO (Voice/Call) stream to link input to output
                audio_manager.setBluetoothScoOn(True)
                audio_manager.startBluetoothSco()
                # Set system state to VoIP/Call mode to maintain the link
                audio_manager.setMode(AudioManager.MODE_IN_COMMUNICATION) 
                print("[+] Audio bridge active! Wait for pohana myzyka.")

            # MODE 2: Local Audio Priority Mode
            elif self.mode == 'priority':
                print("*** Routing Matrix: Severing external input to favor local apps...")
                # Kill SCO routing to ensure clean high-quality stereo playback
                audio_manager.stopBluetoothSco()
                audio_manager.setBluetoothScoOn(False)
                # Reset system state back to standard Media Playback mode
                audio_manager.setMode(AudioManager.MODE_NORMAL)
                print("[+] Audio matrix reset. Local music apps will now rule the device! Save the day!!!")

        except Exception as e:
            print(f"[-] Failed to configure audio routing: {e}")

    @java_method('(ILandroid/bluetooth/BluetoothProfile;)V')
    def onServiceConnected(self, profile, proxy):
        if profile == 11: # 11 = BluetoothProfile.A2DP_SINK
            print("\n*** Successfully hooked into Android's A2DP Sink Profile!")
            self.a2dp_sink = proxy
            print("[+] System is now advertising. Pair device via Android Settings.")
        elif profile == 2: # A2DP (Standard Source)
            print("[+] Connected to Speaker Output Stream (Source)")
            self.a2dp_source = proxy


        if self.a2dp_sink and self.a2dp_source:
            print("[+] Both streams ready. Audio routing active!")
            self.configure_audio_routing()

    @java_method('(I)V')
    def onServiceDisconnected(self, profile):
        if profile == 11:
            self.a2dp_sink = None

def doppleganger(new_name: str, mode:str):
    adapter = BluetoothAdapter.getDefaultAdapter()
    if adapter is None:
        print("[-] Bluetooth adapter not found or not supported.")
        return
    
    # Attempt to change the visible Bluetooth broadcast name
    try:
        adapter.setName(new_name)
        print(f"[+] Changed Bluetooth name to: {new_name}")
    except Exception as e:
        print(f"[-] Failed to change name: {e}")
        print("Tip: Check your BLUETOOTH_CONNECT permissions.")
        return

    print("*** Initializing audio sink profile framework...")
    listener = ProfileListener(mode)

    # Request proxy access to Android's A2DP Sink (11) and A2DP Source (2) channels
    adapter.getProfileProxy(None, listener, 11) 
    adapter.getProfileProxy(None, listener, 2)

    print("*** Press Ctrl+C to stop the doppleganger.")
    import time
    try:
        while True:
            time.sleep(1) 
    except KeyboardInterrupt:
        print("\n*** Looks like day was saved so stopping doppleganger and cleaning up...")
        if listener.a2dp_sink:
            adapter.closeProfileProxy(11, listener.a2dp_sink)
        if listener.a2dp_source:
            adapter.closeProfileProxy(2, listener.a2dp_source)
        print("[+] Cleanup complete. Bluetooth reset.")

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




