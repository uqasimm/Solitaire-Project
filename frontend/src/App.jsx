import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

const SUITS = {
  Hearts: "♥",
  Diamonds: "♦",
  Clubs: "♣",
  Spades: "♠",
};

function PlayingCard({ card, selected, onClick }) {
  if (!card) {
    return <div className="empty-card" />;
  }

  if (!card.face_up) {
    return (
      <div className="playing-card card-back">
        <div className="card-back-pattern">✦</div>
      </div>
    );
  }

  const symbol = SUITS[card.suit];

  return (
    <button
      className={`playing-card ${card.color === "Red" ? "red-card" : "black-card"} ${selected ? "selected-card" : ""}`}
      onClick={onClick}
      type="button"
    >
      <span className="card-rank">{card.rank}</span>
      <span className="card-suit">{symbol}</span>
      <span className="card-center">{symbol}</span>
    </button>
  );
}

function App() {
  const [game, setGame] = useState(null);
  const [selected, setSelected] = useState(null);
  const [moves, setMoves] = useState(0);
  const [message, setMessage] = useState("Welcome to Solitaire!");
  const [loading, setLoading] = useState(true);

  async function requestGame(url, options = {}) {
    try {
      const response = await fetch(`${API}${url}`, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      setMessage("Cannot connect to the game server. Is FastAPI running?");
      console.error(error);
      return null;
    }
  }

  async function loadGame() {
    setLoading(true);

    const data = await requestGame("/game-state");

    if (data) {
      setGame(data);
      setMessage("Game loaded. Good luck!");
    }

    setLoading(false);
  }

  useEffect(() => {
    loadGame();
  }, []);

  async function updateGame(url, body = null) {
    const result = await requestGame(url, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!result) return false;

    if (result.game) {
      setGame(result.game);
    }

    if (result.success) {
      setMoves((previous) => previous + 1);
      setMessage(result.message || "Move successful!");

      if (result.game?.won) {
        setMessage("Congratulations! You won!");
      }
    } else {
      setMessage(result.message || "That move is not allowed.");
    }

    setSelected(null);
    return result.success;
  }

  async function newGame() {
    const result = await requestGame("/new-game", {
      method: "POST",
    });

    if (result) {
      setGame(result.game);
      setSelected(null);
      setMoves(0);
      setMessage("New game started!");
    }
  }

  async function drawCard() {
    if (selected) {
      setSelected(null);
    }

    await updateGame("/draw");
  }

  function selectTableauCard(columnIndex, cardIndex, card) {
    if (!card.face_up) return;

    if (!selected) {
      setSelected({
        source: "tableau",
        column: columnIndex,
        cardIndex,
      });
      setMessage("Card selected. Choose a destination.");
      return;
    }

    if (
      selected.source === "tableau" &&
      selected.column === columnIndex &&
      selected.cardIndex === cardIndex
    ) {
      setSelected(null);
      setMessage("Selection cancelled.");
      return;
    }

    if (selected.source === "waste") {
      updateGame("/move-waste", {
        destination: columnIndex,
      });
      return;
    }

    updateGame("/move-tableau", {
      source: selected.column,
      card_index: selected.cardIndex,
      destination: columnIndex,
    });
  }

  function clickEmptyColumn(columnIndex) {
    if (!selected) return;

    if (selected.source === "waste") {
      updateGame("/move-waste", {
        destination: columnIndex,
      });
    } else {
      updateGame("/move-tableau", {
        source: selected.column,
        card_index: selected.cardIndex,
        destination: columnIndex,
      });
    }
  }

  function moveToFoundation(source, column = -1) {
    if (!selected || selected.source !== source) return;

    updateGame("/move-foundation", {
      source,
      column,
    });
  }

  if (loading) {
    return <div className="loading-screen">Loading Solitaire...</div>;
  }

  if (!game) {
    return (
      <div className="loading-screen">
        {message}
        <button onClick={loadGame}>Try Again</button>
      </div>
    );
  }

  return (
    <main className="app">
      <header className="top-bar">
        <div>
          <h1>Solitaire</h1>
          <p>Classic Klondike Card Game</p>
        </div>

        <div className="game-controls">
          <span className="move-counter">Moves: {moves}</span>
          <button className="new-game-button" onClick={newGame}>
            New Game
          </button>
        </div>
      </header>

      <div className="game-message">{message}</div>

      <section className="game-board">
        <div className="top-piles">
          <div className="stock-waste">
            <div className="pile">
              <span className="pile-label">STOCK</span>

              <button
                className="pile-button"
                onClick={drawCard}
                type="button"
              >
                {game.stock_count > 0 ? (
                  <PlayingCard card={{ face_up: false }} />
                ) : (
                  <div className="empty-card stock-empty">↻</div>
                )}
              </button>

              <span className="card-count">{game.stock_count}</span>
            </div>

            <div className="pile">
              <span className="pile-label">WASTE</span>

              <button
                className="pile-button"
                onClick={() => {
                  if (game.waste) {
                    setSelected({ source: "waste" });
                    setMessage("Waste card selected.");
                  }
                }}
                type="button"
              >
                <PlayingCard
                  card={game.waste}
                  selected={selected?.source === "waste"}
                />
              </button>
            </div>
          </div>

          <div className="foundations">
            {Object.entries(game.foundations).map(([suit, card]) => (
              <div className="pile" key={suit}>
                <span className="pile-label">{suit.toUpperCase()}</span>

                <button
                  className="pile-button"
                  onClick={() => moveToFoundation(selected?.source, selected?.column ?? -1)}
                  type="button"
                >
                  {card ? (
                    <PlayingCard card={card} />
                  ) : (
                    <div className="empty-card foundation-empty">
                      {SUITS[suit]}
                    </div>
                  )}
                </button>
              </div>
            ))}
          </div>
        </div>

        <section className="tableau">
          {game.tableau.map((column, columnIndex) => (
            <div
              className="tableau-column"
              key={columnIndex}
              onClick={() => {
                if (column.length === 0) {
                  clickEmptyColumn(columnIndex);
                }
              }}
            >
              {column.length === 0 && (
                <div className="empty-card tableau-empty" />
              )}

              {column.map((card, cardIndex) => {
                const isSelected =
                  selected?.source === "tableau" &&
                  selected.column === columnIndex &&
                  cardIndex >= selected.cardIndex;

                return (
                  <div
                    className="tableau-card"
                    key={`${columnIndex}-${cardIndex}`}
                    style={{
                      top: `${cardIndex * (card.face_up ? 29 : 15)}px`,
                      zIndex: cardIndex + 1,
                    }}
                  >
                    <PlayingCard
                      card={card}
                      selected={isSelected}
                      onClick={() =>
                        selectTableauCard(columnIndex, cardIndex, card)
                      }
                    />
                  </div>
                );
              })}
            </div>
          ))}
        </section>

        {game.won && (
          <div className="win-message">
            Congratulations! You won the game!
          </div>
        )}
      </section>

      <footer className="instructions">
        Select a face-up card, then select a destination column. Click a
        foundation pile to move an eligible card there. Click the stock to
        draw a card.
      </footer>
    </main>
  );
}

export default App;
