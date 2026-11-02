from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from game import SolitaireGame

from copy import deepcopy
from history import GameHistory

app = FastAPI(title="Solitaire Game API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

game = SolitaireGame()
history = GameHistory()

class TableauMove(BaseModel):
    source: int
    card_index: int
    destination: int


class WasteMove(BaseModel):
    destination: int


class FoundationMove(BaseModel):
    source: str
    column: int = -1

def card_to_dict(card):

    if not card.face_up:
        return {
            "face_up": False
        }

    return {
        "rank": card.rank,
        "suit": card.suit,
        "color": card.color,
        "face_up": True
    }

def get_game_state():

    tableau_data = []

    for column in game.tableau:

        cards = column.get_items()

        tableau_data.append([
            card_to_dict(card) for card in cards
        ])

    waste_data = None

    if not game.waste.is_empty():
        waste_data = card_to_dict(game.waste.peek())

    foundation_data = {}

    for suit, pile in game.foundations.items():
        if pile.is_empty():
            foundation_data[suit] = None
        else:
            foundation_data[suit] = card_to_dict(pile.peek())

    return {
        "tableau": tableau_data,
        "stock_count": game.stock.size(),
        "waste": waste_data,
        "foundations": foundation_data,
        "won": game.check_win()
    }

@app.get("/")
def home():

    return {
        "message": "Solitaire API is running!"
    }

@app.get("/game-state")
def game_state():

    return get_game_state()

@app.post("/new-game")
def new_game():

    global game

    game = SolitaireGame()
    history.clear()

    return {
        "success": True,
        "game": get_game_state()
    }

@app.post("/draw")
def draw_card():

    previous_state = deepcopy(game)

    card = game.draw_from_stock()

    if card is None:

        recycled = game.recycle_stock()

        if not recycled:
            return {
                "success": False,
                "message": "No cards available",
                "game": get_game_state()
            }

    history.save_snapshot(previous_state)

    return {
        "success": True,
        "message": "Card drawn",
        "game": get_game_state()
    }

@app.post("/move-tableau")
def move_tableau(data: TableauMove):

    previous_state = deepcopy(game)

    success = game.move_tableau_to_tableau(
        data.source,
        data.card_index,
        data.destination
    )

    if success:
        history.save_snapshot(previous_state)

    return {
        "success": success,
        "message": "Move successful" if success else "Invalid move",
        "game": get_game_state()
    }

@app.post("/move-waste")
def move_waste(data: WasteMove):

    previous_state = deepcopy(game)

    success = game.move_waste_to_tableau(
        data.destination
    )

    if success:
        history.save_snapshot(previous_state)

    return {
        "success": success,
        "message": "Move successful" if success else "Invalid move",
        "game": get_game_state()
    }

@app.post("/move-foundation")
def move_foundation(data: FoundationMove):

    previous_state = deepcopy(game)

    if data.source == "waste":

        success = game.move_waste_to_foundation()

    elif data.source == "tableau":

        success = game.move_tableau_to_foundation(
            data.column
        )

    else:

        success = False

    if success:
        history.save_snapshot(previous_state)

    return {
        "success": success,
        "message": "Move successful" if success else "Invalid move",
        "game": get_game_state()
    }

@app.post("/undo")
def undo_move():

    global game

    previous_state = history.undo()

    if previous_state is None:
        return {
            "success": False,
            "message": "Nothing to undo",
            "game": get_game_state()
        }

    game = previous_state

    return {
        "success": True,
        "message": "Move undone",
        "game": get_game_state()
    }
