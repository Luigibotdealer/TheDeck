import serial
import time

ser = serial.Serial('/dev/serial0', 9600, timeout=1)
time.sleep(2)

message = "Hello from Pi A!"
ser.write((message + '\n').encode())
print("Sent:", message)
