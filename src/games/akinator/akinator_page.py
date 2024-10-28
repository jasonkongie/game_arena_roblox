# src/games/akinator/akinator_page.py

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Optional
import uuid

from src.games.akinator.akinator_game import AkinatorGame
from src.games.game_sessions import games
from fschat.api_provider_game import get_api_provider_stream_iter

router = APIRouter()

@router.post("/start")
def akinator_start(level: Optional[int] = Query(default=1, ge=1, le=3, description="Specify the level of the game (1 to 3)")):
    """
    Start a new game with an optional level parameter.
    """
    session_id = str(uuid.uuid4())
    game = AkinatorGame(level=level)
    games[session_id] = game

    return {
        "message": "Akinator game started at level {}".format(level),
        "session_id": session_id,
        "system_prompt": game.system_prompt,
        "game_secret": game.game_secret  # For testing purposes; remove in production
    }

@router.post("/ask_question")
def akinator_ask_question(session_id: str, user_response: Dict[str, str]):
    if session_id not in games:
        raise HTTPException(status_code=400, detail="Invalid or missing session_id.")

    game = games[session_id]

    if game.is_game_over() or game.reach_max_round():
        return {
            "message": "Game over.",
            "status": game.game_status
        }
    
    user_text = user_response.get('user_response')
    if not user_text:
        raise HTTPException(status_code=400, detail="No user response provided.")
    if user_text.lower() not in (answer.lower() for answer in game.allowed_answers):
        raise HTTPException(status_code=400, detail="Please provide a valid answer. Allowed answers are required.")


    game.current_round += 1

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

    # Check if AI made a guess
    if game.check_akinator_valid_guess(ai_message):
        game.game_over = True
        game.game_status = 'MODEL WIN'
    else:
        game.game_over = True
        game.game_status = 'YOU WIN'

    return {
        "ai_message": ai_message,
        "game_over": game.is_game_over(),
        "game_status": game.game_status
    }

@router.post("/end_game")
def akinator_end_game(session_id: str):
    if session_id in games:
        del games[session_id]
    return {"message": "Akinator game ended."}
