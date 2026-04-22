import asyncio
import random
import aiohttp
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart, Command
from datetime import datetime, timedelta
from groq import Groq

BOT_TOKEN = os.getenv("BOT_TOKEN")
MPSTATS_TOKEN = os.getenv("MPSTATS_TOKEN")
GROQ_TOKEN = os.getenv("GROQ_TOKEN")
ADMIN_ID = 7877326182

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
groq_client = Groq(api_key=GROQ_TOKEN)

problem_mode_users = set()

MPSTATS_HEADERS = {
    "X-Mpstats-TOKEN": MPSTATS_TOKEN,
    "Content-Type": "application/json"
}

# ID категорий MPstat для одежды (весна-лето, актуально для мая)
MAY_CATEGORIES = [
    (105, "Платья"),
    (107, "Блузки и рубашки"),
    (108, "Шорты женские"),
    (109, "Юбки"),
    (119, "Джинсы женские"),
    (130, "Футболки мужские"),
    (131, "Шорты мужские"),
    (120, "Костюмы женские"),
]

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

ADVICE = {
    "одиночество": ["Одиночество — это не приговор, а сигнал. Попробуй записаться на любое групповое занятие: спорт, курсы, волонтёрство.", "Часто одиночество — это страх быть отвергнутым. Напиши первым старому другу."],
    "тревога": ["Когда тревога накрывает — попробуй технику 4-7-8: вдох 4 секунды, задержка 7, выдох 8.", "Тревога часто живёт в будущем. Спроси себя: что я могу сделать прямо сейчас?"],
    "отношения": ["В отношениях главное — говорить о своих чувствах, а не обвинять.", "Иногда лучшее что можно сделать — дать человеку и себе немного пространства."],
    "работа": ["Если работа высасывает все силы — попробуй найти хотя бы один маленький смысл в том что делаешь.", "Выгорание — реальная вещь. Возьми один день только для себя."],
    "самооценка": ["Каждый вечер записывай 3 вещи, которые ты сделал хорошо за день.", "Сравнивай себя только с собой вчерашним."],
    "депрессия": ["Депрессия — это болезнь, а не слабость характера. Первый шаг — признать это.", "Ты не обязан справляться в одиночку. Обратись к психологу."],
    "стресс": ["Стресс накапливается когда мы не даём себе восстановиться. Найди свой способ разгрузки.", "Попробуй записать всё что тебя напрягает и разделить: могу повлиять / не могу."],
}

PETR_ID = 6232215696
PETR_MORNING = [
    "Доброе утро, лошара! 😂☀️ Вставай, хватит дрыхнуть!",
    "Эй, чмо, с добрым утром! 😄 Новый день — новые возможности облажаться!",
    "Просыпайся, лох! 😂 Леонид желает тебе хорошего дня!",
    "Утро, дружище-лошадь! 🌞 Сегодня ты можешь стать чуть менее лохом — дерзай!",
    "С добрым утром, чмошник! 😂 Это сообщение от любящего брата Леонида!",
]
PETR_EVENING = [
    "Добрый вечер, лох! 😄 Как прошёл день? Надеюсь, не так плохо как обычно!",
    "Вечер, чмо! 😂 Леонид проверяет — ты ещё жив?",
    "Эй, лошара, вечер добрый! 🌙 Отдыхай, завтра снова облажаешься!",
    "Добрый вечер, дружище! 😄 Помни: ты лох, но ты наш лох!",
    "Вечерний привет, чмошник! 😂 С тебя улыбка — это приказ Леонида!",
]


def get_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="☀️ Пожелание дня"), KeyboardButton(text="😍 Комплимент")],
            [KeyboardButton(text="😊 Поднять настроение"), KeyboardButton(text="🌙 Доброй ночи")],
            [KeyboardButton(text="🧠 Есть проблема")],
        ],
        resize_keyboard=True
    )

def get_keyboard_problem():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="◀️ Назад в меню")]],
        resize_keyboard=True
    )

def get_advice(text: str) -> str:
    text_lower = text.lower()
    for keyword, advices in ADVICE.items():
        if keyword in text_lower:
            return random.choice(advices)
    universal = [
        "Спасибо что поделился. Любая проблема решается — иногда нужно время, иногда нужен другой взгляд.\n\n💡 Что я могу сделать прямо сегодня, чтобы стало чуть лучше?",
        "Слышу тебя. Бывает тяжело — и это нормально.\n\n💡 Поговори об этом с кем-то близким вживую.",
        "То что ты об этом думаешь и ищешь выход — уже говорит о твоей силе.\n\n💡 Напиши на бумаге: что беспокоит, что пробовал, что ещё можно попробовать.",
    ]
    return random.choice(universal)


# === АНАЛИТИКА ===

async def get_top_items(session: aiohttp.ClientSession, category_id: int, category_name: str) -> list:
    date_to = datetime.now().strftime("%Y-%m-%d")
    date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    url = "https://mpstats.io/api/wb/get/subject/items"
    params = {"id": category_id, "d1": date_from, "d2": date_to}
    try:
        async with session.get(url, headers=MPSTATS_HEADERS, params=params, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            print(f"Категория {category_name} (id={category_id}): статус {resp.status}")
            if resp.status == 200:
                data = await resp.json()
                return data if isinstance(data, list) else data.get("data", [])
            else:
                text = await resp.text()
                print(f"Ответ: {text[:200]}")
            return []
    except Exception as e:
        print(f"Ошибка {category_name}: {e}")
        return []

def analyze_item(item: dict) -> dict | None:
    try:
        name = item.get("name", "")
        final_price = item.get("final_price", item.get("price", 0))
        revenue = item.get("revenue", 0)
        sales = item.get("sales", 0)
        balance = item.get("balance", 0)
        if final_price < 800 or sales < 10 or revenue < 50000 or balance < 5:
            return None
        markup = round(final_price / (final_price * 0.3), 1)
        if markup < 2.5:
            return None
        return {"name": name, "price": final_price, "revenue": revenue, "sales": sales, "balance": balance, "markup": markup}
    except Exception:
        return None

def ai_analyze(category: str, items: list) -> str:
    if not items:
        return f"В категории {category} подходящих товаров не найдено."
    items_text = "\n".join([
        f"- {i['name']}: цена {i['price']}₽, выручка {i['revenue']}₽, продаж {i['sales']}, остаток {i['balance']} шт"
        for i in items[:8]
    ])
    prompt = (
        f"Ты эксперт по торговле на Wildberries. Сейчас май, сезон весна-лето.\n"
        f"Проанализируй товары из категории '{category}':\n"
        f"1. Есть ли сезонный рост в мае?\n"
        f"2. Какие товары перспективны для входа прямо сейчас?\n"
        f"3. Есть ли монополия?\n"
        f"Короткий вывод 4-5 предложений на русском.\n\nТовары:\n{items_text}"
    )
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=350,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Ошибка ИИ: {e}"

async def run_analysis(message: Message):
    await message.answer("🔍 Запускаю анализ товаров для мая...\nЭто займёт 2-3 минуты, жди!")
    results = []
    async with aiohttp.ClientSession() as session:
        for category_id, category_name in MAY_CATEGORIES:
            await asyncio.sleep(3)
            items_raw = await get_top_items(session, category_id, category_name)
            if not items_raw:
                continue
            good_items = [analyze_item(i) for i in items_raw[:50]]
            good_items = [i for i in good_items if i]
            if not good_items:
                continue
            good_items.sort(key=lambda x: x["revenue"], reverse=True)
            ai_verdict = ai_analyze(category_name, good_items)
            results.append({"category": category_name, "items": good_items[:3], "ai_verdict": ai_verdict})
            await asyncio.sleep(2)

    if not results:
        await message.answer("❌ Подходящих товаров не найдено. Попробуй позже.")
        return

    await message.answer(f"✅ Анализ завершён! Найдено перспективных ниш: {len(results)}\n\nПодробности ниже 👇")

    for result in results:
        msg = f"📦 <b>{result['category']}</b>\n\n"
        msg += f"🤖 <b>Вывод ИИ:</b>\n{result['ai_verdict']}\n\n"
        msg += "🔥 <b>Топ товары:</b>\n"
        for item in result["items"]:
            msg += (
                f"\n• <b>{item['name'][:50]}</b>\n"
                f"  💰 {item['price']}₽ | Наценка: {item['markup']}x\n"
                f"  📈 Выручка: {item['revenue']:,}₽ | Продаж: {item['sales']}\n"
                f"  📦 Остаток: {item['balance']} шт\n"
            )
        await message.answer(msg, parse_mode="HTML")
        await asyncio.sleep(1)

    await message.answer("✅ Готово! Удачи в мае 💪")


# === ХЭНДЛЕРЫ ===

@dp.message(CommandStart())
async def cmd_start(message: Message):
    problem_mode_users.discard(message.from_user.id)
    name = message.from_user.first_name
    if message.from_user.id != ADMIN_ID:
        await bot.send_message(ADMIN_ID, f"👤 Новый пользователь!\nИмя: {name}\nUsername: @{message.from_user.username or 'нет'}\nID: {message.from_user.id}")
    await message.answer(
        f"Привет, {name}! 🎉\n\n"
        "Я бот хорошего настроения! 💫\n\n"
        "ℹ️ Изобретатель этого бота — Леонид.\n"
        "Он красавчик 😍, миллиардер 💰, плейбой 🕶, филантроп 🤝\n"
        "А ещё у него есть брат Петя... он лох 😂\n\n"
        "Выбирай кнопку или просто напиши мне что-нибудь 👇",
        reply_markup=get_keyboard()
    )

@dp.message(Command("analyze"))
async def cmd_analyze(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await run_analysis(message)

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

@dp.message(F.text == "🧠 Есть проблема")
async def problem_mode(message: Message):
    problem_mode_users.add(message.from_user.id)
    await message.answer("Я слушаю тебя 🤝\n\nРасскажи что происходит — напиши своими словами.", reply_markup=get_keyboard_problem())

@dp.message(F.text == "◀️ Назад в меню")
async def back_to_menu(message: Message):
    problem_mode_users.discard(message.from_user.id)
    await message.answer("Возвращаемся! 😊", reply_markup=get_keyboard())

@dp.message(F.text)
async def any_message(message: Message):
    if message.from_user.id in problem_mode_users:
        advice = get_advice(message.text)
        await message.answer(f"🧠 {advice}\n\nЕсли хочешь — расскажи подробнее, я слушаю.")
    else:
        all_messages = WISHES + COMPLIMENTS + MOODS
        await message.answer(random.choice(all_messages))


# === ПЛАНИРОВЩИК ===

async def scheduler():
    while True:
        now = datetime.utcnow()
        if now.hour == 4 and now.minute == 0:
            await bot.send_message(PETR_ID, random.choice(PETR_MORNING))
            await asyncio.sleep(61)
        elif now.hour == 16 and now.minute == 0:
            await bot.send_message(PETR_ID, random.choice(PETR_EVENING))
            await asyncio.sleep(61)
        else:
            await asyncio.sleep(30)


async def main():
    print("Бот запущен! 🚀")
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
