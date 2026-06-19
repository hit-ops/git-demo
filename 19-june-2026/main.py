from fastapi import FastAPI, HTTPException
from database import engine, SessionLocal
from models import Base, User, ChatHistory
from auth import hash_password, verify_password
from chatbot import get_response
from memory import save_message, get_conversation
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {
        "message": "Chatbot API Running"
    }


# Register User
@app.post("/register")
def register(email: str, password: str):
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    db = SessionLocal()
    try:
        existing_user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")

        hashed_password = hash_password(password)

        user = User(
            email=email,
            password=hashed_password
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "message": "User Registered Successfully",
            "user_id": user.id
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error during registration: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")
    finally:
        db.close()


# Login User
@app.post("/login")
def login(email: str, password: str):
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    db = SessionLocal()
    try:
        user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        if not verify_password(
            password,
            user.password
        ):
            raise HTTPException(status_code=401, detail="Invalid Password")

        return {
            "message": "Login Successful",
            "user_id": user.id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")
    finally:
        db.close()


# Chat Endpoint
@app.post("/chat")
def chat(user_id: int, message: str):

    if not message or not message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    db = SessionLocal()

    try:
        # Get previous conversation from Redis
        history = get_conversation(user_id) or []

        # Get response using history + current message
        response = get_response(
            history,
            message
        )

        # Save conversation in Redis
        save_message(
            user_id,
            "Human",
            message
        )

        save_message(
            user_id,
            "AI",
            response
        )

        # Save permanent history in SQLite
        chat_record = ChatHistory(
            user_id=user_id,
            question=message,
            answer=response
        )

        db.add(chat_record)
        db.commit()
        db.refresh(chat_record)

        return {
            "response": response,
            "chat_id": chat_record.id
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error during chat: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail="Chat request failed"
        )

    finally:
        db.close()