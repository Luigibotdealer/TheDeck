import serial
import time

# Read serial data from Arduino
port='/dev/ttyACM0'
baudrate=9600
timeout=1000
arduino = serial.Serial(port, baudrate, timeout=timeout)
def read_arduino_serial():


   if not arduino.is_open: #Break loop if serial port is not open
       print("Failed to open Arduino Serial port.")
       return
  
   data = arduino.readline()  # Read a line from the serial port
   line = data.decode('utf-8').strip() #decodes the data into utf-8 and strips whitespace()

   if "," in line:
       splitline = line.split(',')  # Split the line by commas
       processed_val =[]
       for item in splitline:
           try:
               processed_val.append(int(item))  # Convert each item to an integer
           except ValueError:
               processed_val.append(item)
   else:
       print(line)
       processed_val = ["C",0]
   processed_val[1] = processed_val[1]
   return processed_val  # Return the split data as a list A,9


while True:
   A_Serial = read_arduino_serial()
  
   if A_Serial[0]== "C":
       print("Player Chips:"+str(A_Serial[1]))
  
