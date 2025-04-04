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
train_suits = Cards.load_suits(path + '/Card_Imgs/')

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

        # If there are no contours, do nothing
        if len(cnts_sort) != 0:
            # Initialize a new "cards" list to assign the card objects.
            cards = []
            k = 0

            # For each contour detected:
            for i in range(len(cnts_sort)):
                if cnt_is_card[i] == 1:
                    # Create a card object and extract properties
                    cards.append(Cards.preprocess_card(cnts_sort[i], image))

                    # Find the best rank and suit match for the card
                    cards[k].best_rank_match, cards[k].best_suit_match, \
                        cards[k].rank_diff, cards[k].suit_diff = Cards.match_card(
                        cards[k], train_ranks, train_suits)

                    # Draw center point and match result on the image
                    image = Cards.draw_results(image, cards[k])
                    k += 1
            
            # Draw card contours on image
            if len(cards) != 0:
                temp_cnts = [card.contour for card in cards]
                cv2.drawContours(image, temp_cnts, -1, (255, 0, 0), 2)

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
