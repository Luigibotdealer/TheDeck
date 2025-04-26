import serial 
import time
from VideoStream import VideoStream

class Poker:
    def __init__(self):
        self.dealerHand = []
        self.playerHand = []
        self.winnings = 0
        self.numPlayerCards = 0
        self.numDealerCards = 0

        self.arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        time.sleep(2)

        # self.videostream = VideoStream((640, 480), 10).start()
        # time.sleep(1)  # Give the camera time to warm up

    def get_card_values(card_names):
        card_values = {
            'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5,
            'Six': 6, 'Seven': 7, 'Eight': 8, 'Nine': 9,
            'Ten': 10, 'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11
        }
        return [card_values.get(card, 0) for card in card_names]


    
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
        self.playerHand = self.extract_cards_from_camera(self.numPlayerCards)

        # Deal 1 card to the dealer
        print('initial dealer deal. deal 1 card into camera area. press any button to continue')
        self.get_player_choice_from_buttons()
        self.numDealerCards = 1
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
            self.dispense_Chips(playerBet)

        else:
            self.winnings -= playerBet
            print('player loses :( ')

    def dispense_Chips(self,playerBet):
        print(f'dispensing {playerBet} chips')
        command = f"dispense_chips:{playerBet}\n"
        self.arduino.write(command.encode())

    def dispense_Card(self): #not implemented yet. waiting for arm code
        print(f'dispensing cards...')
        self.arduino.write(b'get_card\n')  # Send command to Arduino

    def play(self):
        playerTotal = 0
        dealerTotal = 0

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
            print('make sure cards are in camera area')
            self.playerHand = self.extract_cards_from_camera(self.numPlayerCards)                 #this would change if we do one card at a time
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
            print('make sure cards are in camera area')
            self.dealerHand = self.extract_cards_from_camera(self.numDealerCards)                 
            dealerTotal = self.calculate_total(self.dealerHand)
            if dealerTotal > 16:
                break
            else:
                print("dealer is taking another card.")
        
        print("Dealer has finished their turn.  Calculating Results..")                         #add wait time
        self.calculate_results(playerTotal,dealerTotal,playerBet)

    def main(self):
        print('Are you ready to play? green = yes, red = no' )
        newGame = self.get_player_choice_from_buttons().lower()

        while newGame != 'no':
            self.play()

            print("Do you want to play another round? green = yes, red = no ")
            newGame = self.get_player_choice_from_buttons().lower()
        print("Thank you for playing!")

if __name__ == "__main__":
    game = Poker()
    game.main()



#ADD A PRINT AND THEN A BUTTON COMMAND. Done.
#PRINT(DO ACTION.HIT ANY BUTTON). Done
#REGISTER BUTTON PRESS. Done
#self.get_player_choice_from_buttons() WILL ALLOW US TO START AND BREAK THE LOOP OF WAITING FOR THE BUTTON. Done
#every time we extract card from camera, tell player to make sure card is in camera area.  Done

#consider adding a confirmation of the cards function
#adjust camera specs
#implement LCD screen or printing to a monitor
#we are going to need a 'card_to_player' function and 'card_to_

