import os, logging, asyncio
from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from bot import router

# ----- config -----
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")          # full https://.../webhook

# ----- init -----
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()
dp.include_router(router)

app = FastAPI(docs_url=None, redoc_url=None)

# ---------- health-check (Heroku needs it) ----------
@app.get("/")
def index():
    return {"status": "ok"}

# ---------- webhook ----------
@app.post(WEBHOOK_PATH)
async def webhook(update: dict):
    """Telegram pushes Update here."""
    await dp.feed_update(bot, update)

# ---------- set webhook on start-up ----------
@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    logging.warning(f"Webhook set to {WEBHOOK_URL}")

# ---------- graceful shutdown ----------
@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.session.close()

# ---------- health-check required by Leapcell ----------
@app.get("/kaithheathcheck")          # MUST be exactly this path
def health():
    return {"status": "ok"}

