from pi4_send import send_keyword_to_pi4

# Pretend you're asking your Pi4 how it's doing
print ("Asking Pi to run Card Detection")
# Send keyword

current_num_cards = 2  # default to 4 cards if not specified

response = send_keyword_to_pi4(keyword="run_card_detection", num_cards=current_num_cards,
)

# Interpret the response like a dumb robot
if response is None:
    print("Pi 4 didn't answer")
else:
    print("Pi 4 says:", response)
