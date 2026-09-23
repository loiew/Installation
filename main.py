from pynput import keyboard
from pythonosc import udp_client #user datagram protocol library

import serial
import time

arduino = serial.Serial(port='/dev/cu.usbmodem142201', baudrate=115200, timeout=1) 
time.sleep(2)

# qlab constants
QLAB_IP = "127.0.0.1"
QLAB_PORT = 53000
PASSCODE = "9929" # go to workspace settings > network > OSC access to update

client = udp_client.SimpleUDPClient(QLAB_IP, QLAB_PORT)

# Authenticate with the passcode
print("Authenticating with QLab...")
client.send_message("/connect", [PASSCODE]) # step 1 connect

def read_arduino():
    while True:
        if arduino.in_waiting > 0:
            line = arduino.readline().decode('utf-8', errors='ignore').rstrip()
            if line:
                distance = float(line)
                print(distance)
                return distance # Process distance here or update a global variable

# listen for trigger (key press)
def on_press(key):
    try:
        value = read_arduino()
        if value <= 66: #if key == keyboard.KeyCode.from_char('m'):
            print("M key pressed! Triggering GO...")
            # client.send_message("/go", []) # go will send everything I think
            
            client.send_message(f"/cue/2/stop", [])
            client.send_message(f"/cue/3/stop", [])
            client.send_message("/cue/1/start", []) # cue will start whatever sequence I have selected

        if value > 66 and value <= 132: #key == keyboard.KeyCode.from_char('l'):
            print("L key pressed! Triggering GO...")
            client.send_message(f"/cue/1/stop", [])
            client.send_message(f"/cue/3/stop", [])
            client.send_message("/cue/2/start", [])

        if value > 132: #key == keyboard.KeyCode.from_char('p'):
            print("P key pressed! Triggering GO...")
            client.send_message(f"/cue/1/stop", [])
            client.send_message(f"/cue/2/stop", [])
            client.send_message("/cue/3/start", []) 

        #STOP CODE
        if key == keyboard.KeyCode.from_char('s'):
            print("S key pressed! Stopping...")
            client.send_message("/stop", [])

    except Exception as e:
        print(f"Error: {e}")


print("Listening for key press M... Press Ctrl+C to exit. Press S key to stop. Click on window before escaping(ESC) black screen.")
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()