# src/games/akinator/akinator_page.py

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, Optional
import uuid

from src.games.akinator.akinator_game import AkinatorGame
from src.database import get_db, GameSession, GameState
from sqlalchemy.orm import Session
from fschat.api_provider_game import get_api_provider_stream_iter

router = APIRouter()

@router.post("/start")
def akinator_start(
    level: Optional[int] = Query(default=1, ge=1, le=3, description="Specify the level of the game (1 to 3)"),
    username: Optional[str] = Query(default="anonymous", description="Specify the username"),
    db: Session = Depends(get_db)
):
    """
    Start a new game with optional level and username parameters.
    """
    session_id = str(uuid.uuid4())
    game = AkinatorGame(level=level)
    # Create a new GameSession in the database
    new_session = GameSession(
        session_id=session_id,
        username=username,
        game_name="Akinator",
        state=GameState.PLAYING,
        target_phrase=game.game_secret,
        model=game.model_name,  # Use the model name from the game instance
        history=game.conversation.messages,
        round=game.current_round,
        game_over=game.game_over,
        game_status=game.game_status,
        level=level  # Store the game level
    )
    db.add(new_session)
    db.commit()

    return {
        "message": f"Akinator game started at level {level}",
        "session_id": session_id,
        "system_prompt": game.system_prompt,
        "game_secret": game.game_secret  # Remove in production
    }

@router.post("/ask_question")
def akinator_ask_question(
    session_id: str,
    user_response: Dict[str, str],
    db: Session = Depends(get_db)
):
    # Retrieve the game session from the database
    game_session = db.query(GameSession).filter_by(session_id=session_id, game_name="Akinator").first()
    if not game_session:
        raise HTTPException(status_code=400, detail="Invalid or missing session_id.")

    # Reconstruct the game state with the correct level
    game = AkinatorGame(level=game_session.level)
    game.conversation.messages = game_session.history
    game.current_round = game_session.round
    game.game_over = game_session.game_over
    game.game_status = game_session.game_status
    game.game_secret = game_session.target_phrase

    if game.is_game_over() or game.reach_max_round():
        game.game_over = True
        game_session.game_over = True
        db.commit()
        return {
            "message": "Game over.",
            "game_over": game.game_over,
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

    # Check if game is over:
    if game.check_akinator_valid_guess(ai_message):
        if game.guessed_word_correctly(ai_message):
            game.game_over = True
            game.game_status = 'MODEL_WIN'

# Update the game session in the database
    game_session.history = list(game.conversation.messages)  # Reassign to new list
    game_session.round = game.current_round
    game_session.game_over = game.game_over
    game_session.game_status = game.game_status
    db.add(game_session)  # Add this line
    db.commit()

    return {
        "ai_message": ai_message,
        "game_over": game.is_game_over(),
        "game_status": game.game_status
    }

@router.post("/end_game")
def akinator_end_game(session_id: str, db: Session = Depends(get_db)):
    game_session = db.query(GameSession).filter_by(session_id=session_id, game_name="Akinator").first()
    if game_session:
        db.delete(game_session)
        db.commit()
    return {"message": "Akinator game ended."}