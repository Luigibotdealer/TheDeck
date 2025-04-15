import socket
import json

# Data to send
my_variable = 42
results = [1.5, 3.2, 7.8]
data = {
    "variable": my_variable,
    "results": results
}

# Set up client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('10.201.62.123', 12345))  # Pi B IP

client_socket.send(json.dumps(data).encode())

# Optional: receive response
response = client_socket.recv(1024).decode()
print("Server response:", json.loads(response))

client_socket.close()
