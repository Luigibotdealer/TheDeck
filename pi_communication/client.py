#!/usr/bin/env python3
import socket, json, time

SERVER_IP = "192.168.4.1"   # IP of Pi 4
# IP of Pi 5 is 192.168.4.2
PORT = 5000

# Example arrays to send
payloads = [
    [1, 2, 3],
    [10, 20, 30],
    [100, 200, 300]
]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((SERVER_IP, PORT))
    for data in payloads:
        print("→ Sending:", data)
        s.sendall(json.dumps(data).encode())
        reply = json.loads(s.recv(4096).decode())
        print("← Received:", reply)
        time.sleep(1)
