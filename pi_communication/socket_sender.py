# socket_sender.py
import socket
import json

def send_data_to_pi(server_ip, port, data):
    """
    Sends a Python dictionary to another Raspberry Pi over a socket connection.

    Args:
        server_ip (str): IP address of the server Raspberry Pi.
        port (int): Port number to connect to.
        data (dict): Data to send (must be JSON-serializable).

    Returns:
        dict: Response received from the server, if any.
    """
    try:
        # Create socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, port))

        # Convert data to JSON and send
        client_socket.send(json.dumps(data).encode())

        # Receive response from server
        response = client_socket.recv(1024).decode()
        client_socket.close()

        return json.loads(response)

    except Exception as e:
        print(f"[Error] Failed to send data: {e}")
        return None
