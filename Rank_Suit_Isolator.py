"""
Takes a card picture and creates a top‑down 200×300 flattened image of it.
Isolates the suit and rank and saves the isolated images.
Runs through A‑K ranks and then the four suits.

Updates in this version (2025‑04‑21)
----------------------------------
* Removed an out‑of‑place reference to `rank_cnts[0]` that caused a NameError.
* Added safety checks so we never access the first element of an empty contour list.
* Added more informative prompts and small refactors for clarity.
"""

import os
import time
from typing import Optional

import cv2
import numpy as np
import Cards  # your custom helper module

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_PATH = os.path.join(SCRIPT_DIR, "Card_Imgs")
os.makedirs(IMG_PATH, exist_ok=True)

#IM_WIDTH, IM_HEIGHT = 1280, 720
IM_WIDTH, IM_HEIGHT = 640, 480

RANK_WIDTH, RANK_HEIGHT = 70, 90
SUIT_WIDTH, SUIT_HEIGHT = 70, 100

# ---------------------------------------------------------------------------
# Helper: select the Iriun (phone) webcam
# ---------------------------------------------------------------------------

def select_camera(max_index: int = 5) -> Optional[cv2.VideoCapture]:
    """Loop through indexes 0‑max_index‑1 and ask the user to confirm."""

    for idx in range(max_index):
        cap = cv2.VideoCapture(idx)
        if not cap.isOpened():
            cap.release()
            continue

        # Grab a single frame for preview
        ret, frame = cap.read()
        if not ret:
            cap.release()
            continue

        cv2.imshow(
            f"Camera {idx} – press any key to select, ESC to skip", frame
        )
        key = cv2.waitKey(0) & 0xFF
        cv2.destroyAllWindows()

        if key != 27:  # not ESC – user accepts this camera
            print(f"[INFO] Selected camera index {idx}.")
            return cap

        cap.release()

    print("[ERROR] Could not find a suitable camera (is Iriun running?).")
    return None


# ---------------------------------------------------------------------------
# Main acquisition loop
# ---------------------------------------------------------------------------

def main() -> None:
    cap = select_camera()
    if cap is None:
        return

    names = [
        "Ace",
        "Two",
        "Three",
        "Four",
        "Five",
        "Six",
        "Seven",
        "Eight",
        "Nine",
        "Ten",
        "Jack",
        "Queen",
        "King",
        "Spades",
        "Diamonds",
        "Clubs",
        "Hearts",
    ]

    counter = 1  # 1‑13 ranks, 14‑17 suits

    for name in names:
        filename = f"{name}.jpg"

        while True:  # allow retake
            print(
                f"Press 'p' to capture {filename}. After capture: 'c' = continue, 'r' = retake"
            )

            # ------------------------------------------------------------------
            # Wait for 'p' to capture a frame
            # ------------------------------------------------------------------
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("[ERROR] Failed to read from camera.")
                    continue
                cv2.imshow("Live", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("p"):
                    image = frame.copy()
                    break

            # ------------------------------------------------------------------
            # Detect the card contour in the captured frame
            # ------------------------------------------------------------------
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY)

            cnts, _ = cv2.findContours(
                thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
            )
            cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
            if not cnts:
                print("[WARN] No contours found – retake the photo.")
                continue

            card_cnt = cnts[0]
            peri = cv2.arcLength(card_cnt, True)
            approx = cv2.approxPolyDP(card_cnt, 0.01 * peri, True)
            pts = np.float32(approx)
            _, _, w, h = cv2.boundingRect(card_cnt)

            # Flatten perspective to 200×300
            warp = Cards.flattener(image, pts, w, h)

            # ------------------------------------------------------------------
            # Extract corner, upscale, and threshold
            # ------------------------------------------------------------------
            corner = warp[0:84, 0:50]
            corner_zoom = cv2.resize(corner, (0, 0), fx=4, fy=4)
            corner_blur = cv2.GaussianBlur(corner_zoom, (5, 5), 0)
            _, corner_thresh = cv2.threshold(
                corner_blur, 155, 255, cv2.THRESH_BINARY_INV
            )

            # ------------------------------------------------------------------
            # Rank or suit isolation
            # ------------------------------------------------------------------
            if counter <= 13:  # ranks A–K
                sub = corner_thresh[15:300, 0:200]
                sub_cnts, _ = cv2.findContours(
                    sub, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
                )
                sub_cnts = sorted(sub_cnts, key=cv2.contourArea, reverse=True)
                if not sub_cnts:
                    print("[WARN] No rank contours – retake.")
                    continue
                x, y, w, h = cv2.boundingRect(sub_cnts[0])
                roi = sub[y : y + h, x : x + w]
                final_img = cv2.resize(roi, (RANK_WIDTH, RANK_HEIGHT))
            else:  # suits
                sub = corner_thresh[186:336, 0:128]
                sub_cnts, _ = cv2.findContours(
                    sub, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
                )
                sub_cnts = sorted(sub_cnts, key=cv2.contourArea, reverse=True)
                if not sub_cnts:
                    print("[WARN] No suit contours – retake.")
                    continue
                x, y, w, h = cv2.boundingRect(sub_cnts[0])
                roi = sub[y : y + h, x : x + w]
                final_img = cv2.resize(roi, (SUIT_WIDTH, SUIT_HEIGHT))

            # ------------------------------------------------------------------
            # Show and decide to keep or retake
            # ------------------------------------------------------------------
            cv2.imshow("Isolated", final_img)
            key = cv2.waitKey(0) & 0xFF
            if key == ord("c"):
                save_path = os.path.join(IMG_PATH, filename)
                cv2.imwrite(save_path, final_img)
                print(f"[INFO] Saved {save_path}")
                break  # go to next card
            elif key == ord("r"):
                print("[INFO] Retaking photo…")
                continue  # stay in the inner while loop

        counter += 1

    cv2.destroyAllWindows()
    cap.release()


if __name__ == "__main__":
    main()
