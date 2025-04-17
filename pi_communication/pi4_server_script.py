import socket
import json

def handle_keyword(keyword):
    """
    Example handler function that responds based on the keyword received.
    You can customize this logic however you want.
    """
    if keyword == "get_status":
        return {"status": "ready"}
    elif keyword == "ping":
        return "pong"
    elif keyword == "temperature":
        return 37.2  # example sensor value
    else:
        return {"error": f"Unknown keyword: {keyword}"}

HOST = ''
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"Listening on port {PORT} …")
    while True:
        conn, addr = s.accept()
        with conn:
            print("Connected by", addr)
            raw = conn.recv(4096)
            if not raw:
                continue
            try:
                keyword = json.loads(raw.decode())
                print("→ Keyword received:", keyword)
                reply = handle_keyword(keyword)
                conn.sendall(json.dumps(reply).encode())
            except Exception as e:
                print("⚠️ Error:", e)
                conn.sendall(json.dumps({"error": str(e)}).encode())
