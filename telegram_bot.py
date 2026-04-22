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

# Пути категорий MPstat (приоритет мужским)
MAY_CATEGORIES = [
    ("Мужчинам/Футболки и поло", "Футболки мужские"),
    ("Мужчинам/Шорты", "Шорты мужские"),
    ("Мужчинам/Рубашки", "Рубашки мужские"),
    ("Мужчинам/Джинсы", "Джинсы мужские"),
    ("Мужчинам/Брюки", "Брюки мужские"),
    ("Мужчинам/Спортивные костюмы", "Спортивные костюмы мужские"),
    ("Мужчинам/Толстовки и свитшоты", "Толстовки мужские"),
    ("Женщинам/Платья и сарафаны", "Платья"),
    ("Женщинам/Шорты", "Шорты женские"),
    ("Женщинам/Юбки", "Юбки"),
    ("Женщинам/Блузки и рубашки", "Блузки женские"),
    ("Женщинам/Джинсы", "Джинсы женские"),
    ("Женщинам/Костюмы", "Костюмы женские"),
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

async def get_top_items(session: aiohttp.ClientSession, category_path: str, category_name: str) -> list:
    date_to = datetime.now().strftime("%Y-%m-%d")
    date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    url = "https://mpstats.io/api/wb/get/category/items"
    params = {"path": category_path, "d1": date_from, "d2": date_to}
    try:
        async with session.get(url, headers=MPSTATS_HEADERS, params=params, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            print(f"Категория {category_name}: статус {resp.status}")
            text = await resp.text()
            print(f"Ответ (первые 500 символов): {text[:500]}")
            if resp.status == 200:
                import json
                data = json.loads(text)
                items = data if isinstance(data, list) else data.get("data", data.get("items", []))
                print(f"Найдено товаров: {len(items)}")
                if items:
                    print(f"Пример товара: {str(items[0])[:300]}")
                return items
            return []
    except Exception as e:
        print(f"Ошибка {category_name}: {e}")
        return []

def analyze_niche(category_name: str, data_points: list) -> dict | None:
    """Анализируем нишу по агрегированным данным категории"""
    try:
        if not data_points:
            return None

        # Суммируем данные по всем точкам (период в целом)
        total_revenue = sum(d.get("revenue", 0) for d in data_points)
        total_sales = sum(d.get("sales", 0) for d in data_points)

        # Берём последнюю точку для текущих показателей
        latest = data_points[-1]
        items = latest.get("items", 0)
        items_with_sells = latest.get("items_with_sells", 0)
        items_with_sells_pct = latest.get("items_with_sells_percent", 0)
        sellers = latest.get("sellers", 0)
        sellers_with_sells = latest.get("sellers_with_sells", 0)
        avg_price = latest.get("avg_price", 0)
        median_price = latest.get("median_price", 0)
        sales_per_item = latest.get("sales_per_items_with_sells_average", 0)
        revenue_per_item = latest.get("revenue_per_items_with_sells_average", 0)
        balance = latest.get("баланс", latest.get("balance", 0))

        # Минимальные фильтры (не строгие)
        if total_revenue < 10_000_000:
            return None
        if avg_price < 300:
            return None

        # Динамика роста (сравниваем первую и последнюю точки)
        if len(data_points) >= 2:
            first = data_points[0]
            first_sales = first.get("sales", 1)
            last_sales = latest.get("sales", 0)
            growth = round(((last_sales - first_sales) / max(first_sales, 1)) * 100, 1)
        else:
            growth = 0

        # Оценка наценки (закупка ~25-30% от цены продажи для одежды)
        estimated_purchase = avg_price * 0.28
        markup = round(avg_price / estimated_purchase, 1)

        # Концентрация рынка (монополия?)
        sellers_pct = round((sellers_with_sells / max(sellers, 1)) * 100, 1)

        return {
            "name": category_name,
            "revenue": total_revenue,
            "sales": total_sales,
            "items": items,
            "items_with_sells": items_with_sells,
            "items_with_sells_pct": items_with_sells_pct,
            "sellers": sellers,
            "sellers_with_sells": sellers_with_sells,
            "sellers_active_pct": sellers_pct,
            "avg_price": round(avg_price),
            "median_price": round(median_price),
            "sales_per_item": round(sales_per_item),
            "revenue_per_item": round(revenue_per_item),
            "balance": balance,
            "growth": growth,
            "markup": markup,
        }
    except Exception as e:
        print(f"Ошибка анализа ниши {category_name}: {e}")
        return None

def ai_analyze_niche(niche: dict) -> str:
    monopoly = "высокая концентрация" if niche['sellers_active_pct'] > 80 else "лидеры меняются"
    prompt = (
        f"Ты эксперт по торговле на Wildberries. Сейчас май, сезон весна-лето.\n"
        f"Оцени нишу '{niche['name']}' строго по критериям:\n\n"
        f"ДАННЫЕ НИШИ:\n"
        f"- Выручка за 30 дней: {niche['revenue']:,}₽\n"
        f"- Продаж: {niche['sales']:,} шт\n"
        f"- Всего товаров в нише: {niche['items']:,}\n"
        f"- Товаров с продажами: {niche['items_with_sells']:,} ({niche['items_with_sells_pct']}%)\n"
        f"- Продавцов всего: {niche['sellers']}, активных: {niche['sellers_with_sells']} ({niche['sellers_active_pct']}%)\n"
        f"- Средняя цена: {niche['avg_price']}₽, медианная: {niche['median_price']}₽\n"
        f"- Продаж на товар (среди продающих): {niche['sales_per_item']}\n"
        f"- Выручка на товар: {niche['revenue_per_item']:,}₽\n"
        f"- Рост за период: {niche['growth']}%\n"
        f"- Концентрация: {monopoly}\n\n"
        f"ОТВЕТЬ:\n"
        f"1. Много ли денег в нише и стоит ли заходить в мае?\n"
        f"2. Монополия есть или лидеры меняются?\n"
        f"3. Слабая ли конкуренция по качеству?\n"
        f"4. Какая стратегия входа?\n"
        f"5. Оценка ниши: 🔥 Топ / ✅ Хорошая / ⚠️ Средняя / ❌ Плохая\n\n"
        f"Ответ строго на русском, 5-6 предложений."
    )
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Ошибка ИИ: {e}"

async def run_analysis(message: Message):
    await message.answer("🔍 Запускаю анализ товаров для мая...\nЭто займёт 2-3 минуты, жди!")
    results = []
    async with aiohttp.ClientSession() as session:
        for category_path, category_name in MAY_CATEGORIES:
            await asyncio.sleep(3)
            data_points = await get_top_items(session, category_path, category_name)
            if not data_points:
                continue
            niche = analyze_niche(category_name, data_points)
            if not niche:
                print(f"Ниша {category_name} не прошла фильтры")
                continue
            ai_verdict = ai_analyze_niche(niche)
            results.append({"niche": niche, "ai_verdict": ai_verdict})
            await asyncio.sleep(2)

    if not results:
        await message.answer("❌ Подходящих товаров не найдено. Попробуй позже.")
        return

    await message.answer(f"✅ Анализ завершён! Найдено перспективных ниш: {len(results)}\n\nПодробности ниже 👇")

    for i, result in enumerate(results, 1):
        n = result["niche"]
        msg = (
            f"{'—'*30}\n"
            f"<b>#{i} {n['name']}</b>\n\n"
            f"💰 <b>Деньги в нише:</b>\n"
            f"   Выручка за 30 дней: <b>{n['revenue']:,}₽</b>\n"
            f"   Продаж: {n['sales']:,} шт\n"
            f"   Выручка на товар: {n['revenue_per_item']:,}₽\n\n"
            f"📊 <b>Движение товаров:</b>\n"
            f"   Всего товаров: {n['items']:,}\n"
            f"   С продажами: {n['items_with_sells']:,} ({n['items_with_sells_pct']}%)\n"
            f"   Продаж на товар: {n['sales_per_item']}\n\n"
            f"🏪 <b>Конкуренция:</b>\n"
            f"   Продавцов всего: {n['sellers']}\n"
            f"   Активных: {n['sellers_with_sells']} ({n['sellers_active_pct']}%)\n\n"
            f"💵 <b>Цена и наценка:</b>\n"
            f"   Средняя цена: {n['avg_price']}₽\n"
            f"   Медианная цена: {n['median_price']}₽\n"
            f"   Наценка (оценка): ~{n['markup']}x\n\n"
            f"📈 <b>Динамика:</b> рост {n['growth']}%\n\n"
            f"🤖 <b>Вывод ИИ:</b>\n{result['ai_verdict']}"
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
