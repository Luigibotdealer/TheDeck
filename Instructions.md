This is a file created purely to transfer instructions to the pis

This is for the pi 5

import socket
import json

# Set up server socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('192.168.1.11', 12345)) # Use Pi B's IP
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

PI 4:

sudo nano /etc/dhcpcd.conf

interface eth0
static ip_address=192.168.4.1/24

sudo systemctl restart dhcpcd

ip -4 addr show eth0

PI 5:

nmcli con show

nmcli con mod "Wired connection 1" ipv4.addresses 192.168.4.2/24 ipv4.method manual

nmcli con up "Wired connection 1"

ip -4 addr show eth0

Expected: inet 192.168.4.2/24
