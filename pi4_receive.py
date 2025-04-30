import socket, json
from CardDetector import detect_cards

def handle_keyword(keyword, num_cards):

    if keyword == "run_card_detection":
        print("[server] Running card detection…")
        try:
            ## LETS CHANGE IT TO NO DEBUG
            cards = detect_cards(num_cards=num_cards, debug=True, num_pi=4)
        except Exception as e:
            print(f"⚠️ [server] Error during detection: {e}")
            return {"status": "error", "message": str(e)}

        # IF THE SCAN IS SUCCESSFUL, WE RETURN ONLY THE CARDS
        if cards:
            print(f"[server] I saw {num_cards} cards:", cards)
            return cards
        else:
            print("[server] User aborted or nothing recognised.")
            return {"status": "aborted"}

HOST, PORT = '', 5000
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"[server] Listening on port {PORT}…")
    while True:
        conn, addr = s.accept()
        with conn:
            print("[server] Connected by", addr)
            raw = conn.recv(4096)
            if not raw:
                continue
            try:
                data = data = json.loads(raw.decode())

                keyword = data.get("keyword")
                num_cards = data.get("num_cards", 1)  # default to 1 cards if not specified
                print("[server] Received keyword:", keyword, "NUMBER OF CARDS TO DETECT:", num_cards)

                reply = handle_keyword(keyword, num_cards)   # run card detect here
                conn.sendall(json.dumps(reply).encode())
                print("[server] ← Reply sent:", reply)

            except Exception as e:
                print("⚠️ [server] Error:", e)
                conn.sendall(json.dumps({"error": str(e)}).encode())
