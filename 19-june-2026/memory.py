import json
from redis_client import redis_client

TTL_12_HOURS = 12 * 60 * 60
MAX_TURNS = 10


def load_history(session_id: str) -> list:
    """Read conversation history."""

    try:
        data = redis_client.get(f"conv:{session_id}")
        return json.loads(data) if data else []

    except Exception:
        return []


def save_turn(
    session_id: str,
    history: list,
    question: str,
    answer: str
) -> list:
    """Save one user question and assistant answer."""

    new_history = history + [
        {
            "role": "user",
            "content": question
        },
        {
            "role": "assistant",
            "content": answer
        }
    ]

    if len(new_history) > MAX_TURNS * 2:
        new_history = new_history[-MAX_TURNS * 2:]

    try:
        redis_client.setex(
            f"conv:{session_id}",
            TTL_12_HOURS,
            json.dumps(new_history)
        )

    except Exception as e:
        print(f"[memory] save failed: {e}")

    return new_history