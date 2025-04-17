import serial
ser = serial.Serial('/dev/serial0', 9600, timeout=1)
ser.readline()  # This waits for a message
