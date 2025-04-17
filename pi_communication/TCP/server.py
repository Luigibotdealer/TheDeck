# Example server.py (minimum working version)
import socket
import json

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('10.217.5.52', 12345))  # or '' for all interfaces
server_socket.listen(1)

print("Waiting for connection...")
conn, addr = server_socket.accept()
print(f"Connected by {addr}")

# Receive data
data = conn.recv(1024).decode()
received = json.loads(data)
print("Received:", received)

# ✅ SEND A RESPONSE
response = {"status": "OK", "received_variable": received["variable"]}
conn.send(json.dumps(response).encode())

conn.close()
