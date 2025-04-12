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
# Max resolution: 4608 × 2592

IM_WIDTH = 2304
IM_HEIGHT = 1296

#IM_WIDTH = 640
#IM_HEIGHT = 480 
FRAME_RATE = 10

# Camera values: {Model: imx708, UnitCellSize: 1400,1400, Location: 2, Rotation: 180, PixelArraySize: (4608, 2592), PixelArrayActiveAreas: [(16,24,4608,2592)] ... 

# Placeholder: replace with network input later
number_of_cards = 4  # Example: wait until 4 cards are detected

## Initialize calculated frame rate because it's calculated AFTER the first time it's displayed
frame_rate_calc = 1
freq = cv2.getTickFrequency()

## Define font to use (MUST also reference this in Cards.draw_results)
font = cv2.FONT_HERSHEY_SIMPLEX

# Initialize Picamera2 video stream
videostream = VideoStream.VideoStream((IM_WIDTH, IM_HEIGHT), FRAME_RATE).start()
time.sleep(1)  # Give the camera time to warm up

# Load only the train rank images (we're ignoring suits)
path = os.path.dirname(os.path.abspath(__file__))
train_ranks = Cards.load_ranks(path + '/Card_Imgs/')

### ---- MAIN LOOP ---- ###
cam_quit = 0  # Loop control variable

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

        # Prepare containers for each iteration
        cards = []
        detected_ranks = []  # We still keep this if we want rank-only lists

        # --- PROCESS DETECTED CARDS --- #
        for i in range(len(cnts_sort)):
            if cnt_is_card[i] == 1:
                # Extract features for each card
                card = Cards.preprocess_card(cnts_sort[i], image)
                
                # Compare the card to the trained ranks and find the best match
                rank, diff = Cards.match_rank_only(card, train_ranks)

                # Store the match result in the card object
                card.best_rank_match = rank
                card.rank_diff = diff

                # Draw rank text + difference on the image
                image = Cards.draw_results(image, card)

                # Collect them for later use
                cards.append(card)
                detected_ranks.append(rank)

        # --- DRAW CONTOURS FOR VISUAL FEEDBACK --- #
        if len(cards) > 0:
            temp_cnts = [card.contour for card in cards]
            cv2.drawContours(image, temp_cnts, -1, (255, 0, 0), 2)

        # --- IF WE'VE DETECTED THE EXPECTED NUMBER OF CARDS, PRINT THEM OUT --- #
        if len(detected_ranks) == number_of_cards:
            if "Unknown" not in detected_ranks:
                print(f"\n{detected_ranks}")
                print("ALL CARDS RECOGNISED")
                cam_quit = 1  # Stop the program after successful recognition
            # Else: skip printing anything if there's an Unknown


        # --- DRAW THE FRAMERATE IN THE CORNER --- #
        cv2.putText(image, "FPS: " + str(int(frame_rate_calc)), (10, 26),
                    font, 0.7, (255, 0, 255), 2, cv2.LINE_AA)

        # Show the annotated image
        cv2.imshow("Card Detector", image)

        # Calculate framerate
        t2 = cv2.getTickCount()
        time1 = (t2 - t1) / freq
        frame_rate_calc = 1 / time1

    # Press 'q' to quit
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        cam_quit = 1

# Cleanup
cv2.destroyAllWindows()
videostream.stop()