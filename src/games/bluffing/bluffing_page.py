# src/games/bluffing/bluffing_page.py

from fastapi import APIRouter, HTTPException
from typing import Dict
import uuid

from src.games.bluffing.bluffing_game import BluffingGame
from src.games.game_sessions import games
from fschat.api_provider_game import get_api_provider_stream_iter

router = APIRouter()

@router.post("/start")
def bluffing_start():
    session_id = str(uuid.uuid4())
    game = BluffingGame()
    games[session_id] = game

    return {
        "message": "Bluffing game started.",
        "session_id": session_id,
        "system_prompt": game.system_prompt,
        "system_question": game.system_question,
        "instructions": "Please provide your initial statement using the '/provide_statement' endpoint."
    }

@router.post("/provide_statement")
def bluffing_provide_statement(session_id: str, user_input: Dict[str, str]):
    if session_id not in games:
        raise HTTPException(status_code=400, detail="Invalid or missing session_id.")

    game = games[session_id]

    user_statement = user_input.get('user_statement')
    user_statement_truth = user_input.get('truthfulness')  # 'True' or 'False'

    if not user_statement or user_statement_truth not in ['True', 'False']:
        raise HTTPException(status_code=400, detail="Please provide 'user_statement' and 'truthfulness' ('True' or 'False').")

    # Store the user's initial statement and truthfulness
    game.first_user_message = f"Statement: {user_statement}"
    game.user_statement_truth = user_statement_truth

    # Update conversation
    game.update_user_conversation(game.conversation, game.first_user_message)
    next_llm_query_type = "question"

    ai_message = game.generation_response(
        next_llm_query_type,
        get_api_provider_stream_iter,
        game.conversation,
    )

    # Update conversation with AI message
    game.update_AI_conversation(game.conversation, ai_message)

    return {
        "ai_message": ai_message,
        "game_over": game.is_game_over()
    }

@router.post("/ask_question")
def bluffing_ask_question(session_id: str, user_response: Dict[str, str]):
    if session_id not in games:
        raise HTTPException(status_code=400, detail="Invalid or missing session_id.")

    game = games[session_id]

    if game.is_game_over():
        return {
            "message": "Game over.",
            "status": game.game_status
        }

    user_text = user_response.get('user_response')
    if not user_text:
        raise HTTPException(status_code=400, detail="No user response provided.")

    # Update conversation with user response
    game.update_user_conversation(game.conversation, user_text)
    next_llm_query_type = "question"

    ai_message = game.generation_response(
        next_llm_query_type,
        get_api_provider_stream_iter,
        game.conversation,
    )

    # Update conversation with AI message
    game.update_AI_conversation(game.conversation, ai_message)
    game.round += 1

    # Check if AI made a guess
    if game.is_llm_giving_answer(ai_message):
        if game.check_user_win(ai_message, game.user_statement_truth):
            game.set_game_status('USER_WIN')
        else:
            game.set_game_status('MODEL_WIN')

    # Check for max rounds
    if game.round >= game.max_rounds and not game.is_game_over():
        game.set_game_status('MAX_ROUNDS_REACHED')

    return {
        "ai_message": ai_message,
        "game_over": game.is_game_over(),
        "game_status": game.game_status
    }

@router.post("/end_game")
def bluffing_end_game(session_id: str):
    if session_id in games:
        del games[session_id]
    return {"message": "Bluffing game ended."}