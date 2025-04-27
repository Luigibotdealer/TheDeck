"""
Card recognition helper
—————————
detect_cards(num_cards=4, im_size=(640, 480), fps=10, debug=False)  -> list[str]

Returns a list of recognised rank names.  Runs until it sees exactly
`num_cards` cards *all* identified (no “Unknown”), or until the user
presses q / ESC.
"""
from __future__ import annotations
import cv2, os, time, json
import Cards, VideoStream                          # your existing modules

# Default camera constants
DEFAULT_IM_SIZE = (640, 480)                       # width, height

#DEFAULT_IM_SIZE = (1280, 720)                       # width, height

DEFAULT_FPS      = 10

def detect_cards(
        num_cards: int,
        im_size: tuple[int, int] = DEFAULT_IM_SIZE,
        fps: int = DEFAULT_FPS,
        debug: bool = False
    ) -> list[str] | None:

    # Print statement to see what the camera is seeing 
    print(f"[detect_cards] Waiting for {num_cards} card(s)…  (debug={debug})")

    """
    Blocks until `num_cards` unique cards are recognised.
    Returns a list of rank strings, or None if the user aborts.

    Raises RuntimeError if camera cannot be opened.
    """
    im_w, im_h = im_size
    # ① Spin up camera stream
    vs = VideoStream.VideoStream((im_w, im_h), fps).start()
    time.sleep(1)                                  # allow camera warm‑up

    # ② Load rank training images once
    path_here   = os.path.dirname(os.path.abspath(__file__))
    train_ranks = Cards.load_ranks(path_here + "/Card_Imgs/")

    font            = cv2.FONT_HERSHEY_SIMPLEX
    frame_rate_calc = 1
    freq            = cv2.getTickFrequency()

    try:
        while True:
            frame = vs.read()
            if frame is None:
                raise RuntimeError("Camera frame blank — check connection")

            t1 = cv2.getTickCount()
            pre  = Cards.preprocess_image(frame)
            cnts, flags = Cards.find_cards(pre)

            found_cards, ranks = [], []
            for c, is_card in zip(cnts, flags):
                if is_card:
                    card      = Cards.preprocess_card(c, frame)
                    #rank, _   = Cards.match_rank_only(card, train_ranks)
                    #card.best_rank_match = rank
                    frame     = Cards.draw_results(frame, card)

                    found_cards.append(card)
                    #ranks.append(rank)

            # Draw blue contours for visual feedback
            if debug and found_cards:
                cv2.drawContours(frame,
                                 [c.contour for c in found_cards],
                                 -1, (255, 0, 0), 2)

            # Success?
            if len(ranks) == num_cards and "Unknown" not in ranks:
                #! Could be changed to only if in debug mode to improve perfomance
                print(f"[detect_cards] ✅ Detected {num_cards} cards:", ranks)
                return ranks                              # 🎉 done!

            # Show FPS if debug flag
            if debug:
                t2 = cv2.getTickCount()
                frame_rate_calc = 1 / ((t2 - t1) / freq)
                cv2.putText(frame, f"FPS: {int(frame_rate_calc)}",
                            (10, 26), font, 0.7, (255, 0, 255), 2)

                cv2.imshow("Card Detector", frame)
                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), 27):             # q or ESC
                    break
            else:
                # headless mode: small sleep so we don’t peg 100 % CPU
                time.sleep(0.01)

    finally:
        vs.stop()
        cv2.destroyAllWindows()
        print("[detect_cards] Camera cleaned up.")


    return None      # user aborted

# --------------------------------------------------------------------------- #
# if __name__ == "__main__":                         # test‑run
#     ranks = detect_cards(num_cards=4, debug=True)
#     print("Returned:", ranks)
