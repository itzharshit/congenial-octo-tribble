from aiogram import Router, types
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Hi! I echo everything you say.")

@router.message()
async def echo(message: types.Message):
    await message.send_copy(chat_id=message.chat.id)
