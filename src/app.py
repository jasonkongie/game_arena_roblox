from flask import Flask, Response, request, jsonify
from TextGeneration import GenerateText, GenerateModelInput
from src.games.akinator_game import AkinatorGame
from src.games.text_generation import generate_ai_response
import uuid

app = Flask(__name__)

# Use an in-memory store for sessions
games = {}

# Remove the 'POST' method from the default route
@app.route("/", methods=["GET"])
def main():
    return "Welcome to the Flask App!"

# Place specific routes below
@app.route('/start_game', methods=['POST'])
def start_game():
    # Generate a unique session ID
    session_id = str(uuid.uuid4())
    # Initialize a new game and store it in the games dictionary
    game = AkinatorGame()
    games[session_id] = game

    return jsonify({
        "message": "Game started.",
        "session_id": session_id,
        "system_prompt": game.system_prompt
    })

@app.route('/ask_question', methods=['POST'])
def ask_question():
    # Get session ID from request
    session_id = request.args.get('session_id')
    if not session_id or session_id not in games:
        return jsonify({"error": "Invalid or missing session_id."}), 400

    game = games[session_id]

    if game.is_game_over():
        return jsonify({"message": "Game over.", "status": game.game_status}), 200

    # Get user response from request
    user_response = request.json.get('user_response')

    if not user_response:
        return jsonify({"error": "No user response provided."}), 400

    # Update conversation with user response
    game.update_conversation('user', user_response)

    # Generate AI's next question or guess
    ai_message = generate_ai_response(game)

    # Update conversation with AI message
    game.update_conversation('assistant', ai_message)
    game.current_round += 1

    # Check if AI made a guess
    if game.check_valid_guess(ai_message):
        game.game_over = True
        game.game_status = 'MODEL_WIN'

    # Update the game state in the games dictionary
    games[session_id] = game

    return jsonify({
        "ai_message": ai_message,
        "game_over": game.is_game_over()
    })

@app.route('/end_game', methods=['POST'])
def end_game():
    # Get session ID from request
    session_id = request.args.get('session_id')
    if session_id in games:
        del games[session_id]
    return jsonify({"message": "Game ended."})