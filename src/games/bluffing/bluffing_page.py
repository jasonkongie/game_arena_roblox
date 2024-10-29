# src/games/bluffing/bluffing_page.py

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, Optional
import uuid

from src.games.bluffing.bluffing_game import BluffingGame
from src.database import get_db, GameSession, GameState
from sqlalchemy.orm import Session
from fschat.api_provider_game import get_api_provider_stream_iter

router = APIRouter()

@router.post("/start")
def bluffing_start(
    level: Optional[int] = Query(default=1, ge=1, le=3, description="Specify the level of the game (1 to 3)"),
    username: Optional[str] = Query(default="anonymous", description="Specify the username"),
    db: Session = Depends(get_db)
):
    """
    Start a new Bluffing game with optional level and username parameters.
    """
    session_id = str(uuid.uuid4())
    game = BluffingGame(game_level=level)

    # Create a new GameSession in the database
    new_session = GameSession(
        session_id=session_id,
        username=username,
        game_name="Bluffing",
        state=GameState.PLAYING,
        target_phrase=game.system_question,  # Store the system question as the target phrase
        model=game.model_name,  # Use the model name from the game instance
        history=game.conversation.messages,
        round=game.round,
        game_over=game.game_over,
        game_status=game.game_status,
        level=level
    )
    db.add(new_session)
    db.commit()

    return {
        "message": "Bluffing game started.",
        "session_id": session_id,
        "system_prompt": game.system_prompt,
        "system_question": game.system_question,  # Remove or hide in production
        "instructions": "Please provide your initial statement using the '/provide_statement' endpoint."
    }

@router.post("/provide_statement")
def bluffing_provide_statement(
    session_id: str,
    user_input: Dict[str, str],
    db: Session = Depends(get_db)
):
    """
    Handle the user's initial statement and truthfulness in the Bluffing game.
    """
    game_session = db.query(GameSession).filter_by(session_id=session_id, game_name="Bluffing").first()
    if not game_session:
        raise HTTPException(status_code=400, detail="Invalid or missing session_id.")

    # Reconstruct the game state
    game = BluffingGame(game_level=game_session.level)
    game.conversation.messages = game_session.history or []
    game.round = game_session.round
    game.game_over = game_session.game_over
    game.game_status = game_session.game_status
    game.system_question = game_session.target_phrase

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

    # Update the game session in the database
    game_session.history = list(game.conversation.messages)
    game_session.round = game.round
    game_session.game_over = game.game_over
    game_session.game_status = game.game_status
    db.add(game_session)
    db.commit()

    return {
        "ai_message": ai_message,
        "game_over": game.is_game_over()
    }

@router.post("/ask_question")
def bluffing_ask_question(
    session_id: str,
    user_response: Dict[str, str],
    db: Session = Depends(get_db)
):
    """
    Handle user's input and generate AI's response during the Bluffing game.
    """
    game_session = db.query(GameSession).filter_by(session_id=session_id, game_name="Bluffing").first()
    if not game_session:
        raise HTTPException(status_code=400, detail="Invalid or missing session_id.")

    # Reconstruct the game state
    game = BluffingGame(game_level=game_session.level)
    game.conversation.messages = game_session.history or []
    game.round = game_session.round
    game.game_over = game_session.game_over
    game.game_status = game_session.game_status
    game.system_question = game_session.target_phrase
    game.user_statement_truth = None  # Retrieve from game or store in session if needed

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
def bluffing_end_game(session_id: str, db: Session = Depends(get_db)):
    """
    End the Bluffing game and remove the session from the database.
    """
    game_session = db.query(GameSession).filter_by(session_id=session_id, game_name="Bluffing").first()
    if game_session:
        db.delete(game_session)
        db.commit()
    return {"message": "Bluffing game ended."}