import socket
import json
from CardDetector import detect_cards

def handle_keyword(keyword):
    """
    Example handler function that responds based on the keyword received.
    You can customize this logic however you want.
    """
    if keyword == "run_card_detection":
        # Now we run the card detection code
        # some_other_script.py
        wanted = 4
        cards  = detect_cards(num_cards=wanted, debug=True)   # run headless
        if cards:
            print(f"I saw {wanted} cards:", cards)
        else:
            print("User aborted or nothing recognised.")

        return {"status": "ready"}
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
                # Call the handler function with the received keyword to figure out the response
                reply = handle_keyword(keyword)
                # Send the reply back to the client (Pi 5)
                conn.sendall(json.dumps(reply).encode())
            except Exception as e:
                print("⚠️ Error:", e)
                conn.sendall(json.dumps({"error": str(e)}).encode())
