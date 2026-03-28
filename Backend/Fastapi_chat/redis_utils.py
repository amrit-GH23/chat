import redis.asyncio as redis
import asyncio
from .manager import manager
# from ..app.config import REDIS_URL

REDIS_URL = "redis://localhost:6379"  # Update this if your Redis is running elsewhere
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


async def redis_connector(channel_name:str):
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel_name)
    for message in pubsub.listen():
        if message['type'] == 'message':
            await manager.broadcast(message['data'])