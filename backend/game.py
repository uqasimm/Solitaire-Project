from deck import Deck
from stack import Stack
from queue import Queue
from linked_list import LinkedList

class SolitaireGame:

    def __init__(self):
        self.new_game()
    
    def new_game(self):
        self.deck = Deck()
        self.deck.shuffle()

        self.tableau = []

        for i in range(7):
            column = LinkedList()
            self.tableau.append(column)

        self.stock = Queue()
        self.waste = Stack()

        self.foundations = {
            "Hearts": Stack(),
            "Diamonds": Stack(),
            "Clubs": Stack(),
            "Spades": Stack()
        }

        self.card_locations = {}

        for i in range(7):
            for j in range(i + 1):
                card = self.deck.deal_card()
                if j == i:
                    card.face_up = True

                self.tableau[i].append(card)
                self.card_locations[card] = {
                    "pile": "tableau",
                    "column": i
                }

        while self.deck.remaining_cards() > 0:
            card = self.deck.deal_card()
            self.stock.enqueue(card)

            self.card_locations[card] = {
                "pile": "stock"
            }

    def draw_from_stock(self):
        if self.stock.is_empty():
            return None

        card = self.stock.dequeue()
        card.face_up = True
        self.waste.push(card)

        self.card_locations[card] = {
            "pile": "waste"
        }

        return card

    def display_game(self):

        print("\n========== SOLITAIRE GAME ==========")

        print("\nTableau:")

        for i, column in enumerate(self.tableau):
            print(f"Column {i + 1}:")
            column.display()

        print("\nStockpile cards:", self.stock.size())

        print("Waste pile cards:", self.waste.size())

        print("\nFoundation piles:")

        for suit, pile in self.foundations.items():
            print(suit, ":", pile.size())

        print("====================================")