import socket, json
from CardDetector import detect_cards

def handle_keyword(keyword):
    # HOW MANY CARDS DO WE WANT?
    wanted = 2        # ← note: removed the stray comma so wanted is int(2)

    if keyword == "run_card_detection":
        print("[server] Running card detection…")
        cards = detect_cards(num_cards=wanted, debug=True)

        if cards:
            print(f"[server] I saw {wanted} cards:", cards)
            # Send the actual list back so Pi‑5 can use it
            return {"status": "success", "cards": cards}
        else:
            print("[server] User aborted or nothing recognised.")
            return {"status": "aborted"}

    # Unknown keyword
    return {"error": f"Unknown keyword: {keyword}"}

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
                keyword = json.loads(raw.decode())
                print("[server] → Keyword received:", keyword)

                reply = handle_keyword(keyword)   # run card detect here
                conn.sendall(json.dumps(reply).encode())
                print("[server] ← Reply sent:", reply)

            except Exception as e:
                print("⚠️ [server] Error:", e)
                conn.sendall(json.dumps({"error": str(e)}).encode())
