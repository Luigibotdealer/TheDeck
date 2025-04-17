from socket_sender import send_data_to_pi

# Your code logic
my_variable = 9000
results = [0.1, 0.5, 0.9]

data = {
    "variable": my_variable,
    "results": results
}

# IP and port of the server Raspberry Pi
server_ip = "10.249.109.4"  # change this to your server Pi's IP
port = 12345

response = send_data_to_pi(server_ip, port, data)

print("Response from server:", response)
