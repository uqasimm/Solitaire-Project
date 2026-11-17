from game import SolitaireGame
from card import Card
from linked_list import LinkedList
from game_queue import Queue
from history import GameHistory

def set_column(game, column_index, *cards):
    game.tableau[column_index] = LinkedList()

    for card in cards:
        game.tableau[column_index].append(card)

def test_valid_tableau_move():
    game = SolitaireGame()

    red_five = Card("Hearts", "5", True)
    black_six = Card("Spades", "6", True)

    set_column(game, 0, red_five)
    set_column(game, 1, black_six)

    result = game.move_tableau_to_tableau(0, 0, 1)

    assert result is True
    assert game.tableau[0].is_empty()
    assert game.tableau[1].size() == 2
    assert game.tableau[1].peek_last() == red_five


def test_invalid_same_color_tableau_move():
    game = SolitaireGame()

    red_five = Card("Hearts", "5", True)
    red_six = Card("Diamonds", "6", True)

    set_column(game, 0, red_five)
    set_column(game, 1, red_six)

    result = game.move_tableau_to_tableau(0, 0, 1)

    assert result is False
    assert game.tableau[0].size() == 1
    assert game.tableau[1].size() == 1


def test_invalid_rank_tableau_move():
    game = SolitaireGame()

    red_four = Card("Hearts", "4", True)
    black_six = Card("Spades", "6", True)

    set_column(game, 0, red_four)
    set_column(game, 1, black_six)

    result = game.move_tableau_to_tableau(0, 0, 1)

    assert result is False


def test_cannot_move_face_down_card():
    game = SolitaireGame()

    hidden_card = Card("Hearts", "5", False)
    black_six = Card("Spades", "6", True)

    set_column(game, 0, hidden_card)
    set_column(game, 1, black_six)

    result = game.move_tableau_to_tableau(0, 0, 1)

    assert result is False


def test_move_king_to_empty_column():
    game = SolitaireGame()

    king = Card("Hearts", "King", True)

    set_column(game, 0, king)
    set_column(game, 1)

    result = game.move_tableau_to_tableau(0, 0, 1)

    assert result is True
    assert game.tableau[0].is_empty()
    assert game.tableau[1].peek_last() == king


def test_non_king_cannot_move_to_empty_column():
    game = SolitaireGame()

    queen = Card("Hearts", "Queen", True)

    set_column(game, 0, queen)
    set_column(game, 1)

    result = game.move_tableau_to_tableau(0, 0, 1)

    assert result is False


def test_exposed_card_flips_after_tableau_move():
    game = SolitaireGame()

    hidden_four = Card("Hearts", "4", False)
    red_six = Card("Hearts", "6", True)
    black_seven = Card("Spades", "7", True)

    set_column(game, 0, hidden_four, red_six)
    set_column(game, 1, black_seven)

    result = game.move_tableau_to_tableau(0, 1, 1)

    assert result is True
    assert hidden_four.face_up is True

def test_valid_waste_to_tableau_move():
    game = SolitaireGame()

    red_five = Card("Hearts", "5", True)
    black_six = Card("Spades", "6", True)

    game.waste.push(red_five)
    set_column(game, 0, black_six)

    result = game.move_waste_to_tableau(0)

    assert result is True
    assert game.waste.is_empty()
    assert game.tableau[0].peek_last() == red_five


def test_invalid_waste_to_tableau_move():
    game = SolitaireGame()

    red_five = Card("Hearts", "5", True)
    red_six = Card("Diamonds", "6", True)

    game.waste.push(red_five)
    set_column(game, 0, red_six)

    result = game.move_waste_to_tableau(0)

    assert result is False
    assert game.waste.peek() == red_five

def test_foundation_accepts_ace_first():
    game = SolitaireGame()

    ace = Card("Hearts", "Ace", True)
    game.waste.push(ace)

    result = game.move_waste_to_foundation()

    assert result is True
    assert game.waste.is_empty()
    assert game.foundations["Hearts"].peek() == ace


def test_foundation_accepts_next_rank():
    game = SolitaireGame()

    ace = Card("Hearts", "Ace", True)
    two = Card("Hearts", "2", True)

    game.foundations["Hearts"].push(ace)
    game.waste.push(two)

    result = game.move_waste_to_foundation()

    assert result is True
    assert game.foundations["Hearts"].size() == 2
    assert game.foundations["Hearts"].peek() == two


def test_foundation_rejects_wrong_rank():
    game = SolitaireGame()

    two = Card("Hearts", "2", True)
    game.waste.push(two)

    result = game.move_waste_to_foundation()

    assert result is False
    assert game.waste.peek() == two

def test_recycle_stock():
    game = SolitaireGame()

    first_card = Card("Hearts", "5", True)
    second_card = Card("Spades", "7", True)

    game.stock = Queue()

    game.waste.push(first_card)
    game.waste.push(second_card)

    result = game.recycle_stock()

    assert result is True
    assert game.stock.size() == 2
    assert game.waste.is_empty()

    assert first_card.face_up is False
    assert second_card.face_up is False


def test_cannot_recycle_when_stock_not_empty():
    game = SolitaireGame()

    game.waste.push(Card("Hearts", "5", True))

    result = game.recycle_stock()

    assert result is False

def test_history_save_and_undo():
    history = GameHistory()

    snapshot = {"moves": 5}

    history.save_snapshot(snapshot)

    assert history.can_undo() is True
    assert history.undo() == snapshot
    assert history.can_undo() is False


def test_undo_when_history_is_empty():
    history = GameHistory()

    assert history.undo() is None


def test_clear_history():
    history = GameHistory()

    history.save_snapshot({"moves": 1})
    history.save_snapshot({"moves": 2})

    history.clear()

    assert history.can_undo() is False
    assert history.undo() is None