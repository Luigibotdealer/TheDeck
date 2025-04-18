import socket
import json

# THis is a function to call to receive a keyword from the Pi 4 server and return the response.

# In this case the Pi 4 acts as the server and the Pi 5 acts as the client

### This function is used to send a keyword to the Pi 4 server and wait for a response.
### You can send "run_card_detection" as the keyword to get the Pi 4 to run the card detection code.
def send_keyword_to_pi4(keyword, server_ip="192.168.4.1", port=5000, timeout=3): 
    """
    Connects to Pi 4 server, sends a keyword, and waits for a response.
    Returns the response (decoded from JSON).
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((server_ip, port))
            # Send the keyword as JSON
            s.sendall(json.dumps(keyword).encode())
            # Wait for response
            raw = s.recv(4096)
            if not raw:
                raise ConnectionError("No response from server")
            return json.loads(raw.decode())
    except Exception as e:
        print(f"⚠️ Error communicating with Pi 4: {e}")
        return None
