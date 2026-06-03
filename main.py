import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from config import BOT_TOKEN
from database import (
    init_db,
    get_masters,
    get_booked,
    add_booking
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_state = {}


# START
@dp.message(F.text == "/start")
async def start(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📅 Записаться")]],
        resize_keyboard=True
    )

    await message.answer("Привет 👋 Нажми кнопку:", reply_markup=kb)


# START BOOKING
@dp.message(F.text == "📅 Записаться")
async def choose_master(message: types.Message):
    masters = await get_masters()

    kb = []
    for m in masters:
        kb.append([KeyboardButton(text=f"{m[0]}|{m[1]}")])

    await message.answer(
        "Выбери мастера:",
        reply_markup=ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    )


# MASTER SELECT
@dp.message(F.text.contains("|"))
async def master_selected(message: types.Message):
    master_id, name = message.text.split("|")

    user_state[message.from_user.id] = {
        "master_id": int(master_id),
        "name": name
    }

    await message.answer("Введи дату (YYYY-MM-DD)")


# DATE
@dp.message(lambda m: len(m.text) == 10 and "-" in m.text)
async def date_selected(message: types.Message):
    user_state[message.from_user.id]["date"] = message.text

    slots = ["10:00","11:00","12:00","13:00","14:00","15:00","16:00","17:00"]

    data = user_state[message.from_user.id]

    booked = await get_booked(data["master_id"], data["date"])
    free = [s for s in slots if s not in booked]

    kb = [[KeyboardButton(text=s)] for s in free]

    await message.answer(
        "Выбери время:",
        reply_markup=ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    )


# TIME
@dp.message(F.text.contains(":"))
async def time_selected(message: types.Message):
    user_id = message.from_user.id
    data = user_state.get(user_id)

    ok = await add_booking(
        user_id,
        data["master_id"],
        data["date"],
        message.text
    )

    if ok:
        await message.answer(f"✅ Записан к {data['name']} на {data['date']} {message.text}")
    else:
        await message.answer("❌ Уже занято")


# START BOT
async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
