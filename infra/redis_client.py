import os
import redis.asyncio as redis

REDIS_URL = os.environ["REDIS_URL"]

redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_timeout=10,
    socket_connect_timeout=10,
    health_check_interval=30,
    retry_on_timeout=True,
)

STREAM_NAME = "chat:requests"
GROUP_NAME = "chat-workers"
