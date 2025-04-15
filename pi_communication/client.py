import socket
import json

# Data to send
my_variable = 42
results = [1.5, 3.2, 7.8]

# This data is a python dictionary, which is a data structure that holds key-value pairs
data = {
    "variable": my_variable,
    "results": results
}

# Set up client socket
# This is a TCP socket (stream-based reliable connection) (like a phone ready to dial)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('10.249.109.4', 12345))  # Pi B IP

# Converts the Python dictionary to a JSON string, then encodes it to bytes, then sends it 
client_socket.send(json.dumps(data).encode())

# Optional: receive response
response = client_socket.recv(1024).decode()
print("Server response:", json.loads(response))

# Communication closed, phone is closed
client_socket.close()

