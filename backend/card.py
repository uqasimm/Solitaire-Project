class Card:
    
    def __init__(self, suit, rank, face_up = False):
        self.suit = suit
        self.rank = rank
        self.face_up = face_up

        if suit == "Hearts" or suit == "Diamonds":
            self.color = "Red"
        else:
            self.color = "Black"

    def flip(self):
        self.face_up = not self.face_up

    def __str__(self):
        if self.face_up:
            return f"{self.rank} of {self.suit}"
        else:
            return "Face-down Card"