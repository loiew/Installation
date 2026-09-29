from pynput import keyboard
from pythonosc import udp_client
import serial
import time

'''
State Tracking (current_cue): The trigger_cue() function checks if the video is already playing. 
If the sensor reports 50.2 cm 50 times in a second, QLab receives the /start command only once 
upon entry to Zone 1.

Clean Main Loop: The distance processing runs cleanly in the while True: main loop, eliminating 
the need to call a function inside on_press().

Data Protection (try/except ValueError): Serial ports sometimes receive partial
or corrupted strings (like "" or "66.1a"). Converting string to float() safely 
inside a try block prevents the script from crashing during execution.
'''

# Arduino Serial Setup
arduino = serial.Serial(port='/dev/cu.usbmodem14201', baudrate=115200, timeout=1) 
time.sleep(2)

# QLab OSC Setup
QLAB_IP = "127.0.0.1"
QLAB_PORT = 53000
PASSCODE = "9929"

client = udp_client.SimpleUDPClient(QLAB_IP, QLAB_PORT)
print("Authenticating with QLab...")
client.send_message("/connect", [PASSCODE])

# Track currently active cue to avoid spamming QLab continuously
current_cue = None

def trigger_cue(cue_number):
    """Utility function to stop other cues and start the target cue."""
    global current_cue
    if current_cue == cue_number:
        return  # Already playing this cue, do nothing!
    
    print(f"Distance changed zone! Switching to Cue {cue_number}...")
    
    # Stop all cues
    for c in [1, 2, 3]:
        if c != cue_number:
            client.send_message(f"/cue/{c}/stop", [])
            
    # Start target cue
    client.send_message(f"/cue/{cue_number}/start", [])
    current_cue = cue_number

def on_press(key):
    """Keyboard shortcuts handler (e.g. Press 'S' to stop everything)."""
    try:
        if key == keyboard.KeyCode.from_char('s'):
            print("S key pressed! Stopping all cues...")
            client.send_message("/stop", [])
            global current_cue
            current_cue = None
    except Exception as e:
        print(f"Key error: {e}")

# Start keyboard listener non-blocking
listener = keyboard.Listener(on_press=on_press)
listener.start()

print("Listening for distance sensor data & keypresses. Press Ctrl+C to exit.")

try:
    while True:
        if arduino.in_waiting > 0:
            line = arduino.readline().decode('utf-8', errors='ignore').rstrip()
            if line:
                try:
                    distance = float(line)
                    print(f"Distance: {distance} in")

                    # Evaluate distance thresholds
                    if distance <= 66:
                        trigger_cue(1)
                    elif 66 < distance <= 132:
                        trigger_cue(2)
                    elif distance > 132:
                        trigger_cue(3)

                except ValueError:
                    # Ignore non-numeric garbage data over serial
                    pass

        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nExiting program...")
    listener.stop()