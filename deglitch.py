from pynput import keyboard
from pythonosc import udp_client
import serial
import time

# Arduino Serial Setup
arduino = serial.Serial(port='/dev/cu.usbmodem142101', baudrate=115200, timeout=1) 
time.sleep(2)

# QLab OSC Setup
QLAB_IP = "127.0.0.1"
QLAB_PORT = 53000
PASSCODE = "9929"

client = udp_client.SimpleUDPClient(QLAB_IP, QLAB_PORT)
print("Authenticating with QLab...")
client.send_message("/connect", [PASSCODE])

# Track active cue state and debounce counter
current_cue = None
pending_cue = None
consecutive_reads = 0
DEBOUNCE_THRESHOLD = 3  # Require 3 consecutive readings in a new zone before switching

def get_zone(distance):
    """Map distance (inches) to a cue number with hysteresis safety."""
    print(distance)
    if distance <= 66:
        print('less than 66')
        return 1
    elif 66 < distance <= 132:
        print('less than 132')
        return 2
    else:
        print('more than 132')
        return 3

def trigger_cue(cue_number):
    """Switches QLab cues cleanly."""
    global current_cue
    if current_cue == cue_number:
        return

    print(f"Switching to Cue {cue_number}...")

    # Stop previous cue specifically rather than looping through all cues
    if current_cue is not None:
        client.send_message(f"/cue/{current_cue}/stop", [])

    # Start target cue
    client.send_message(f"/cue/{cue_number}/start", [])
    current_cue = cue_number

def on_press(key):
    """Keyboard shortcuts handler (Press 'S' to stop everything)."""
    global current_cue
    try:
        if key == keyboard.KeyCode.from_char('s'):
            print("S key pressed! Stopping all cues...")
            client.send_message("/stop", [])
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
            # Read latest line from serial
            line = arduino.readline().decode('utf-8', errors='ignore').rstrip()
            if line:
                try:
                    distance = float(line)
                    target_zone = get_zone(distance)

                    # Debounce check to ignore random sensor spikes
                    if target_zone != current_cue:
                        if target_zone == pending_cue:
                            consecutive_reads += 1
                        else:
                            pending_cue = target_zone
                            consecutive_reads = 1

                        if consecutive_reads >= DEBOUNCE_THRESHOLD:
                            trigger_cue(target_zone)
                    else:
                        pending_cue = None
                        consecutive_reads = 0

                except ValueError:
                    pass

        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nExiting program...")
    listener.stop()