#!/usr/bin/env python3
import socket, json

HOST = ''          # Listen on all interfaces
PORT = 5000        # Any free port

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"Listening on port {PORT} …")
    conn, addr = s.accept()
    with conn:
        print("Connected by", addr)
        while True:
            raw = conn.recv(4096)
            if not raw:
                break
            arr = json.loads(raw.decode())
            print("→ Received:", arr)
            # Example response: double each number
            reply = json.dumps([x * 2 for x in arr]).encode()
            conn.sendall(reply)
