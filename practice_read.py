import serial 
import time 

arduino = serial.Serial(port='/dev/cu.usbmodem141201', baudrate=115200, timeout=1) 
# timeout: maximum time (in seconds) that readline() or read() will wait for data 
# to arrive before giving up and returning whatever it has collected so far.

time.sleep(2) 
# Pauses the execution of your Python script.
# Allow Arduino time to reset on connection. 

while True:
    if arduino.in_waiting > 0:
        line = arduino.readline().decode('utf-8').rstrip()
        if line:
            distance = line #int(line)
            print(distance) #(f"Distance: {distance} cm")