import socket
import json

# Set up server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('10.249.109.4', 12345))  # Use Pi B's IP
server_socket.listen(1)

print("Waiting for connection...")
conn, addr = server_socket.accept()
print(f"Connected by {addr}")

# Receive data
data = conn.recv(1024).decode()
received = json.loads(data)
print("Received:", received)

# Send back a response (optional)
response = {"status": "OK", "received_variable": received["variable"]}
conn.send(json.dumps(response).encode())

conn.close()