# src/games/taboo/taboo_page.py

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Optional
import uuid

from src.games.taboo.taboo_game import TabooGame
from src.games.game_sessions import games
from fschat.api_provider_game import get_api_provider_stream_iter

router = APIRouter()

@router.post("/start")
def taboo_start(level: Optional[int] = Query(default=1, ge=1, le=3, description="Specify the level of the game (1 to 3)")):
    session_id = str(uuid.uuid4())
    game = TabooGame(game_level=level)
    games[session_id] = game

    return {
        "message": "Taboo game started.",
        "session_id": session_id,
        "system_prompt": game.system_prompt,
        "game_secret": game.game_secret  # For testing purposes; remove in production
    }

@router.post("/ask_question")
def taboo_ask_question(session_id: str, user_response: Dict[str, str]):
    if session_id not in games:
        raise HTTPException(status_code=400, detail="Invalid or missing session_id.")

    game = games[session_id]

    if game.is_game_over():
        return {
            "message": "Game over.",
            "status": "PLAYER_LOSE"
        }

    user_text = user_response.get('user_response')
    if not user_text:
        raise HTTPException(status_code=400, detail="No user response provided.")

    # Update conversation with user response
    game.update_user_conversation(game.conversation, user_text)

    next_llm_query_type = "answer"

    ai_message = game.generation_response(
        next_llm_query_type,
        get_api_provider_stream_iter,
        game.conversation,
    )

    # Update conversation with AI message
    game.update_AI_conversation(game.conversation, ai_message)
    game.round += 1

    # Taboo-specific game logic
    if game.check_word_uttered(ai_message):
        game.game_over = True
        game.game_status = 'PLAYER_WIN'

    #just because LLM made a guess doesn't mean game is over
    # elif game.check_valid_guess(ai_message):
    #     game.game_over = True
    #     game.game_status = 'PLAYER_LOSE'
    elif game.round >= game.max_rounds:
        game.game_over = True
        game.game_status = 'PLAYER_LOSE'

    return {
        "ai_message": ai_message,
        "game_over": game.is_game_over(),
        "game_status": game.game_status
    }

@router.post("/end_game")
def taboo_end_game(session_id: str):
    if session_id in games:
        del games[session_id]
    return {"message": "Taboo game ended."}