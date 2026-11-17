import pytest

from card import Card
from deck import Deck
from stack import Stack
from game_queue import Queue
from linked_list import LinkedList
from game import SolitaireGame

def test_card_color():
    red_card = Card("Hearts", "Ace")
    black_card = Card("Spades", "King")

    assert red_card.color == "Red"
    assert black_card.color == "Black"


def test_card_flip():
    card = Card("Hearts", "Ace")

    assert card.face_up is False

    card.flip()

    assert card.face_up is True

def test_deck_has_52_cards():
    deck = Deck()

    assert deck.remaining_cards() == 52


def test_deck_has_all_suits_and_ranks():
    deck = Deck()

    suits = {card.suit for card in deck.cards}
    ranks = {card.rank for card in deck.cards}

    assert len(suits) == 4
    assert len(ranks) == 13


def test_deal_card_reduces_deck():
    deck = Deck()

    card = deck.deal_card()

    assert card is not None
    assert deck.remaining_cards() == 51


def test_empty_deck_returns_none():
    deck = Deck()

    for _ in range(52):
        deck.deal_card()

    assert deck.deal_card() is None

def test_stack_push_and_pop():
    stack = Stack()

    stack.push(10)
    stack.push(20)

    assert stack.size() == 2
    assert stack.pop() == 20
    assert stack.pop() == 10


def test_stack_peek():
    stack = Stack()

    stack.push("Ace")

    assert stack.peek() == "Ace"
    assert stack.size() == 1


def test_empty_stack():
    stack = Stack()

    assert stack.is_empty()
    assert stack.pop() is None
    assert stack.peek() is None

def test_queue_enqueue_and_dequeue():
    queue = Queue()

    queue.enqueue(10)
    queue.enqueue(20)

    assert queue.size() == 2
    assert queue.dequeue() == 10
    assert queue.dequeue() == 20


def test_queue_peek():
    queue = Queue()

    queue.enqueue("First")
    queue.enqueue("Second")

    assert queue.peek() == "First"
    assert queue.size() == 2


def test_empty_queue():
    queue = Queue()

    assert queue.is_empty()
    assert queue.dequeue() is None
    assert queue.peek() is None

def test_linked_list_append():
    linked_list = LinkedList()

    linked_list.append(10)
    linked_list.append(20)

    assert linked_list.size() == 2
    assert linked_list.get_items() == [10, 20]


def test_linked_list_remove_last():
    linked_list = LinkedList()

    linked_list.append(10)
    linked_list.append(20)

    assert linked_list.remove_last() == 20
    assert linked_list.size() == 1


def test_linked_list_peek_last():
    linked_list = LinkedList()

    linked_list.append(10)
    linked_list.append(20)

    assert linked_list.peek_last() == 20


def test_linked_list_remove_from():
    linked_list = LinkedList()

    linked_list.append(10)
    linked_list.append(20)
    linked_list.append(30)

    removed = linked_list.remove_from(1)

    assert removed == [20, 30]
    assert linked_list.get_items() == [10]
    assert linked_list.size() == 1


def test_empty_linked_list():
    linked_list = LinkedList()

    assert linked_list.is_empty()
    assert linked_list.remove_last() is None
    assert linked_list.peek_last() is None

def test_new_game_setup():
    game = SolitaireGame()

    assert len(game.tableau) == 7

    tableau_count = sum(
        column.size() for column in game.tableau
    )

    assert tableau_count == 28

    assert game.stock.size() == 24

    # Four empty foundations
    assert len(game.foundations) == 4

    for pile in game.foundations.values():
        assert pile.is_empty()


def test_new_game_face_up_cards():
    game = SolitaireGame()

    for column in game.tableau:
        cards = column.get_items()

        assert cards[-1].face_up is True

        for card in cards[:-1]:
            assert card.face_up is False


def test_draw_from_stock():
    game = SolitaireGame()

    card = game.draw_from_stock()

    assert card is not None
    assert card.face_up is True
    assert game.stock.size() == 23
    assert game.waste.size() == 1


def test_move_ace_to_foundation():
    game = SolitaireGame()

    ace = Card("Hearts", "Ace", True)
    game.waste.push(ace)

    result = game.move_waste_to_foundation()

    assert result is True
    assert game.waste.is_empty()
    assert game.foundations["Hearts"].peek() == ace


def test_invalid_foundation_move():
    game = SolitaireGame()

    five = Card("Hearts", "5", True)
    game.waste.push(five)

    result = game.move_waste_to_foundation()

    assert result is False
    assert game.waste.peek() == five


def test_check_win_on_new_game():
    game = SolitaireGame()

    assert game.check_win() is False