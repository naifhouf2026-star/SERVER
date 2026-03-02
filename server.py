import asyncio
import websockets
import os
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import ApiTelegramException

BOT_TOKEN = "8290696483:AAG-yonVayadxER2bWAUUVzxV0tOxhTGYws"
CHANNEL_ID = -1002484572207

bot = AsyncTeleBot(BOT_TOKEN)
connected_clients = set()

async def ws_handler(websocket):
    print("[Server] New client connected.")
    connected_clients.add(websocket)
    try:
         await websocket.wait_closed()
    finally:
         connected_clients.remove(websocket)
         print("[Server] Client disconnected.")

@bot.channel_post_handler(func=lambda message: message.chat.id == CHANNEL_ID)
async def handle_channel_post(message):
    if message.text:
        print(f"[Telegram] New signal received:\n{message.text}")
        if connected_clients:
            await asyncio.gather(
                *(ws.send(message.text) for ws in connected_clients),
                return_exceptions=True
            )

async def start_bot():
    while True:
        try:
            print("Starting Telegram bot polling...")
            # التعديل الخاص بك هنا: حذف الويب هوك مع تجاهل التحديثات المتراكمة
            await bot.delete_webhook(drop_pending_updates=True) 
            await bot.infinity_polling(skip_pending=True)
        except ApiTelegramException as e:
            if e.error_code == 409:
                print("⚠️ Conflict detected (409). Another instance is running! Waiting 10s...")
                await asyncio.sleep(10)
            else:
                print("Telegram API Error:", e)
                await asyncio.sleep(5)
        except Exception as e:
            print("Unexpected error:", e)
            await asyncio.sleep(5)

async def main():
    port = int(os.environ.get("PORT", 8765))
    host = "0.0.0.0"
    print(f"Starting WebSocket server on port {port}...")
    
    async with websockets.serve(ws_handler, host, port):
        await start_bot()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user.")