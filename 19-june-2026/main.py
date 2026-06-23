from fastapi import (
    FastAPI,
    HTTPException,
    Depends
)
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)
from pydantic import EmailStr
import logging

from database import engine, SessionLocal
from models import Base, User, ChatHistory
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token
)
from chatbot import get_response
from memory import (
    save_message,
    get_conversation
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

security = HTTPBearer()

# Create tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {
        "message": "Chatbot API Running"
    }


# ---------------- REGISTER ----------------
@app.post("/register")
def register(
        email: EmailStr,
        password: str
):
    if len(password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters"
        )

    db = SessionLocal()

    try:
        existing_user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )

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

        logger.error(
            f"Registration Error: {str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail="Registration failed"
        )

    finally:
        db.close()


# ---------------- LOGIN ----------------
@app.post("/login")
def login(
        email: EmailStr,
        password: str
):
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        if not verify_password(
                password,
                user.password
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid Password"
            )

        access_token = create_access_token(
            {
                "user_id": user.id
            }
        )

        return {
            "message": "Login Successful",
            "access_token": access_token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            f"Login Error: {str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail="Login failed"
        )

    finally:
        db.close()


# ---------------- CHAT ----------------
@app.post("/chat")
def chat(
        message: str,
        credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    user_id = verify_token(token)

    if not message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # Get previous conversation from Redis
        history = get_conversation(user_id) or []

        # Get response from Gemini
        response = get_response(
            history,
            message
        )

        # Save in Redis
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

        # Save in SQLite
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

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()

        logger.error(
            f"Chat Error: {str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail="Chat request failed"
        )

    finally:
        db.close()