import serial 
import time
from VideoStream import VideoStream

class Blackjack:
    def __init__(self):
        self.dealerHand = []
        self.playerHand = []
        self.winnings = 0
        self.numPlayerCards = 0
        self.numDealerCards = 0
        self.initialplayerPosition = 300
        self.currentplayerPosition = self.initialplayerPosition
        self.initialdealerPosition = 40
        self.currentdealerPosition = self.initialdealerPosition
        self.homePosition = 180
        self.initialscoopPosition = 330
        self.finalscoopPosition = 30
        self.cardSpacing = 10

        self.arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        time.sleep(2)

        # self.videostream = VideoStream((640, 480), 10).start()
        # time.sleep(1)  # Give the camera time to warm up
   
    # def extract_cards_from_camera(self,number_of_cards):
    #     import cv2
    #     import os
    #     import Cards
    #     import time

    #     def get_card_values(card_names):
    #         card_values = {
    #             'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5,
    #             'Six': 6, 'Seven': 7, 'Eight': 8, 'Nine': 9,
    #             'Ten': 10, 'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11
    #         }
    #         return [card_values.get(card, 0) for card in card_names]
        
    #     ## Initialize calculated frame rate because it's calculated AFTER the first time it's displayed
    #     frame_rate_calc = 1
    #     freq = cv2.getTickFrequency()
       
    #     ## Define font to use (MUST also reference this in Cards.draw_results)
    #     font = cv2.FONT_HERSHEY_SIMPLEX

    #     # Load only the train rank images (we're ignoring suits)
    #     path = os.path.dirname(os.path.abspath(__file__))
    #     train_ranks = Cards.load_ranks(path + '/Card_Imgs/')

    #     timeout = time.time() + 10  # Shorter timeout

    #     cam_quit = False
    #     while cam_quit == False:

    #         image = None
    #         while image is None:
    #             image = self.videostream.read()

    #         # Start timer (for calculating frame rate)
    #         t1 = cv2.getTickCount()

    #         # Pre-process camera image (gray, blur, and threshold it)
    #         pre_proc = Cards.preprocess_image(image)
            
    #         # Find and sort the contours of all cards in the image (query cards)
    #         cnts_sort, cnt_is_card = Cards.find_cards(pre_proc)

    #         # Prepare containers for each iteration
    #         cards = []
    #         detected_ranks = []  # We still keep this if we want rank-only lists

    #         # --- PROCESS each DETECTED CARD --- #
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
    #                 cam_quit = True
    #                   # Stop the program after successful recognition
    #             # Else: skip printing anything if there's an Unknown


    #         # --- DRAW THE FRAMERATE IN THE CORNER --- #
    #         cv2.putText(image, "FPS: " + str(int(frame_rate_calc)), (10, 26),
    #                     font, 0.7, (255, 0, 255), 2, cv2.LINE_AA)

    #         # Show the annotated image
    #         cv2.imshow("Card Detector", image)

    #         # Calculate framerate
    #         t2 = cv2.getTickCount()
    #         time1 = (t2 - t1) / freq

    #     return card_values if card_values else 0

    def get_player_choice_from_buttons(self):
        print("Waiting for button press...")

        while True:
            if self.arduino.in_waiting:
                line = self.arduino.readline().decode('utf-8').strip()
                print(line)

                if line in set(['green','red','yellow']):
                    return line

    def takeBets(self):
        self.arduino.write(b'get_weight\n')  # Send command to Arduino

        while True:
            if self.arduino.in_waiting:
                line = self.arduino.readline().decode('utf-8').strip()
                if line.startswith("weight:"):
                    try:
                        total_weight = int(line.split(":")[1])
                        playerBet = round(total_weight)
                        return playerBet
                    except ValueError:
                        print("Error parsing weight from Arduino.")
                        return None

    def card_confirmation(self): #not used currently
        while True:
            print(f"Player cards: {self.playerHand}")
            confirmation = input("Are the detected card values correct? Yes or No: ").strip().lower()
            if confirmation == 'yes':
                break
            elif confirmation == 'no':
                print("Re-detecting cards... Please lay them down again.")
                self.playerHand = []
                self.initialDeal()
            else:
                print("Please enter 'Yes' or 'No'.")

        while True:
            print("now deal one card to dealer. flip over one card")                                    
            confirmation = input("Has one card been dealt? Yes or No ").lower()
            if confirmation == 'yes':
                break
            else:
                print("Please enter 'Yes' or 'No'.")

    def calculate_total(self, hand):
        total = sum(hand)
        num_aces = hand.count(11)
        while total > 21 and num_aces > 0:
            total -= 10
            num_aces -= 1
        return total

    def initialDeal(self):
        # Deal 2 cards to the player
        self.numPlayerCards = 2
        self.move_arm(self.currentplayerPosition)
        self.currentplayerPosition = self.currentplayerPosition - self.cardSpacing
        self.dispense_Card()
        self.move_arm(self.currentplayerPosition)
        self.currentplayerPosition = self.currentplayerPosition + self.cardSpacing
        self.dispense_Card()
        self.move_arm(self.homePosition)
        self.playerHand = [self.extract_cards_from_camera(self.numPlayerCards)]

        # Deal 1 card to the dealer
        print('now dealing dealer card..')
        self.numDealerCards = 1
        self.move_arm(self.currentdealerPosition)
        self.currentdealerPosition = self.currentdealerPosition + self.cardSpacing
        self.dispense_Card()
        self.move_arm(self.homePosition)
        self.dealerHand = [self.extract_cards_from_camera(self.numDealerCards)]

        # Update totals
        return self.playerHand, self.dealerHand

    def calculate_results(self,playerTotal,dealerTotal,playerBet):
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
            print("It's a tie, dealer wins in a tie.")
            playerWon = False
        else:
            playerWon = (playerTotal > dealerTotal)


        if playerWon:
            self.winnings += playerBet
            print('player wins!')
            print('Your winnings =', self.winnings)
            print('you will not receive your winnings.  move away from arm.  hit any button to continue')
            self.get_player_choice_from_buttons()
            self.move_arm(self.initialplayerPosition)
            self.dispense_Chips(playerBet)
            print('remove winnings from table. then move away from arm. hit any button to continue')
            self.get_player_choice_from_buttons()
            self.move_arm(self.homePosition)

        else:
            self.winnings -= playerBet
            print('player loses :( place bet into pick up area. move away from arm. hit any button to continue')
            self.get_player_choice_from_buttons()
            self.move_arm(self.initialscoopPosition)
            self.scoop_down()
            self.move_arm(self.finalscoopPosition)
            self.scoop_up()
            self.move_arm(self.homePosition)

    def dispense_Chips(self,playerBet):
        print(f'dispensing {playerBet} chips')
        command = f"dispense_chips:{playerBet}\n"
        self.arduino.write(command.encode())

    def dispense_Card(self): #not implemented yet. waiting for arm code
        print(f'dispensing cards...')
        self.arduino.write(b'get_card\n')  # Send command to Arduino

    def scoop_up(self):
        self.arduino.write(b'scoop_up\n')  # Send command to Arduino
        return

    def scoop_down(self):
        self.arduino.write(b'scoop_down\n')  # Send command to Arduino
        return

    def move_arm(self,target):
        command = f"move_arm:{target}\n"
        self.arduino.write(command.encode())  # Send command to Arduino

    def play(self):
        playerTotal = 0
        dealerTotal = 0

        print('move away from table for arm to move. Hit any button to continue')
        self.get_player_choice_from_buttons()
        self.move_arm(self.homePosition)

        print("make your bet. place chips on sensor. Hit any button to continue")
        self.get_player_choice_from_buttons()
        playerBet = self.takeBets()
        print("remove all chips from table. Hit any button to continue")
        self.get_player_choice_from_buttons()

        print('initial player deal. deal 2 player cards into camera area. press any button to continue')
        self.get_player_choice_from_buttons()
        self.initialDeal()

        playerTotal = self.calculate_total(self.playerHand)
        dealerTotal = self.calculate_total(self.dealerHand)
        print('player total =',playerTotal)
        print('dealer total =',dealerTotal)

        print('Do you want to Hit or Stay? (green = hit, red = stay)')
        while self.get_player_choice_from_buttons() == 'green':
            self.numPlayerCards += 1
            self.move_arm(self.currentplayerPosition)
            self.currentplayerPosition = self.currentplayerPosition - self.cardSpacing
            self.dispense_Card()
            self.move_arm(self.homePosition)
            print('make sure cards are in camera area')
            self.playerHand = self.extract_cards_from_camera(self.numPlayerCards)                 #initial deal as this in brackets
            playerTotal = self.calculate_total(self.playerHand)
            if playerTotal == 21:
                print("You hit 21!")
                break
            elif playerTotal > 21:
                print("You busted!")            
                break      
            else:
                print('Do you want to Hit or Stay? (green = hit, red = stay)')
            
        print("ok now the dealer's turn")
        while dealerTotal < 17:
            self.numDealerCards += 1
            self.move_arm(self.currentdealerPosition)
            self.currentdealerPosition = self.currentdealerPosition + self.cardSpacing
            self.dispense_Card()
            self.move_arm(self.homePosition)
            print('make sure cards are in camera area')
            self.dealerHand = self.extract_cards_from_camera(self.numDealerCards)           #this is in brackets in initial deal      
            dealerTotal = self.calculate_total(self.dealerHand)
            if dealerTotal > 16:
                break
            else:
                print("dealer is taking another card.")
        
        print("Dealer has finished their turn. Now Scooping up cards. move away from arm. hit any button to continue")
        self.get_player_choice_from_buttons()
        self.move_arm(self.initialscoopPosition)
        self.scoop_down()
        self.move_arm(self.finalscoopPosition)
        self.scoop_up()
        self.move_arm(self.homePosition)


        print('Now Calculating Results...')                 #add wait time
        self.calculate_results(playerTotal,dealerTotal,playerBet)

    def main(self):
        # First we prompt the user wether he wants to start a new game or not
        #! There is no difference between any of the buttons right now
        print('Are you ready to play? green=yes red=no' )
        newGame = self.get_player_choice_from_buttons().lower()

        while newGame != 'no':
            self.play()

            print("Do you want to play another round? green = yes, red = no ")
            newGame = self.get_player_choice_from_buttons().lower()
        print("Thank you for playing!")

if __name__ == "__main__":
    game = Blackjack()
    game.main()



#ADD A PRINT AND THEN A BUTTON COMMAND. Done.
#PRINT(DO ACTION.HIT ANY BUTTON). Done
#REGISTER BUTTON PRESS. Done
#self.get_player_choice_from_buttons() WILL ALLOW US TO START AND BREAK THE LOOP OF WAITING FOR THE BUTTON. Done
#every time we extract card from camera, tell player to make sure card is in camera area.  Done

#consider adding a confirmation of the cards function
#adjust camera specs. DONE

#build in delays
#build in warnings about the arm

#K2SO BTEMO theory








