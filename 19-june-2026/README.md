# Chatbot API (19-june-2026)

A FastAPI-based chatbot backend that stores user data and conversation history in SQLite, with temporary conversation memory backed by Redis.

## Features

- User registration and login
- Chat endpoint for sending messages and receiving responses
- Persistent chat history stored in `data/chatbot.db`
- Conversation memory stored in Redis
- Automatic SQLite database file creation

## Requirements

- Python 3.11+ (or compatible)
- Redis access for conversation memory
- `requirements.txt` contains the dependencies

## Setup

1. Create and activate a Python virtual environment.

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in this folder with the following values:

```env
GOOGLE_API_KEY=your_google_api_key
REDIS_HOST=your_redis_host
REDIS_PORT=your_redis_port
REDIS_USERNAME=your_redis_username
REDIS_PASSWORD=your_redis_password
```

4. Make sure the `data/` folder exists. The SQLite database `data/chatbot.db` is created automatically when the app starts.

## Run the app

```bash
uvicorn main:app --reload
```

## API Endpoints

- `GET /` - Health check
- `POST /register` - Register a new user
- `POST /login` - Login existing user
- `POST /chat` - Send a chat message and receive a response

## Notes

- `.env` is ignored by Git and should not be committed.
- The database schema is created automatically via SQLAlchemy when the app starts.
- Untracked files such as local test data should remain outside the committed project.
