import asyncio
import websockets

async def test_ws():
    uri = "ws://localhost:8000/ws/chat/room1/"
    async with websockets.connect(uri) as ws:
        print("✅ Connected to WebSocket!")
        await ws.send("Hello, WebSocket!")
        response = await ws.recv()
        print(f"📥 Received: {response}")

asyncio.run(test_ws())
