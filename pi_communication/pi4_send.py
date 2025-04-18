import socket, json

def send_keyword_to_pi4(keyword,
                        server_ip="192.168.4.1",
                        port=5000,
                        timeout=None):
    """
    Connects to Pi-4 (server), sends a keyword, and returns the JSON-decoded
    response.

    Parameters
    ----------
    keyword : string
    server_ip : str IP address of the Pi4 server.
    port : int TCP port on which the server is listening.
    timeout : float | None
        • None  -> no timeout (block indefinitely, good for long card detection)  
        • n>0   -> seconds before socket timeout/raise exception.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if timeout is not None:          # leave blocking mode if None
                s.settimeout(timeout)

            s.connect((server_ip, port))

            # Send the keyword
            s.sendall(json.dumps(keyword).encode())

            # Wait for the reply (blocks until data arrives if no timeout)
            raw = s.recv(4096)
            if not raw:
                raise ConnectionError("No response from server")

            return json.loads(raw.decode())

    except Exception as e:
        print(f"⚠️  Error communicating with Pi 4: {e}")
        return None
