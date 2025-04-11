# Import necessary packages
import cv2
import numpy as np
import time
import os
import Cards
import VideoStream

### ----------------------------------- THIS IS THE MAIN SCRIPT -------------------------------- ####

### ---- INITIALIZATION ---- ###
# Define constants and initialize variables

## Camera settings
IM_WIDTH = 1280
IM_HEIGHT = 720 
FRAME_RATE = 10

# Placeholder: replace with network input later
number_of_cards = 4  # Example: wait until 2 cards are detected

## Initialize calculated frame rate because it's calculated AFTER the first time it's displayed
frame_rate_calc = 1
freq = cv2.getTickFrequency()

## Define font to use
font = cv2.FONT_HERSHEY_SIMPLEX

# Initialize Picamera2 video stream
videostream = VideoStream.VideoStream((IM_WIDTH, IM_HEIGHT), FRAME_RATE).start()
time.sleep(1)  # Give the camera time to warm up

# Load the train rank and suit images
path = os.path.dirname(os.path.abspath(__file__))
train_ranks = Cards.load_ranks(path + '/Card_Imgs/')

#We just want the number of the card, we do not care about the suit
#train_suits = Cards.load_suits(path + '/Card_Imgs/')

### ---- MAIN LOOP ---- ###
# The main loop repeatedly grabs frames from the video stream
# and processes them to find and identify playing cards.

cam_quit = 0  # Loop control variable

# Begin capturing frames
while cam_quit == 0:
    # Grab frame from video stream
    image = videostream.read()

    if image is not None:  # Ensure frame is valid before processing
        # Start timer (for calculating frame rate)
        t1 = cv2.getTickCount()

        # Pre-process camera image (gray, blur, and threshold it)
        pre_proc = Cards.preprocess_image(image)
        
        # Find and sort the contours of all cards in the image (query cards)
        cnts_sort, cnt_is_card = Cards.find_cards(pre_proc)

        cards = []
        detected_ranks = []

        for i in range(len(cnts_sort)):
            if cnt_is_card[i] == 1:
                card = Cards.preprocess_card(cnts_sort[i], image)
                # compares the card to the trained ranks and finds the best match
                rank, diff = Cards.match_rank_only(card, train_ranks)

                # It stores the match result into the query card object so it can be drawn later
                card.best_rank_match = rank
                card.rank_diff = diff
                

                image = Cards.draw_results(image, card)
                cards.append(card)
                detected_ranks.append(rank)

        # Check if we have the expected number of cards
        if len(detected_ranks) == number_of_cards:
            print(f"\n🎴 Detected {number_of_cards} cards:")
            for idx, rank in enumerate(detected_ranks):
                print(f"  Card {idx + 1}: {rank}")
            
            # OPTIONAL: Exit after one detection round
            #cam_quit = 1


        # Draw framerate in the corner of the image
        cv2.putText(image, "FPS: " + str(int(frame_rate_calc)), (10, 26), 
                    font, 0.7, (255, 0, 255), 2, cv2.LINE_AA)

        # Display the image with identified cards
        cv2.imshow("Card Detector", image)

        # Calculate framerate
        t2 = cv2.getTickCount()
        time1 = (t2 - t1) / freq
        frame_rate_calc = 1 / time1

    # Poll the keyboard. If 'q' is pressed, exit the main loop.
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        cam_quit = 1

# Close all windows and stop the video stream.
cv2.destroyAllWindows()
videostream.stop()
