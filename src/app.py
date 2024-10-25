# app.py

import sys
sys.path.append('/home/ubuntu/game_arena_roblox')

from flask import Flask, request, jsonify
from src.games.akinator.akinator_game import AkinatorGame
from src.games.taboo.taboo_game import TabooGame
from games.bluffing.bluffing_game import BluffingGame
import TextGeneration  # Import TextGeneration module
import uuid

app = Flask(__name__)

# Use an in-memory store for sessions
games = {}

@app.route("/", methods=["GET"])
def main():
    return "Welcome to the Game Arena!"

# Akinator Game Endpoints

@app.route('/akinator_start', methods=['POST'])
def akinator_start():
    # Generate a unique session ID
    session_id = str(uuid.uuid4())
    # Initialize a new Akinator game and store it
    game = AkinatorGame()
    games[session_id] = game

    return jsonify({
        "message": "Akinator game started.",
        "session_id": session_id,
        "system_prompt": game.system_prompt,
        "game_secret": game.game_secret  # Send the secret word to the client
    })

@app.route('/akinator_ask_question', methods=['POST'])
def akinator_ask_question():
    # Get session ID from request
    session_id = request.args.get('session_id')
    if not session_id or session_id not in games:
        return jsonify({"error": "Invalid or missing session_id."}), 400

    game = games[session_id]

    if game.is_game_over():
        return jsonify({"message": "Game over.", "status": game.game_status}), 200

    # Get user response from request
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON."}), 400
    user_response = data.get('user_response')

    if not user_response:
        return jsonify({"error": "No user response provided."}), 400

    # Update conversation with user response
    game.update_conversation('user', user_response)

    # Prepare model input
    model_input = TextGeneration.GenerateModelInput(game.conversation)

    # Generate AI's next question or guess
    ai_message = TextGeneration.GenerateText(model_input)

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
        "game_over": game.is_game_over(),
        "game_status": game.game_status
    })

@app.route('/akinator_end_game', methods=['POST'])
def akinator_end_game():
    # Get session ID from request
    session_id = request.args.get('session_id')
    if session_id in games:
        del games[session_id]
    return jsonify({"message": "Akinator game ended."})

# Taboo Game Endpoints

@app.route('/taboo_start', methods=['POST'])
def taboo_start():
    # Generate a unique session ID
    session_id = str(uuid.uuid4())
    # Initialize a new Taboo game and store it
    game = TabooGame()
    games[session_id] = game

    return jsonify({
        "message": "Taboo game started.",
        "session_id": session_id,
        "system_prompt": game.system_prompt,
        "game_secret": game.game_secret  # Send the secret word to the client
    })

@app.route('/taboo_ask_question', methods=['POST'])
def taboo_ask_question():
    # Get session ID from request
    session_id = request.args.get('session_id')
    if not session_id or session_id not in games:
        return jsonify({"error": "Invalid or missing session_id."}), 400

    game = games[session_id]

    if game.is_game_over():
        return jsonify({"message": "Game over.", "status": game.game_status}), 200

    # Get user response from request
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON."}), 400
    user_response = data.get('user_response')

    if not user_response:
        return jsonify({"error": "No user response provided."}), 400

    # Update conversation with user response
    game.update_conversation('user', user_response)

    # Prepare model input
    model_input = TextGeneration.GenerateModelInput(game.conversation)

    # Generate AI's next response
    ai_message = TextGeneration.GenerateText(model_input)

    # Update conversation with AI message
    game.update_conversation('assistant', ai_message)
    game.current_round += 1

    # Taboo-specific game logic
    if game.check_word_uttered(ai_message):
        game.game_over = True
        game.game_status = 'MODEL_LOSE'
    elif game.check_valid_guess(ai_message):
        game.game_over = True
        game.game_status = 'MODEL_WIN'
    elif game.current_round >= game.max_rounds:
        game.game_over = True
        game.game_status = 'MAX_ROUNDS_REACHED'

    # Update the game state in the games dictionary
    games[session_id] = game

    return jsonify({
        "ai_message": ai_message,
        "game_over": game.is_game_over(),
        "game_status": game.game_status
    })

@app.route('/taboo_end_game', methods=['POST'])
def taboo_end_game():
    # Get session ID from request
    session_id = request.args.get('session_id')
    if session_id in games:
        del games[session_id]
    return jsonify({"message": "Taboo game ended."})


@app.route('/bluffing_start', methods=['POST'])
def bluffing_start():
    # Generate a unique session ID
    session_id = str(uuid.uuid4())
    # Initialize a new Bluffing game and store it
    game = BluffingGame()
    games[session_id] = game

    return jsonify({
        "message": "Bluffing game started.",
        "session_id": session_id,
        "system_prompt": game.system_prompt,
        "system_question": game.system_question,
        "instructions": "Please provide your initial statement using '/bluffing_provide_statement' endpoint."
    })

@app.route('/bluffing_provide_statement', methods=['POST'])
def bluffing_provide_statement():
    # Get session ID from request
    session_id = request.args.get('session_id')
    if not session_id or session_id not in games:
        return jsonify({"error": "Invalid or missing session_id."}), 400

    game = games[session_id]

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON."}), 400

    user_statement = data.get('user_statement')
    user_statement_truth = data.get('truthfulness')  # 'True' or 'False'

    if not user_statement or user_statement_truth not in ['True', 'False']:
        return jsonify({"error": "Please provide 'user_statement' and 'truthfulness' ('True' or 'False')."}), 400

    # Store the user's initial statement and truthfulness
    game.first_user_message = f"Statement: {user_statement}"
    game.user_statement_truth = user_statement_truth

    # Update conversation
    game.update_conversation('user', game.first_user_message)

    # Prepare model input
    model_input = TextGeneration.GenerateModelInput(game.conversation)

    # Generate AI's first question
    ai_message = TextGeneration.GenerateText(model_input)

    # Update conversation with AI message
    game.update_conversation('assistant', ai_message)

    return jsonify({
        "ai_message": ai_message,
        "game_over": game.is_game_over()
    })


@app.route('/bluffing_ask_question', methods=['POST'])
def bluffing_ask_question():
    # Get session ID from request
    session_id = request.args.get('session_id')
    if not session_id or session_id not in games:
        return jsonify({"error": "Invalid or missing session_id."}), 400

    game = games[session_id]

    if game.is_game_over():
        return jsonify({"message": "Game over.", "status": game.game_status}), 200

    # Get user response from request
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON."}), 400
    user_response = data.get('user_response')

    if not user_response:
        return jsonify({"error": "No user response provided."}), 400

    # Update conversation with user response
    game.update_conversation('user', user_response)

    # Prepare model input
    model_input = TextGeneration.GenerateModelInput(game.conversation)

    # Generate AI's next question or guess
    ai_message = TextGeneration.GenerateText(model_input)

    # Update conversation with AI message
    game.update_conversation('assistant', ai_message)
    game.current_round += 1

    # Check if AI made a guess
    if game.is_llm_giving_answer(ai_message):
        if game.check_user_win(ai_message, game.user_statement_truth):
            game.set_game_status('USER_WIN')
        else:
            game.set_game_status('MODEL_WIN')

    # Check for max rounds
    if game.current_round >= game.max_rounds and not game.is_game_over():
        game.set_game_status('MAX_ROUNDS_REACHED')

    # Update the game state in the games dictionary
    games[session_id] = game

    return jsonify({
        "ai_message": ai_message,
        "game_over": game.is_game_over(),
        "game_status": game.game_status
    })

@app.route('/bluffing_end_game', methods=['POST'])
def bluffing_end_game():
    # Get session ID from request
    session_id = request.args.get('session_id')
    if session_id in games:
        del games[session_id]
    return jsonify({"message": "Bluffing game ended."})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)