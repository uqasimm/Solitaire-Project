from deck import Deck
from stack import Stack
from game_queue import Queue
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

    def get_card_value(self, card):

        rank_values = {
            "Ace": 1,
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "10": 10,
            "Jack": 11,
            "Queen": 12,
            "King": 13
        }

        return rank_values[card.rank]

    def is_valid_tableau_move(self, moving_card, destination_card):

        if not destination_card.face_up:
            return False

        if moving_card.color == destination_card.color:
            return False

        if self.get_card_value(moving_card) != self.get_card_value(destination_card) - 1:
            return False

        return True

    def flip_top_card(self, column_index):

        column = self.tableau[column_index]

        if column.is_empty():
            return

        top_card = column.peek_last()

        if not top_card.face_up:
            top_card.flip()

    def move_tableau_to_tableau(self, source_column, card_index, destination_column):

        if source_column == destination_column:
            return False

        if source_column < 0 or source_column >= 7:
            return False

        if destination_column < 0 or destination_column >= 7:
            return False

        source = self.tableau[source_column]
        destination = self.tableau[destination_column]

        cards = source.get_items()

        if card_index < 0 or card_index >= len(cards):
            return False

        moving_cards = cards[card_index:]

        for card in moving_cards:
            if not card.face_up:
                return False

        first_card = moving_cards[0]

        if destination.is_empty():

            if self.get_card_value(first_card) != 13:
                return False

        else:

            destination_card = destination.peek_last()

            if not self.is_valid_tableau_move(first_card, destination_card):
                return False

        removed_cards = source.remove_from(card_index)

        for card in removed_cards:
            destination.append(card)

            self.card_locations[card] = {
                "pile": "tableau",
                "column": destination_column
            }

        self.flip_top_card(source_column)

        return True

    def move_waste_to_tableau(self, destination_column):

        if self.waste.is_empty():
            return False

        if destination_column < 0 or destination_column >= 7:
            return False

        moving_card = self.waste.peek()
        destination = self.tableau[destination_column]

        if destination.is_empty():

            if self.get_card_value(moving_card) != 13:
                return False

        else:

            destination_card = destination.peek_last()

            if not self.is_valid_tableau_move(moving_card, destination_card):
                return False

        card = self.waste.pop()
        destination.append(card)

        self.card_locations[card] = {
            "pile": "tableau",
            "column": destination_column
        }

        return True

    def is_valid_foundation_move(self, card):

        foundation = self.foundations[card.suit]

        if foundation.is_empty():

            return self.get_card_value(card) == 1

        top_card = foundation.peek()

        return self.get_card_value(card) == self.get_card_value(top_card) + 1

    def move_waste_to_foundation(self):

        if self.waste.is_empty():
            return False

        card = self.waste.peek()

        if not self.is_valid_foundation_move(card):
            return False

        card = self.waste.pop()

        self.foundations[card.suit].push(card)

        self.card_locations[card] = {
            "pile": "foundation",
            "suit": card.suit
        }

        return True

    def move_tableau_to_foundation(self, column_index):

        if column_index < 0 or column_index >= 7:
            return False

        column = self.tableau[column_index]

        if column.is_empty():
            return False

        card = column.peek_last()

        if not card.face_up:
            return False

        if not self.is_valid_foundation_move(card):
            return False

        card = column.remove_last()

        self.foundations[card.suit].push(card)

        self.card_locations[card] = {
            "pile": "foundation",
            "suit": card.suit
        }

        self.flip_top_card(column_index)

        return True

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

    def recycle_stock(self):

        if not self.stock.is_empty():
            return False

        if self.waste.is_empty():
            return False

        while not self.waste.is_empty():

            card = self.waste.pop()

            card.face_up = False

            self.stock.enqueue(card)

            self.card_locations[card] = {
                "pile": "stock"
            }

        return True

    def check_win(self):

        for pile in self.foundations.values():

            if pile.size() != 13:
                return False

        return True

    def display_game(self):

        print("\n========== SOLITAIRE GAME ==========")

        print("\nTableau:")

        for i, column in enumerate(self.tableau):

            print(f"\nColumn {i + 1}:")

            column.display()

        print("\nStockpile cards:", self.stock.size())

        print("Waste pile cards:", self.waste.size())

        print("\nFoundation piles:")

        for suit, pile in self.foundations.items():

            print(suit, ":", pile.size())

        print("\n====================================")
