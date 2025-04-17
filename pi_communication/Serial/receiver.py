import serial
import time

ser = serial.Serial('/dev/serial0', 9600, timeout=1)
time.sleep(2)  # Give time for connection to stabilize

print("Waiting for data...")

while True:
    if ser.in_waiting > 0:
        data = ser.readline().decode().strip()
        print("Received:", data)
