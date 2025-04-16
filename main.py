#import serial 
import time
from VideoStream import VideoStream

class Poker:
    def __init__(self):
        self.dealerHand = [0]
        self.playerHand = [0, 0]
        self.winnings = 0
       # self.arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
       # time.sleep(2)

       # self.videostream = VideoStream((640, 480), 10).start()

        time.sleep(1)  # Give the camera time to warm up
        
    #! Placeholder for the card detection logic
    def extract_card_from_camera(self):
        # import cv2
        # import os
        # import Cards
        # import time

        # def get_card_values(card_names):
        #     card_values = {
        #         'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5,
        #         'Six': 6, 'Seven': 7, 'Eight': 8, 'Nine': 9,
        #         'Ten': 10, 'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11
        #     }
        #     return [card_values.get(card, 0) for card in card_names]
        
        # number_of_cards = 2
        # ## Initialize calculated frame rate because it's calculated AFTER the first time it's displayed
        # frame_rate_calc = 1
        # freq = cv2.getTickFrequency()
       
        # ## Define font to use (MUST also reference this in Cards.draw_results)
        # font = cv2.FONT_HERSHEY_SIMPLEX

        # # Load only the train rank images (we're ignoring suits)
        # path = os.path.dirname(os.path.abspath(__file__))
        # train_ranks = Cards.load_ranks(path + '/Card_Imgs/')

        # timeout = time.time() + 10  # Shorter timeout

        # while time.time() < timeout:
        #     image = self.videostream.read()
        #     if image is not None:  # Ensure frame is valid before processing
        #         # Start timer (for calculating frame rate)
        #         t1 = cv2.getTickCount()

        #         # Pre-process camera image (gray, blur, and threshold it)
        #         pre_proc = Cards.preprocess_image(image)
                
        #         # Find and sort the contours of all cards in the image (query cards)
        #         cnts_sort, cnt_is_card = Cards.find_cards(pre_proc)

        #         # Prepare containers for each iteration
        #         cards = []
        #         detected_ranks = []  # We still keep this if we want rank-only lists

        #         # --- PROCESS DETECTED CARDS --- #
        #         for i in range(len(cnts_sort)):
        #             if cnt_is_card[i] == 1:
        #                 # Extract features for each card
        #                 card = Cards.preprocess_card(cnts_sort[i], image)
                        
        #                 # Compare the card to the trained ranks and find the best match
        #                 rank, diff = Cards.match_rank_only(card, train_ranks)

        #                 # Store the match result in the card object
        #                 card.best_rank_match = rank
        #                 card.rank_diff = diff

        #                 # Draw rank text + difference on the image
        #                 image = Cards.draw_results(image, card)

        #                 # Collect them for later use
        #                 cards.append(card)
        #                 detected_ranks.append(rank)
        #                 card_values = get_card_values(detected_ranks)


        #         # --- DRAW CONTOURS FOR VISUAL FEEDBACK --- #
        #         if len(cards) > 0:
        #             temp_cnts = [card.contour for card in cards]
        #             cv2.drawContours(image, temp_cnts, -1, (255, 0, 0), 2)

        #         # --- IF WE'VE DETECTED THE EXPECTED NUMBER OF CARDS, PRINT THEM OUT --- #
        #         if len(detected_ranks) == number_of_cards:
        #             if "Unknown" not in detected_ranks:
        #                 print(f"\n{detected_ranks}")
        #                 print("ALL CARDS RECOGNISED")
        #                 cam_quit = 1  # Stop the program after successful recognition
        #             # Else: skip printing anything if there's an Unknown


        #         # --- DRAW THE FRAMERATE IN THE CORNER --- #
        #         cv2.putText(image, "FPS: " + str(int(frame_rate_calc)), (10, 26),
        #                     font, 0.7, (255, 0, 255), 2, cv2.LINE_AA)

        #         # Show the annotated image
        #         cv2.imshow("Card Detector", image)

        #         # Calculate framerate
        #         t2 = cv2.getTickCount()
        #         time1 = (t2 - t1) / freq

        return card_values if card_values else 0

    def takeBets(self):
        #! Placeholder to read the input from the Arduino on the number of chips each player has
        playerBet = 5
        return playerBet

    def calculate_total(self, hand):

        # Calculate the total value of the hand, adjusting for Aces
        total = sum(hand)
        num_aces = hand.count(11)
        while total > 21 and num_aces > 0:
            total -= 10
            num_aces -= 1
        return total

    def initialDeal(self):
        #! Deal 2 cards to the player
        #self.playerHand = self.extract_card_from_camera()
        
        while True:
            print(f"Player cards: {self.playerHand}")
            confirmation = input("Are the detected card values correct? Yes or No: ").strip().lower()
            if confirmation == 'yes':
                break
            elif confirmation == 'no':
                print("Re-detecting cards... Please lay them down again.")
                self.playerHand = [0, 0]
                self.initialDeal()
            else:
                print("Please enter 'Yes' or 'No'.")

        # Deal 1 card to the dealer
       # self.dealerHand = [self.extract_card_from_camera()]

        # Update totals
        self.playerTotal = self.calculate_total(self.playerHand)
        self.dealerTotal = self.calculate_total(self.dealerHand)

        print( self.playerTotal)
        print(self.dealerTotal)
        return self.playerTotal, self.dealerTotal

    def play(self):
        playerTotal = 0
        dealerTotal = 0

        playerBet = self.takeBets()
        self.initialDeal()

        playerTotal = self.calculate_total(self.playerHand)
        dealerTotal = self.calculate_total(self.dealerHand)
        while input("Hit or Stay? ").lower() == 'hit':
            self.playerHand.append(self.extract_card_from_camera())
            playerTotal = self.calculate_total(self.playerHand)
            if playerTotal == 21:
                print("You hit 21!")
                break
            elif playerTotal > 21:
                print("You busted!")            
                break                    

        while dealerTotal < 17:
            self.dealerHand.append(self.extract_card_from_camera())
            dealerTotal = self.calculate_total(self.dealerHand)
            if dealerTotal > 16:
                break

        if playerTotal == 21 and len(self.playerHand) == 2:
            if dealerTotal == 21 and len(self.dealerHand) == 2:
                print("It's a tie! Dealer wins in a blackjack tie.")
                playerWon = False
            else:
                print("Blackjack! You win!")
                playerWon = True
        elif dealerTotal == 21 and len(self.dealerHand) == 2:
            print("Dealer has a blackjack. You lose.")
            playerWon = False
        elif playerTotal > 21:
            playerWon = False
        elif dealerTotal > 21:
            playerWon = True
        elif playerTotal == dealerTotal:
            print("It's a tie, but the dealer wins.")
            playerWon = False
        else:
            playerWon = (playerTotal > dealerTotal)

        if playerWon:
            self.winnings += playerBet
        else:
            self.winnings -= playerBet

        print('Your winnings =', self.winnings)

    def main(self):
        while True:
            self.play()
            newGame = input("Do you want to play another round? Yes or No ").lower()
            if newGame == 'no':
                print("Thank you for playing!")
                break


# ✅ This will now run correctly when you run the script
if __name__ == "__main__":
    game = Poker()
    game.main()
