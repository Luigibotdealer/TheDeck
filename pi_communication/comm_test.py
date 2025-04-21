from pi4_send import send_keyword_to_pi4

# Pretend you're asking your Pi4 how it's doing
print ("Asking Pi to run Card Detection")
# Send keyword

response = send_keyword_to_pi4("run_card_detection")

# Interpret the response like a dumb robot
if response is None:
    print("Pi 4 didn't answer")
else:
    print("Pi 4 says:", response)
