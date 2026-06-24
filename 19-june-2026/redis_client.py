import os
import redis
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("REDIS_HOST")
PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

redis_client = redis.Redis(
    host=HOST,
    port=int(PORT),
    decode_responses=True,
    username="default",
    password=REDIS_PASSWORD,
)

try:
    print(redis_client.ping())
    print("Redis Connected Successfully")
except Exception as e:
    print("Redis Connection Error:", e)