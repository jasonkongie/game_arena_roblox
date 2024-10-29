# src/games/taboo/taboo_page.py

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, Optional
import uuid

from src.games.taboo.taboo_game import TabooGame
from src.database import get_db, GameSession, GameState
from sqlalchemy.orm import Session
from fschat.api_provider_game import get_api_provider_stream_iter

router = APIRouter()

@router.post("/start")
def taboo_start(
    level: Optional[int] = Query(default=1, ge=1, le=3, description="Specify the level of the game (1 to 3)"),
    username: Optional[str] = Query(default="anonymous", description="Specify the username"),
    db: Session = Depends(get_db)
):
    """
    Start a new Taboo game with optional level and username parameters.
    """
    session_id = str(uuid.uuid4())
    game = TabooGame(game_level=level)
    
    # Create a new GameSession in the database
    new_session = GameSession(
        session_id=session_id,
        username=username,
        game_name="Taboo",
        state=GameState.PLAYING,
        target_phrase=game.game_secret,
        model=game.model_name,  # Use the model name from the game instance
        history=game.conversation.messages,
        round=game.round,
        game_over=game.game_over,
        game_status=game.game_status,
        level=level  # Store the game level
    )
    db.add(new_session)
    db.commit()

    return {
        "message": "Taboo game started.",
        "session_id": session_id,
        "system_prompt": game.system_prompt,
        "game_secret": game.game_secret  # Remove or hide in production
    }

@router.post("/ask_question")
def taboo_ask_question(
    session_id: str,
    user_response: Dict[str, str],
    db: Session = Depends(get_db)
):
    """
    Handle user's input and generate AI's response in the Taboo game.
    """
    # Retrieve the game session from the database
    game_session = db.query(GameSession).filter_by(session_id=session_id, game_name="Taboo").first()
    if not game_session:
        raise HTTPException(status_code=400, detail="Invalid or missing session_id.")

    # Reconstruct the game state with the correct level
    game = TabooGame(game_level=game_session.level)
    game.conversation.messages = game_session.history or []
    game.round = game_session.round
    game.game_over = game_session.game_over
    game.game_status = game_session.game_status
    game.game_secret = game_session.target_phrase

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
        game.game_status = 'MODEL_LOSE'
    elif game.check_valid_guess(ai_message):
        game.game_over = True
        game.game_status = 'MODEL_WIN'
    elif game.round >= game.max_rounds:
        game.game_over = True
        game.game_status = 'MAX_ROUNDS_REACHED'

    # Update the game session in the database
    game_session.history = list(game.conversation.messages)
    game_session.round = game.round
    game_session.game_over = game.game_over
    game_session.game_status = game.game_status
    db.add(game_session)
    db.commit()

    return {
        "ai_message": ai_message,
        "game_over": game.is_game_over(),
        "game_status": game.game_status
    }

@router.post("/end_game")
def taboo_end_game(session_id: str, db: Session = Depends(get_db)):
    """
    End the Taboo game and remove the session from the database.
    """
    game_session = db.query(GameSession).filter_by(session_id=session_id, game_name="Taboo").first()
    if game_session:
        db.delete(game_session)
        db.commit()
    return {"message": "Taboo game ended."}