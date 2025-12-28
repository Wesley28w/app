import os
import redis.asyncio as redis

STREAM_NAME = "chat:requests"
GROUP_NAME = "chat-workers"


def get_redis():
    """
    Always create a NEW Redis client.
    Redis Cloud drops idle TLS connections.
    """
    return redis.from_url(
        os.environ["REDIS_URL"],
        decode_responses=True,
        socket_timeout=None,          # 🔑 required for Redis Cloud
        socket_connect_timeout=5,
        retry_on_timeout=True,
        health_check_interval=30,     # 🔑 keepalive
    )