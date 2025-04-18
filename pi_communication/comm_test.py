from pi4_sending import send_keyword_to_pi4
import time

# Pretend you're asking your Pi4 how it's doing
print ("Asking Pi to run Card Detection")
# Send keyword

response = send_keyword_to_pi4("run_card_detection")

# Interpret the response like a dumb robot
if response is None:
    print("Pi 4 didn't answer")
elif response.get("status") == "ready":
    print("🤖 Pi 4 says it's feeling READY and awesome.")
else:
    print("🤔 Pi 4 says:", response)
