import asyncio
import random
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart, Command
import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "8505307205:AAE0SOPG9dEbJJqkWzX-Xd7zMFvDJXCgSv0")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

WISHES = [
    "☀️ Хорошего тебе дня, всё получится!",
    "🌸 Пусть этот день принесёт тебе только радость!",
    "✨ Сегодня будет отличный день, я уверен!",
    "🌈 Пусть всё идёт легко и приятно!",
    "🍀 Удача сегодня на твоей стороне!",
    "💫 Этот день создан специально для тебя!",
    "🌺 Пусть каждый час сегодня будет приятным!",
    "🎉 Сегодня точно будет что-то хорошее!",
]

COMPLIMENTS = [
    "😍 Ты просто красавчик/красавица — это факт!",
    "💎 Ты особенный человек, таких мало!",
    "🌟 Ты светишься изнутри, это видно!",
    "🦋 Ты невероятно притягательный человек!",
    "💫 Твоя улыбка способна осветить любую комнату!",
    "👑 Ты настоящая королева/король — держи корону ровно!",
    "🌹 Ты красивый/красивая — и снаружи, и внутри!",
    "✨ Рядом с тобой всем становится лучше!",
    "💪 Ты сильный и красивый человек!",
    "🥰 Ты заслуживаешь всего самого лучшего!",
]

MOODS = [
    "😊 Желаю тебе отличного настроения весь день!",
    "🎵 Пусть внутри играет любимая музыка и всё радует!",
    "🌞 Заряжайся позитивом — ты этого достоин(а)!",
    "💃 Пусть настроение будет как на вечеринке!",
    "🍭 Жизнь сладкая — наслаждайся каждым моментом!",
    "🎊 Сегодня поводов для улыбки будет много!",
    "🌻 Пусть на душе будет тепло и спокойно!",
    "🦄 Ты уникальный — радуйся этому!",
]

EVENING = [
    "🌙 Хорошего вечера! Ты сегодня молодец.",
    "⭐ Пусть ночь будет спокойной и сны приятными!",
    "🌜 Отдыхай, завтра будет новый отличный день!",
    "💤 Хорошего отдыха — ты заслужил(а)!",
]

def get_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="☀️ Пожелание дня"), KeyboardButton(text="😍 Комплимент")],
            [KeyboardButton(text="😊 Поднять настроение"), KeyboardButton(text="🌙 Доброй ночи")],
        ],
        resize_keyboard=True
    )


@dp.message(CommandStart())
async def cmd_start(message: Message):
    name = message.from_user.first_name
    await message.answer(
        f"Привет, {name}! 🎉\n\n"
        "Я бот хорошего настроения! 💫\n"
        "Буду желать тебе хорошего дня, говорить комплименты и поднимать настроение!\n\n"
        "Выбирай кнопку или просто напиши мне что-нибудь 👇",
        reply_markup=get_keyboard()
    )


@dp.message(F.text == "☀️ Пожелание дня")
async def wish_day(message: Message):
    await message.answer(random.choice(WISHES))


@dp.message(F.text == "😍 Комплимент")
async def compliment(message: Message):
    await message.answer(random.choice(COMPLIMENTS))


@dp.message(F.text == "😊 Поднять настроение")
async def mood(message: Message):
    await message.answer(random.choice(MOODS))


@dp.message(F.text == "🌙 Доброй ночи")
async def good_night(message: Message):
    await message.answer(random.choice(EVENING))


@dp.message(F.text)
async def any_message(message: Message):
    all_messages = WISHES + COMPLIMENTS + MOODS
    await message.answer(random.choice(all_messages))


async def main():
    print("Бот запущен! 🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
