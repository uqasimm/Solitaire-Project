import random
from card import Card

class Deck:
    def __init__(self):
        self.cards = []
        self.create_deck()

    def create_deck(self):
        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]

        ranks = [
            "Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"
        ]

        for suit in suits:
            for rank in ranks:
                card = Card(suit, rank)
                self.cards.append(card)

    def shuffle(self):
        random.shuffle(self.cards)

    def deal_card(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        else:
            return None

    def remaining_cards(self):
        return len(self.cards)