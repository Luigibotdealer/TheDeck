from pi4_client_utils import send_keyword_to_pi4
import time

# Pretend you're asking your Pi4 how it's doing
print("Asking Pi 4 how it's feeling today...")

# Send keyword
response = send_keyword_to_pi4("get_status")

# Interpret the response like a dumb robot
if response is None:
    print("😵 Pi 4 didn't answer... maybe it needs a hug.")
elif response.get("status") == "ready":
    print("🤖 Pi 4 says it's feeling READY and awesome.")
else:
    print("🤔 Pi 4 says:", response)
