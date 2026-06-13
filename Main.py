# main.py - Complete Script for Railway
import asyncio
import json
import os
import sys
import random
from datetime import datetime, timezone, timedelta
from telegram import Update, ChatMemberUpdated, ChatMember
from telegram.error import RetryAfter
from telegram.ext import Application, CommandHandler, ContextTypes, ChatMemberHandler
import logging

# ---------------------------
# YOUR 11 BOT TOKENS
# ---------------------------
TOKENS = [
    "8875719610:AAEPZpAFmsLfGpcfq5G6IRqrkRw-oW6wawc",
    "8819644187:AAEfMcd3Y1iUs3a5bswYwuXHMFhe1EdzOEo",
    "8945796268:AAEn4esqIx4JbbNQC5G8LsWD6uALOarqDD0",
    "8896368359:AAHZiQbpOJF-TpL5e-oeXJ4WP-hU2nV6sfQ",
    "8933273450:AAEUY5KkCkdDMKDlmww4-3V6W6ZLUxwZm7M",
    "8907464798:AAHGPbLN37eCgA1qsTbpijqN84eXE0KddzE",
    "8782264249:AAHzdBfPHq8ugHIiSkjNyVIcvnjKnkB8cQ0",
    "8142959042:AAHsO409iZu7S5BTm1NENuiu2UwjJeLK584",
    "8672754851:AAFYrY7xGXywkEtSFmMqO6Mgn1F_K7sd2a4",
    "8666579675:AAGrPDFoJPe8zsuvA6WIP5YqsY2bu7QS9vg",
    "8731707655:AAEhXd7amPipwvx87I1vBEG4eEcgO6IsrkQ"
]

# ---------------------------
# OWNER & SUDO CONFIG
# ---------------------------
OWNER_ID = 8680250815
SUDO_FILE = "sudo_users.json"

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
GLOBAL_DELAY = 0.05

STOP_MESSAGE = "𝑂𝐾𝐼 𝑌𝐿𝐿 ¡! 🐣"
ADMIN_MESSAGE = "ꪖᦔꪑ꠸ꪀ ꫝꫀ᥅ꫀ ~ 🪽"
BYE_MESSAGE = "𝐆𝐀𝐌𝐄 𝐎𝐕𝐄𝐑 !! 📌"
GREETING_MESSAGE = "ꪑ꠸ꫀ ꪖᧁꪗꪖ 🫣"

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
# NC EMOJI LISTS
# ---------------------------
DARK_EMOJIS = ["🕳️", "🌑", "👣", "🗝️", "🧬", "🔌", "⬛", "🦾", "📜", "🕯️", "🍷", "🥀", "🖤", "🕸️", "🗡️", "🎱", "🐦‍⬛", "🔮", "🌑", "🪄", "🌝", "🌚", "🌜", "🌛", "🌙", "⭐", "🌟", "✨", "🪐", "🌍", "🌠", "🌌", "☄️", "🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]

HAND_EMOJIS = ["👀", "👁️", "👄", "🫦", "👅", "👃🏻", "👂🏻", "🦻🏻", "🦶🏻", "🦵🏻", "🦿", "🦾", "💪🏻", "👏🏻", "👍🏻", "👎🏻", "🫶🏻", "🙌🏻", "👐🏻", "🤲🏻", "🤜🏻", "🤛🏻", "✊🏻", "👊🏻", "🫳🏻", "🫴🏻", "🫱🏻", "🫲🏻", "🫸🏻", "🫷🏻", "👋🏻", "🤚🏻", "🖐🏻", "✋🏻", "🖖🏻", "🤟🏻", "🤘🏻", "✌🏻", "🤞🏻", "🫰🏻", "🤙🏻", "🤌🏻", "🤏🏻", "👌🏻", "🫵🏻", "👉🏻", "👈🏻", "☝🏻", "👆🏻", "👇🏻", "🖕🏻", "✍🏻", "🤳🏻", "🙏🏻", "💅🏻", "🤝🏼", "🌘"]

MARVEL_EMOJIS = ["🛡️", "🇺🇸", "🎖️", "🦾", "🚀", "⚡", "🤖", "⚡", "🔨", "🌩️", "🔱", "🕷️", "🕶️", "🔫", "🥀", "🏹", "🎯", "🦅", "🧪", "☢️", "👊", "🟢", "💎", "🤖", "🟡"]

MAGIC_EMOJIS = ["🧪", "⚗️", "📜", "💎", "🕳️", "🌑", "🧿", "🐦‍⬛", "🌀", "⚡", "🪄", "🧿", "🕯️", "📜", "🏛️", "🖤", "✥", "♱", "⚖︎", "∞", "𖦹"]

NATURE_EMOJIS = ["💐", "🌹", "🥀", "🌺", "🌷", "🪷", "🌸", "💮", "🏵️", "🪻", "🌻", "🌼", "🍂", "🍁", "🍄", "🌾", "🌿", "🌱", "🍃", "☘️", "🍀", "🪴", "🌵", "🌴", "🪾", "🌳", "🌲", "🪵", "🪹", "🪺"]

FOOD_EMOJIS = ["🍧", "🧋", "🧃", "🥛", "🍿", "🧊", "🍵", "☕", "🍻", "🍺", "🧉", "🫖", "🍾", "🍷", "🥃", "🫗", "🍸", "🍹", "🍶", "🥢", "🥂", "🧈", "🧁", "🍭", "🍬", "🍫", "🍨", "🍡", "🍙", "🍥", "🥠", "🥟", "🍛", "🍤", "🍜", "🦪", "🍚", "🥣", "🥫", "🌯"]

FACE_EMOJIS = ["☺️", "😌", "🙂‍↕️", "🙂‍↔️", "😏", "🤤", "😋", "😛", "😝", "😜", "🤪", "😔", "🥺", "😬", "😑", "😐", "😶", "😶‍🌫️", "🫥", "🤐", "🫡", "🤔", "🤫", "🫢", "🤭", "🥱", "🤗", "🫣", "😱", "🤨", "🧐", "😒", "🙄", "😮‍💨", "😤", "😠", "😡", "🤬", "😞", "😓", "😟", "😥", "😢", "☹️", "🙁", "🫤", "😕", "😰", "😨", "😧", "😦", "😮", "😯", "😲", "🤯", "🫨", "😵‍💫", "😵", "😫", "🥴", "🥶", "🥵"]

HOBBY_EMOJIS = ["🃏", "🪄", "🎩", "📷", "🀄", "🎴", "🎰", "📸", "🖼️", "🎨", "🫟", "🖌️", "🖍️", "🪡", "🧵", "🧶", "🎹", "🎷", "🎺", "🎸", "🪕", "🎻", "🪉", "🪘", "🥁", "🪇", "🪈", "🪗", "🎤", "🎧", "🎚️", "🎛️", "🎙️", "📼", "📻", "📺", "📹", "📽️", "🎥", "🎞️", "🎬", "🎭", "🎫", "🎟️"]

TECH_EMOJIS = ["🔋", "🪫", "🖲️", "💽", "💾", "💿", "📀", "🖥️", "💻", "⌨️", "🖨️", "鼠标", "🪙", "💎", "💸", "💵", "💴", "💶", "💷", "💳", "💰", "🧾", "🧮", "⚖️", "🛒", "🛍️", "💡", "🕯️", "🔦", "🏮", "🧱", "🪟", "🪞", "🚪", "🚿", "🛁", "🚽", "🧻", "🪠", "🧸", "🪆", "🧷", "🪢", "🧹", "🧴", "🧽", "🧼", "🪥", "🪒", "🪮", "🧺", "🧦", "🧤", "🧣", "👖"]

ANIMAL_EMOJIS = ["🪼", "🐚", "🦋", "🐞", "🐝", "🐛", "🪱", "🦠", "🐾", "🫧", "🪸", "🦪", "🪼", "🐙", "🦑", "🐡", "🐠", "🐟", "🐳", "🐋", "🐬", "🦈", "🦭", "🐧", "🦃", "🐦‍🔥", "🦚", "🦩", "🪿", "🦆", "🦢", "🦤", "🕊️", "🦜", "🦉", "🦅", "🐥", "🐤", "🐣", "🐓", "🐦", "🪶", "🪽", "t", "🦦", "🦔", "🦡", "🦨", "🐅", "🐆", "🦒", "🦏", "🦣", "🐘", "🦓", "🦘", "🦥", "🦬", "🐃", "🐏", "🐂", "🐄", "🐎", "🐈", "🐩"]

# ---------------------------
# WORD LIST FOR TYPENC
# ---------------------------
TYPENC_WORDS = [
    "𝗧𝗔𝗧𝗧𝗘", "𝗚𝗨𝗟𝗔𝗠", "𝗠𝗔𝗗𝗔𝗥𝗖𝗛𝗢𝗗", "𝗕𝗛𝗘𝗡𝗞𝗟𝗡𝗗", "𝗧𝗠𝗞𝗖", "𝗧𝗠𝗞𝗕",
    "𝗥🇳🇩𝗬", "𝗚𝗔𝗥𝗘𝗘𝗕", "𝗠𝗜𝗦𝗧𝗜 𝗞𝗘 𝗟𝗔𝗗𝗞𝗘", "𝗚🇳🇩🇺", "𝗖𝗛𝗔𝗣𝗥𝗜", "𝗖𝗛𝗠𝗥",
    "𝗕𝗦𝗗𝗞", "𝗞🇪🇪🇩🇪", "𝗖𝗛🇺🇩", "𝗧𝗕𝗞𝗟", "𝗛𝗔𝗥𝗔𝗠𝗞𝗛𝗢𝗥", "𝗥"
]

# ---------------------------
# SLIDER TEXTS
# ---------------------------
ALEXA_TEXTS = [
    "𝗔index𝗘𝗫𝗔 🇮𝗦𝗦 𝗠𝗖 𝗞🇮 𝗠𝗔𝗔 𝗞𝗘 𝗡𝗢𝗧🇪𝗦 𝗗🇮𝗞𝗛𝗔𝗢 🙁",
    "𝗔index𝗘𝗫𝗔 🇮𝗦𝗞🇮 𝗕𝗛🇪🇳 𝗖𝗛𝗢𝗗 𝗗𝗢 🌙",
    "𝗔index𝗘𝗫𝗔 🇮𝗦𝗞🇪 𝗕𝗔‌𝗔𝗣 𝗞🇮 🇬🇳🇩 𝗠🇮🇪 𝗟𝗔𝗧𝗛 𝗗𝗔𝗔𝗟 𝗗𝗢 😆",
    "𝗔index𝗘𝗫𝗔 🇮𝗦𝗞𝗔 🇬𝗔𝗠🇪 𝗢𝗩🇪𝗥 𝗞𝗔 𝗩🇮𝗗🇪𝗢 𝗗𝗢𝗡🇪 𝗞𝗥𝗢 🥹"
]

ANIMAL_TEXTS = [
    "𝗢𝗬🇪 𝗧𝗠𝗞𝗖 𝗠🇮🇪 🇬𝗢𝗥🇮𝗟𝗟𝗔  🦍",
    "𝗢𝗬🇪 𝗧🇪走🇪 𝗕𝗛🇪🇳 𝗞🇮 𝗖𝗛🇺𝗧 𝗠🇮🇪 🇬𝗛𝗢𝗗𝗔 🐎",
    "𝗢𝗬🇪 𝗧🇪走🇪 𝗕𝗔🇦𝗣 𝗞🇮 🇬体🇩 𝗠🇮🇪 𝗞🇦🇳🇬🇦走𝗢𝗢 🦘",
    "𝗢𝗬🇪 𝗧🇪走🇪 🇬体🇩 𝗠🇮🇪 𝗖🇦𝗠🇪𝗟 🐪",
    "𝗢𝗬🇪 𝗧🇺 𝗝🇦🇳𝗪🇦走𝗢𝗦 𝗦🇪 𝗖𝗛🇺🇩 🇬𝗬🇦 ? 😆"
]

SWIPE_TEXTS = [
    "𝗧🇪走🇮 𝗠𝗞𝗖 𝗦🇦𝗦𝗧🇮 𝗛🇦🇮 𝗕🇦🇦𝗧 𝗞𝗛𝗧𝗠 😡",
    "𝗖𝗛𝗟 🇬🇺𝗟🇦𝗠🇮 𝗞走 𝗧🇦𝗧𝗧🇪 😆",
    "𝗖𝗛🇮施行𝗬🇦 𝗖𝗛🇦走🇮 𝗣𝗛🇦🇦🇩 𝗣🇪 🇺𝗦🇳🇪 𝗗🇮𝗬🇦 𝗠🇺𝗧 𝗧𝗠𝗞🇨 😆",
    "🇪𝗞 𝗟🇦🇦‌𝗧 𝗠🇮🇪 𝗟🇳🇩 𝗖𝗛🇦𝗧𝗧🇦 𝗙🇮走🇪🇬🇦 𝗕𝗦施行𝗞 😆"
]

# ---------------------------
# SPAM PATTERNS
# ---------------------------
TEXTS_PATTERN = "{text}  𝑶𝒀𝑬 𝑩𝑲𝑳 𝑻𝑬𝑹𝑰 𝑴𝑨𝑨 𝑲𝑨 𝑲𝑯𝑨𝑺𝑨𝑴 𝑯𝑼 𝑨𝑼𝑲𝑨𝑻 𝑴𝑰𝑬 𝑹𝑯 𝑹𝑵𝑫𝒀 𝑷𝑼𝑻𝑹𝑨 ☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲\\~   "
TEXTS_REPEAT = 10

SHAYARI_PATTERN = "𝙏𝙄𝙆 𝙏𝙄𝙆 𝘾𝙃𝙇𝙏𝘼 𝙂𝙃𝙊𝘿𝘼 {text} 𝙆𝙄 𝘽𝙃𝙀𝙉 𝙆𝘼 𝙇𝙊𝘿𝘼 ╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍ "
SHAYARI_REPEAT = 10

SONGY_PATTERN = """{text} 𝗗𝗮狠𝗲!
𝗕𝗲𝘁𝗮 𝗗𝗮狠𝗲 𝗕𝗲𝗻𝗶 𝗕a𝗮𝗽 𝗧𝗲𝗿𝗮 𝗡𝗮狠𝗮 𝗛𝗮𝗶
𝗟*𝗱𝗮 𝗛𝗼𝗼𝗸𝗮ʜ 𝗠𝗲𝗿𝗮, 𝗠𝗮𝗺𝘁𝗮 𝗠𝗲𝗿𝗶 𝗖𝗵𝗮狠𝗮 𝗛𝗮𝗶
...
"""

CUSTOM_PATTERN = "{text}  ⩇⩇:⩇⩇ {kaomoji}"
CUSTOM_KAOMOJI = ["(◕‿◕)", "(✿◠‿嫁)", "(◔‿◔)", "(◡‿◡✿)", "(ᵔ◡ᵔ)", "😊", "😄", "😁"]

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
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def tmkcnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = HAND_EMOJIS[i % len(HAND_EMOJIS)]
            new_title = f"{text} ⭞ ᴛᴍκᴄ ￫ {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def evonc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = HAND_EMOJIS[i % len(HAND_EMOJIS)]
            new_title = f"{text} 𝙂𝙐𝙇𝘼𝙈﹏{emoji}﹏"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def marvelnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = MARVEL_EMOJIS[i % len(MARVEL_EMOJIS)]
            new_title = f"{text} 𝙏𝘽 Kenny ᯓ {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def magicnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = MAGIC_EMOJIS[i % len(MAGIC_EMOJIS)]
            new_title = f"{text} 𝙍𝙉𝘿𝙔 𝘽𝘼𝙇𝘼𝙆⁀➴༯ {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def sportnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = MARVEL_EMOJIS[i % len(MARVEL_EMOJIS)]
            new_title = f"{text} 𝙏𝙀𝙍𝑰 𝙂体🇩 🇲🇮🇪 ≯ {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def lndnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = NATURE_EMOJIS[i % len(NATURE_EMOJIS)]
            new_title = f"{text} 𝘾𝙃𝙐𝘿 𓀐𓂺 {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def ncspeed_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = FOOD_EMOJIS[i % len(FOOD_EMOJIS)]
            new_title = f"{text} 𝙏𝙀𝙍𝑰 𝙈𝘼𝘼 𝘾𝙃𝙐𝘿𝘼𝙆𝘼𝘿 ≫ {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def emognc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = FACE_EMOJIS[i % len(FACE_EMOJIS)]
            new_title = f"{text} 𝙆𝙀𝙀𝘿𝙀 𝘼𝙐𝙆𝘼𝙏 𝘽𝙉𝘼⁀➴♡ {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def yournc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = HOBBY_EMOJIS[i % len(HOBBY_EMOJIS)]
            new_title = f"{text} 𓆩 {emoji} 𓆪"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def customnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = FACE_EMOJIS[i % len(FACE_EMOJIS)]
            new_title = f"{text} જ⁀➴ {emoji} ִֶָ𓂃 ࣪ ִֶָ🦢་༘࿐"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def typenc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            word = TYPENC_WORDS[i % len(TYPENC_WORDS)]
            new_title = f"{text} {word} ִֶָ࣪𓏲ᥫ᭡ ₊ ⊹ ˑ ִ ֶ 𓂃"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def flashnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = TECH_EMOJIS[i % len(TECH_EMOJIS)]
            new_title = f"{text} ═══ {emoji} ═══"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def foxync_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = ANIMAL_EMOJIS[i % len(ANIMAL_EMOJIS)]
            new_title = f"{text} 𝗖𝗛🇺🇩 𝗞走 𝗗🇦🇫🇦🇳~{emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

# ---------------------------
# SPAM LOOP FUNCTIONS
# ---------------------------
async def texts_spam_loop(bot, chat_id, text):
    message = (TEXTS_PATTERN.format(text=text) + "\n") * TEXTS_REPEAT
    while True:
        try:
            await bot.send_message(chat_id, message)
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def shayari_spam_loop(bot, chat_id, text):
    message = (SHAYARI_PATTERN.format(text=text) + "\n") * SHAYARI_REPEAT
    while True:
        try:
            await bot.send_message(chat_id, message)
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def songy_spam_loop(bot, chat_id, text):
    message = SONGY_PATTERN.format(text=text)
    while True:
        try:
            await bot.send_message(chat_id, message)
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def custom_spam_loop(bot, chat_id, text):
    while True:
        try:
            kaomoji = random.choice(CUSTOM_KAOMOJI)
            message = CUSTOM_PATTERN.format(text=text, kaomoji=kaomoji)
            await bot.send_message(chat_id, message)
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

# ---------------------------
# SLIDER LOOP FUNCTIONS
# ---------------------------
async def make_slider_loop(texts, bot, chat_id, target_msg_id):
    i = 0
    while True:
        try:
            await bot.send_message(chat_id=chat_id, text=texts[i % len(texts)], reply_to_message_id=target_msg_id)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

# ---------------------------
# AUTO HANDLER
# ---------------------------
async def handle_my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result: ChatMemberUpdated = update.my_chat_member
    if result.chat.type not in ["group", "supergroup"]:
        return
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
    if not context.args:
        return await update.message.reply_text("❌ Usage: /ncdark <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(ncdark_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ ncdark started for: {text}")

@sudo_only
async def tmkcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /tmkcnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(tmkcnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ tmkcnc started for: {text}")

@sudo_only
async def evonc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /evonc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(evonc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ evonc started for: {text}")

@sudo_only
async def marvelnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /marvelnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(marvelnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ marvelnc started for: {text}")

@sudo_only
async def magicnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /magicnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(magicnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ magicnc started for: {text}")

@sudo_only
async def sportnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /sportnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(sportnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ sportnc started for: {text}")

@sudo_only
async def lndnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /lndnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(lndnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ lndnc started for: {text}")

@sudo_only
async def ncspeed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /ncspeed <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(ncspeed_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ ncspeed started for: {text}")

@sudo_only
async def emognc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /emognc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(emognc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ emognc started for: {text}")

@sudo_only
async def yournc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /yournc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(yournc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ yournc started for: {text}")

@sudo_only
async def customnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /customnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(customnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ customnc started for: {text}")

@sudo_only
async def typenc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /typenc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(typenc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ typenc started for: {text}")

@sudo_only
async def flashnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /flashnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(flashnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ flashnc started for: {text}")

@sudo_only
async def foxync(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /foxync <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
    tasks = [asyncio.create_task(foxync_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ foxync started for: {text}")

# ---------------------------
# COMMAND HANDLERS - SPAM
# ---------------------------
@sudo_only
async def texts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /texts <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]
    tasks = [asyncio.create_task(texts_spam_loop(b, chat_id, text)) for b in bots]
    spam_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ texts spam started for: {text}")

@sudo_only
async def shayari(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /shayari <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]
    tasks = [asyncio.create_task(shayari_spam_loop(b, chat_id, text)) for b in bots]
    spam_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ shayari spam started for: {text}")

@sudo_only
async def songy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /songy <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]
    tasks = [asyncio.create_task(songy_spam_loop(b, chat_id, text)) for b in bots]
    spam_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ songy spam started for: {text}")

@sudo_only
async def custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /custom <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]
    tasks = [asyncio.create_task(custom_spam_loop(b, chat_id, text)) for b in bots]
    spam_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ custom spam started for: {text}")

# ---------------------------
# COMMAND HANDLERS - SLIDER
# ---------------------------
@sudo_only
async def alexa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a message to start alexa!")
    chat_id = update.message.chat_id
    target_msg_id = update.message.reply_to_message.message_id
    if chat_id in slider_tasks:
        for task in slider_tasks[chat_id]:
            task.cancel()
        del slider_tasks[chat_id]
    tasks = [asyncio.create_task(make_slider_loop(ALEXA_TEXTS, b, chat_id, target_msg_id)) for b in bots]
    slider_tasks[chat_id] = tasks
    await update.message.reply_text("✅ Alexa started on that message.")

@sudo_only
async def animal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a message to start animal!")
    chat_id = update.message.chat_id
    target_msg_id = update.message.reply_to_message.message_id
    if chat_id in slider_tasks:
        for task in slider_tasks[chat_id]:
            task.cancel()
        del slider_tasks[chat_id]
    tasks = [asyncio.create_task(make_slider_loop(ANIMAL_TEXTS, b, chat_id, target_msg_id)) for b in bots]
    slider_tasks[chat_id] = tasks
    await update.message.reply_text("✅ Animal started on that message.")

@sudo_only
async def swipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a message to start swipe!")
    chat_id = update.message.chat_id
    target_msg_id = update.message.reply_to_message.message_id
    if chat_id in slider_tasks:
        for task in slider_tasks[chat_id]:
            task.cancel()
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
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
        await update.message.reply_text(STOP_MESSAGE)
    else:
        await update.message.reply_text("❌ No NC running in this chat.")

@sudo_only
async def stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in spam_tasks and spam_tasks[chat_id]:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]
        await update.message.reply_text(STOP_MESSAGE)
    else:
        await update.message.reply_text("❌ No spam running in this chat.")

@sudo_only
async def stopslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in slider_tasks and slider_tasks[chat_id]:
        for task in slider_tasks[chat_id]:
            task.cancel()
        del slider_tasks[chat_id]
        await update.message.reply_text(STOP_MESSAGE)
    else:
        await update.message.reply_text("❌ No slider running in this chat.")

@sudo_only
async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]
    if chat_id in slider_tasks:
        for task in slider_tasks[chat_id]:
            task.cancel()
        del slider_tasks[chat_id]
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
    except ValueError:
        await update.message.reply_text("❌ Invalid number. Use /delay <0.005-0.05>")

# ---------------------------
# COMMAND HANDLERS - OWNER
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
        except Exception as e:
            logging.warning(f"Failed to promote bot {bot_info['id']}: {e}")
    await update.message.reply_text(f"Promotion completed. {promoted_count} bots promoted.")

@owner_only
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a user's message")
    uid = update.message.reply_to_message.from_user.id
    SUDO_USERS.add(uid)
    save_sudo()
    await update.message.reply_text(f"✅ Added sudo: {uid}")

@owner_only
async def delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a user's message")
    uid = update.message.reply_to_message.from_user.id
    if uid in SUDO_USERS and uid != OWNER_ID:
        SUDO_USERS.remove(uid)
        save_sudo()
        await update.message.reply_text(f"✅ Removed sudo: {uid}")
    else:
        await update.message.reply_text("❌ Cannot remove owner or user not in sudo")

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
        except Exception as e:
            logging.warning(f"Bot {bot.id} could not leave: {e}")

# ---------------------------
# HELP COMMAND
# ---------------------------
HELP_MENU = """
𝐌𝙰𝙳𝙰𝚁𝙰  𝙺𝙴  𝙱𝙰𝙰𝙿  𝙺𝙸  𝚂𝙲𝚁𝙸𝙿𝚃 < 🪐
﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏
──────𝐍𝚌'𝚜──────
⤹!ncdark
⤹!tmkcnc
⤹!evonc
⤹!marvelnc
⤹!magicnc
⤹!sportnc
⤹!lndnc
⤹!ncspeed
⤹!emognc
⤹!yournc
⤹!customnc
⤹!typenc
⤹!flashnc
⤹!foxync
﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏
──────𝐒𝚙𝚊𝚖───────
⤹!texts
⤹!shayari
⤹!songy
⤹!custom
﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏
──────𝐒𝚕𝚒𝚍𝚎rer──────
⤹!alexa
⤹!animal
⤹!swipe
﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏
──────𝐎𝚠nent───────
⤹!promote
⤹!addusdo 
⤹!delsudo
⤹!sudo
⤹!bye
﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏
──────𝐂𝚘𝚗𝘁𝚛𝚘𝚕──────
⤹!stopnc
⤹!stopspam
⤹!stopslide
⤹!stopall
⤹!delay [0.05 ~ 0.005]
﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏
─────𝐄𝙽𝙹𝙾𝚈 ᥫ᭡.─────
"""

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_owner_or_sudo(update.effective_user.id):
        await update.message.reply_text(HELP_MENU)
    else:
        await update.message.reply_text("𝐆𝐔𝐋𝐀𝐌𝐈 𝐊𝐑 𝐏𝐇𝐋𝐄 𝐅𝐈𝐑 𝐒𝐔𝐃𝐎 𝐌𝐈𝐋𝐄𝐆𝐀 😂")

# ---------------------------
# BOT SETUP
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
            print(f"🚀 Bot started: @{me.username} (ID: {me.id})")
        except Exception as e:
            print(f"❌ Failed to start bot: {e}")

    print(f"\n🎉 MADARA KE BAAP KI SCRIPT is running with {len(bots)} bots!")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"⚡ Default speed: {GLOBAL_DELAY:.3f}s per action")
    print("="*40)
    await asyncio.Event().wait()

if __name__ == "__main__":
    print("\n" + "="*40)
    print("      MADARA KE BAAP KI SCRIPT - RUNNING ON CLOUD")
    print("="*40)
    try:
        asyncio.run(run_all_bots())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user.")
    except Exception as e:
        print(f"❌ Error: {e}")
