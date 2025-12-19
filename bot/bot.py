#!/usr/bin/env python3
"""
Telegram Weather Bot - простой запуск
"""

import asyncio
import logging
import sys
import os

# Критически важно: добавляем родительскую директорию в путь Python
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    # Пробуем импортировать модули
    from bot.config import BOT_TOKEN, LOG_FILE
    from bot.weather_api import WeatherAPI
    from aiogram import Bot, Dispatcher, types, F
    from aiogram.filters import Command
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    
    print("✅ Все модули импортированы успешно")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Установите зависимости: pip install aiogram==3.0.0 aiohttp==3.8.5")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
weather_api = WeatherAPI()

# Клавиатура
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌤 Погода сейчас")],
        [KeyboardButton(text="📅 Прогноз на 3 дня")],
        [KeyboardButton(text="ℹ️ Помощь")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("👋 Привет! Отправь мне название города.", reply_markup=keyboard)

@dp.message(Command("weather"))
async def cmd_weather(message: types.Message):
    args = message.text.split()
    if len(args) > 1:
        city = " ".join(args[1:])
        await get_weather(message, city)
    else:
        await message.answer("Пример: /weather Москва")

@dp.message(F.text == "🌤 Погода сейчас")
async def button_weather(message: types.Message):
    await message.answer("Отправьте название города:")

@dp.message()
async def handle_city(message: types.Message):
    text = message.text.strip()
    if text in ["🌤 Погода сейчас", "📅 Прогноз на 3 дня", "ℹ️ Помощь"]:
        return
    
    await get_weather(message, text)

async def get_weather(message: types.Message, city: str):
    await message.bot.send_chat_action(message.chat.id, "typing")
    result = await weather_api.get_current_weather(city)
    
    if result.get("success"):
        response = f"""{result['icon']} <b>Погода в {result['city']}, {result['country']}</b>
Температура: {result['temp']:.1f}°C
Ощущается как: {result['feels_like']:.1f}°C
Влажность: {result['humidity']}%
Ветер: {result['wind_speed']} м/с
{result['description'].capitalize()}"""
        await message.answer(response, reply_markup=keyboard, parse_mode="HTML")
    else:
        await message.answer(f"❌ Ошибка: {result.get('error')}", reply_markup=keyboard)

async def main():
    logger.info("🚀 Запуск бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
