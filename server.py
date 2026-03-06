import asyncio
import websockets
import os
from telethon import TelegramClient, events

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
PHONE = os.environ.get("PHONE")

CHANNEL_IDS = [-1003740216444, -1003830801197]

connected_clients = set()

client = TelegramClient("session", API_ID, API_HASH)


async def ws_handler(websocket):
    print("[Server] New client connected.")
    connected_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        connected_clients.remove(websocket)
        print("[Server] Client disconnected.")


@client.on(events.NewMessage(chats=CHANNEL_IDS))
async def handler(event):
    text = event.raw_text
    if text:
        print(f"[Telegram] New signal:\n{text}")

        if connected_clients:
            await asyncio.gather(
                *(ws.send(text) for ws in connected_clients),
                return_exceptions=True
            )


async def start_telegram():
    await client.start(phone=PHONE)
    print("Telegram connected.")
    await client.run_until_disconnected()


async def main():
    port = int(os.environ.get("PORT", 8765))
    host = "0.0.0.0"

    print(f"Starting WebSocket server on {port}")

    async with websockets.serve(ws_handler, host, port):
        await start_telegram()


if __name__ == "__main__":
    asyncio.run(main())
