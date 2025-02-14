from flask import Flask, render_template, request, jsonify
import chess
import chess.engine

app = Flask(__name__)

# Initialize the chess board and engine
board = chess.Board()
engine = None  # Initialize engine later if needed

# You'll need to specify the path to your Stockfish engine.
# Download Stockfish from: https://stockfishchess.org/download/
STOCKFISH_PATH = "/path/to/stockfish" # Replace with your Stockfish path!

@app.route("/")
def index():
    return render_template("index.html", board=board.fen())

@app.route("/move", methods=["POST"])
def move():
    try:
        move_uci = request.form.get("move")
        move = chess.Move.from_uci(move_uci)

        if move in board.legal_moves:
            board.push(move)

            # Computer move (if engine is available)
            if engine:
                result = engine.play(board, chess.engine.Limit(time=2.0)) # Adjust time limit
                if result.move:
                    board.push(result.move)
                    return jsonify({"board": board.fen(), "computer_move": result.move.uci()})
                else:
                    return jsonify({"board": board.fen(), "message": "No legal computer move."})
            return jsonify({"board": board.fen()})
        else:
            return jsonify({"error": "Illegal move."})

    except ValueError:
        return jsonify({"error": "Invalid move format."})
    except Exception as e:
        return jsonify({"error": str(e)})  # Handle other potential errors

@app.route("/reset", methods=["POST"])
def reset():
    global board
    board = chess.Board()
    return jsonify({"board": board.fen()})

@app.route("/start_engine", methods=["POST"])
def start_engine():
    global engine
    try:
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        return jsonify({"message": "Engine started."})
    except FileNotFoundError:
        return jsonify({"error": "Stockfish engine not found.  Check the path."})
    except Exception as e:
        return jsonify({"error": f"Error starting engine: {e}"})

@app.route("/stop_engine", methods=["POST"])
def stop_engine():
    global engine
    if engine:
        engine.quit()
        engine = None
        return jsonify({"message": "Engine stopped."})
    return jsonify({"message": "Engine not running."})


if __name__ == "__main__":
    app.run(debug=True)  # Set debug=False in production
