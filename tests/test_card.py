from backend.card import Card

card1 = Card("Hearts", "Ace", True)
card2 = Card("Spades", "King", False)
card3 = Card("Diamonds", "5", True)

print(card1)
print(card2)
print(card3)

print("\nCard Colors:")
print(card1.color)
print(card2.color)
print(card3.color)

print("\nBefore flipping:")
print(card2)

card2.flip()

print("After flipping:")
print(card2)