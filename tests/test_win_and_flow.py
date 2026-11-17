import random

import pytest
from fastapi.testclient import TestClient

import main
from game import SolitaireGame
from card import Card
from linked_list import LinkedList
from stack import Stack

RANKS = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]

def set_column(game, column_index, *cards):
    game.tableau[column_index] = LinkedList()
    for card in cards:
        game.tableau[column_index].append(card)


def fill_foundation(game, suit, up_to=13):
    """Put Ace..up_to cards of a suit on its foundation pile."""
    game.foundations[suit] = Stack()
    for rank in RANKS[:up_to]:
        game.foundations[suit].push(Card(suit, rank, True))


def empty_board(game):
    """Remove every card from tableau, stock, waste and foundations."""
    for i in range(7):
        game.tableau[i] = LinkedList()
    while not game.stock.is_empty():
        game.stock.dequeue()
    game.waste = Stack()
    for suit in SUITS:
        game.foundations[suit] = Stack()


def count_cards(game):
    return (
        sum(col.size() for col in game.tableau)
        + game.stock.size()
        + game.waste.size()
        + sum(pile.size() for pile in game.foundations.values())
    )


@pytest.fixture
def client():
    main.game = SolitaireGame()
    main.history.clear()
    with TestClient(main.app) as test_client:
        yield test_client

def test_win_when_all_foundations_full():
    game = SolitaireGame()
    empty_board(game)

    for suit in SUITS:
        fill_foundation(game, suit, 13)

    assert game.check_win() is True


def test_not_won_when_one_foundation_is_short():
    game = SolitaireGame()
    empty_board(game)

    for suit in SUITS:
        fill_foundation(game, suit, 13)

    fill_foundation(game, "Spades", 12)

    assert game.check_win() is False


def test_not_won_when_foundations_empty():
    game = SolitaireGame()
    empty_board(game)

    assert game.check_win() is False


def test_win_after_last_card_moved_to_foundation():
    game = SolitaireGame()
    empty_board(game)

    for suit in SUITS:
        fill_foundation(game, suit, 12)

    for i, suit in enumerate(SUITS):
        set_column(game, i, Card(suit, "King", True))

    for i in range(3):
        assert game.move_tableau_to_foundation(i) is True
        assert game.check_win() is False

    assert game.move_tableau_to_foundation(3) is True
    assert game.check_win() is True

def test_tableau_to_foundation_moves_ace():
    game = SolitaireGame()
    ace = Card("Hearts", "Ace", True)
    set_column(game, 0, ace)

    result = game.move_tableau_to_foundation(0)

    assert result is True
    assert game.tableau[0].is_empty()
    assert game.foundations["Hearts"].peek() == ace


def test_tableau_to_foundation_flips_exposed_card():
    game = SolitaireGame()
    hidden = Card("Clubs", "9", False)
    ace = Card("Spades", "Ace", True)
    set_column(game, 0, hidden, ace)

    result = game.move_tableau_to_foundation(0)

    assert result is True
    assert hidden.face_up is True
    assert game.tableau[0].peek_last() == hidden


def test_tableau_to_foundation_rejects_non_ace_on_empty_foundation():
    game = SolitaireGame()
    two = Card("Hearts", "2", True)
    set_column(game, 0, two)

    result = game.move_tableau_to_foundation(0)

    assert result is False
    assert game.tableau[0].peek_last() == two
    assert game.foundations["Hearts"].is_empty()


def test_tableau_to_foundation_rejects_face_down_card():
    game = SolitaireGame()
    hidden_ace = Card("Hearts", "Ace", False)
    set_column(game, 0, hidden_ace)

    assert game.move_tableau_to_foundation(0) is False
    assert game.foundations["Hearts"].is_empty()


def test_tableau_to_foundation_rejects_empty_column_and_bad_index():
    game = SolitaireGame()
    set_column(game, 0)

    assert game.move_tableau_to_foundation(0) is False
    assert game.move_tableau_to_foundation(-1) is False
    assert game.move_tableau_to_foundation(7) is False


def test_tableau_to_foundation_builds_sequence_in_order():
    game = SolitaireGame()
    ace = Card("Diamonds", "Ace", True)
    two = Card("Diamonds", "2", True)
    three = Card("Diamonds", "3", True)

    set_column(game, 0, three)
    set_column(game, 1, two)
    set_column(game, 2, ace)

    assert game.move_tableau_to_foundation(0) is False
    assert game.move_tableau_to_foundation(1) is False
    assert game.move_tableau_to_foundation(2) is True
    assert game.move_tableau_to_foundation(1) is True
    assert game.move_tableau_to_foundation(0) is True
    assert game.foundations["Diamonds"].size() == 3


def test_tableau_to_foundation_updates_card_locations():
    game = SolitaireGame()
    ace = Card("Clubs", "Ace", True)
    set_column(game, 0, ace)

    game.move_tableau_to_foundation(0)

    assert game.card_locations[ace] == {"pile": "foundation", "suit": "Clubs"}


def test_multi_card_move_keeps_order():
    game = SolitaireGame()

    black_eight = Card("Spades", "8", True)
    red_seven = Card("Hearts", "7", True)
    black_six = Card("Clubs", "6", True)
    red_nine = Card("Diamonds", "9", True)

    set_column(game, 0, black_eight, red_seven, black_six)
    set_column(game, 1, red_nine)

    result = game.move_tableau_to_tableau(0, 0, 1)

    assert result is True
    assert game.tableau[0].is_empty()
    assert game.tableau[1].get_items() == [red_nine, black_eight, red_seven, black_six]


def test_multi_card_move_updates_card_locations():
    game = SolitaireGame()

    black_eight = Card("Spades", "8", True)
    red_seven = Card("Hearts", "7", True)
    red_nine = Card("Diamonds", "9", True)

    set_column(game, 0, black_eight, red_seven)
    set_column(game, 1, red_nine)

    game.move_tableau_to_tableau(0, 0, 1)

    assert game.card_locations[black_eight] == {"pile": "tableau", "column": 1}
    assert game.card_locations[red_seven] == {"pile": "tableau", "column": 1}


def test_multi_card_move_rejected_if_run_contains_face_down_card():
    game = SolitaireGame()

    hidden = Card("Spades", "8", False)
    red_seven = Card("Hearts", "7", True)
    red_nine = Card("Diamonds", "9", True)

    set_column(game, 0, hidden, red_seven)
    set_column(game, 1, red_nine)

    assert game.move_tableau_to_tableau(0, 0, 1) is False
    assert game.tableau[0].size() == 2
    assert game.tableau[1].size() == 1


def test_waste_to_foundation_updates_card_locations():
    game = SolitaireGame()
    ace = Card("Spades", "Ace", True)
    game.waste.push(ace)

    game.move_waste_to_foundation()

    assert game.card_locations[ace] == {"pile": "foundation", "suit": "Spades"}


def test_draw_updates_card_locations_to_waste_and_back_to_stock():
    game = SolitaireGame()
    drawn = game.draw_from_stock()

    assert game.card_locations[drawn] == {"pile": "waste"}

    while not game.stock.is_empty():
        game.draw_from_stock()

    assert game.recycle_stock() is True
    assert game.card_locations[drawn] == {"pile": "stock"}
    assert drawn.face_up is False

def test_flow_new_game_is_correctly_initialised():
    game = SolitaireGame()

    for i in range(7):
        column = game.tableau[i].get_items()
        assert len(column) == i + 1
        assert all(not c.face_up for c in column[:-1])
        assert column[-1].face_up is True

    assert game.stock.size() == 24
    assert game.waste.is_empty()
    assert all(pile.is_empty() for pile in game.foundations.values())
    assert count_cards(game) == 52
    assert len(game.card_locations) == 52
    assert game.check_win() is False


def test_flow_all_cards_in_tableau_played_to_foundation_wins():
    """Init -> rig a fully sorted board -> play it out -> win."""
    game = SolitaireGame()
    empty_board(game)

    for i, suit in enumerate(SUITS):
        set_column(game, i, *[Card(suit, rank, True) for rank in reversed(RANKS)])

    assert count_cards(game) == 52
    assert game.check_win() is False

    moves = 0
    for i in range(4):
        while not game.tableau[i].is_empty():
            assert game.move_tableau_to_foundation(i) is True
            moves += 1

    assert moves == 52
    assert all(pile.size() == 13 for pile in game.foundations.values())
    assert game.check_win() is True


def test_flow_cards_from_stock_and_waste_reach_foundation_and_win():
    """Stock -> waste -> foundation, mixed with tableau moves, until won."""
    game = SolitaireGame()
    empty_board(game)

    for i, suit in enumerate(SUITS):
        set_column(game, i, Card(suit, "King", True))

    for rank in RANKS[:12]:
        for suit in SUITS:
            game.stock.enqueue(Card(suit, rank, False))

    while not game.stock.is_empty():
        assert game.draw_from_stock() is not None
        assert game.move_waste_to_foundation() is True

    assert game.check_win() is False

    for i in range(4):
        assert game.move_tableau_to_foundation(i) is True

    assert game.check_win() is True


def test_flow_random_play_never_breaks_invariants():
    """Play many random legal/illegal moves; cards must never be lost or duplicated."""
    rng = random.Random(42)

    for _ in range(5):
        game = SolitaireGame()

        for _ in range(1500):
            action = rng.random()

            if action < 0.30:
                if game.draw_from_stock() is None:
                    game.recycle_stock()
            elif action < 0.45:
                game.move_waste_to_foundation()
            elif action < 0.55:
                game.move_waste_to_tableau(rng.randrange(7))
            elif action < 0.75:
                game.move_tableau_to_foundation(rng.randrange(7))
            else:
                game.move_tableau_to_tableau(
                    rng.randrange(7), rng.randrange(8), rng.randrange(7)
                )

            assert count_cards(game) == 52

        for column in game.tableau:
            if not column.is_empty():
                assert column.peek_last().face_up is True

        for i, column in enumerate(game.tableau):
            for card in column.get_items():
                assert game.card_locations[card] == {"pile": "tableau", "column": i}


def test_api_game_state_reports_won_false_on_new_game(client):
    response = client.get("/game-state")

    assert response.json()["won"] is False


def test_api_game_state_reports_won_true(client):
    empty_board(main.game)

    for suit in SUITS:
        fill_foundation(main.game, suit, 13)

    response = client.get("/game-state")

    assert response.status_code == 200
    assert response.json()["won"] is True


def test_api_final_move_wins_the_game(client):
    empty_board(main.game)

    for suit in SUITS:
        fill_foundation(main.game, suit, 12)

    for i, suit in enumerate(SUITS):
        set_column(main.game, i, Card(suit, "King", True))

    last = None
    for i in range(4):
        last = client.post(
            "/move-foundation",
            json={"source": "tableau", "column": i}
        ).json()
        assert last["success"] is True

    assert last["game"]["won"] is True


def test_api_move_foundation_from_tableau_success(client):
    ace = Card("Hearts", "Ace", True)
    set_column(main.game, 0, ace)

    data = client.post(
        "/move-foundation",
        json={"source": "tableau", "column": 0}
    ).json()

    assert data["success"] is True
    assert data["game"]["tableau"][0] == []
    assert data["game"]["foundations"]["Hearts"]["rank"] == "Ace"


def test_api_move_foundation_from_tableau_failure_creates_no_undo(client):
    two = Card("Hearts", "2", True)
    set_column(main.game, 0, two)

    data = client.post(
        "/move-foundation",
        json={"source": "tableau", "column": 0}
    ).json()

    assert data["success"] is False

    undo = client.post("/undo").json()
    assert undo["success"] is False


def test_api_foundation_move_can_be_undone(client):
    ace = Card("Hearts", "Ace", True)
    set_column(main.game, 0, ace)

    client.post("/move-foundation", json={"source": "tableau", "column": 0})
    undo = client.post("/undo").json()

    assert undo["success"] is True
    assert undo["game"]["foundations"]["Hearts"] is None
    assert len(undo["game"]["tableau"][0]) == 1


def test_api_hides_face_down_cards(client):
    state = client.get("/game-state").json()

    for column in state["tableau"]:
        for card in column[:-1]:
            assert card == {"face_up": False}
        assert column[-1]["face_up"] is True


def test_recycle_keeps_original_draw_order():
    game = SolitaireGame()

    first_pass = []
    while not game.stock.is_empty():
        first_pass.append(game.draw_from_stock())

    assert game.recycle_stock() is True

    second_pass = []
    while not game.stock.is_empty():
        second_pass.append(game.draw_from_stock())

    assert second_pass == first_pass