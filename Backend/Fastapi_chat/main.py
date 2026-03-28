from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .manager import manager
from .redis_utils import redis_client, redis_connector
import asyncio

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Start the Redis listener as a background task
    asyncio.create_task(redis_connector("global_chat"))

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from the client
            data = await websocket.receive_text()
            
            # Instead of broadcasting directly, we send it to Redis
            # This ensures ALL server instances see the message
            payload = f"User {client_id}: {data}"
            await redis_client.publish("global_chat", payload)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await redis_client.publish("global_chat", f"User {client_id} left the chat")