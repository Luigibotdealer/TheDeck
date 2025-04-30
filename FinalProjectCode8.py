import serial 
import time
from VideoStream import VideoStream
from CardDetector import detect_cards
from pi4_send import send_keyword_to_pi4


class Blackjack:
    def __init__(self):
        self.dealerHand = []
        self.playerHand = []
        self.winnings = 0
        self.numPlayerCards = 0
        self.numDealerCards = 0
        # we want to create a dynamic input to update as the arm moves in the game for the player and the dealer
        self.initialplayerPosition = 260
        self.currentplayerPosition = self.initialplayerPosition
        self.initialdealerPosition = 50
        self.currentdealerPosition = self.initialdealerPosition
        self.currentArmPosition = 0
        self.homePosition = 190.000
        self.initialscoopPosition = 300
        self.finalscoopPosition = 50
        self.cardSpacing = 15

        self.arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        time.sleep(2)

    def card_value(self, rank: str) -> int:
        rank_to_value = {
            'Ace': 11,
            'Two': 2,
            'Three': 3,
            'Four': 4,
            'Five': 5,
            'Six': 6,
            'Seven': 7,
            'Eight': 8,
            'Nine': 9,
            'Ten': 10,
            'Jack': 10,
            'Queen': 10,
            'King': 10,
        }
        return rank_to_value.get(rank, 0)  # 0 as default if unknown


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
                        print(f"Player bet: {playerBet}")
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

    # This function goes to card_values function and returns a total score accounting for aces

    def calculate_total(self, hand):
        if not isinstance(hand, list):
            raise TypeError(f"Expected list of card names, got {type(hand).__name__}: {hand}")

        total = sum(self.card_value(card) for card in hand)
        num_aces = hand.count('Ace')
        
        while total > 21 and num_aces > 0:
            total -= 10
            num_aces -= 1
        return total


    def initialDeal(self):
        # Deal 2 cards to the player
        self.numPlayerCards = 2
        self.numDealerCards = 1

        # We move the arm to the current player position, dispense a card 
        self.move_arm(self.currentplayerPosition)
        self.dispense_Card()

        # Now we move the arm to the dealer's position, dispense a card
        self.move_arm(self.currentdealerPosition)

        self.dispense_Card()

        self.currentplayerPosition = self.currentplayerPosition - self.cardSpacing

        # we move the arm the space of a card to the right 
        self.move_arm(self.currentplayerPosition)
        self.dispense_Card()
        self.move_arm(self.homePosition)
        
        # We are sending the instruction to recognise cards to the pi4 and the pi5
        self.playerHand = detect_cards(self.numPlayerCards, debug=True) # pi5 should detect the player's cards
        #! We are adding a stop to change monitors in debug, should be removed in production
        #self.get_player_choice_from_buttons()
        self.dealerHand = send_keyword_to_pi4(keyword="run_card_detection", num_cards=self.numDealerCards,) 

        # Code works up to here for sure 
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
            print('you will now receive your winnings.  move away from arm.  hit any button to continue')
            self.get_player_choice_from_buttons()
            self.move_arm(self.initialplayerPosition)
            self.dispense_Chips(playerBet)
            self.move_arm(self.homePosition)
            print('remove winnings from table. then move away from arm. hit any button to continue')
            #self.get_player_choice_from_buttons()

        else:
            self.winnings -= playerBet
            print('player loses :( place bet into pick up area. move away from arm. hit any button to continue')
            #self.get_player_choice_from_buttons()
            #self.scoop_up()

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

    def move_arm(self, target):
        command = f"move_arm:{target}\n"
        self.arduino.write(command.encode())  # Send command to Arduino

        print(f"[move_arm] Command sent: {command.strip()}")
        while True:
            if self.arduino.in_waiting:
                response = self.arduino.readline().decode('utf-8').strip()
                print(f"[move_arm] Arduino says: {response}")

                if response == "Finished":
                    print("[move_arm] Arm has reached target.")
                    break

    def play(self):
        playerTotal = 0
        dealerTotal = 0

        print('move away from table for arm to move. Hit any button to continue')
        self.get_player_choice_from_buttons()

        # Scoop up before we move the arm to the home position
        self.scoop_up()
        # We tell the arduino to move the arm to the home position
        self.move_arm(self.homePosition)

        # Player shouldpress button then place chips then press button again to continue
        print("make your bet. place chips on sensor. Hit any button to continue")

        # Wait for player to place chips on the sensor
        self.get_player_choice_from_buttons()

        playerBet = self.takeBets()

        print("Take your chips off the table. Hit any button to continue")

        self.get_player_choice_from_buttons()

        print("Bets are placed. Game begins now!")
        # We are calling initial deal function to deal cards to player and dealer and we are returning their hands
        playerHand, dealerHand = game.initialDeal()

        print("Player hand:",playerHand)
        print("Dealer hand:",dealerHand)

        # We have returned the hands of the player and dealer as an array of strings
        # e.g ['Ace', 'King'], now we need to calculate the total of the hand

        playerTotal = self.calculate_total(self.playerHand)
        dealerTotal = self.calculate_total(self.dealerHand)

        print('player total =',playerTotal)
        print('dealer total =',dealerTotal)

        print('Do you want to Hit or Stay? (green = hit, red = stay)')
        while self.get_player_choice_from_buttons() == 'green':
            self.numPlayerCards += 1

            # We are updating the current player position from the previous position in initial deal
            self.currentplayerPosition = self.currentplayerPosition - self.cardSpacing

            self.move_arm(self.currentplayerPosition)
            self.dispense_Card()
            self.move_arm(self.homePosition)
            print('make sure cards are in camera area')
            self.playerHand = detect_cards(self.numPlayerCards, debug=True) # pi5 should detect the player's cards
            playerTotal = self.calculate_total(self.playerHand)
            print("New player hand:",self.dealerHand, "With total:", playerTotal)

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
            # We are updating the current dealer position from the previous position in initial deal
            self.currentdealerPosition = self.currentdealerPosition + self.cardSpacing
            self.move_arm(self.currentdealerPosition)
            self.dispense_Card()
            self.move_arm(self.homePosition)
            print('make sure cards are in camera area')
            self.dealerHand = send_keyword_to_pi4(keyword="run_card_detection", num_cards=self.numDealerCards,) 
            dealerTotal = self.calculate_total(self.dealerHand)
            print("New dealer hand:",self.dealerHand, "With total:", playerTotal)

            if dealerTotal > 16:
                break
            else:
                print("dealer is taking another card.")

        print("Dealer has finished their turn. Now Calculating Results...")
        # Prints are within the calculate results function just like distribute winnings
        self.calculate_results(playerTotal,dealerTotal,playerBet)
        self.get_player_choice_from_buttons()
        self.move_arm(self.initialscoopPosition)
        self.scoop_down()
        self.move_arm(self.finalscoopPosition)
        print ("Scooped finished")
        self.scoop_up()

    def main(self):
        # First we prompt the user wether he wants to start a new game or not
        #! There is no difference between any of the buttons right now
        print('Are you ready to play? green=yes red=no' )
        newGame = self.get_player_choice_from_buttons().lower()

        while newGame != 'red':
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








