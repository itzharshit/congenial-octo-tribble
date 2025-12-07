import os, logging, asyncio
from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from bot import router
from aiogram.types import Update

from datetime import datetime
import aiohttp

BOT_TOKEN   = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")          # full https://... (no path)

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp  = Dispatcher()
dp.include_router(router)

app = FastAPI(docs_url=None, redoc_url=None)

@app.get("/")
@app.get("/kaithhealthcheck")
@app.get("/kaithheathcheck")          
def health():                                 
    return {"status": "ok"}

# ---------- 2.  Telegram posts to /  (because WEBHOOK_URL has no path) ----------

@app.post("/")
async def telegram(update: dict):
    await dp.feed_update(bot, Update(**update))

# ---------- keep-alive function ----------
async def keep_alive():
    # Clean the URL - remove trailing slash if present
    url = WEBHOOK_URL.rstrip('/')
    
    while True:
        await asyncio.sleep(26)  # Ping every 26 seconds (less than 30s idle timeout)
        try:
            # Simple request with short timeout and no SSL verification
            async with aiohttp.ClientSession() as session:
                # 4 second timeout is plenty for a simple GET request
                async with session.get(url, timeout=4, ssl=False) as resp:
                    if resp.status == 200:
                        logging.debug(f"Keep-alive success at {datetime.now()}")
                    else:
                        logging.debug(f"Keep-alive status {resp.status} at {datetime.now()}")
        except asyncio.TimeoutError:
            # Timeouts happen occasionally, not an error
            logging.debug(f"Keep-alive timeout at {datetime.now()} (expected)")
        except Exception as e:
            # Any other error - log at debug level, not error
            logging.debug(f"Keep-alive attempt failed: {type(e).__name__}")

# ---------- startup / shutdown ----------
@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    logging.warning(f"Webhook set to {WEBHOOK_URL}")
    
    # Start keep-alive as a background task
    asyncio.create_task(keep_alive())
    logging.info("Keep-alive task started (pinging every 26 seconds)")
    
@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.session.close()
