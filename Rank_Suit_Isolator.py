### Takes a card picture and creates a top-down 200x300 flattened image
### of it. Isolates the suit and rank and saves the isolated images.
### Runs through A - K ranks and then the 4 suits.

# Import necessary packages
import cv2
import numpy as np
import time
import Cards
import os

img_path = os.path.dirname(os.path.abspath(__file__)) + '/Card_Imgs/'

IM_WIDTH = 1280
IM_HEIGHT = 720

RANK_WIDTH = 70
RANK_HEIGHT = 125

SUIT_WIDTH = 70
SUIT_HEIGHT = 100

# Function to select Iriun Webcam

def select_camera():
    for i in range(5):  # Trying first 5 indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                cv2.imshow(f'Press any key if this is the Iriun Webcam (Camera {i})', frame)
                key = cv2.waitKey(0) & 0xFF
                cv2.destroyAllWindows()

                if key != 27:  # If user confirms (not pressing 'ESC')
                    print(f'Iriun Webcam selected at index {i}.')
                    return cap
            cap.release()
    print('Could not find Iriun Webcam. Please make sure it is properly connected.')
    return None

cap = select_camera()

if cap is None:
    exit()

# Use counter variable to switch from isolating Rank to isolating Suit
i = 1

for Name in ['Ace','Two','Three','Four','Five','Six','Seven','Eight',
             'Nine','Ten','Jack','Queen','King','Spades','Diamonds',
             'Clubs','Hearts']:

    filename = Name + '.jpg'

    while True:  # Allows retaking of photo
        print(f'Press "p" to take a picture of {filename}. Press "r" to retake or "c" to continue after taking the picture.')
        
        # Press 'p' to take a picture
        while True:
            ret, frame = cap.read()
            cv2.imshow("Card", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("p"):
                image = frame
                break

        # Pre-process image
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray,(5,5),0)
        retval, thresh = cv2.threshold(blur,100,255,cv2.THRESH_BINARY)

        # Find contours and sort them by size
        cnts, hier = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key=cv2.contourArea,reverse=True)

        # Assume largest contour is the card. If there are no contours, print an error
        if len(cnts) == 0:
            print('No contours found! Retake the photo.')
            continue

        card = cnts[0]

        # Approximate the corner points of the card
        peri = cv2.arcLength(card,True)
        approx = cv2.approxPolyDP(card,0.01*peri,True)
        pts = np.float32(approx)

        x,y,w,h = cv2.boundingRect(card)

        # Flatten the card and convert it to 200x300
        warp = Cards.flattener(image,pts,w,h)

        # Grab corner of card image, zoom, and threshold
        corner = warp[0:84, 0:32]
        corner_zoom = cv2.resize(corner, (0,0), fx=4, fy=4)
        corner_blur = cv2.GaussianBlur(corner_zoom,(5,5),0)
        retval, corner_thresh = cv2.threshold(corner_blur, 155, 255, cv2. THRESH_BINARY_INV)

        # Isolate suit or rank
        if i <= 13: # Isolate rank
            rank = corner_thresh[20:185, 0:128]
            rank_cnts, hier = cv2.findContours(rank, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            rank_cnts = sorted(rank_cnts, key=cv2.contourArea,reverse=True)
            x,y,w,h = cv2.boundingRect(rank_cnts[0])
            rank_roi = rank[y:y+h, x:x+w]
            rank_sized = cv2.resize(rank_roi, (RANK_WIDTH, RANK_HEIGHT), 0, 0)
            final_img = rank_sized

        if i > 13: # Isolate suit
            suit = corner_thresh[186:336, 0:128]
            suit_cnts, hier = cv2.findContours(suit, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            suit_cnts = sorted(suit_cnts, key=cv2.contourArea,reverse=True)
            x,y,w,h = cv2.boundingRect(suit_cnts[0])
            suit_roi = suit[y:y+h, x:x+w]
            suit_sized = cv2.resize(suit_roi, (SUIT_WIDTH, SUIT_HEIGHT), 0, 0)
            final_img = suit_sized

        cv2.imshow("Image",final_img)

        # Save or Retake option
        key = cv2.waitKey(0) & 0xFF
        if key == ord('c'):
            cv2.imwrite(img_path+filename,final_img)
            break
        elif key == ord('r'):
            print('Retaking photo...')

    i += 1

cv2.destroyAllWindows()
cap.release()
