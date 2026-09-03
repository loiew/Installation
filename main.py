from pynput import keyboard
from pythonosc import udp_client #user datagram protocol library

# qlab constants
QLAB_IP = "127.0.0.1"
QLAB_PORT = 53000
PASSCODE = "9929" # go to workspace settings > network > OSC access to update

client = udp_client.SimpleUDPClient(QLAB_IP, QLAB_PORT)

# Authenticate with the passcode
print("Authenticating with QLab...")
client.send_message("/connect", [PASSCODE]) # step 1 connect

# listen for trigger (key press)

def on_press(key):
    try:
        if key == keyboard.KeyCode.from_char('m'):
            print("M key pressed! Triggering GO...")
            # client.send_message("/go", []) # go will send everything I think
            
            client.send_message(f"/cue/2/stop", [])
            client.send_message(f"/cue/3/stop", [])
            client.send_message("/cue/1/start", []) # cue will start whatever sequence I have selected

        if key == keyboard.KeyCode.from_char('l'):
            print("L key pressed! Triggering GO...")
            client.send_message(f"/cue/1/stop", [])
            client.send_message(f"/cue/3/stop", [])
            client.send_message("/cue/2/start", [])

        if key == keyboard.KeyCode.from_char('p'):
            print("P key pressed! Triggering GO...")
            client.send_message(f"/cue/1/stop", [])
            client.send_message(f"/cue/2/stop", [])
            client.send_message("/cue/3/start", []) 

        #STOP CODE
        if key == keyboard.KeyCode.from_char('s'):
            print("S key pressed! Stopping...")
            client.send_message("/stop", []) # Stop will stop everything I think

    except Exception as e:
        print(f"Error: {e}")


print("Listening for key press M... Press Ctrl+C to exit. Press S key to stop. Click on window before escaping(ESC) black screen.")
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()