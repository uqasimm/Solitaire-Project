import pytest

from fastapi.testclient import TestClient

import main
from game import SolitaireGame
from card import Card
from linked_list import LinkedList

@pytest.fixture
def client():
    main.game = SolitaireGame()
    main.history.clear()

    with TestClient(main.app) as test_client:
        yield test_client

def test_home_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Solitaire API is running!"


def test_get_game_state(client):
    response = client.get("/game-state")

    assert response.status_code == 200

    data = response.json()

    assert len(data["tableau"]) == 7
    assert data["stock_count"] == 24
    assert data["waste"] is None
    assert data["won"] is False


def test_new_game_endpoint(client):
    response = client.post("/new-game")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert len(data["game"]["tableau"]) == 7
    assert data["game"]["stock_count"] == 24

def test_draw_endpoint(client):
    response = client.post("/draw")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["game"]["stock_count"] == 23
    assert data["game"]["waste"] is not None


def test_draw_can_be_undone(client):
    client.post("/draw")

    response = client.post("/undo")

    data = response.json()

    assert data["success"] is True
    assert data["game"]["stock_count"] == 24
    assert data["game"]["waste"] is None

def test_valid_tableau_move_endpoint(client):
    red_five = Card("Hearts", "5", True)
    black_six = Card("Spades", "6", True)

    main.game.tableau[0] = LinkedList()
    main.game.tableau[0].append(red_five)

    main.game.tableau[1] = LinkedList()
    main.game.tableau[1].append(black_six)

    response = client.post(
        "/move-tableau",
        json={
            "source": 0,
            "card_index": 0,
            "destination": 1
        }
    )

    data = response.json()

    assert response.status_code == 200
    assert data["success"] is True
    assert len(data["game"]["tableau"][0]) == 0
    assert len(data["game"]["tableau"][1]) == 2


def test_invalid_tableau_move_endpoint(client):
    red_five = Card("Hearts", "5", True)
    red_six = Card("Diamonds", "6", True)

    main.game.tableau[0] = LinkedList()
    main.game.tableau[0].append(red_five)

    main.game.tableau[1] = LinkedList()
    main.game.tableau[1].append(red_six)

    response = client.post(
        "/move-tableau",
        json={
            "source": 0,
            "card_index": 0,
            "destination": 1
        }
    )

    data = response.json()

    assert response.status_code == 200
    assert data["success"] is False


def test_invalid_tableau_move_does_not_create_undo(client):
    response = client.post(
        "/move-tableau",
        json={
            "source": 0,
            "card_index": 0,
            "destination": 0
        }
    )

    assert response.json()["success"] is False

    undo_response = client.post("/undo")

    assert undo_response.json()["success"] is False

def test_valid_waste_move_endpoint(client):
    red_five = Card("Hearts", "5", True)
    black_six = Card("Spades", "6", True)

    main.game.waste.push(red_five)

    main.game.tableau[0] = LinkedList()
    main.game.tableau[0].append(black_six)

    response = client.post(
        "/move-waste",
        json={"destination": 0}
    )

    data = response.json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["game"]["waste"] is None
    assert len(data["game"]["tableau"][0]) == 2


def test_invalid_waste_move_endpoint(client):
    red_five = Card("Hearts", "5", True)
    red_six = Card("Diamonds", "6", True)

    main.game.waste.push(red_five)

    main.game.tableau[0] = LinkedList()
    main.game.tableau[0].append(red_six)

    response = client.post(
        "/move-waste",
        json={"destination": 0}
    )

    data = response.json()

    assert response.status_code == 200
    assert data["success"] is False
    assert data["game"]["waste"]["rank"] == "5"

def test_move_waste_ace_to_foundation_endpoint(client):
    ace = Card("Hearts", "Ace", True)
    main.game.waste.push(ace)

    response = client.post(
        "/move-foundation",
        json={"source": "waste"}
    )

    data = response.json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["game"]["waste"] is None
    assert data["game"]["foundations"]["Hearts"]["rank"] == "Ace"


def test_invalid_foundation_source(client):
    response = client.post(
        "/move-foundation",
        json={"source": "invalid"}
    )

    assert response.status_code == 200
    assert response.json()["success"] is False

def test_undo_endpoint(client):
    # First perform a valid move
    red_five = Card("Hearts", "5", True)
    black_six = Card("Spades", "6", True)

    main.game.tableau[0] = LinkedList()
    main.game.tableau[0].append(red_five)

    main.game.tableau[1] = LinkedList()
    main.game.tableau[1].append(black_six)

    move_response = client.post(
        "/move-tableau",
        json={
            "source": 0,
            "card_index": 0,
            "destination": 1
        }
    )

    assert move_response.json()["success"] is True

    undo_response = client.post("/undo")

    data = undo_response.json()

    assert undo_response.status_code == 200
    assert data["success"] is True
    assert len(data["game"]["tableau"][0]) == 1
    assert len(data["game"]["tableau"][1]) == 1


def test_undo_without_previous_move(client):
    response = client.post("/undo")

    data = response.json()

    assert response.status_code == 200
    assert data["success"] is False
    assert data["message"] == "Nothing to undo"

def test_new_game_clears_undo_history(client):
    client.post("/draw")

    response = client.post("/new-game")

    assert response.json()["success"] is True

    undo_response = client.post("/undo")

    assert undo_response.json()["success"] is False
