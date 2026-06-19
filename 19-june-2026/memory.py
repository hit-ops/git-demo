from redis_client import redis_client


def save_message(user_id, role, message):
    key = f"chat:{user_id}"

    redis_client.rpush(
        key,
        f"{role}: {message}"
    )

    # Keep only the last 20 messages
    redis_client.ltrim(key, -20, -1)


def get_conversation(user_id):
    key = f"chat:{user_id}"

    return redis_client.lrange(
        key,
        0,
        -1
    )