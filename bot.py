"""
Beruniy ilmi maktabi — @ustoztarix1_bot
Majburiy obuna: /start bosilganda @yoldashaliisakov kanaliga obuna tekshiriladi.
Obuna bo'lganlarga test ilovasi (Web App) tugmasi ochiladi.
"""
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonCommands,
    MenuButtonWebApp,
    Message,
    WebAppInfo,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL", "@yoldashaliisakov")
APP_URL = os.getenv("APP_URL", "https://yoldashaliisaqov8-alt.github.io/tarix-test/")

logging.basicConfig(level=logging.INFO)
bot = Bot(BOT_TOKEN)
dp = Dispatcher()


async def is_subscribed(user_id: int) -> bool:
    """Foydalanuvchi kanalga a'zomi — tekshiradi (bot kanalda admin bo'lishi shart)."""
    try:
        member = await bot.get_chat_member(CHANNEL, user_id)
        return member.status in ("member", "administrator", "creator", "restricted")
    except Exception as e:
        logging.warning("Obunani tekshirib bo'lmadi: %s", e)
        return False


def subscribe_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Kanalga obuna bo'lish",
                              url=f"https://t.me/{CHANNEL.lstrip('@')}")],
        [InlineKeyboardButton(text="✅ Obuna bo'ldim — tekshirish",
                              callback_data="check_sub")],
    ])


def app_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Testni boshlash",
                              web_app=WebAppInfo(url=APP_URL))],
    ])


async def open_app(chat_id: int, name: str):
    """Obuna tasdiqlangach: shu foydalanuvchi uchun Menu tugmasini ochadi va xabar yuboradi."""
    await bot.set_chat_menu_button(
        chat_id=chat_id,
        menu_button=MenuButtonWebApp(text="📚 Testlar", web_app=WebAppInfo(url=APP_URL)),
    )
    await bot.send_message(
        chat_id,
        f"Assalomu alaykum, {name}! 👋\n\n"
        "🏛 <b>Beruniy ilmi maktabi</b>ga xush kelibsiz.\n"
        "6–10-sinf Jahon tarixi va O'zbekiston tarixi testlari sizni kutmoqda.\n\n"
        "Boshlash uchun pastdagi tugmani bosing 👇",
        reply_markup=app_kb(),
        parse_mode="HTML",
    )


@dp.message(CommandStart())
async def start(message: Message):
    user = message.from_user
    if await is_subscribed(user.id):
        await open_app(message.chat.id, user.first_name)
    else:
        # Obuna bo'lmaganlarda Menu tugmasi ham yopiq turadi
        await bot.set_chat_menu_button(chat_id=message.chat.id, menu_button=MenuButtonCommands())
        await message.answer(
            f"Assalomu alaykum, {user.first_name}! 👋\n\n"
            f"Botdan foydalanish uchun avval {CHANNEL} kanalimizga obuna bo'ling.\n"
            "Obuna bo'lgach, «✅ Obuna bo'ldim — tekshirish» tugmasini bosing.",
            reply_markup=subscribe_kb(),
        )


@dp.callback_query(F.data == "check_sub")
async def check_sub(call: CallbackQuery):
    if await is_subscribed(call.from_user.id):
        await call.answer("Rahmat! Obuna tasdiqlandi ✅")
        await call.message.delete()
        await open_app(call.message.chat.id, call.from_user.first_name)
    else:
        await call.answer("❌ Siz hali kanalga obuna bo'lmagansiz!", show_alert=True)


async def main():
    # BotFather'dagi umumiy Web App menyusini o'chiradi — ilova faqat obunachilarga ochiladi
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
