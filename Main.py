# RAYUGA_V4.py - Updated with Photo Changer Logic for Railway
import asyncio
import json
import os
import sys
import random
from datetime import datetime, timezone, timedelta
from telegram import Update, ChatMemberUpdated, ChatMember
from telegram.error import RetryAfter, TelegramError
from telegram.ext import Application, CommandHandler, ContextTypes, ChatMemberHandler
import logging

# ---------------------------
# BOT TOKENS (Total: 15 Bots)
# ---------------------------
TOKENS = [
    "8740459646:AAFcREbuESNeOPzKpqjPHwh6_c7qGx9YqZA",
    "8962784249:AAE2ETLssO9-xaK_tJE9GeigRc1HBJTUvRY",
    "8886121179:AAEDwemt817iGaOWj3Es-tM_522tc1NO1CY",
    "8908241132:AAH8Og0G9hrfFdrejT3DYrYOFekfeM0rXno",
    "8720442284:AAH6nPFouNSQ072FqnQ8l-Q1lmJpakf5d7E",
    "8824627261:AAFBsT4UhqF-qIjczxXGe9MDZ1ZE2D1yamY",
    "8281717629:AAHCReokj1KKp4x9kRHDdOGJjsJMjrDjqIo",
    "8914243255:AAHA4Wykd1DCjvO3ApX7Ujzm1axOGNIwMXs",
    "8882291229:AAGMhumA39ldCDj5JQHtCN6TRWq5ZT-qpcU",
    "8627173096:AAFu7TdF0dQUepWLQ9s2kdMkUajeEYn8Hg0",
    "8907464798:AAE3_9DLSAzlEFvElhHAN8C_ZJ8Iz66JOio",
    "8933273450:AAHA9Ckplp3zMgZOO_9wu8obWwRrb8qSgQY",
    "8896368359:AAGUp6GxfZt-j1iE7Lf-kpH1X1VPW-6gS10",
    "8945796268:AAEpeyW-M_-TxaxUimPLQbewhupNbxZOol8",
    "8819644187:AAFx-TfdExfmZgYhgufxur-tucVnI75t774"
]

# ---------------------------
# OWNER CONFIG & STORAGE
# ---------------------------
OWNER_ID = 8680250815
SUDO_FILE = "sudo_users.json"
SAVED_PHOTO_PATH = "rayuga_target_pfp.jpg"

# Load sudo users
if os.path.exists(SUDO_FILE):
    with open(SUDO_FILE) as f:
        SUDO_USERS = set(json.load(f))
else:
    SUDO_USERS = {OWNER_ID}

def save_sudo():
    with open(SUDO_FILE, "w") as f:
        json.dump(list(SUDO_USERS), f)

# ---------------------------
# GLOBAL STATE
# ---------------------------
apps = []
bots = []
bots_info = []
nc_tasks = {}
spam_tasks = {}
slider_tasks = {}
pfp_tasks = {} # For Tracking GC Photo Changer Loops
GLOBAL_DELAY = 0.05

STOP_MESSAGE = "𝑂𝐾𝐼 𝑌𝐿𝐿 ¡! 🐣"
ADMIN_MESSAGE = "⚡ 𝐑𝐀𝐘𝐔𝐆𝐀 𝐀𝐃𝐌𝐈𝐍 𝐇𝐄𝐑𝐄 ~ 🪽"
BYE_MESSAGE = "𝐆𝐀𝐌𝐄 𝐎𝐕𝐄𝐑 𝐁𝐘 𝐑𝐀𝐘𝐔𝐆𝐀 !! 📌"
GREETING_MESSAGE = "🌌 𝐑𝐀𝐘𝐔𝐆𝐀 𝐄𝐍𝐓𝐄𝐑𝐄𝐃 🫣"

logging.basicConfig(level=logging.INFO)

# ---------------------------
# PERMISSION HELPERS
# ---------------------------
def is_owner_or_sudo(uid):
    return uid == OWNER_ID or uid in SUDO_USERS

def owner_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id == OWNER_ID:
            return await func(update, context)
        await update.message.reply_text("❌ Only owner can use this command!")
    return wrapper

def sudo_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if is_owner_or_sudo(update.effective_user.id):
            return await func(update, context)
        await update.message.reply_text("𝐆𝐔𝐋𝐀𝐌𝐈 𝐊𝐑 𝐏𝐇𝐋𝐄 𝐅𝐈𝐑 𝐒𝐔𝐃𝐎 𝐌𝐈𝐋𝐄𝐆𝐀 😂")
    return wrapper

# ---------------------------
# EMOJI & TEXT LISTS
# ---------------------------
DARK_EMOJIS = ["🕳️", "🌑", "👣", "🗝️", "🧬", "🔌", "⬛", "🦾", "📜", "🕯️", "🍷", "🥀", "🖤", "🕸️", "🗡️", "🎱", "🐦‍⬛", "🔮", "🌑", "🪄", "🌝", "🌚", "🌜", "🌛", "🌙", "⭐", "🌟", "✨", "🪐", "🌍", "🌠", "🌌", "☄️", "🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
HAND_EMOJIS = ["👀", "👁️", "👄", "🫦", "👅", "👃🏻", "👂🏻", "🦻🏻", "🦶🏻", "🦵🏻", "🦿", "🦾", "💪🏻", "👏🏻", "👍🏻", "👎🏻", "🫶🏻", "🙌🏻", "👐🏻", "🤲🏻", "🤜🏻", "🤛🏻", "✊🏻", "👊🏻", "🫳🏻", "🫴🏻", "🫱🏻", "🫲🏻", "🫸🏻", "🫷🏻", "👋🏻", "🤚🏻", "🖐🏻", "✋🏻", "🖖🏻", "🤟🏻", "🤘🏻", "✌🏻", "🤞🏻", "🫰🏻", "🤙🏻", "🤌🏻", "🤏🏻", "👌🏻", "🫵🏻", "👉🏻", "👈🏻", "☝🏻", "👆🏻", "👇🏻", "🖕🏻", "✍🏻", "🤳🏻", "🙏🏻", "💅🏻", "🤝🏼", "🌘"]
MARVEL_EMOJIS = ["🛡️", "🇺🇸", "🎖️", "🦾", "🚀", "⚡", "🤖", "⚡", "🔨", "🌩️", "🔱", "🕷️", "🕶️", "🔫", "🥀", "🏹", "🎯", "🦅", "🧪", "☢️", "👊", "🟢", "💎", "🤖", "🟡"]
MAGIC_EMOJIS = ["🧪", "⚗️", "📜", "💎", "🕳️", "🌑", "🧿", "🐦‍⬛", "🌀", "⚡", "🪄", "🧿", "🕯️", "📜", "🏛️", "🖤", "✥", "♱", "⚖︎", "∞", "𖦹"]
NATURE_EMOJIS = ["💐", "🌹", "🥀", "🌺", "🌷", "🪷", "🌸", "💮", "🏵️", "🪻", "🌻", "🌼", "🍂", "🍁", "🍄", "🌾", "🌿", "🌱", "🍃", "☘️", "🍀", "🪴", "🌵", "🌴", "🪾", "🌳", "🌲", "🪵", "🪹", "🪺"]
FOOD_EMOJIS = ["🍧", "🧋", "🧃", "🥛", "🍿", "🧊", "🍵", "☕", "🍻", "🍺", "🧉", "🫖", "🍾", "🍷", "🥃", "🫗", "🍸", "🍹", "🍶", "🥢", "🥂", "🍟", "🧁", "🍭", "🍬", "🍫", "🍨", "🍡", "🍙", "🍥", "🥠", "🥟", "🍛", "🍤", "🍜", "🦪", "🍚", "🥣", "🥫", "🌯"]
FACE_EMOJIS = ["☺️", "😌", "🙂‍↕️", "🙂‍↔️", "😏", "🤤", "😋", "😛", "😝", "😜", "🤪", "😔", "🥺", "😬", "😑", "😐", "😶", "😶‍🌫️", "🫥", "🤐", "🫡", "🤔", "🤫", "🫢", "🤭", "🥱", "🤗", "🫣", "😱", "🤨", "🧐", "😒", "🙄", "😮‍💨", "😤", "😠", "😡", "🤬", "😞", "😓", "😟", "😥", "😢", "☹️", "🙁", "🫤", "😕", "😰", "😨", "😧", "😦", "😮", "😯", "😲", "🤯", "🫨", "😵‍💫", "😵", "😫", "🥴", "🥶", "🥵"]
HOBBY_EMOJIS = ["🃏", "🪄", "🎩", "📷", "🀄", "🎴", "🎰", "📸", "🖼️", "🎨", "🫟", "🖌️", "🖍️", "🪡", "🧵", "🧶", "🎹", "🎷", "🎺", "🎸", "🪕", "🎻", "🪉", "🪘", "🥁", "🪇", "🪈", "🪗", "🎤", "🎧", "🎚️", "🎛️", "🎙️", "📼", "📻", "📺", "📹", "📽️", "🎥", "🎞️", "🎬", "🎭", "🎫", "🎟️"]
TECH_EMOJIS = ["🔋", "🪫", "🖲️", "💽", "💾", "💿", "📀", "🖥️", "💻", "⌨️", "🖨️", "🖱️", "🪙", "💎", "💸", "💵", "💴", "🇪🇺", "💷", "💳", "💰", "🧾", "🧮", "⚖️", "🛒", "🛍️", "💡", "🕯️", "🔦", "🏮", "🧱", "🪟", "🪞", "🚪", "🚿", "🛁", "🚽", "🧻", "🪠", "🧸", "🪆", "🧷", "🪢", "🧹", "齊", "🧽", "🧼", "🪥", "🪒", "🪮", "🧺", "🧦", "🧤", "🧣", "👖"]
ANIMAL_EMOJIS = ["🪼", "🐚", "🦋", "🐞", "🐝", "🐛", "🪱", "🦠", "🐾", "🫧", "🪸", "🦪", "🪼", "🐙", "🦑", "🐡", "🐠", "🐟", "🐳", "🐋", "🐬", "🦈", "🦭", "🐧", "🦃", "🐦‍🔥", "🦚", "🦩", "🪿", "🦆", "🦢", "🦤", "🕊️", "🦜", "🦉", "🦅", "🐥", "🐤", "🐣", "🐓", "🐦", "🪶", "🪽", "🦇", "🦦", "🦔", "🦡", "🦨", "🐅", "🐆", "🦒", "🦏", "🦣", "Elephant", "🦓", "🦘", "🦥", "🦬", "🐃", "🐏", "🐂", "🐄", "🐎", "🐈", "🐩"]

TYPENC_WORDS = [
    "𝗧𝗔𝗧𝗧𝗘", "𝗚𝗨🇱𝗔🇲", "𝗠𝗔𝗗𝗔𝗥𝗖𝗛𝗢𝗗", "𝗕𝗛𝗘🇳𝗞🇱🇳🇩", "𝗧𝗠𝗞🇨", "𝗧𝗠𝗞做",
    "🇷🇳🇩🇾", "🇬🇦🇷🇪🇪🇧", "🇲🇮🇸🇹🇮 🇰🇪 🇱🇦🇩🇰🇪", "🇬🇳🇩🇺", "🇨🇭🇦🇵🇷🇮", "🇨🇭🇲🇷",
    "🇧🇸🇩🇰", "🇰🇪🇪🇩🇪", "🇨🇭🇺🇩", "🇹🇧🇰🇱", "🇭🇦🇷🇦🇲🇰🇭🇴🇷", "🇷🇷 🇲🇹 🇰🇷",
    "🇹🇪🇷🇮 🇲🇦🇦 🇲🇦🇷 🇬🇾🇮", "🇹🇪🇷🇮 🇧🇭🇪🇳 🇨🇭🇺🇩🇬🇾🇮", "🇬🇺🇱🇦🇲🇮 🇰🇷"
]

ALEXA_TEXTS = [
    "𝗔package𝗟🇪𝗫𝗔 🇮🇸🇸 🇲🇨 🇰🇮 🇲🇦🇦 🇰🇪 🇳🇴🇹🇪🇸 🇩🇮🇰🇭🇦🇴 🙁",
    "𝗔𝗟🇪𝗫𝗔 🇮🇸🇸 🇷🇳🇩🇾 🇰🇦 🇲🇺🇭 🇧🇳🇩 🇰🇷🇩🇴 😆",
    "𝗔停🇪𝗫𝗔 🇮🇸🇰🇮 🇧🇭🇪🇳 🇨🇭🇴🇩 🇩🇴 🌙",
    "𝗔package𝗟🇪𝗫𝗔 🇮🇸🇰🇪 🇧🇦‌🇦🇵 🇰🇮 🇬🇳🇩 🇲🇮🇪 🇱🇦🇹🇭 🇩🇦🇦🇱 🇩🇴 😆",
    "𝗔𝗟🇪𝗫𝗔 🇮🇸🇰🇦 🇬🇦🇲🇪 🇴🇻🇪🇷 🇰🇦 🇻🇮🇩🇪🇴 🇩🇴🇳🇪 🇰🇷🇴 🥹"
]

ANIMAL_TEXTS = [
    "𝗢𝗬🇪 𝗧🇲🇰🇨 🇲🇮🇪 🇬🇴🇷🇮🇱🇱🇦  🦍",
    "𝗢𝗬🇪 𝗧🇪🇷🇮 🇧🇭🇪🇳 🇰🇮 🇨🇭🇺🇹 🇲🇮🇪 🇬🇭🇴🇩🇦 🐎",
    "𝗢𝗬🇪 𝗧🇪🇷🇪 🇧🇦🇦🇵 🇰🇮 🇬🇳🇩 🇲🇮🇪 🇰🇦🇳🇬🇦🇷🇴🇴 🦘",
    "𝗢𝗬🇪 𝗧🇪🇷🇮 🇬🇳🇩 🇲🇮🇪 🇨🇦🇲🇪🇱 🐪",
    "𝗢𝗬🇪 𝗧🇺 🇯🇦🇳🇼🇦🇷🇴 🇸🇪 🇨🇭🇺🇩 🇬🇾🇦 ? 😆😆😆"
]

SWIPE_TEXTS = [
    "𝗧🇪🇷🇮 🇲🇰🇨 🇸🇦🇸🇹🇮 🇭🇦🇮 🇧🇦🇦🇹 🇰🇭🇹🇲 😡",
    "🇨🇭🇱 🇬🇺🇱🇦🇲🇮 🇰🇷 𝗧🇦𝗧𝗧🇪 😆",
    "🇨🇭🇮🇩🇮🇾🇦 🇨🇭🇦🇩🇮 🇵🇭🇦🇦🇩 🇵🇪 🇺🇸🇳🇪 🇩🇮🇾🇦 🇲🇺🇹 𝗧🇲🇰🇨 😆",
    "🇪𝗞 🇱🇦🇦‌🇹 🇲🇮🇪 🇱🇳🇩 🇨🇭🇦🇹🇹🇦 🇫🇮🇷🇪🇬🇦 🇧🇸🇩🇰 😆"
]

TEXTS_PATTERN = "{text}  𝑶𝒀𝑬 𝑩𝑲𝑳 𝑻𝑬𝑹𝑰 𝑴𝑨𝑨 𝑲𝑨 𝑲𝑯𝑨𝑺𝑨𝑴 𝑯𝑼 𝑨𝑼𝑲𝑨𝑻 𝑴𝑰𝑬 𝑹𝑯 𝑹𝑵加快 𝑷𝑼𝑻𝑹𝑨 ☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲\\~   "
TEXTS_REPEAT = 10
SHAYARI_PATTERN = "𝙏𝙄𝙆 𝙏𝙄𝙆 𝘾𝙃𝙇𝙏𝘼 𝙂𝙃𝙊𝘿𝘼 {text} 𝙆𝙄 🇧🇭🇪🇳 𝙆𝘼 𝙇𝙊𝘿𝘼 ╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍☲☲☲☲☲☲☲☲☲☲☲☲☲ "
SHAYARI_REPEAT = 10
SONGY_PATTERN = "{text} 𝗗𝗮𝗹𝗹𝗲!\n𝗕𝗲𝘁𝗮 𝗗𝗮𝗹𝗹𝗲 𝗕𝗲𝗻𝗶 𝗕𝗮𝗮𝗽 𝗧𝗲𝗿α 🇳𝗮𝗹𝗹α 𝗛𝗮𝗶\n𝗟*δα 𝗛𝗸α𝗵 𝗠𝗲𝗿α, 𝗠α𝗺𝘁α 𝗠𝗲𝗿𝗶 🇨𝗵𝗮𝗹𝗹α 𝗛α𝗶..."
CUSTOM_PATTERN = "{text}  ⩇⩇:⩇⩇ {kaomoji}"
CUSTOM_KAOMOJI = ["(◕‿◕)", "(✿◠‿GAIN)", "(◔‿◔)", "(◡‿◡✿)", "(◕‿◕✿)", "(ᵔ◡ᵔ)", "(◠‿◠✿)", "(◕ᴗ◕✿)", "(◡‿◡)", "(◠‿◠)", "(◕‿◕)", "(◡ω◡)", "(◕ω◕)", "(◠ω◠)", "(ᵔᴗᵔ)", "(◕ᴗ◕)", "(◡ᴗ◡)", "(◠ᴗ◠)", "(｡◕‿◕｡)", "♥‿♥", "😊", "😄", "😁"]

# ---------------------------
# NC LOOP FUNCTIONS
# ---------------------------
async def ncdark_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = DARK_EMOJIS[i % len(DARK_EMOJIS)]
            new_title = f"{text} ＴＭＫＣ ＲＮＤＹＫＥ⪩ {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def tmkcnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = HAND_EMOJIS[i % len(HAND_EMOJIS)]
            new_title = f"{text} ⭞ ᴛᴍᴋᴄ ￫ {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def evonc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = HAND_EMOJIS[i % len(HAND_EMOJIS)]
            new_title = f"{text} 𝙗𝙪𝙡𝙖𝙢{emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def marvelnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = MARVEL_EMOJIS[i % len(MARVEL_EMOJIS)]
            new_title = f"{text} 𝙏𝘽𝙆🇨 ᯓ {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def magicnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = MAGIC_EMOJIS[i % len(MAGIC_EMOJIS)]
            new_title = f"{text} 𝙍𝙉𝘿🇾 𝘽𝘼𝙇𝘼𝙆⁀➴ {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def sportnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = MARVEL_EMOJIS[i % len(MARVEL_EMOJIS)]
            new_title = f"{text} 𝙏🇪🇷🇮 𝙂🇳🇩 𝙈🇮🇪 ≯ {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def lndnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = NATURE_EMOJIS[i % len(NATURE_EMOJIS)]
            new_title = f"{text} 𝘾𝙃𝙐🇩 {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def ncspeed_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = FOOD_EMOJIS[i % len(FOOD_EMOJIS)]
            new_title = f"{text} 𝙏🇪🇷🇮 𝙈🇦🇦 🇨🇭🇺🇩🇦𝙆🇦𝘿 ≫ {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def emognc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = FACE_EMOJIS[i % len(FACE_EMOJIS)]
            new_title = f"{text} 𝙆🇪🇪🇩🇪 𝘼🇺𝙆🇦🇹 𝘽🇳🇦⁀➴ {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def yournc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = HOBBY_EMOJIS[i % len(HOBBY_EMOJIS)]
            new_title = f"{text} 𓆩 {emoji} 𓆪"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def customnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = FACE_EMOJIS[i % len(FACE_EMOJIS)]
            new_title = f"{text} જ⁀➴ {emoji} "
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def typenc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            word = TYPENC_WORDS[i % len(TYPENC_WORDS)]
            new_title = f"{text} {word} "
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def flashnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = TECH_EMOJIS[i % len(TECH_EMOJIS)]
            new_title = f"{text} ═══ {emoji} ═══"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def foxync_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = ANIMAL_EMOJIS[i % len(ANIMAL_EMOJIS)]
            new_title = f"{text} 👑𝗖🇭🇺🇩 𝗞🇷 𝗗🇦𝗙🇦🇳~{emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)


# ---------------------------
# NEW: GC PHOTO CHANGER LOOP
# ---------------------------
async def gc_photo_changer_loop(bot, chat_id):
    """Multi-bot powered fast profile photo changer loop"""
    bot_index = 0
    while True:
        try:
            if not os.path.exists(SAVED_PHOTO_PATH):
                break
                
            # Pick next available bot to bypass individual rate limits
            current_bot = bots[bot_index % len(bots)]
            bot_index += 1
            
            with open(SAVED_PHOTO_PATH, "rb") as photo_file:
                await current_bot.set_chat_photo(chat_id=chat_id, photo=photo_file)
                
            # Configurable global safety delay to prevent crash
            await asyncio.sleep(GLOBAL_DELAY)
            
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            await asyncio.sleep(0.5)

# ---------------------------
# SPAM & SLIDER LOOP FUNCTIONS
# ---------------------------
async def texts_spam_loop(bot, chat_id, text):
    message = (TEXTS_PATTERN.format(text=text) + "\n") * TEXTS_REPEAT
    while True:
        try:
            await bot.send_message(chat_id, message)
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def shayari_spam_loop(bot, chat_id, text):
    message = (SHAYARI_PATTERN.format(text=text) + "\n") * SHAYARI_REPEAT
    while True:
        try:
            await bot.send_message(chat_id, message)
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def songy_spam_loop(bot, chat_id, text):
    message = SONGY_PATTERN.format(text=text)
    while True:
        try:
            await bot.send_message(chat_id, message)
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def custom_spam_loop(bot, chat_id, text):
    while True:
        try:
            kaomoji = random.choice(CUSTOM_KAOMOJI)
            message = CUSTOM_PATTERN.format(text=text, kaomoji=kaomoji)
            await bot.send_message(chat_id, message)
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def make_slider_loop(texts, bot, chat_id, target_msg_id):
    i = 0
    while True:
        try:
            await bot.send_message(chat_id=chat_id, text=texts[i % len(texts)], reply_to_message_id=target_msg_id)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

# ---------------------------
# AUTO HANDLER
# ---------------------------
async def handle_my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result: ChatMemberUpdated = update.my_chat_member
    if result.chat.type not in ["group", "supergroup"]: return
    old = result.old_chat_member
    new = result.new_chat_member
    if old.status in [ChatMember.LEFT, ChatMember.BANNED] and new.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR]:
        await context.bot.send_message(chat_id=result.chat.id, text=GREETING_MESSAGE)
    elif old.status == ChatMember.MEMBER and new.status == ChatMember.ADMINISTRATOR:
        await context.bot.send_message(chat_id=result.chat.id, text=ADMIN_MESSAGE)

# ---------------------------
# COMMAND HANDLERS - NC
# ---------------------------
@sudo_only
async def ncdark(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /ncdark <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]: task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(ncdark_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ ncdark started for: {text}")

@sudo_only
async def tmkcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /tmkcnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]: task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(tmkcnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ tmkcnc started for: {text}")

@sudo_only
async def evonc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /evonc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]: task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(evonc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ evonc started for: {text}")

@sudo_only
async def marvelnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /marvelnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]: task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(marvelnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ marvelnc started for: {text}")

@sudo_only
async def magicnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /magicnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]: task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(magicnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ magicnc started for: {text}")

@sudo_only
async def sportnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /sportnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]: task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(sportnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ sportnc started for: {text}")

@sudo_only
async def lndnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /lndnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]: task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(lndnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ lndnc started for: {text}")

@sudo_only
async def ncspeed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /ncspeed <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]: task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(ncspeed_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ ncspeed started for: {text}")

@sudo_only
async def emognc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /emognc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]: task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(emognc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ emognc started for: {text}")

@sudo_only
async def yournc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /yournc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]: task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(yournc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ yournc started for: {text}")

@sudo_only
async def customnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /customnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]: task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(customnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ customnc started for: {text}")

@sudo_only
async def typenc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /typenc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]: task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(typenc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ typenc started for: {text}")

@sudo_only
async def flashnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /flashnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]: task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(flashnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ flashnc started for: {text}")

@sudo_only
async def foxync(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /foxync <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]: task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(foxync_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ foxync started for: {text}")

# ---------------------------
# NEW: GC PHOTO CONTROLLERS
# ---------------------------
@sudo_only
async def photosave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Saves replied image on local Railway disk"""
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        return await update.message.reply_text("❌ Kisi Image par reply karke `/photosave` use karo!")
    
    status_msg = await update.message.reply_text("📥 Photo download ho rhi hai, rukiy...")
    try:
        photo_file = await update.message.reply_to_message.photo[-1].get_file()
        await photo_file.download_to_drive(SAVED_PHOTO_PATH)
        await status_msg.edit_text("✅ Target PFP successfully save ho gayi! Ab group me `/setgc` type karo loop start karne ke liye.")
    except Exception as e:
        await status_msg.edit_text(f"❌ Error while downloading: {e}")

@sudo_only
async def setgc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts continuous PFP changing loop"""
    chat_id = update.message.chat_id
    if not os.path.exists(SAVED_PHOTO_PATH):
        return await update.message.reply_text("❌ Pehle `/photosave` se target photo store karo!")
        
    if chat_id in pfp_tasks:
        pfp_tasks[chat_id].cancel()
        del pfp_tasks[chat_id]
        
    # Launching async loop background task
    task = asyncio.create_task(gc_photo_changer_loop(context.bot, chat_id))
    pfp_tasks[chat_id] = task
    await update.message.reply_text("⚙️ **RAYUGA Fast GC Photo Changer Active!**\nLoop dynamic multi-bot power ke saath back-to-back fast run ho rha hai.")

@sudo_only
async def stopgc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stops PFP changer loop"""
    chat_id = update.message.chat_id
    if chat_id in pfp_tasks:
        pfp_tasks[chat_id].cancel()
        del pfp_tasks[chat_id]
        await update.message.reply_text(STOP_MESSAGE)
    else:
        await update.message.reply_text("❌ No GC Photo Changer loop running here.")

# ---------------------------
# SPAM & SLIDER HANDLERS
# ---------------------------
@sudo_only
async def texts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /texts <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]: task.cancel()
        del spam_tasks[chat_id]
    tasks = [asyncio.create_task(texts_spam_loop(b, chat_id, text)) for b in bots]
    spam_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ texts spam started for: {text}")

@sudo_only
async def shayari(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /shayari <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]: task.cancel()
        del spam_tasks[chat_id]
    tasks = [asyncio.create_task(shayari_spam_loop(b, chat_id, text)) for b in bots]
    spam_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ shayari spam started for: {text}")

@sudo_only
async def songy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /songy <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]: task.cancel()
        del spam_tasks[chat_id]
    tasks = [asyncio.create_task(songy_spam_loop(b, chat_id, text)) for b in bots]
    spam_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ songy spam started for: {text}")

@sudo_only
async def custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("❌ Usage: /custom <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]: task.cancel()
        del spam_tasks[chat_id]
    tasks = [asyncio.create_task(custom_spam_loop(b, chat_id, text)) for b in bots]
    spam_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ custom spam started for: {text}")

@sudo_only
async def alexa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return await update.message.reply_text("❌ Reply to a message to start alexa!")
    chat_id = update.message.chat_id
    target_msg_id = update.message.reply_to_message.message_id
    if chat_id in slider_tasks:
        for task in slider_tasks[chat_id]: task.cancel()
        del slider_tasks[chat_id]
    tasks = [asyncio.create_task(make_slider_loop(ALEXA_TEXTS, b, chat_id, target_msg_id)) for b in bots]
    slider_tasks[chat_id] = tasks
    await update.message.reply_text("✅ Alexa started on that message.")

@sudo_only
async def animal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return await update.message.reply_text("❌ Reply to a message to start animal!")
    chat_id = update.message.chat_id
    target_msg_id = update.message.reply_to_message.message_id
    if chat_id in slider_tasks:
        for task in slider_tasks[chat_id]: task.cancel()
        del slider_tasks[chat_id]
    tasks = [asyncio.create_task(make_slider_loop(ANIMAL_TEXTS, b, chat_id, target_msg_id)) for b in bots]
    slider_tasks[chat_id] = tasks
    await update.message.reply_text("✅ Animal started on that message.")

@sudo_only
async def swipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return await update.message.reply_text("❌ Reply to a message to start swipe!")
    chat_id = update.message.chat_id
    target_msg_id = update.message.reply_to_message.message_id
    if chat_id in slider_tasks:
        for task in slider_tasks[chat_id]: task.cancel()
        del slider_tasks[chat_id]
    tasks = [asyncio.create_task(make_slider_loop(SWIPE_TEXTS, b, chat_id, target_msg_id)) for b in bots]
    slider_tasks[chat_id] = tasks
    await update.message.reply_text("✅ Swipe started on that message.")

# ---------------------------
# COMMAND HANDLERS - CONTROL
# ---------------------------
@sudo_only
async def stopnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in nc_tasks and nc_tasks[chat_id]:
        for task in nc_tasks[chat_id]: task.cancel()
        del nc_tasks[chat_id]
        await update.message.reply_text(STOP_MESSAGE)
    else: await update.message.reply_text("❌ No NC running in this chat.")

@sudo_only
async def stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in spam_tasks and spam_tasks[chat_id]:
        for task in spam_tasks[chat_id]: task.cancel()
        del spam_tasks[chat_id]
        await update.message.reply_text(STOP_MESSAGE)
    else: await update.message.reply_text("❌ No spam running in this chat.")

@sudo_only
async def stopslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in slider_tasks and slider_tasks[chat_id]:
        for task in slider_tasks[chat_id]: task.cancel()
        del slider_tasks[chat_id]
        await update.message.reply_text(STOP_MESSAGE)
    else: await update.message.reply_text("❌ No slider running in this chat.")

@sudo_only
async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]: task.cancel()
        del nc_tasks[chat_id]
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]: task.cancel()
        del spam_tasks[chat_id]
    if chat_id in slider_tasks:
        for task in slider_tasks[chat_id]: task.cancel()
        del slider_tasks[chat_id]
    if chat_id in pfp_tasks:
        pfp_tasks[chat_id].cancel()
        del pfp_tasks[chat_id]
    await update.message.reply_text(STOP_MESSAGE)

@sudo_only
async def delay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_DELAY
    if not context.args:
        await update.message.reply_text(f"⏱ Current delay: {GLOBAL_DELAY:.3f}s\nUsage: /delay <0.005-0.05>")
        return
    try:
        new_delay = float(context.args[0])
        if new_delay < 0.005 or new_delay > 0.05:
            await update.message.reply_text("❌ Delay must be between 0.005 and 0.05 seconds.")
            return
        GLOBAL_DELAY = new_delay
        await update.message.reply_text(f"✅ Delay set to {GLOBAL_DELAY:.3f}s")
    except ValueError: await update.message.reply_text("❌ Invalid number. Use /delay <0.005-0.05>")

# ---------------------------
# COMMAND HANDLERS - ADMIN ACTION
# ---------------------------
@sudo_only
async def make_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Kisi user ke message par reply karke /admin likho!")
    
    chat_id = update.message.chat_id
    target_user = update.message.reply_to_message.from_user
    
    permissions = {
        'can_change_info': True, 'can_post_messages': True, 'can_edit_messages': True,
        'can_delete_messages': True, 'can_invite_users': True, 'can_restrict_members': True,
        'can_pin_messages': True, 'can_promote_members': True, 'can_manage_video_chats': True,
        'can_manage_chat': True
    }
    
    status_msg = await update.message.reply_text(f"⏳ {target_user.first_name} ko saare bots se Admin banaya jaa rha hai...")
    promoted_by_bots = 0
    
    for bot in bots:
        try:
            await bot.promote_chat_member(chat_id=chat_id, user_id=target_user.id, **permissions)
            promoted_by_bots += 1
            await asyncio.sleep(0.05)
        except Exception: continue
            
    if promoted_by_bots > 0:
        await status_msg.edit_text(f"👑 **𝐑𝐀𝐘𝐔𝐆𝐀 Power** 👑\n\n✅ {target_user.mention_markdown_v2()} ko successfully total {promoted_by_bots} bots ne Full Admin bana diya hai!")
    else:
        await status_msg.edit_text("❌ Koi bhi bot is chat me Admin nahi hai ya permissions nahi hain!")

# ---------------------------
# COMMAND HANDLERS - OWNER Only
# ---------------------------
@owner_only
async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    promoter_bot = context.bot
    promoter_id = promoter_bot.id
    other_bots = [info for info in bots_info if info['id'] != promoter_id]
    if not other_bots:
        await update.message.reply_text("No other bots to promote.")
        return
    permissions = {
        'can_change_info': True, 'can_post_messages': True, 'can_edit_messages': True,
        'can_delete_messages': True, 'can_invite_users': True, 'can_restrict_members': True,
        'can_pin_messages': True, 'can_promote_members': True, 'can_manage_video_chats': True,
        'can_manage_chat': True
    }
    promoted_count = 0
    for bot_info in other_bots:
        try:
            await promoter_bot.promote_chat_member(chat_id=chat_id, user_id=bot_info['id'], **permissions)
            promoted_count += 1
        except Exception as e: logging.warning(f"Failed to promote bot {bot_info['id']}: {e}")
    await update.message.reply_text(f"Promotion completed. {promoted_count} bots promoted.")

@owner_only
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return await update.message.reply_text("❌ Reply to a user's message")
    uid = update.message.reply_to_message.from_user.id
    SUDO_USERS.add(uid)
    save_sudo()
    await update.message.reply_text(f"✅ Added sudo: {uid}")

@owner_only
async def delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return await update.message.reply_text("❌ Reply to a user's message")
    uid = update.message.reply_to_message.from_user.id
    if uid in SUDO_USERS and uid != OWNER_ID:
        SUDO_USERS.remove(uid)
        save_sudo()
        await update.message.reply_text(f"✅ Removed sudo: {uid}")
    else: await update.message.reply_text("❌ Cannot remove master owner or user not in sudo")

@owner_only
async def sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = [f"👑 {uid}" for uid in SUDO_USERS]
    await update.message.reply_text(f"**SUDO USERS:**\n" + "\n".join(lines) + f"\n\nTotal: {len(SUDO_USERS)}")

@owner_only
async def bye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    await update.message.reply_text("👋 All bots are leaving...")
    for bot in bots:
        try:
            await bot.send_message(chat_id, BYE_MESSAGE)
            await bot.leave_chat(chat_id)
        except Exception as e: logging.warning(f"Bot {bot.id} could not leave: {e}")

# ---------------------------
# STYLIZED HELP MENU
# ---------------------------
HELP_MENU = """
╔═══════════════════════════╗
     ⚡ 𝐑 𝐀 𝐘 𝐔 𝐆 𝐀  𝐕 𝟒 ⚡
╚═══════════════════════════╝
 ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
 ┃ 🔮 𝘕𝘈𝘔𝘌 𝘊𝘏𝘈𝘕𝘎𝘌 (𝘕𝘊) 𝘔𝘖𝘋𝘌𝘚 ┃
 ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
   ⚡ /ncdark   │ ⚡ /tmkcnc   
   ⚡ /evonc    │ ⚡ /marvelnc 
   ⚡ /magicnc  │ ⚡ /sportnc  
   ⚡ /lndnc    │ ⚡ /ncspeed  
   ⚡ /emognc   │ ⚡ /yournc   
   ⚡ /customnc │ ⚡ /typenc   
   ⚡ /flashnc  │ ⚡ /foxync   
 ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
 ┃ 🖼️ 𝘗𝘍𝘗 𝘓𝘖𝘖𝘗 𝘊𝘏𝘈𝘕𝘎𝘛𝘌𝘙      ┃
 ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
   📸 /photosave (Reply to image)
   🖼️ /setgc     │ 🛑 /stopgc
 ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
 ┃ 💥 𝘚𝘗𝘈𝘔𝘔𝘐𝘕𝘎 𝘚𝘠𝘚𝘛𝘌𝘔       ┃
 ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
   🔥 /texts    │ 🔥 /shayari  
   🔥 /songy    │ 🔥 /custom   
 ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
 ┃ 🌊 𝘚𝘓𝘐𝘋𝘌𝘙 & 𝘈𝘛𝘛𝘈𝘊𝘚       ┃
 ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
   🫧 /alexa    │ 🫧 /animal   
   🫧 /swipe    (Reply to target)
 ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
 ┃ 👑 𝘖WN𝘌𝘙 & 𝘚𝘜𝘋O 𝘗𝘈𝘕𝘌𝘓     ┃
 ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
   ⭐ /admin    │ ⭐ /promote  
   ⭐ /addsudo  │ ⭐ /delsudo  
   ⭐ /sudo     │ ⭐ /bye      
 ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
 ┃ ⚙️ 𝘊𝘖𝘕𝘛𝘙𝘖𝘓𝘚 & 𝘚𝘗𝘌𝘌𝘋        ┃
 ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
   🛑 /stopnc   │ 🛑 /stopspam 
   🛑 /stopslide│ 🛑 /stopall  
   ⏱️ /delay [0.05 ~ 0.005]    
 ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
 ⚡ 𝘗𝘖𝘞𝘌𝘙𝘌𝙳 𝘉𝘠 𝘙𝘈𝘠𝘜𝘎𝘗 𝘕𝘌𝘛𝘎𝘙𝘖𝘙𝘒 ⚡
"""

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_owner_or_sudo(update.effective_user.id): 
        await update.message.reply_text(HELP_MENU)
    else: 
        await update.message.reply_text("𝐆𝐔𝐋𝐀𝐌𝐈 𝐊𝐑 𝐏𝐇𝐋𝐄 𝐅𝐈𝐑 𝐒𝐔𝐃O 𝐌𝐈𝐋𝐄𝐆𝐀 😂")

# ---------------------------
# BOT APPLICATION BUILDER
# ---------------------------
def build_app(token):
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("ncdark", ncdark))
    app.add_handler(CommandHandler("tmkcnc", tmkcnc))
    app.add_handler(CommandHandler("evonc", evonc))
    app.add_handler(CommandHandler("marvelnc", marvelnc))
    app.add_handler(CommandHandler("magicnc", magicnc))
    app.add_handler(CommandHandler("sportnc", sportnc))
    app.add_handler(CommandHandler("lndnc", lndnc))
    app.add_handler(CommandHandler("ncspeed", ncspeed))
    app.add_handler(CommandHandler("emognc", emognc))
    app.add_handler(CommandHandler("yournc", yournc))
    app.add_handler(CommandHandler("customnc", customnc))
    app.add_handler(CommandHandler("typenc", typenc))
    app.add_handler(CommandHandler("flashnc", flashnc))
    app.add_handler(CommandHandler("foxync", foxync))
    app.add_handler(CommandHandler("photosave", photosave))
    app.add_handler(CommandHandler("setgc", setgc))
    app.add_handler(CommandHandler("stopgc", stopgc))
    app.add_handler(CommandHandler("texts", texts))
    app.add_handler(CommandHandler("shayari", shayari))
    app.add_handler(CommandHandler("songy", songy))
    app.add_handler(CommandHandler("custom", custom))
    app.add_handler(CommandHandler("alexa", alexa))
    app.add_handler(CommandHandler("animal", animal))
    app.add_handler(CommandHandler("swipe", swipe))
    app.add_handler(CommandHandler("stopnc", stopnc))
    app.add_handler(CommandHandler("stopspam", stopspam))
    app.add_handler(CommandHandler("stopslide", stopslide))
    app.add_handler(CommandHandler("stopall", stopall))
    app.add_handler(CommandHandler("delay", delay))
    app.add_handler(CommandHandler("admin", make_admin))
    app.add_handler(CommandHandler("promote", promote))
    app.add_handler(CommandHandler("addsudo", addsudo))
    app.add_handler(CommandHandler("delsudo", delsudo))
    app.add_handler(CommandHandler("sudo", sudo))
    app.add_handler(CommandHandler("bye", bye))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(ChatMemberHandler(handle_my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))
    return app

async def run_all_bots():
    global bots_info
    for token in TOKENS:
        try:
            app = build_app(token)
            await app.initialize()
            bot = app.bot
            me = await bot.get_me()
            bots_info.append({'id': me.id, 'username': me.username, 'bot': bot})
            apps.append(app)
            bots.append(bot)
            await app.start()
            await app.updater.start_polling()
            print(f"🚀 Rayuga Bot started: @{me.username} (ID: {me.id})")
        except Exception as e: print(f"❌ Failed to start bot: {e}")

    print(f"\n🎉 𝐑𝐀𝐘𝐔𝐆𝐀 V4 is running with {len(bots)} bots!")
    print(f"👑 Primary Owner ID: {OWNER_ID}")
    print(f"⚡ Default speed: {GLOBAL_DELAY:.3f}s per action")
    print("="*40)
    await asyncio.Event().wait()

if __name__ == "__main__":
    print("\n" + "="*40)
    print("        𝐑𝐀𝐘𝐔𝐆𝐀 𝐒𝐘𝐒𝐓𝐄𝐌 - V4 STARTING")
    print("="*40)
    print("\n... STARTING RAYUGA CORE UTILS ...\n")
    try: asyncio.run(run_all_bots())
    except KeyboardInterrupt: print("\n🛑 Bot stopped by user.")
    except Exception as e: print(f"❌ Error: {e}")
