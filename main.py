import os, logging, asyncio
from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from bot import router

# ---------- config ----------
BOT_TOKEN   = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")          # full https://... (no path)

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp  = Dispatcher()
dp.include_router(router)

app = FastAPI(docs_url=None, redoc_url=None)

# ---------- 1.  EXACT health-check required by Leapcell ----------
@app.get("/kaithheathcheck")          #  single ‘a’  ─┐
def health():                         #                ├─ do NOT change
    return {"status": "ok"}           #                ┘

# ---------- 2.  Telegram posts to /  (because WEBHOOK_URL has no path) ----------

from aiogram.types import Update   # add this import at the top

@app.post("/")
async def telegram(update: dict):
    await dp.feed_update(bot, Update(**update))



# ---------- startup / shutdown ----------
@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    logging.warning(f"Webhook set to {WEBHOOK_URL}")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.session.close()
# ---------- health-check required by Leapcell ----------
@app.get("/kaithheathcheck")          # MUST be exactly this path
def health():
    return {"status": "ok"}
