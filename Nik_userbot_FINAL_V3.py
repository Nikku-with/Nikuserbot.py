#BY 𝐍ɪᴋ PAPA 

# ────────────────────────────────────────────────
#                 STANDARD LIB
# ────────────────────────────────────────────────
import asyncio
import os
import time
import json
import random
import logging
import traceback
import re
from typing import Dict, Set, Optional
from io import BytesIO

# ────────────────────────────────────────────────
#                 THIRD PARTY
# ────────────────────────────────────────────────
import requests
import qrcode
from gtts import gTTS
import yt_dlp

# ────────────────────────────────────────────────
#                 TELETHON
# ────────────────────────────────────────────────
from telethon import TelegramClient, events, functions, types
from telethon.errors import FloodWaitError, RPCError

# ────────────────────────────────────────────────
#                 BASIC PATH SETUP
# ────────────────────────────────────────────────
BASE_DIR = os.getcwd()

DOWNLOAD_PATH = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

TEMP_PATH = os.path.join(BASE_DIR, "temp")
os.makedirs(TEMP_PATH, exist_ok=True)

# ────────────────────────────────────────────────
#                 USERBOT CONFIG
# ────────────────────────────────────────────────
# ── V3 FINAL CONFIG - @Nikkkwa | Termux Single File ──
API_ID = 30157921          # <-- apna API_ID (my.telegram.org)
API_HASH = '32bdfcd45922c3abcf4d956fda29e747'  # <-- apna API_HASH
OWNER_ID = 8742036730      # <-- apna ID @userinfobot
SESSION = "aeris"          # <-- Termux pe 'aeris' hi rakho
SESSION_IS_STRING = len(SESSION) > 30 and ":" in SESSION
print(f"👑 NIK V3 | @Nikkkwa | Session: {SESSION[:12]}...")

# V3 Smart Client (file + StringSession)
try:
    from telethon.sessions import StringSession
    if 'SESSION_IS_STRING' in globals() and SESSION_IS_STRING:
        try:
            bot = TelegramClient(StringSession(SESSION), API_ID, API_HASH, auto_reconnect=True, connection_retries=10, retry_delay=3, flood_sleep_threshold=60)
        except:
            bot = TelegramClient(SESSION, API_ID, API_HASH, auto_reconnect=True, connection_retries=10, retry_delay=3, flood_sleep_threshold=60)
    else:
        bot = TelegramClient(SESSION, API_ID, API_HASH, auto_reconnect=True, connection_retries=10, retry_delay=3, flood_sleep_threshold=60)
except:
    bot = TelegramClient(SESSION, API_ID, API_HASH, auto_reconnect=True, connection_retries=10, retry_delay=3)

# ────────────────────────────────────────────────
#                 STORAGE FILES
# ────────────────────────────────────────────────
ADMINS_FILE = "admins.json"
NOTES_FILE = "notes.json"
BANNER_FILE = "banner_msg_id.txt"

# ────────────────────────────────────────────────
#                 CLONE ENGINE STATE
# ────────────────────────────────────────────────
CLONE_ACTIVE: bool = False
LAST_CLONE_ID: Optional[int] = None

CLONE_DATA: Dict[str, Optional[object]] = {
    "name": None,
    "username": None,
    "bio": None,
    "photo_bytes": None,
}

# ────────────────────────────────────────────────
#                 RUNTIME STATE
# ────────────────────────────────────────────────
admins: Set[int] = set()
notes: Dict[int, str] = {}

menu_banner_msg: Optional[tuple] = None
auto_react_emoji: Optional[str] = None

muted_users: Set[int] = set()
global_muted: Set[int] = set()

reply_users: Set[int] = set()
rr_users: Set[int] = set()
flag_users: Set[int] = set()
hrr_users: Set[int] = set()
replygod_users: Set[int] = set()

replyyorichi_users: Dict[int, Dict[str, object]] = {}
replyking_users: Dict[int, Dict[str, object]] = {}  # V3 fix
replyraid_users: Set[int] = set()
spray_tasks: Dict[int, asyncio.Task] = {}
spam_tasks: Dict[int, asyncio.Task] = {}


group_locks: Set[int] = set()

START_TIME = time.time()

SPRAY_DELAY = 3
SPAM_DELAY_V2 = 0.7
AFK_STATE = {"active": False, "reason": None, "since": None}
ECHO_USERS: Set[int] = set()
GHOST_MODE = False
TAGALL_ACTIVE = False
COMMAND_COOLDOWN: Dict[int, float] = {}
V2_VERSION = "3.0 FINAL @Nikkkwa"


# ────────────────────────────────────────────────
#                 BOT ADD ENGINE
# ────────────────────────────────────────────────
ADD_BOTS_LIST = [
    "Nik6_bot",
    "Nik5bot",
    "Nik_3_bot",
    "Nik_2bot",
    "Nik7bot",
    "Nik_8bot",
    "Nik1bot",
    "Nik_10ibot",
    "Nik4_bot",
    "Nik_6bot",
]

# ────────────────────────────────────────────────
#                 FASTGC ENGINE STATE
# ────────────────────────────────────────────────
FASTGC_STATE: Dict[str, Optional[object]] = {
    "active": False,
    "template": None,
    "task": None,
    "chat_id": None,
}

GC_FAST_INTERVAL = 1

GC_FAST_EMOJIS = [
    "❤️","🧡","💛","💚","💙","💜",
    "🖤","🤍","🤎","🩷","🩵","🩶",
    "💖","💘","💝","💗","💓","💞",
    "💕","💟","❣️","❤️‍🔥","❤️‍🩹"
]

# ────────────────────────────────────────────────
#                   HELPERS
# ────────────────────────────────────────────────
# ================= ADMIN STORAGE =================

def load_admins():
    global admins
    try:
        if not os.path.isfile(ADMINS_FILE):
            admins = set()
            return

        with open(ADMINS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        clean = set()

        if isinstance(data, list):
            for x in data:
                try:
                    clean.add(int(x))
                except:
                    continue

        admins = clean

    except Exception as e:
        print(f"[LOAD ADMINS ERROR] {str(e)[:80]}")
        admins = set()


def save_admins():
    try:
        tmp = sorted(set(int(x) for x in admins))
        with open(ADMINS_FILE, "w", encoding="utf-8") as f:
            json.dump(tmp, f, indent=2)
    except Exception as e:
        print(f"[SAVE ADMINS ERROR] {str(e)[:80]}")


def is_admin(uid: int) -> bool:
    if not uid:
        return False
    return uid == OWNER_ID or uid in admins


# ================= SAFE EDIT V3 =================
async def safe_edit(event, text: str):
    if not text:
        return
    try:
        uid = event.sender_id
        now = time.time()
        if uid in COMMAND_COOLDOWN and now - COMMAND_COOLDOWN[uid] < 0.3:
            await asyncio.sleep(0.3)
        COMMAND_COOLDOWN[uid] = now
    except: pass
    try:
        return await event.edit(text)
    except FloodWaitError as fw:
        try:
            await asyncio.sleep(min(fw.seconds, 10))
            return await event.edit(text)
        except: pass
    except Exception:
        try:
            msg = await event.reply(text)
        except:
            return
        try:
            if event.out:
                await event.delete()
        except:
            pass
        return msg


# ================= NOTES STORAGE =================

def load_notes():
    global notes
    try:
        if not os.path.isfile(NOTES_FILE):
            notes = {}
            return

        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)

        clean = {}

        if isinstance(raw, dict):
            for k, v in raw.items():
                try:
                    clean[int(k)] = str(v)
                except:
                    continue

        notes = clean

    except Exception as e:
        print(f"[LOAD NOTES ERROR] {str(e)[:80]}")
        notes = {}


def save_notes():
    try:
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[SAVE NOTES ERROR] {str(e)[:80]}")


# ================= MENU BANNER STORAGE =================

def load_banner():
    global menu_banner_msg
    try:
        if not os.path.isfile(BANNER_FILE):
            menu_banner_msg = None
            return

        with open(BANNER_FILE, "r", encoding="utf-8") as f:
            raw = f.read().strip()

        if ":" not in raw:
            menu_banner_msg = None
            return

        chat, msg = raw.split(":", 1)

        menu_banner_msg = (int(chat), int(msg))

    except Exception as e:
        print(f"[LOAD BANNER ERROR] {str(e)[:80]}")
        menu_banner_msg = None


def save_banner():
    try:
        if not menu_banner_msg:
            if os.path.isfile(BANNER_FILE):
                os.remove(BANNER_FILE)
            return

        with open(BANNER_FILE, "w", encoding="utf-8") as f:
            f.write(f"{menu_banner_msg[0]}:{menu_banner_msg[1]}")

    except Exception as e:
        print(f"[SAVE BANNER ERROR] {str(e)[:80]}")


# ───── UNIVERSAL TARGET RESOLVER ─────
async def get_targets(event, arg: str = "") -> Set[int]:

    targets: Set[int] = set()

    # ⭐ reply resolver
    if event.is_reply:
        try:
            reply = await event.get_reply_message()
            if reply and reply.sender_id:
                targets.add(int(reply.sender_id))
        except:
            pass

    # ⭐ argument resolver
    if arg:
        for part in arg.strip().split():

            if not part:
                continue

            if part.isdigit():
                try:
                    targets.add(int(part))
                    continue
                except:
                    pass

            try:
                ent = await bot.get_entity(part)
                if ent and getattr(ent, "id", None):
                    targets.add(int(ent.id))
            except:
                pass

    # ⭐ self protection
    try:
        me = await bot.get_me()
        targets.discard(me.id)
    except:
        pass

    return targets


# ⭐ INITIAL LOAD
load_admins()
load_notes()
load_banner()
# ────────────────────────────────────────────────
#                   TEXT LISTS (unchanged)
# ────────────────────────────────────────────────
reply_list = ["𝐊ʏᴀ 𝐑ᴇ 𝐑ᴀɴᴅɪᴋᴇ 𝐂ᴏᴏʟ 𝐁ᴀɴᴇɢᴀ 𝐓ᴜ 𝐂ʜᴀʟ 𝐀ʙ 𝐂ʜᴜᴅ 𝐀ᴘɴᴇ 𝐁ᴀᴘ  𝐍ɪᴋ  𝐒ᴇ - 🦢💘",
    "𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ 𝐘ᴀᴀʀ - 𝐉ᴀɪ Dʜʀᴜᴠ ! 🌙",
    "acha beta 😂🔥👊🏻 ? coi na me toh HATER codunga 😹💔🔥😆👊🏻💥",
    "chudke bhaga kaise 😂💥🤣🤘🏻",
    "ne toh  𝐍ɪᴋ ka lun muh me lelia 😂🙏🏻😂🙏🏻",
    "try maa सूर्य☀ nikalte hi pel du 😹🔥💔",
    "mkl lun te vaj 😂✊🏻💦",
    "𝗧ᴍᴋ𝗕 pe  𝐍ɪᴋ ka hamla 😂⚔🔥💥",
    "𝐂ʜʟ 𝐇ᴀʀᴍᴢᴀᴅ𝐈 𝐊ᴇ लड़के 💛🤍🩵",
    "oi 𝐓ᴇʀɪ 𝐌‌ᴀᴀ गुलाम ₰🖤",
    "chl rndyce chud ke dikha 😂💥🤣🔥",
    "𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ naacho 💃🏻💃🏻🕺🏻🎶😂😆💞🔥 !",
    "tera baap bass 𝐵��������������������hai 😂🎀",
    " try maa hagte hue paad mari -#😹🔥🥀",
    "  𝐓ᴇʀɪ 𝐌ᴜᴍᴍʏ 𝐂ʜᴏᴅ 𝐃ɪ  𝐍ɪᴋ 𝐍ᴇ 𝐁ᴡᴀʜᴀʜᴀʜᴀ ⚜","𝐊ʏᴀ 𝐑ᴇ 𝐑ᴀɴᴅɪᴋᴇ 𝐂ᴏᴏʟ 𝐁ᴀɴᴇɢᴀ 𝐓ᴜ 𝐂ʜᴀʟ 𝐀ʙ 𝐂ʜᴜᴅ 𝐀ᴘɴᴇ 𝐁ᴀᴀᴘ 𝐵��������������������𝐒ᴇ - 🦢💘",
    "𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ 𝐘ᴀᴀʀ - 𝐉ᴀɪ  𝐍ɪᴋ ! 🌙",
    "acha beta 😂🔥👊🏻 ? coi na me toh HATER codunga 😹💔🔥😆👊🏻💥",
    "chudke bhaga kaise 😂💥🤣🤘🏻",
    "ne toh  𝐍ɪᴋ ka lun muh me lelia 😂🙏🏻😂🙏🏻",
    "try maa सूर्य☀ nikalte hi pel du 😹🔥💔",
    "mkl lun te vaj 😂✊🏻💦",
    "𝗧ᴍᴋ𝗕 pe  𝐍ɪᴋ ka hamla 😂⚔🔥💥",
    "𝐂ʜʟ 𝐇ᴀʀᴍᴢᴀᴅ𝐈 𝐊ᴇ लड़के 💛🤍🩵",
    "oi 𝐓ᴇʀɪ 𝐌‌ᴀᴀ गुलाम ₰🖤",
    "chl rndyce chud ke dikha 😂💥🤣🔥",
    "𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ naacho 💃🏻💃🏻🕺🏻🎶😂😆💞🔥 !",
    "tera baap bass  𝐍ɪᴋ hai 😂🎀",
    " try maa hagte hue paad mari -#😹🔥🥀",
    "  𝐓ᴇʀɪ 𝐌ᴜᴍᴍʏ 𝐂ʜᴏᴅ 𝐃ɪ  𝐍ɪᴋ 𝐍ᴇ 𝐁ᴡᴀʜᴀʜᴀʜᴀ ⚜"]

reply_texts = ["⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद 𝐍ɪᴋ बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ  𝐍ɪᴋ बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को  𝐍ɪᴋ बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन  𝐍ɪᴋ /\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ  𝐍ɪᴋ बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके MOAN करती है ! 🛐","⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद  𝐍ɪᴋ बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ  𝐍ɪᴋ बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को  𝐍ɪᴋ बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन  𝐍ɪᴋ /\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ  𝐍ɪᴋ बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके MOAN करती है ! 🛐","⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद  𝐍ɪᴋ बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ  𝐍ɪᴋ बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को  𝐍ɪᴋ बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन  𝐍ɪᴋ /\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ  𝐍ɪᴋ बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके MOAN करती है ! 🛐","⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद  𝐍ɪᴋ  बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ  𝐍ɪᴋ बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को  𝐍ɪᴋ बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन  𝐍ɪᴋ /\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ  𝐍ɪᴋ बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके MOAN करती है ! 🛐"]

fun_texts = ["तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）",
"𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜. ㅅ ͜. )🥛 ʏᴜᴍᴍʏ ",
"𓂃☁︎ 𓂃𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही .-‘🚂-‘.ᯓᡣ𐭩______ 𓂃☁︎ 𓂃",
"˙✧˖°📷༘ ⋆｡° 𝐓ᴇʀʏ 𝐌ᴀ  𝐊ᴀ 𝐂ʜɪʟᴅ 𝐏ᴏʀɴ 𝐑ᴇᴄᴏʀᴅ 𝐇ᴏɢʏᴀ 𝐀ʙ 𝐓ᴏ 𝐒ɪᴅʜᴀ 𝐕ɪʀᴀʟ 𝐇ᴏɢᴀ 𝐘ᴇ ˙✧˖°📷༘ ⋆｡°",
"𓂃✍︎ 𝑵ʏ 𝑵ʏ 𝑨ʙ 𝑲ᴜᴄʜ 𝑵ʏ 𝑯ᴏ 𝑺ᴋᴛᴀ 𝑻ᴇʀɪ  𝑪ᴜᴅᴀɪ 𝑲ɪ 𝑺ᴄʀɪᴘᴛ 𝑨ʙ 𝑳ᴇᴀᴋ 𝑯ᴏᴋᴇ 𝑯ʏ 𝑴ᴀɴᴇɢɪ 𓂃✍︎",
"⋆⭒˚.⋆🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ⋆⭒˚.⋆🔭","तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）",
"𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜. ㅅ ͜. )🥛 ʏᴜᴍᴍʏ ",
"𓂃☁︎ 𓂃𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही .-‘🚂-‘.ᯓᡣ𐭩______ 𓂃☁︎ 𓂃",
"˙✧˖°📷༘ ⋆｡° 𝐓ᴇʀʏ 𝐌ᴀ  𝐊ᴀ 𝐂ʜɪʟᴅ 𝐏ᴏʀɴ 𝐑ᴇᴄᴏʀᴅ 𝐇ᴏɢʏᴀ 𝐀ʙ 𝐓ᴏ 𝐒ɪᴅʜᴀ 𝐕ɪʀᴀʟ 𝐇ᴏɢᴀ 𝐘ᴇ ˙✧˖°📷༘ ⋆｡°",
"𓂃✍︎ 𝑵ʏ 𝑵ʏ 𝑨ʙ 𝑲ᴜᴄʜ 𝑵ʏ 𝑯ᴏ 𝑺ᴋᴛᴀ 𝑻ᴇʀɪ  𝑪ᴜᴅᴀɪ 𝑲ɪ 𝑺ᴄʀɪᴘᴛ 𝑨ʙ 𝑳ᴇᴀᴋ 𝑯ᴏᴋᴇ 𝑯ʏ 𝑴ᴀɴᴇɢɪ 𓂃✍︎",
"⋆⭒˚.⋆🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ⋆⭒˚.⋆🔭","तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）",
"𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜. ㅅ ͜. )🥛 ʏᴜᴍᴍʏ ",
"𓂃☁︎ 𓂃𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही .-‘🚂-‘.ᯓᡣ𐭩______ 𓂃☁︎ 𓂃",
"˙✧˖°📷༘ ⋆｡° 𝐓ᴇʀʏ 𝐌ᴀ  𝐊ᴀ 𝐂ʜɪʟᴅ 𝐏ᴏʀɴ 𝐑ᴇᴄᴏʀᴅ 𝐇ᴏɢʏᴀ 𝐀ʙ 𝐓ᴏ 𝐒ɪᴅʜᴀ 𝐕ɪʀᴀʟ 𝐇ᴏɢᴀ 𝐘ᴇ ˙✧˖°📷༘ ⋆｡°",
"𓂃✍︎ 𝑵ʏ 𝑵ʏ 𝑨ʙ 𝑲ᴜᴄʜ 𝑵ʏ 𝑯ᴏ 𝑺ᴋᴛᴀ 𝑻ᴇʀɪ  𝑪ᴜᴅᴀɪ 𝑲ɪ 𝑺ᴄʀɪᴘᴛ 𝑨ʙ 𝑳ᴇᴀᴋ 𝑯ᴏᴋᴇ 𝑯ʏ 𝑴ᴀɴᴇɢɪ 𓂃✍︎",
"⋆⭒˚.⋆🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ⋆⭒˚.⋆🔭","तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）",
"𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜. ㅅ ͜. )🥛 ʏᴜᴍᴍʏ ",
"𓂃☁︎ 𓂃𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही .-‘🚂-‘.ᯓᡣ𐭩______ 𓂃☁︎ 𓂃",
"˙✧˖°📷༘ ⋆｡° 𝐓ᴇʀʏ 𝐌ᴀ  𝐊ᴀ 𝐂ʜɪʟᴅ 𝐏ᴏʀɴ 𝐑ᴇᴄᴏʀᴅ 𝐇ᴏɢʏᴀ 𝐀ʙ 𝐓ᴏ 𝐒ɪᴅʜᴀ 𝐕ɪʀᴀʟ 𝐇ᴏɢᴀ 𝐘ᴇ ˙✧˖°📷༘ ⋆｡°",
"𓂃✍︎ 𝑵ʏ 𝑵ʏ 𝑨ʙ 𝑲ᴜᴄʜ 𝑵ʏ 𝑯ᴏ 𝑺ᴋᴛᴀ 𝑻ᴇʀɪ  𝑪ᴜᴅᴀɪ 𝑲ɪ 𝑺ᴄʀɪᴘᴛ 𝑨ʙ 𝑳ᴇᴀᴋ 𝑯ᴏᴋᴇ 𝑯ʏ 𝑴ᴀɴᴇɢɪ 𓂃✍︎",
"⋆⭒˚.⋆🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ⋆⭒˚.⋆🔭" ]

flag_texts = [" ོ༘₊⁺🇮🇳 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 𝐍ɪᴋ 𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐈ɴᴅɪᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇮🇳 ₊⁺⋆.˚",
" ོ༘₊⁺🇯🇵 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝐍ɪᴋ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐉ᴀᴘᴀɴ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇯🇵 ₊⁺⋆. " ,
" ₊⁺🇺🇸 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝐍ɪᴋ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐒𝐀 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇺🇸 ₊⁺⋆.˚",
" ོ༘₊⁺🇬🇧 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝐍ɪᴋ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐊 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇬🇧 ₊⁺⋆.˚", 
" ོ༘₊⁺🇰🇷 ₊⁺⋆.˚𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ   𝗗𝗛𝗥𝗨𝗩 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐊ᴏʀᴇᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇰🇷 ₊⁺⋆.˚",
" ོ༘₊⁺🇩🇪 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝐍ɪᴋ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐆ᴇʀᴍᴀɴʏ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇩🇪 ₊⁺⋆.˚",
" ོ༘₊⁺🇫🇷 ₊⁺⋆.˚𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ   𝐍ɪᴋ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐅ʀᴀɴᴄᴇ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇫🇷 ₊⁺⋆.˚",
" ོ༘₊⁺🇮🇹 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝐍ɪᴋ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐈ᴛᴀʟʏ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇮🇹 ₊⁺⋆.˚",
" ོ༘₊⁺🇧🇷 ₊⁺⋆.˚𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ   𝐍ɪᴋ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐁ʀᴀᴢɪʟ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇧🇷 ₊⁺⋆.˚",
" ོ༘₊⁺🇨🇦 ₊⁺⋆.˚𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝐍ɪᴋ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐂ᴀɴᴀᴅᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇨🇦 ₊⁺⋆.˚"," ོ༘₊⁺🇮🇳 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 𝐍ɪᴋ 𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐈ɴᴅɪᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇮🇳 ₊⁺⋆.˚",
" ོ༘₊⁺🇯🇵 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝐍ɪᴋ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐉ᴀᴘᴀɴ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇯🇵 ₊⁺⋆. " ,
" ₊⁺🇺🇸 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝐍ɪᴋ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐒𝐀 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇺🇸 ₊⁺⋆.˚",
" ོ༘₊⁺🇬🇧 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝐍ɪᴋ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐊 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇬🇧 ₊⁺⋆.˚", 
" ོ༘₊⁺🇰🇷 ₊⁺⋆.˚𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ   𝐍ɪᴋ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐊ᴏʀᴇᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇰🇷 ₊⁺⋆.˚",
" ོ༘₊⁺🇩🇪 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝐍ɪᴋ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐆ᴇʀᴍᴀɴʏ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇩🇪 ₊⁺⋆.˚",
" ོ༘₊⁺🇫🇷 ₊⁺⋆.˚𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ   𝐍ɪᴋ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐅ʀᴀɴᴄᴇ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇫🇷 ₊⁺⋆.˚",
" ོ༘₊⁺🇮🇹 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ   𝐍ɪᴋ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐈ᴛᴀʟʏ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇮🇹 ₊⁺⋆.˚",
" ོ༘₊⁺🇧🇷 ₊⁺⋆.˚𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ   𝐍ɪᴋ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐁ʀᴀᴢɪʟ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇧🇷 ₊⁺⋆.˚",
" ོ༘₊⁺🇨🇦 ₊⁺⋆.˚𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  𝐍ɪᴋ 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐂ᴀɴᴀᴅᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇨🇦 ₊⁺⋆.˚"]

heart_replies = ["𓂃˖˳·˖ ִֶָ ⋆❤️͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚❤️ ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆🧡͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚🧡 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💛͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💛 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💚͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💚 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💙͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💙 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💜͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💜 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆🖤͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚🖤 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆🤍͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚🤍 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆🤎͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚🤎 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💖͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💖 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💗͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💗 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💓͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💓 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💞͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💞 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💕͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💕 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💘͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💘 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💝͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💝 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💟͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💟 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆❣️͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚❣️ ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆❤️‍🔥͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚❤️‍🔥 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆❤️‍🩹͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚❤️‍🩹 ݁˖⭑.ᐟ","𓂃˖˳·˖ ִֶָ ⋆❤️͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚❤️ ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆🧡͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚🧡 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💛͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💛 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💚͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💚 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💙͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💙 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💜͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💜 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆🖤͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚🖤 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆🤍͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚🤍 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆🤎͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚🤎 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💖͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💖 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💗͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💗 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💓͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💓 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💞͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💞 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💕͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💕 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💘͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💘 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💝͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💝 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💟͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💟 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆❣️͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚❣️ ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆❤️‍🔥͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚❤️‍🔥 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆❤️‍🩹͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚❤️‍🩹 ݁˖⭑.ᐟ"]

# ────────────────────────────────────────────────
#                   DECORATOR
# ────────────────────────────────────────────────
# ================= COMMAND REGISTRY =================

commands = {}

def register_cmd(name: str, needs_reply: bool = False, group_only: bool = False):

    def decorator(func):

        key = (name or "").lower().strip()

        if not key:
            raise ValueError("Command name cannot be empty")

        if key in commands:
            raise ValueError(f"Duplicate command registered: {key}")

        commands[key] = {
            "func": func,
            "needs_reply": bool(needs_reply),
            "group_only": bool(group_only),
        }

        return func

    return decorator


# ================= FASTGC ENGINE =================

async def fast_title_edit(chat_id, title):

    safe_title = (title or "").strip()[:255]

    if not safe_title:
        return False

    try:
        await bot(functions.channels.EditTitleRequest(
            channel=chat_id,
            title=safe_title
        ))
        return True

    except Exception:

        try:
            await bot(functions.messages.EditChatTitleRequest(
                chat_id=chat_id,
                title=safe_title
            ))
            return True

        except Exception as e:
            print(f"[FastGC] Title edit failed → {str(e)[:80]}")
            return False


async def gc_fast_loop(chat_id):

    try:

        while True:

            # ⭐ state validation
            if not FASTGC_STATE.get("active"):
                break

            template = FASTGC_STATE.get("template")
            if not template:
                break

            try:
                emoji = random.choice(GC_FAST_EMOJIS)
            except:
                emoji = "⚡"

            try:
                new_title = template.replace("{emoji}", emoji)
            except:
                await asyncio.sleep(2)
                continue

            ok = await fast_title_edit(chat_id, new_title)

            # ⭐ adaptive delay engine
            try:
                if ok:
                    await asyncio.sleep(max(1, GC_FAST_INTERVAL))
                else:
                    await asyncio.sleep(5)
            except:
                await asyncio.sleep(3)

    except asyncio.CancelledError:
        # ⭐ silent cancel safe
        return

    except Exception as e:
        print(f"[FastGC Loop Crash] → {str(e)[:80]}")

# ────────────────────────────────────────────────
#                   MENU (STYLISH) - UNCHANGED
# ────────────────────────────────────────────────
@register_cmd("menu")
async def cmd_menu(event, _):
    global menu_banner_msg
    menu = """╭━━━〔 👑 𝐍𝐈𝐊 𝐃𝐀𝐃𝐃𝐘 𝐕𝟑 @𝐍𝐢𝐤𝐤𝐤𝐰𝐚 👑 〕━━━╮
┃ ⚡ Owner : @Nikkkwa | Nik Daddy
┃ 🔥 Version : V3 FINAL GAAND FAAD
┃ 🛡️ Mode : Termux Single File | 24x7
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯

╭─〔 🎯 𝐌𝐀𝐈𝐍 〕─╮
│ • .alive → Status + uptime
│ • .ping → Speed
│ • .status → Full stats
│ • .help → Guide
│ • .id → ID grabber
╰────────────────╯

╭─〔 🔥 𝐑𝐀𝐈𝐃 𝐄𝐍𝐆𝐈𝐍𝐄 〕─╮
│ • .reply / .sreply
│ • .rr / .srr 🤣
│ • .flag / .sflag
│ • .hrr / .shrr 💜
│ • .replygod / .sgod
│ • .replynik <count> <text>
│ • .nik → Stop
│ • .raidstopall 🔴 Sab band
╰────────────────╯

╭─〔 💣 𝐒𝐏𝐀𝐌 〕─╮
│ • .spray / .dspray
│ • .spam <n> <text>
│ • .mspam <n> media spam
│ • .delayspam <delay> <n> <text>
│ • .purge / .purgeall
╰────────────────╯

╭─〔 🔇 𝐌𝐔𝐓𝐄 〕─╮
│ • .mute/.unmute • .gmute/.gunmute
│ • .mutelist • .lock/.unlock • .throw
╰────────────────╯

╭─〔 👑 𝐀𝐃𝐌𝐈𝐍 〕─╮
│ • .admins • .addadmin/.deladmin
│ • .addbots <n> (Nik bots)
│ • .fastgc set {emoji} / stop
╰────────────────╯

╭─〔 🎬 𝐒𝐓𝐎𝐑𝐘 10+ (NEW) 〕─╮
│ ❤️ Love : .love1 College .love2 Insta
│         .love3 Office .love4 Distance
│         .love5 Shaadi .lovestory Classic
│ 😂 Fun : .fun1 Chai .fun2 Exam
│        .fun3 Cricket .fun4 Udhaar
│        .fun5 Flirt .fun6 Thug .fun7 Mummy
│        .fun8 Nasha .dosti .attack
╰────────────────╯

╭─〔 😜 𝐌𝐀𝐒𝐓𝐈 〕─╮
│ • .bomb • .love • .gali <n>
│ • .hackstory • .tagall / .stop
│ • .heartrain • .hack
╰────────────────╯

╭─〔 👻 𝐕𝟑 𝐀𝐃𝐕𝐀𝐍𝐂𝐄𝐃 〕─╮
│ • .afk / .unafk • .ghost on/off
│ • .echo/.unecho • .ar/.sar
╰────────────────╯

╭─〔 💾 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 𝐒𝐀𝐕𝐄𝐑 🦫 〕─╮
│ • .setchannel @channel → Set
│ • .save (reply) → Channel save
│ • .savelist → List
│ • .fwd (reply) → Forward + WorkDone 🦫
│ • .delsave → Delete
╰────────────────╯

╭─〔 🛠️ 𝐓𝐎𝐎𝐋𝐒 〕─╮
│ • .tts .qrcode .fancy .style .emoji
│ • .calc .weather .ip .short .info
│ • .music .copy/.normal
╰────────────────╯

╭─〔 📝 𝐍𝐎𝐓𝐄𝐒 〕─╮
│ • .notesadd/.noteslist/.notesdelete
│ • .banner/.rembanner
╰────────────────╯

━━━━━━━━━━━━━━━━━━━━
✨ Powered by @Nikkkwa | Nik Daddy 👑
💾 Save → .fwd anywhere! 🦫
━━━━━━━━━━━━━━━━━━━━
"""
    await safe_edit(event, menu)
    if menu_banner_msg:
        chat_id, msg_id = menu_banner_msg
        try:
            msg = await bot.get_messages(chat_id, ids=msg_id)
            await bot.send_file(event.chat_id, file=msg.media, caption="👑 NIK LORD ENTERS @Nikkkwa ❤️‍🔥")
        except: pass

# ────────────────────────────────────────────────
#                   COMMANDS

# ────────────────────────────────────────────────

# Banner
@register_cmd("banner", needs_reply=True)
async def cmd_banner(event, _):
    global menu_banner_msg

    reply = await event.get_reply_message()

    # ─── MEDIA VALIDATION ENGINE ───
    if not reply:
        return await safe_edit(
            event,
            "❌ 𝐍ᴏ 𝐑ᴇᴘʟʏ\n👉 𝐑ᴇᴘʟʏ 𝐓ᴏ 𝐏ʜᴏᴛᴏ / 𝐕ɪᴅᴇᴏ"
        )

    if not reply.media:
        return await safe_edit(
            event,
            "❌ 𝐈ɴᴠᴀʟɪᴅ 𝐌ᴇᴅɪᴀ\n👉 𝐎ɴʟʏ 𝐏ʜᴏᴛᴏ / 𝐕ɪᴅᴇᴏ"
        )

    await safe_edit(
        event,
        "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐁ᴀɴɴᴇʀ...\n━━━━━━━━━━━━━━━"
    )

    try:
        # ─── FORWARD TRY FIRST (FAST PATH) ───
        try:
            saved = await reply.forward_to("me")
        except Exception:
            # ⭐ FORWARD RESTRICTED FALLBACK
            file = await reply.download_media(file=bytes)
            if not file:
                return await safe_edit(event,
                    "❌ 𝐌ᴇᴅɪᴀ 𝐃ᴏᴡɴʟᴏᴀᴅ 𝐅ᴀɪʟ"
                )

            bio = BytesIO(file)
            bio.name = "banner"
            saved = await bot.send_file("me", bio)

        menu_banner_msg = (saved.chat_id, saved.id)
        save_banner()

        text = (
            "🖼️ 𝐁ᴀɴɴᴇʀ 𝐒ᴇᴛ\n"
            "━━━━━━━━━━━━━━━\n"
            f"📌 𝐒ᴀᴠᴇᴅ 𝐈ᴅ → `{saved.id}`"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except FloodWaitError as fw:
        await safe_edit(event,
            f"⏳ 𝐅ʟᴏᴏᴅ 𝐖ᴀɪᴛ → {fw.seconds}s"
        )

    except RPCError as e:
        await safe_edit(event,
            f"❌ 𝐓ɢ 𝐄ʀʀ → `{str(e)[:40]}`"
        )

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐁ᴀɴɴᴇʀ 𝐄ʀʀ → `{str(e)[:50]}`"
        )


@register_cmd("rembanner")
async def cmd_rembanner(event, _):
    global menu_banner_msg

    if not menu_banner_msg:
        return await safe_edit(event,
            "⚠️ 𝐍ᴏ 𝐁ᴀɴɴᴇʀ 𝐒ᴇᴛ"
        )

    await safe_edit(
        event,
        "⚡ 𝐑ᴇᴍᴏᴠɪɴɢ 𝐁ᴀɴɴᴇʀ...\n━━━━━━━━━━━━━━━"
    )

    try:
        chat_id, msg_id = menu_banner_msg

        try:
            await bot.delete_messages(chat_id, [msg_id])
        except Exception:
            # ⭐ banner already manually deleted
            pass

        menu_banner_msg = None
        save_banner()

        text = (
            "🗑️ 𝐁ᴀɴɴᴇʀ 𝐑ᴇᴍᴏᴠᴇᴅ\n"
            "━━━━━━━━━━━━━━━"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except FloodWaitError as fw:
        await safe_edit(event,
            f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s"
        )

    except RPCError as e:
        await safe_edit(event,
            f"❌ 𝐓ɢ 𝐄ʀʀ → `{str(e)[:40]}`"
        )

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐑ᴇᴍᴏᴠᴇ 𝐄ʀʀ → `{str(e)[:50]}`"
        )
        
# Admin Commands (Updated)
@register_cmd("addadmin", needs_reply=True)
async def cmd_addadmin(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐕ᴀʟɪᴅ 𝐓ᴀʀɢᴇᴛ\n👉 𝐑ᴇᴘʟʏ / @username / ID"
            )

        await safe_edit(
            event,
            "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐀ᴅᴍɪɴ 𝐀ᴅᴅ...\n━━━━━━━━━━━━━━━"
        )

        added = []
        already = []
        skipped_owner = []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid == OWNER_ID:
                skipped_owner.append(str(uid))
                continue

            if uid in admins:
                already.append(str(uid))
            else:
                admins.add(uid)
                added.append(str(uid))

        try:
            save_admins()
        except Exception:
            pass

        parts = []

        if added:
            parts.append(
                f"✅ 𝐀ᴅᴍɪɴ 𝐀ᴅᴅᴇᴅ → `{', '.join(added)}`"
            )

        if already:
            parts.append(
                f"⚠️ 𝐀ʟʀᴇᴀᴅʏ 𝐀ᴅᴍɪɴ → `{', '.join(already)}`"
            )

        if skipped_owner:
            parts.append(
                f"👑 𝐎ᴡɴᴇʀ 𝐒ᴋɪᴘᴘᴇᴅ → `{', '.join(skipped_owner)}`"
            )

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇs 𝐌ᴀᴅᴇ")

        text = "\n".join(parts)

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except FloodWaitError as fw:
        await safe_edit(event,
            f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s"
        )
    except RPCError as e:
        await safe_edit(event,
            f"❌ 𝐓ɢ 𝐄ʀʀ → `{str(e)[:40]}`"
        )
    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐀ᴅᴍɪɴ 𝐀ᴅᴅ 𝐄ʀʀ → `{str(e)[:50]}`"
        )


@register_cmd("deladmin", needs_reply=True)
async def cmd_deladmin(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐕ᴀʟɪᴅ 𝐓ᴀʀɢᴇᴛ\n👉 𝐑ᴇᴘʟʏ / @username / ID"
            )

        await safe_edit(
            event,
            "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐀ᴅᴍɪɴ 𝐑ᴇᴍᴏᴠᴇ...\n━━━━━━━━━━━━━━━"
        )

        removed = []
        not_admin = []
        skipped_owner = []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid == OWNER_ID:
                skipped_owner.append(str(uid))
                continue

            if uid in admins:
                admins.remove(uid)
                removed.append(str(uid))
            else:
                not_admin.append(str(uid))

        try:
            save_admins()
        except Exception:
            pass

        parts = []

        if removed:
            parts.append(
                f"🗑️ 𝐀ᴅᴍɪɴ 𝐑ᴇᴍᴏᴠᴇᴅ → `{', '.join(removed)}`"
            )

        if not_admin:
            parts.append(
                f"⚠️ 𝐍ᴏᴛ 𝐀ᴅᴍɪɴ → `{', '.join(not_admin)}`"
            )

        if skipped_owner:
            parts.append(
                f"👑 𝐎ᴡɴᴇʀ 𝐏ʀᴏᴛᴇᴄᴛᴇᴅ → `{', '.join(skipped_owner)}`"
            )

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇs 𝐌ᴀᴅᴇ")

        text = "\n".join(parts)

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except FloodWaitError as fw:
        await safe_edit(event,
            f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s"
        )
    except RPCError as e:
        await safe_edit(event,
            f"❌ 𝐓ɢ 𝐄ʀʀ → `{str(e)[:40]}`"
        )
    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐀ᴅᴍɪɴ 𝐑ᴇᴍᴏᴠᴇ 𝐄ʀʀ → `{str(e)[:50]}`"
        )


@register_cmd("admins")
async def cmd_admins(event, _):
    try:
        await safe_edit(
            event,
            "⚡ 𝐅ᴇᴛᴄʜɪɴɢ 𝐀ᴅᴍɪɴ 𝐋ɪsᴛ...\n━━━━━━━━━━━━━━━"
        )

        if admins:
            admin_list = "\n".join(
                f"• `{a}`" for a in sorted(admins)
            )
        else:
            admin_list = "⚠️ 𝐍ᴏ 𝐄xᴛʀᴀ 𝐀ᴅᴍɪɴs"

        txt = (
            "👑 𝐀ᴅᴍɪɴ 𝐋ɪsᴛ\n"
            "━━━━━━━━━━━━━━━\n"
            f"👑 𝐎ᴡɴᴇʀ → `{OWNER_ID}`\n\n"
            f"{admin_list}\n\n"
            f"📊 𝐓ᴏᴛᴀʟ → `{len(admins)}`"
        )

        await safe_edit(event, txt)

    except FloodWaitError as fw:
        await safe_edit(event,
            f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s"
        )
    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐀ᴅᴍɪɴ 𝐋ɪsᴛ 𝐄ʀʀ → `{str(e)[:50]}`"
        )

# Basic Commands (Unchanged)
@register_cmd("ping")
async def cmd_ping(event, _):
    try:
        t0 = time.perf_counter()

        # ─── MESSAGE DISPATCH SAFE ───
        try:
            if event.out:
                msg = await event.edit("🏓 𝐏ɪɴɢ...")
            else:
                msg = await event.reply("🏓 𝐏ɪɴɢ...")
        except:
            msg = None

        t1 = time.perf_counter()
        ms = round((t1 - t0) * 1000)

        # ─── RESPONSE EDIT SAFE ───
        try:
            if msg:
                await msg.edit(f"🏓 𝐏ᴏɴɢ → `{ms} ms`")
            else:
                await event.reply(f"🏓 𝐏ᴏɴɢ → `{ms} ms`")
        except:
            pass

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐏ɪɴɢ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("status")
async def cmd_status(event, _):
    try:
        now = time.time()

        # ─── START TIME CORRUPTION SAFE ───
        try:
            uptime = int(now - START_TIME)
            if uptime < 0:
                uptime = 0
        except:
            uptime = 0

        # ─── ADMIN STORAGE SAFE ───
        try:
            admin_count = len(admins)
        except:
            admin_count = 0

        txt = (
            "✅ 𝐔sᴇʀʙᴏᴛ 𝐒ᴛᴀᴛᴜs\n"
            "━━━━━━━━━━━━━━━\n"
            f"⏱️ 𝐔ᴘᴛɪᴍᴇ → `{uptime}s`\n"
            f"👑 𝐀ᴅᴍɪɴs → `{admin_count}`\n"
            f"⚙️ 𝐌ᴏᴅᴇ → `Operational`"
        )

        try:
            if event.out:
                await safe_edit(event, txt)
            else:
                await event.reply(txt)
        except:
            pass

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐒ᴛᴀᴛᴜs 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("flip")
async def cmd_flip(event, _):
    try:
        # ─── RANDOM SAFE ───
        try:
            result = random.choice(["🪙 𝐇ᴇᴀᴅs", "🪙 𝐓ᴀɪʟs"])
        except:
            result = "🪙 𝐇ᴇᴀᴅs"

        text = (
            "🎲 𝐂ᴏɪɴ 𝐅ʟɪᴘ\n"
            "━━━━━━━━━━━━━━━\n"
            f"👉 𝐑ᴇsᴜʟᴛ → {result}"
        )

        try:
            if event.out:
                await safe_edit(event, text)
            else:
                await event.reply(text)
        except:
            pass

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐅ʟɪᴘ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("dice")
async def cmd_dice(event, _):
    try:
        # ─── RANDOM SAFE ───
        try:
            num = random.randint(1, 6)
        except:
            num = 1

        text = (
            "🎲 𝐃ɪᴄᴇ 𝐑ᴏʟʟ\n"
            "━━━━━━━━━━━━━━━\n"
            f"👉 𝐑ᴇsᴜʟᴛ → `{num}`"
        )

        try:
            if event.out:
                await safe_edit(event, text)
            else:
                await event.reply(text)
        except:
            pass

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐃ɪᴄᴇ 𝐄ʀʀ → `{str(e)[:40]}`")

# Raid Commands
@register_cmd("reply", needs_reply=True)
async def cmd_reply(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(event,
                "❌ 𝐍ᴏ 𝐕ᴀʟɪᴅ 𝐓ᴀʀɢᴇᴛ"
            )

        await safe_edit(event,
            "⚡ 𝐄ɴᴀʙʟɪɴɢ 𝐑ᴇᴘʟʏ 𝐑ᴀɪᴅ (𝐆ʟᴏʙᴀʟ)...\n━━━━━━━━━━━━━━━"
        )

        added, already = [], []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid in reply_users:
                already.append(str(uid))
            else:
                reply_users.add(uid)
                added.append(str(uid))

        parts = []

        if added:
            parts.append(f"🔥 𝐑ᴇᴘʟʏ 𝐑ᴀɪᴅ 𝐎ɴ → `{', '.join(added)}`")

        if already:
            parts.append(f"⚠️ 𝐀ʟʀᴇᴀᴅʏ 𝐀ᴄᴛɪᴠᴇ → `{', '.join(already)}`")

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

        msg = "\n".join(parts)

        if event.out:
            await safe_edit(event, msg)
        else:
            await event.reply(msg)

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐑ᴇᴘʟʏ 𝐑ᴀɪᴅ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("rr", needs_reply=True)
async def cmd_rr(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(event,
                "❌ 𝐍ᴏ 𝐕ᴀʟɪᴅ 𝐓ᴀʀɢᴇᴛ"
            )

        await safe_edit(event,
            "⚡ 𝐄ɴᴀʙʟɪɴɢ 𝐑𝐑 𝐑ᴀɪᴅ (𝐆ʟᴏʙᴀʟ)...\n━━━━━━━━━━━━━━━"
        )

        added, already = [], []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid in rr_users:
                already.append(str(uid))
            else:
                rr_users.add(uid)
                added.append(str(uid))

        parts = []

        if added:
            parts.append(f"⚡ 𝐑𝐑 𝐎ɴ → `{', '.join(added)}`")

        if already:
            parts.append(f"⚠️ 𝐀ʟʀᴇᴀᴅʏ → `{', '.join(already)}`")

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

        msg = "\n".join(parts)

        if event.out:
            await safe_edit(event, msg)
        else:
            await event.reply(msg)

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐑𝐑 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("flag", needs_reply=True)
async def cmd_flag(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(event,
                "❌ 𝐍ᴏ 𝐕ᴀʟɪᴅ 𝐓ᴀʀɢᴇᴛ"
            )

        await safe_edit(event,
            "⚡ 𝐄ɴᴀʙʟɪɴɢ 𝐅ʟᴀɢ 𝐑ᴀɪᴅ (𝐆ʟᴏʙᴀʟ)...\n━━━━━━━━━━━━━━━"
        )

        added, already = [], []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid in flag_users:
                already.append(str(uid))
            else:
                flag_users.add(uid)
                added.append(str(uid))

        parts = []

        if added:
            parts.append(f"🌊 𝐅ʟᴀɢ 𝐎ɴ → `{', '.join(added)}`")

        if already:
            parts.append(f"⚠️ 𝐀ʟʀᴇᴀᴅʏ → `{', '.join(already)}`")

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

        msg = "\n".join(parts)

        if event.out:
            await safe_edit(event, msg)
        else:
            await event.reply(msg)

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐅ʟᴀɢ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("hrr", needs_reply=True)
async def cmd_hrr(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(event,
                "❌ 𝐍ᴏ 𝐕ᴀʟɪᴅ 𝐓ᴀʀɢᴇᴛ"
            )

        await safe_edit(event,
            "⚡ 𝐄ɴᴀʙʟɪɴɢ 𝐇ᴇᴀʀᴛ 𝐑ᴀɪᴅ (𝐆ʟᴏʙᴀʟ)...\n━━━━━━━━━━━━━━━"
        )

        added, already = [], []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid in hrr_users:
                already.append(str(uid))
            else:
                hrr_users.add(uid)
                added.append(str(uid))

        parts = []

        if added:
            parts.append(f"💜 𝐇ᴇᴀʀᴛ 𝐑ᴀɪᴅ → `{', '.join(added)}`")

        if already:
            parts.append(f"⚠️ 𝐀ʟʀᴇᴀᴅʏ → `{', '.join(already)}`")

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

        msg = "\n".join(parts)

        if event.out:
            await safe_edit(event, msg)
        else:
            await event.reply(msg)

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐇𝐑𝐑 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("replygod", needs_reply=True)
async def cmd_replygod(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(event,
                "❌ 𝐍ᴏ 𝐕ᴀʟɪᴅ 𝐓ᴀʀɢᴇᴛ"
            )

        await safe_edit(event,
            "⚡ 𝐄ɴᴀʙʟɪɴɢ 𝐑ᴇᴘʟʏ𝐆ᴏᴅ (𝐆ʟᴏʙᴀʟ)...\n━━━━━━━━━━━━━━━"
        )

        added, already = [], []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid in replygod_users:
                already.append(str(uid))
            else:
                replygod_users.add(uid)
                added.append(str(uid))

        parts = []

        if added:
            parts.append(f"💥 𝐑ᴇᴘʟʏ𝐆ᴏᴅ → `{', '.join(added)}`")

        if already:
            parts.append(f"⚠️ 𝐀ʟʀᴇᴀᴅʏ → `{', '.join(already)}`")

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

        msg = "\n".join(parts)

        if event.out:
            await safe_edit(event, msg)
        else:
            await event.reply(msg)

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐑𝐆 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("replyyorichi", needs_reply=True)
async def cmd_replyyorichi(event, arg):
    try:
        if not arg or len(arg.split()) < 2:
            return await safe_edit(event,
                "❌ 𝐈ɴᴠᴀʟɪᴅ 𝐅ᴏʀᴍᴀᴛ\n👉 `.replyyorichi <text> <count>`"
            )

        text, count = arg.rsplit(" ", 1)

        try:
            count = int(count)
        except:
            return await safe_edit(event,
                "❌ 𝐂ᴏᴜɴᴛ 𝐌ᴜsᴛ 𝐁ᴇ 𝐍ᴜᴍʙᴇʀ"
            )

        if count <= 0:
            count = 1
        if count > 100:
            count = 100

        targets = await get_targets(event, "")

        if not targets:
            return await safe_edit(event,
                "❌ 𝐍ᴏ 𝐕ᴀʟɪᴅ 𝐓ᴀʀɢᴇᴛ"
            )

        await safe_edit(event,
            "⚡ 𝐒ᴇᴛᴛɪɴɢ 𝐑ᴇᴘʟʏ𝐑ɪᴛɪᴋ (𝐆ʟᴏʙᴀʟ)...\n━━━━━━━━━━━━━━━"
        )

        added, overridden = [], []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid in replyyorichi_users:
                overridden.append(str(uid))

            replyyorichi_users[uid] = {
                "text": text,
                "count": count
            }
            added.append(str(uid))

        parts = []

        if added:
            parts.append(f"☄️ 𝐑𝐘 → `{', '.join(added)}` × `{count}`")

        if overridden:
            parts.append(f"⚠️ 𝐎ᴠᴇʀʀɪᴅᴇ → `{', '.join(overridden)}`")

        msg = "\n".join(parts)

        if event.out:
            await safe_edit(event, msg)
        else:
            await event.reply(msg)

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐑𝐘 𝐄ʀʀ → `{str(e)[:40]}`")

@register_cmd("spray")
async def cmd_spray(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐓ᴇxᴛ 𝐆ɪᴠᴇɴ\n"
                "👉 𝐔sᴀɢᴇ: `.spray <text>`"
            )

        chat = event.chat_id

        # ─── HUGE TEXT GUARD ───
        if len(arg) > 4000:
            arg = arg[:4000]

        # ─── ALREADY ACTIVE GUARD ───
        if chat in spray_tasks and not spray_tasks[chat].done():
            msg = "⚠️ 𝐒ᴘʀᴀʏ 𝐀ʟʀᴇᴀᴅʏ 𝐀ᴄᴛɪᴠᴇ"
            if event.out:
                return await safe_edit(event, msg)
            else:
                return await event.reply(msg)

        await safe_edit(
            event,
            "⚡ 𝐈ɴɪᴛɪᴀʟɪᴢɪɴɢ 𝐒ᴘʀᴀʏ...\n━━━━━━━━━━━━━━━"
        )

        async def spray_loop():
            try:
                while True:
                    # stop condition
                    if chat not in spray_tasks:
                        break

                    try:
                        await bot.send_message(chat, arg)
                    except FloodWaitError as fw:
                        await asyncio.sleep(fw.seconds)
                    except RPCError:
                        # permission lost / banned / readonly
                        spray_tasks.pop(chat, None)
                        break
                    except Exception:
                        # network / msg send fail
                        await asyncio.sleep(2)

                    await asyncio.sleep(SPRAY_DELAY)

            except asyncio.CancelledError:
                pass
            finally:
                spray_tasks.pop(chat, None)

        spray_tasks[chat] = asyncio.create_task(spray_loop())

        text = (
            "💣 𝐒ᴘʀᴀʏ 𝐒ᴛᴀʀᴛᴇᴅ\n"
            "━━━━━━━━━━━━━━━\n"
            f"📢 𝐓ᴇxᴛ → `{arg[:40]}`"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐒ᴘʀᴀʏ 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("dspray")
async def cmd_dspray(event, _):
    try:
        chat = event.chat_id

        if chat not in spray_tasks:
            msg = "⚠️ 𝐍ᴏ 𝐀ᴄᴛɪᴠᴇ 𝐒ᴘʀᴀʏ"
            if event.out:
                return await safe_edit(event, msg)
            else:
                return await event.reply(msg)

        await safe_edit(
            event,
            "⚡ 𝐒ᴛᴏᴘᴘɪɴɢ 𝐒ᴘʀᴀʏ...\n━━━━━━━━━━━━━━━"
        )

        try:
            spray_tasks[chat].cancel()
        except:
            pass

        spray_tasks.pop(chat, None)

        text = (
            "🛑 𝐒ᴘʀᴀʏ 𝐒ᴛᴏᴘᴘᴇᴅ\n"
            "━━━━━━━━━━━━━━━"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐃𝐒ᴘʀᴀʏ 𝐄ʀʀ → `{str(e)[:40]}`"
        )

# Mute Commands
@register_cmd("mute", needs_reply=True)
async def cmd_mute(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ\n👉 `.mute` (reply / @username / id)"
            )

        await safe_edit(
            event,
            "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐌ᴜᴛᴇ...\n━━━━━━━━━━━━━━━"
        )

        added, already = [], []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid in muted_users:
                already.append(str(uid))
            else:
                muted_users.add(uid)
                added.append(str(uid))

        parts = []

        if added:
            parts.append(f"🔇 𝐌ᴜᴛᴇ → `{', '.join(added)}`")

        if already:
            parts.append(f"⚠️ 𝐀ʟʀᴇᴀᴅʏ 𝐌ᴜᴛᴇᴅ → `{', '.join(already)}`")

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

        msg = "\n".join(parts)

        if event.out:
            await safe_edit(event, msg)
        else:
            await event.reply(msg)

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐌ᴜᴛᴇ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("unmute", needs_reply=True)
async def cmd_unmute(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ\n👉 `.unmute` (reply / @username / id)"
            )

        await safe_edit(
            event,
            "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐔ɴᴍᴜᴛᴇ...\n━━━━━━━━━━━━━━━"
        )

        removed, not_muted = [], []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid in muted_users:
                muted_users.remove(uid)
                removed.append(str(uid))
            else:
                not_muted.append(str(uid))

        parts = []

        if removed:
            parts.append(f"🗣️ 𝐔ɴᴍᴜᴛᴇ → `{', '.join(removed)}`")

        if not_muted:
            parts.append(f"⚠️ 𝐍ᴏᴛ 𝐌ᴜᴛᴇᴅ → `{', '.join(not_muted)}`")

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

        msg = "\n".join(parts)

        if event.out:
            await safe_edit(event, msg)
        else:
            await event.reply(msg)

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐔ɴᴍᴜᴛᴇ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("gmute", needs_reply=True)
async def cmd_gmute(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ\n👉 `.gmute` (reply / @username / id)"
            )

        await safe_edit(
            event,
            "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐆ᴍᴜᴛᴇ...\n━━━━━━━━━━━━━━━"
        )

        added, already = [], []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid in global_muted:
                already.append(str(uid))
            else:
                global_muted.add(uid)
                added.append(str(uid))

        parts = []

        if added:
            parts.append(f"🔕 𝐆ᴍᴜᴛᴇ → `{', '.join(added)}`")

        if already:
            parts.append(f"⚠️ 𝐀ʟʀᴇᴀᴅʏ 𝐆ᴍᴜᴛᴇᴅ → `{', '.join(already)}`")

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

        msg = "\n".join(parts)

        if event.out:
            await safe_edit(event, msg)
        else:
            await event.reply(msg)

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐆ᴍᴜᴛᴇ 𝐄ʀʀ → `{str(e)[:40]}`")


@register_cmd("gunmute", needs_reply=True)
async def cmd_gunmute(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ\n👉 `.gunmute` (reply / @username / id)"
            )

        await safe_edit(
            event,
            "⚡ 𝐏ʀᴏᴄᴇssɪɴɢ 𝐆ᴜɴᴍᴜᴛᴇ...\n━━━━━━━━━━━━━━━"
        )

        removed, not_muted = [], []

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid in global_muted:
                global_muted.remove(uid)
                removed.append(str(uid))
            else:
                not_muted.append(str(uid))

        parts = []

        if removed:
            parts.append(f"🔊 𝐆ᴜɴᴍᴜᴛᴇ → `{', '.join(removed)}`")

        if not_muted:
            parts.append(f"⚠️ 𝐍ᴏᴛ 𝐆ᴍᴜᴛᴇᴅ → `{', '.join(not_muted)}`")

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

        msg = "\n".join(parts)

        if event.out:
            await safe_edit(event, msg)
        else:
            await event.reply(msg)

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event, f"❌ 𝐆𝐔𝐍𝐌𝐔𝐓𝐄 𝐄ʀʀ → `{str(e)[:40]}`")

# Group Mod
@register_cmd("purge")
async def cmd_purge(event, arg):
    try:
        try:
            count = int(arg) if arg else 50
        except:
            count = 50

        # ─── HARD LIMIT ENGINE ───
        if count < 1:
            count = 1
        if count > 200:
            count = 200

        await safe_edit(
            event,
            "⚡ 𝐏ᴜʀɢɪɴɢ 𝐌ᴇssᴀɢᴇs...\n━━━━━━━━━━━━━━━"
        )

        msgs = []
        async for m in bot.iter_messages(event.chat_id, limit=count + 1):
            msgs.append(m.id)

        if not msgs:
            return await safe_edit(event,
                "⚠️ 𝐍ᴏ 𝐌ᴇssᴀɢᴇs 𝐅ᴏᴜɴᴅ"
            )

        # ─── SAFE DELETE BATCH ───
        try:
            await bot.delete_messages(event.chat_id, msgs)
        except FloodWaitError as fw:
            await asyncio.sleep(fw.seconds)
            await bot.delete_messages(event.chat_id, msgs)
        except RPCError:
            # readonly / no rights / protected msgs
            pass

        text = (
            "🧹 𝐏ᴜʀɢᴇ 𝐂ᴏᴍᴘʟᴇᴛᴇ\n"
            "━━━━━━━━━━━━━━━\n"
            f"🗑️ 𝐃ᴇʟᴇᴛᴇᴅ → `{max(len(msgs)-1,0)}`"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐏ᴜʀɢᴇ 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("throw", needs_reply=True, group_only=True)
async def cmd_throw(event, arg):
    try:
        targets = await get_targets(event, arg)

        if not targets:
            return await safe_edit(event,
                "❌ 𝐍ᴏ 𝐓ᴀʀɢᴇᴛ"
            )

        # ─── ADMIN CHECK SAFE ───
        try:
            perms = await bot.get_permissions(event.chat_id, 'me')
            if not perms.is_admin:
                return await safe_edit(event,
                    "❌ 𝐍ᴏ 𝐀ᴅᴍɪɴ 𝐑ɪɢʜᴛs"
                )
        except:
            return await safe_edit(event,
                "❌ 𝐏ᴇʀᴍ𝐢ssɪᴏɴ 𝐂ʜᴇᴄᴋ 𝐅ᴀɪʟ"
            )

        await safe_edit(
            event,
            "⚡ 𝐊ɪᴄᴋɪɴɢ 𝐓ᴀʀɢᴇᴛs...\n━━━━━━━━━━━━━━━"
        )

        kicked, failed, skipped = [], [], []

        me = await bot.get_me()

        for uid in targets:
            try:
                uid = int(uid)
            except:
                continue

            if uid == me.id:
                skipped.append(str(uid))
                continue

            try:
                await bot.kick_participant(event.chat_id, uid)
                kicked.append(str(uid))
            except:
                failed.append(str(uid))

        parts = []

        if kicked:
            parts.append(f"👞 𝐊ɪᴄᴋᴇᴅ → `{', '.join(kicked)}`")

        if failed:
            parts.append(f"⚠️ 𝐅ᴀɪʟᴇᴅ → `{', '.join(failed)}`")

        if skipped:
            parts.append(f"👑 𝐒ᴇʟғ 𝐒ᴋɪᴘ → `{', '.join(skipped)}`")

        if not parts:
            parts.append("❌ 𝐍ᴏ 𝐀ᴄᴛɪᴏɴ")

        msg = "\n".join(parts)

        if event.out:
            await safe_edit(event, msg)
        else:
            await event.reply(msg)

    except FloodWaitError as fw:
        await safe_edit(event, f"⏳ 𝐅ʟᴏᴏᴅ → {fw.seconds}s")
    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐓ʜʀᴏᴡ 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("sreply")
async def cmd_sreply(event, arg):
    try:
        targets = await get_targets(event, arg)

        if targets:
            stopped, not_active = [], []

            for uid in targets:
                try:
                    uid = int(uid)
                except:
                    continue

                if uid in reply_users:
                    reply_users.discard(uid)
                    stopped.append(str(uid))
                else:
                    not_active.append(str(uid))

            parts = []

            if stopped:
                parts.append(f"🛑 𝐑ᴇᴘʟʏ 𝐎ғғ → `{', '.join(stopped)}`")

            if not_active:
                parts.append(f"⚠️ 𝐍ᴏᴛ 𝐀ᴄᴛɪᴠᴇ → `{', '.join(not_active)}`")

            if not parts:
                parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

            text = "\n".join(parts)

        else:
            reply_users.clear()
            text = (
                "🛑 𝐑ᴇᴘʟʏ 𝐎ғғ\n"
                "━━━━━━━━━━━━━━━\n"
                "👉 𝐀ʟʟ 𝐔sᴇʀs"
            )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐒𝐑𝐄𝐏𝐋𝐘 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("srr")
async def cmd_srr(event, arg):
    try:
        targets = await get_targets(event, arg)

        if targets:
            stopped, not_active = [], []

            for uid in targets:
                try:
                    uid = int(uid)
                except:
                    continue

                if uid in rr_users:
                    rr_users.discard(uid)
                    stopped.append(str(uid))
                else:
                    not_active.append(str(uid))

            parts = []

            if stopped:
                parts.append(f"🛑 𝐑𝐑 𝐎ғғ → `{', '.join(stopped)}`")

            if not_active:
                parts.append(f"⚠️ 𝐍ᴏᴛ 𝐀ᴄᴛɪᴠᴇ → `{', '.join(not_active)}`")

            if not parts:
                parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

            text = "\n".join(parts)

        else:
            rr_users.clear()

            text = (
                "🛑 𝐑𝐑 𝐎ғғ\n"
                "━━━━━━━━━━━━━━━\n"
                "👉 𝐀ʟʟ 𝐔sᴇʀs"
            )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐒𝐑𝐑 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("sflag")
async def cmd_sflag(event, arg):
    try:
        targets = await get_targets(event, arg)

        if targets:
            stopped, not_active = [], []

            for uid in targets:
                try:
                    uid = int(uid)
                except:
                    continue

                if uid in flag_users:
                    flag_users.discard(uid)
                    stopped.append(str(uid))
                else:
                    not_active.append(str(uid))

            parts = []

            if stopped:
                parts.append(f"🛑 𝐅ʟᴀɢ 𝐎ғғ → `{', '.join(stopped)}`")

            if not_active:
                parts.append(f"⚠️ 𝐍ᴏᴛ 𝐀ᴄᴛɪᴠᴇ → `{', '.join(not_active)}`")

            if not parts:
                parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

            text = "\n".join(parts)

        else:
            flag_users.clear()

            text = (
                "🛑 𝐅ʟᴀɢ 𝐎ғғ\n"
                "━━━━━━━━━━━━━━━\n"
                "👉 𝐀ʟʟ 𝐔sᴇʀs"
            )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐒𝐅𝐋𝐀𝐆 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("shrr")
async def cmd_shrr(event, arg):
    try:
        targets = await get_targets(event, arg)

        if targets:
            await safe_edit(
                event,
                "⚡ 𝐃ɪsᴀʙʟɪɴɢ 𝐇ᴇᴀʀᴛ 𝐑ᴀɪᴅ (𝐆ʟᴏʙᴀʟ)...\n━━━━━━━━━━━━━━━"
            )

            stopped, not_active = [], []

            for uid in targets:
                try:
                    uid = int(uid)
                except:
                    continue

                if uid in hrr_users:
                    hrr_users.discard(uid)
                    stopped.append(str(uid))
                else:
                    not_active.append(str(uid))

            parts = []

            if stopped:
                parts.append(
                    f"🛑 𝐇ᴇᴀʀᴛ 𝐎ғғ → `{', '.join(stopped)}`"
                )

            if not_active:
                parts.append(
                    f"⚠️ 𝐍ᴏᴛ 𝐀ᴄᴛɪᴠᴇ → `{', '.join(not_active)}`"
                )

            if not parts:
                parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

            text = "\n".join(parts)

        else:
            hrr_users.clear()

            text = (
                "🛑 𝐇ᴇᴀʀᴛ 𝐎ғғ\n"
                "━━━━━━━━━━━━━━━\n"
                "👉 𝐀ʟʟ 𝐔sᴇʀs"
            )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐒𝐇𝐑𝐑 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("sgod")
async def cmd_sgod(event, arg):
    try:
        targets = await get_targets(event, arg)

        if targets:
            await safe_edit(
                event,
                "⚡ 𝐃ɪsᴀʙʟɪɴɢ 𝐑ᴇᴘʟʏ𝐆ᴏᴅ (𝐆ʟᴏʙᴀʟ)...\n━━━━━━━━━━━━━━━"
            )

            stopped, not_active = [], []

            for uid in targets:
                try:
                    uid = int(uid)
                except:
                    continue

                if uid in replygod_users:
                    replygod_users.discard(uid)
                    stopped.append(str(uid))
                else:
                    not_active.append(str(uid))

            parts = []

            if stopped:
                parts.append(
                    f"🛑 𝐑𝐆 𝐎ғғ → `{', '.join(stopped)}`"
                )

            if not_active:
                parts.append(
                    f"⚠️ 𝐍ᴏᴛ 𝐀ᴄᴛɪᴠᴇ → `{', '.join(not_active)}`"
                )

            if not parts:
                parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

            text = "\n".join(parts)

        else:
            replygod_users.clear()

            text = (
                "🛑 𝐑𝐆 𝐎ғғ\n"
                "━━━━━━━━━━━━━━━\n"
                "👉 𝐀ʟʟ 𝐔sᴇʀs"
            )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐒𝐆𝐎𝐃 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("syorichi")
async def cmd_syorichi(event, arg):
    try:
        targets = await get_targets(event, arg)

        if targets:
            await safe_edit(
                event,
                "⚡ 𝐃ɪsᴀʙʟɪɴɢ 𝐑𝐘 (𝐆ʟᴏʙᴀʟ)...\n━━━━━━━━━━━━━━━"
            )

            stopped, not_active = [], []

            for uid in targets:
                try:
                    uid = int(uid)
                except:
                    continue

                if uid in replyyorichi_users:
                    replyyorichi_users.pop(uid, None)
                    stopped.append(str(uid))
                else:
                    not_active.append(str(uid))

            parts = []

            if stopped:
                parts.append(
                    f"🛑 𝐑𝐘 𝐎ғғ → `{', '.join(stopped)}`"
                )

            if not_active:
                parts.append(
                    f"⚠️ 𝐍ᴏᴛ 𝐀ᴄᴛɪᴠᴇ → `{', '.join(not_active)}`"
                )

            if not parts:
                parts.append("❌ 𝐍ᴏ 𝐂ʜᴀɴɢᴇ")

            text = "\n".join(parts)

        else:
            replyyorichi_users.clear()

            text = (
                "🛑 𝐑𝐘 𝐎ғғ\n"
                "━━━━━━━━━━━━━━━\n"
                "👉 𝐀ʟʟ 𝐔sᴇʀs"
            )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐒𝐘𝐎𝐑𝐈𝐂𝐇𝐈 𝐄ʀʀ → `{str(e)[:40]}`"
        )

# Lock / Unlock
@register_cmd("lock", group_only=True)
async def cmd_lock(event, _):
    try:
        chat = event.chat_id

        # ─── ADMIN CHECK ───
        try:
            perms = await bot.get_permissions(chat, 'me')
            if not perms.is_admin:
                return await safe_edit(event,
                    "❌ 𝐍ᴏ 𝐀ᴅᴍɪɴ 𝐑ɪɢʜᴛs"
                )
        except:
            pass

        if chat in group_locks:
            msg = "⚠️ 𝐆ʀᴏᴜᴘ 𝐀ʟʀᴇᴀᴅʏ 𝐋ᴏᴄᴋᴇᴅ"
            if event.out:
                return await safe_edit(event, msg)
            else:
                return await event.reply(msg)

        await safe_edit(
            event,
            "⚡ 𝐀ᴘᴘʟʏɪɴɢ 𝐋ᴏᴄᴋ...\n━━━━━━━━━━━━━━━"
        )

        group_locks.add(chat)

        text = (
            "🔒 𝐆ʀᴏᴜᴘ 𝐋ᴏᴄᴋᴇᴅ\n"
            "━━━━━━━━━━━━━━━\n"
            "🚫 𝐍ᴏɴ-𝐀ᴅᴍɪɴ 𝐌ᴇssᴀɢᴇs 𝐁ʟᴏᴄᴋᴇᴅ"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐋ᴏᴄᴋ 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("unlock", group_only=True)
async def cmd_unlock(event, _):
    try:
        chat = event.chat_id

        # ─── ADMIN CHECK ───
        try:
            perms = await bot.get_permissions(chat, 'me')
            if not perms.is_admin:
                return await safe_edit(event,
                    "❌ 𝐍ᴏ 𝐀ᴅᴍɪɴ 𝐑ɪɢʜᴛs"
                )
        except:
            pass

        if chat not in group_locks:
            msg = "⚠️ 𝐆ʀᴏᴜᴘ 𝐀ʟʀᴇᴀᴅʏ 𝐔ɴʟᴏᴄᴋᴇᴅ"
            if event.out:
                return await safe_edit(event, msg)
            else:
                return await event.reply(msg)

        await safe_edit(
            event,
            "⚡ 𝐑ᴇᴍᴏᴠɪɴɢ 𝐋ᴏᴄᴋ...\n━━━━━━━━━━━━━━━"
        )

        group_locks.discard(chat)

        text = (
            "🔓 𝐆ʀᴏᴜᴘ 𝐔ɴʟᴏᴄᴋᴇᴅ\n"
            "━━━━━━━━━━━━━━━\n"
            "✅ 𝐌ᴇssᴀɢɪɴɢ 𝐑ᴇsᴛᴏʀᴇᴅ"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐔ɴʟᴏᴄᴋ 𝐄ʀʀ → `{str(e)[:40]}`"
        )


# ───────── AUTO REACT ─────────

@register_cmd("ar")
async def cmd_ar(event, arg):
    global auto_react_emoji

    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐄ᴍᴏᴊɪ\n👉 `.ar <emoji>`"
            )

        emoji = arg.strip()

        # ─── EMOJI SANITY GUARD ───
        if len(emoji) > 8:
            return await safe_edit(event,
                "❌ 𝐈ɴᴠᴀʟɪᴅ 𝐄ᴍᴏᴊɪ"
            )

        if auto_react_emoji == emoji:
            msg = f"⚠️ 𝐀ʀ 𝐀ʟʀᴇᴀᴅʏ → {emoji}"
            if event.out:
                return await safe_edit(event, msg)
            else:
                return await event.reply(msg)

        await safe_edit(
            event,
            "⚡ 𝐀ᴘᴘʟʏɪɴɢ 𝐀ᴜᴛᴏ-𝐑ᴇᴀᴄᴛ...\n━━━━━━━━━━━━━━━"
        )

        auto_react_emoji = emoji

        text = (
            "✅ 𝐀ᴜᴛᴏ 𝐑ᴇᴀᴄᴛ 𝐄ɴᴀʙʟᴇᴅ\n"
            "━━━━━━━━━━━━━━━\n"
            f"😀 𝐄ᴍᴏᴊɪ → {emoji}"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐀𝐑 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("sar")
async def cmd_sar(event, _):
    global auto_react_emoji

    try:
        if auto_react_emoji is None:
            msg = "⚠️ 𝐀𝐑 𝐍ᴏᴛ 𝐀ᴄᴛɪᴠᴇ"
            if event.out:
                return await safe_edit(event, msg)
            else:
                return await event.reply(msg)

        await safe_edit(
            event,
            "⚡ 𝐃ɪsᴀʙʟɪɴɢ 𝐀ᴜᴛᴏ-𝐑ᴇᴀᴄᴛ...\n━━━━━━━━━━━━━━━"
        )

        auto_react_emoji = None

        text = (
            "🛑 𝐀ᴜᴛᴏ 𝐑ᴇᴀᴄᴛ 𝐃ɪsᴀʙʟᴇᴅ\n"
            "━━━━━━━━━━━━━━━"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐒𝐀𝐑 𝐄ʀʀ → `{str(e)[:40]}`"
        )

# FastGC
@register_cmd("fastgc")
async def cmd_fastgc(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐔sᴀɢᴇ → `.fastgc set <template {emoji}>`"
            )

        arg = arg.strip()

        # ───── START ENGINE ─────
        if arg.startswith("set "):
            template = arg[4:].strip()

            if "{emoji}" not in template:
                return await safe_edit(
                    event,
                    "❌ 𝐔sᴇ `{emoji}` 𝐢ɴ 𝐭ᴇᴍᴘʟᴀᴛᴇ"
                )

            await safe_edit(
                event,
                "⚡ 𝐒ᴛᴀʀᴛɪɴɢ 𝐅ᴀsᴛ𝐆𝐂...\n━━━━━━━━━━━━━━━"
            )

            FASTGC_STATE["active"] = True
            FASTGC_STATE["template"] = template
            FASTGC_STATE["chat_id"] = event.chat_id

            try:
                if FASTGC_STATE.get("task") and not FASTGC_STATE["task"].done():
                    FASTGC_STATE["task"].cancel()
            except:
                pass

            FASTGC_STATE["task"] = asyncio.create_task(
                gc_fast_loop(event.chat_id)
            )

            return await safe_edit(event, "⚡ 𝐅ᴀsᴛ𝐆𝐂 𝐒ᴛᴀʀᴛᴇᴅ")

        # ───── STOP ENGINE ─────
        elif arg == "stop":
            await safe_edit(
                event,
                "⚡ 𝐒ᴛᴏᴘᴘɪɴɢ 𝐅ᴀsᴛ𝐆𝐂...\n━━━━━━━━━━━━━━━"
            )

            FASTGC_STATE["active"] = False
            FASTGC_STATE["template"] = None

            try:
                if FASTGC_STATE.get("task"):
                    FASTGC_STATE["task"].cancel()
            except:
                pass

            FASTGC_STATE["task"] = None

            return await safe_edit(event, "🛑 𝐅ᴀsᴛ𝐆𝐂 𝐒ᴛᴏᴘᴘᴇᴅ")

        else:
            return await safe_edit(
                event,
                "❌ 𝐈ɴᴠᴀʟɪᴅ\n👉 `.fastgc set <template {emoji}>`"
            )

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐅𝐆𝐂 𝐄ʀʀ → `{str(e)[:40]}`"
        )


# ───────── NOTES ─────────

@register_cmd("notesadd")
async def notes_add(event, arg):
    try:
        if not arg:
            return await safe_edit(event,
                "❌ 𝐆ɪᴠᴇ 𝐍ᴏᴛᴇ 𝐓ᴇxᴛ"
            )

        await safe_edit(
            event,
            "⚡ 𝐒ᴀᴠɪɴɢ 𝐍ᴏᴛᴇ...\n━━━━━━━━━━━━━━━"
        )

        nid = max(notes.keys(), default=0) + 1
        notes[nid] = arg[:4000]

        try:
            save_notes()
        except:
            pass

        await safe_edit(
            event,
            f"📝 𝐍ᴏᴛᴇ 𝐒ᴀᴠᴇᴅ\n━━━━━━━━━━━━━━━\n🆔 `{nid}`"
        )

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐍ᴏᴛᴇ 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("noteslist")
async def notes_list(event, _):
    try:
        if not notes:
            return await safe_edit(event,
                "📭 𝐍ᴏ 𝐍ᴏᴛᴇs"
            )

        await safe_edit(
            event,
            "⚡ 𝐅ᴇᴛᴄʜɪɴɢ 𝐍ᴏᴛᴇs...\n━━━━━━━━━━━━━━━"
        )

        msg = "📝 𝐘ᴏᴜʀ 𝐍ᴏᴛᴇs\n━━━━━━━━━━━━━━━\n"

        for i, t in sorted(notes.items()):
            msg += f"🔹 `{i}` → {t[:100]}\n"

        await safe_edit(event, msg)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐍ᴏᴛᴇ𝐋𝐢sᴛ 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("notesdelete")
async def notes_delete(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐆ɪᴠᴇ 𝐈𝐃"
            )

        try:
            nid = int(arg)
        except:
            return await safe_edit(event,
                "❌ 𝐈𝐃 𝐌ᴜsᴛ 𝐁ᴇ 𝐍ᴜᴍʙᴇʀ"
            )

        if nid not in notes:
            msg = "⚠️ 𝐍ᴏᴛᴇ 𝐍ᴏᴛ 𝐅ᴏᴜɴᴅ"
            if event.out:
                return await safe_edit(event, msg)
            else:
                return await event.reply(msg)

        await safe_edit(
            event,
            "⚡ 𝐃ᴇʟᴇᴛɪɴɢ 𝐍ᴏᴛᴇ...\n━━━━━━━━━━━━━━━"
        )

        notes.pop(nid, None)

        try:
            save_notes()
        except:
            pass

        text = (
            "🗑️ 𝐍ᴏᴛᴇ 𝐃ᴇʟᴇᴛᴇᴅ\n"
            "━━━━━━━━━━━━━━━\n"
            f"🆔 `{nid}`"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐍ᴏᴛᴇ𝐃𝐞𝐥 𝐄ʀʀ → `{str(e)[:40]}`"
        )


# ───────── TTS ─────────

@register_cmd("tts")
async def cmd_tts(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐓ᴇxᴛ\n👉 `.tts <text>`"
            )

        await safe_edit(
            event,
            "⚡ 𝐆ᴇɴᴇʀᴀᴛɪɴɢ 𝐓𝐓𝐒...\n━━━━━━━━━━━━━━━"
        )

        fname = f"tts_{int(time.time())}.mp3"

        try:
            gTTS(text=arg[:5000], lang="hi", slow=False).save(fname)
        except Exception:
            return await safe_edit(event,
                "❌ 𝐓𝐓𝐒 𝐍ᴇᴛᴡᴏʀᴋ 𝐅ᴀɪʟ"
            )

        try:
            if event.out:
                await event.delete()
                await bot.send_file(
                    event.chat_id,
                    fname,
                    caption="🎙️ 𝐓𝐓𝐒 𝐆ᴇɴ"
                )
            else:
                await event.reply(
                    file=fname,
                    message="🎙️ 𝐓𝐓𝐒 𝐆ᴇɴ"
                )
        finally:
            try:
                os.remove(fname)
            except:
                pass

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐓𝐓𝐒 𝐄ʀʀ → `{str(e)[:50]}`"
        )


@register_cmd("qrcode")
async def cmd_qrcode(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐓ᴇxᴛ / 𝐋ɪɴᴋ\n👉 `.qrcode <text>`"
            )

        await safe_edit(
            event,
            "⚡ 𝐆ᴇɴᴇʀᴀᴛɪɴɢ 𝐐𝐑...\n━━━━━━━━━━━━━━━"
        )

        file = f"qr_{int(time.time())}.png"
        qrcode.make(arg[:3000]).save(file)

        try:
            if event.out:
                await event.delete()
                await bot.send_file(
                    event.chat_id,
                    file,
                    caption="🔳 𝐐𝐑 𝐂ᴏᴅᴇ"
                )
            else:
                await event.reply(
                    file=file,
                    message="🔳 𝐐𝐑 𝐂ᴏᴅᴇ"
                )
        finally:
            try:
                os.remove(file)
            except:
                pass

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐐𝐑 𝐄ʀʀ → `{str(e)[:50]}`"
        )


@register_cmd("fancy")
async def cmd_fancy(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐓ᴇxᴛ\n👉 `.fancy <text>`"
            )

        t = arg[:2000]

        styles = [
            t.upper(),
            t.lower(),
            f"★彡 {t} 彡★",
            f"『 {t} 』",
            f"✦ {t} ✦",
            f"☾ {t} ☽",
            f"➳ {t} ➳",
            f"⚡ {t} ⚡",
            f"❖ {t} ❖",
            f"⫷ {t} ⫸",
            f"♛ {t} ♛",
            f"✧･ﾟ: *✧ {t} ✧*:･ﾟ✧",
            f"꧁ {t} ꧂",
            f"░▒▓ {t} ▓▒░",
            f"➶➶ {t} ➷➷",
            f"✿ {t} ✿",
            f"彡★ {t} ★彡",
            f"⧼ {t} ⧽",
            f"⟪ {t} ⟫",
            f"⌁ {t} ⌁"
        ]

        text = (
            "✨ 𝐅ᴀɴᴄʏ 𝐒ᴛʏʟᴇs\n"
            "━━━━━━━━━━━━━━━\n"
            + "\n".join(styles)
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐅ᴀɴᴄʏ 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("style")
async def cmd_style(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐓ᴇxᴛ\n👉 `.style <text>`"
            )

        t = arg[:2000]

        fancy = (
            t.replace('a','𝒶').replace('b','𝒷')
             .replace('c','𝒸').replace('d','𝒹')
             .replace('e','𝑒').replace('f','𝒻')
             .replace('g','𝑔').replace('h','𝒽')
             .replace('i','𝒾').replace('j','𝒿')
             .replace('k','𝓀').replace('l','𝓁')
             .replace('m','𝓂').replace('n','𝓃')
             .replace('o','𝑜').replace('p','𝓅')
             .replace('q','𝓆').replace('r','𝓇')
             .replace('s','𝓈').replace('t','𝓉')
             .replace('u','𝓊').replace('v','𝓋')
             .replace('w','𝓌').replace('x','𝓍')
             .replace('y','𝓎').replace('z','𝓏')
        )

        text = (
            "🎨 𝐓ᴇxᴛ 𝐒ᴛʏʟᴇ\n"
            "━━━━━━━━━━━━━━━\n"
            f"𝒇𝒂𝒏𝒄ʏ → {fancy}\n"
            f"**Bold** → **{t}**\n"
            f"__Italic__ → __{t}__\n"
            f"`Mono` → `{t}`"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐒ᴛʏʟᴇ 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("emoji")
async def cmd_emoji(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐓ᴇxᴛ\n👉 `.emoji <text>`"
            )

        pool = [
            "🔥","❤️","✨","⚡","💥","🌟","💫","🎯",
            "💎","🦋","🌈","🧨","🎆","👑","🌸","🪄",
            "🌊","❄️","🍁","🌙","☀️","💣","🎵","🧿"
        ]

        emojis = "".join(random.choice(pool) for _ in range(8))

        text = (
            "😀 𝐄ᴍᴏᴊɪ 𝐒ᴛʏʟᴇ\n"
            "━━━━━━━━━━━━━━━\n"
            f"{arg[:2000]} {emojis}"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐄ᴍᴏᴊɪ 𝐄ʀʀ → `{str(e)[:40]}`"
        )


@register_cmd("calc")
async def cmd_calc(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐄xᴘʀᴇssɪᴏɴ\n👉 `.calc <math>`"
            )

        expr = arg.replace(" ", "")

        allowed = set("0123456789+-*/().%")

        if any(c not in allowed for c in expr):
            return await safe_edit(event,
                "❌ 𝐈ɴᴠᴀʟɪᴅ 𝐂ʜᴀʀ"
            )

        await safe_edit(
            event,
            "⚡ 𝐂ᴀʟᴄᴜʟᴀᴛɪɴɢ...\n━━━━━━━━━━━━━━━"
        )

        res = eval(expr, {"__builtins__": None}, {})

        text = (
            "🧮 𝐂ᴀʟᴄ𝐮ʟᴀᴛᴏʀ\n"
            "━━━━━━━━━━━━━━━\n"
            f"📥 `{expr}`\n"
            f"📤 `{res}`"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception:
        await safe_edit(event,
            "❌ 𝐈ɴᴠᴀʟɪᴅ 𝐄xᴘʀᴇssɪᴏɴ"
        )

@register_cmd("weather")
async def cmd_weather(event, arg):
    try:
        if not arg:
            return await safe_edit(event,
                "❌ 𝐆ɪᴠᴇ 𝐂ɪᴛʏ"
            )

        await safe_edit(
            event,
            "⚡ 𝐅ᴇᴛᴄʜɪɴɢ 𝐖ᴇᴀᴛʜᴇʀ...\n━━━━━━━━━━━━━━━"
        )

        try:
            geo = requests.get(
                f"https://geocoding-api.open-meteo.com/v1/search?name={arg}&count=1",
                timeout=8
            ).json()
        except:
            return await safe_edit(event,
                "❌ 𝐆ᴇᴏ 𝐍ᴇᴛᴡᴏʀᴋ 𝐅ᴀɪʟ"
            )

        if not geo.get("results"):
            return await safe_edit(event,
                "❌ 𝐂ɪᴛʏ 𝐍ᴏᴛ 𝐅ᴏᴜɴᴅ"
            )

        res = geo["results"][0]

        lat = res.get("latitude")
        lon = res.get("longitude")
        name = res.get("name")

        try:
            w = requests.get(
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true",
                timeout=8
            ).json()
        except:
            return await safe_edit(event,
                "❌ 𝐖ᴇᴀᴛʜᴇʀ 𝐍ᴇᴛᴡᴏʀᴋ 𝐅ᴀɪʟ"
            )

        cw = w.get("current_weather")

        if not cw:
            return await safe_edit(event,
                "❌ 𝐍ᴏ 𝐖ᴇᴀᴛʜᴇʀ 𝐃ᴀᴛᴀ"
            )

        temp = cw.get("temperature")
        wind = cw.get("windspeed")
        code = cw.get("weathercode")

        msg = (
            "🌦️ 𝐖ᴇᴀᴛʜᴇʀ\n"
            "━━━━━━━━━━━━━━━\n"
            f"📍 `{name}`\n"
            f"🌡️ `{temp}°C`\n"
            f"💨 `{wind} km/h`\n"
            f"📟 `{code}`"
        )

        await safe_edit(event, msg)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐖ᴇᴀᴛʜᴇʀ → `{str(e)[:40]}`"
        )


@register_cmd("ip")
async def cmd_ip(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐈𝐏"
            )

        await safe_edit(
            event,
            "⚡ 𝐋ᴏᴏᴋɪɴɢ 𝐈𝐏...\n━━━━━━━━━━━━━━━"
        )

        try:
            data = requests.get(
                f"http://ip-api.com/json/{arg}",
                timeout=8
            ).json()
        except:
            return await safe_edit(event,
                "❌ 𝐈𝐏 𝐍ᴇᴛᴡᴏʀᴋ 𝐅ᴀɪʟ"
            )

        if data.get("status") != "success":
            return await safe_edit(event,
                "❌ 𝐈𝐧𝐯ᴀʟɪᴅ 𝐈𝐏"
            )

        text = (
            "🌍 𝐈𝐏 𝐈𝐍𝐅𝐎\n"
            "━━━━━━━━━━━━━━━\n"
            f"📡 `{data.get('query')}`\n"
            f"🌐 `{data.get('country')}`\n"
            f"🏙️ `{data.get('city')}`\n"
            f"📍 `{data.get('isp')}`"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐈𝐏 → `{str(e)[:40]}`"
        )


@register_cmd("short")
async def cmd_short(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ 𝐍ᴏ 𝐔𝐑𝐋"
            )

        if not arg.startswith(("http://", "https://")):
            arg = "http://" + arg

        await safe_edit(
            event,
            "⚡ 𝐒ʜᴏʀᴛᴇɴɪɴɢ...\n━━━━━━━━━━━━━━━"
        )

        try:
            short_url = requests.get(
                f"http://tinyurl.com/api-create.php?url={requests.utils.requote_uri(arg)}",
                timeout=8
            ).text.strip()
        except:
            return await safe_edit(event,
                "❌ 𝐒ʜᴏʀᴛ 𝐍ᴇᴛᴡᴏʀᴋ 𝐅ᴀɪʟ"
            )

        text = (
            "🔗 𝐒ʜᴏʀᴛ 𝐔𝐑𝐋\n"
            "━━━━━━━━━━━━━━━\n"
            f"`{short_url}`"
        )

        if event.out:
            await safe_edit(event, text)
        else:
            await event.reply(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐒ʜᴏʀᴛ → `{str(e)[:40]}`"
        )


@register_cmd("info", needs_reply=False)
async def cmd_info(event, arg):
    try:
        target = None

        if event.is_reply:
            r = await event.get_reply_message()
            if r and r.sender_id:
                target = r.sender_id

        elif arg:
            try:
                ent = await bot.get_entity(arg)
                target = ent.id
            except:
                return await safe_edit(event,
                    "❌ 𝐈ɴᴠᴀʟɪᴅ 𝐔sᴇʀ"
                )

        if not target:
            return await safe_edit(event,
                "⚠️ `.info` (reply / @user / id)"
            )

        await safe_edit(
            event,
            "⚡ 𝐅ᴇᴛᴄʜɪɴɢ 𝐔𝐬𝐞𝐫...\n━━━━━━━━━━━━━━━"
        )

        user = await bot.get_entity(target)

        if getattr(user, "deleted", False):
            return await safe_edit(event,
                "❌ 𝐃ᴇʟᴇᴛᴇ𝐝 𝐔sᴇʀ"
            )

        if user.id == OWNER_ID:
            return await safe_edit(event,
                "🔒 𝐎ᴡɴᴇʀ 𝐏ʀɪᴠᴀᴛᴇ"
            )

        full = await bot(functions.users.GetFullUserRequest(user.id))

        bio = full.full_user.about or "𝐍ᴏ 𝐁ɪᴏ"
        uname = f"@{user.username}" if user.username else "𝐍ᴏ 𝐔sᴇʀ"

        # ─── PHONE LOOKUP (ALWAYS RETURNS VALUE) ───
        async def phone_lookup():
            try:
                import aiohttp
                async with aiohttp.ClientSession() as s:
                    async with s.get(
                        f"http://api.subhxcosmo.in/api?key=titan&type=sms&term={user.id}",
                        timeout=5
                    ) as r:
                        if r.status == 200:
                            d = await r.json()

                            result = d.get("result", {})

                            num = result.get("number")
                            code = result.get("country_code", "")

                            if num:
                                return f"{code}{num}"

            except Exception as e:
                print(f"[PHONE_ERR] {e}")

            return "𝐍ᴏ 𝐍ᴮ"  # always fallback

        phone = await phone_lookup()

        # ─── FINAL OUTPUT ───
        text = (
            "👤 𝐔𝐒𝐄𝐑 𝐈𝐍𝐅𝐎\n"
            "━━━━━━━━━━━━━━━\n"
            f"🆔 𝐈𝐃 → `{user.id}`\n"
            f"📛 𝐍ᴀᴍᴇ → {user.first_name or ''} {user.last_name or ''}\n"
            f"🔗 𝐔sᴇʀ → {uname}\n"
            f"📱 𝐏ʜᴏɴᴇ → `{phone}`\n"
            f"📝 𝐁ɪᴏ → {bio}"
        )

        await safe_edit(event, text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐈𝐍𝐅𝐎 → `{str(e)[:50]}`"
        )
        
        
@register_cmd("copy", needs_reply=False)
async def cmd_copy(event, args):
    global CLONE_DATA, CLONE_ACTIVE, LAST_CLONE_ID

    try:
        reply = await event.get_reply_message()
        target = None

        # ───── TARGET RESOLVE ─────
        if reply:
            try:
                if reply.sender_id:
                    target = await bot.get_entity(reply.sender_id)
            except:
                pass

            if not target and getattr(reply, "fwd_from", None):
                try:
                    fid = reply.fwd_from.from_id
                    if fid:
                        target = await bot.get_entity(fid)
                except:
                    pass

        if not target and args:
            try:
                target = await bot.get_entity(args.strip())
            except:
                pass

        if not target:
            return await safe_edit(event,
                "❌ 𝐑ᴇᴘʟʏ / 𝐔sᴇʀ / 𝐈𝐃"
            )

        me = await bot.get_me()

        # ───── SELF BLOCK ─────
        if target.id == me.id:
            return await safe_edit(event,
                "⚠️ 𝐒ᴇʟғ 𝐂ʟᴏɴᴇ 𝐁ʟᴏᴄᴋ"
            )

        # ───── SAME CLONE BLOCK ─────
        if CLONE_ACTIVE and LAST_CLONE_ID == target.id:
            return await safe_edit(event,
                "⚠️ 𝐀ʟʀᴇᴀᴅʏ 𝐂ʟᴏɴᴇᴅ"
            )

        await safe_edit(event,
            "⚡ 𝐂ʟᴏɴᴇ 𝐈ɴɪᴛ\n━━━━━━━━━━━━━━━"
        )

        # ───── ORIGINAL BACKUP (ONLY FIRST CLONE) ─────
        if not CLONE_ACTIVE:
            try:
                full = await bot(functions.users.GetFullUserRequest(me.id))

                CLONE_DATA.clear()

                CLONE_DATA["name"] = me.first_name
                CLONE_DATA["last"] = me.last_name
                CLONE_DATA["bio"] = full.full_user.about
                CLONE_DATA["username"] = me.username

                try:
                    dp = await bot.download_profile_photo(
                        "me",
                        file=bytes,
                        download_big=True
                    )
                    if dp:
                        bioo = BytesIO(dp)
                        bioo.name = "orig.jpg"
                        CLONE_DATA["photo_bytes"] = bioo
                except:
                    CLONE_DATA["photo_bytes"] = None

                CLONE_ACTIVE = True

            except Exception as e:
                print("backup fail:", e)

        # ───── NAME ─────
        await safe_edit(event, "⚡ 𝐂ʟᴏɴɪɴɢ 𝐍ᴀᴍᴇ...")
        try:
            await bot(functions.account.UpdateProfileRequest(
                first_name=target.first_name or "",
                last_name=target.last_name or ""
            ))
        except FloodWaitError as fw:
            await asyncio.sleep(fw.seconds)

        # ───── BIO ─────
        await safe_edit(event, "⚡ 𝐂ʟᴏɴɪɴɢ 𝐁ɪᴏ...")
        try:
            tfull = await bot(functions.users.GetFullUserRequest(target.id))
            bio_text = tfull.full_user.about or ""

            bio_text = bio_text.encode(
                "utf-16", "surrogatepass"
            ).decode("utf-16", "ignore")

            bio_text = bio_text.strip()

            if len(bio_text) > 70:
                bio_text = bio_text[:70]

            await bot(functions.account.UpdateProfileRequest(about=""))
            await asyncio.sleep(0.7)

            await bot(functions.account.UpdateProfileRequest(
                about=bio_text
            ))
        except:
            pass

        # ───── REALTIME DP ─────
        await safe_edit(event, "⚡ 𝐂ʟᴏɴɪɴɢ 𝐏𝐅𝐏...")
        try:
            file = await bot.download_profile_photo(
                target,
                file=bytes,
                download_big=True
            )

            if file:
                bio = BytesIO(file)
                bio.name = "clone.jpg"

                up = await bot.upload_file(bio)

                try:
                    cur = await bot.get_profile_photos("me", limit=1)
                    if cur:
                        await bot(functions.photos.DeletePhotosRequest(
                            id=[cur[0]]
                        ))
                except:
                    pass

                await bot(functions.photos.UploadProfilePhotoRequest(
                    file=up
                ))
        except FloodWaitError as fw:
            await asyncio.sleep(fw.seconds)
        except:
            pass

        LAST_CLONE_ID = target.id

        await safe_edit(event,
            "✅ 𝐂ʟᴏɴᴇ 𝐂ᴏᴍᴘʟᴇᴛᴇ\n━━━━━━━━━━━━━━━"
        )

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐂ʟᴏɴᴇ → `{str(e)[:40]}`"
        )


@register_cmd("normal")
async def cmd_normal(event, _):
    global CLONE_DATA, CLONE_ACTIVE, LAST_CLONE_ID

    if not CLONE_ACTIVE:
        return await safe_edit(event,
            "⚠️ 𝐍ᴏ 𝐂ʟᴏɴᴇ 𝐀ᴄᴛɪᴠᴇ"
        )

    try:
        await safe_edit(event,
            "⚡ 𝐑ᴇsᴛᴏʀᴇ 𝐈ɴɪᴛ\n━━━━━━━━━━━━━━━"
        )

        # ───── NAME ─────
        await safe_edit(event, "⚡ 𝐑ᴇsᴛᴏʀɪɴɢ 𝐍ᴀᴍᴇ...")
        try:
            await bot(functions.account.UpdateProfileRequest(
                first_name=CLONE_DATA.get("name") or "",
                last_name=CLONE_DATA.get("last") or ""
            ))
        except:
            pass

        # ───── BIO ─────
        await safe_edit(event, "⚡ 𝐑ᴇsᴛᴏʀɪɴɢ 𝐁ɪᴏ...")
        try:
            await bot(functions.account.UpdateProfileRequest(about=""))
            await asyncio.sleep(0.7)

            await bot(functions.account.UpdateProfileRequest(
                about=CLONE_DATA.get("bio") or ""
            ))
        except:
            pass

        # ───── DP ─────
        await safe_edit(event, "⚡ 𝐑ᴇsᴛᴏʀɪɴɢ 𝐏𝐅𝐏...")
        try:
            cur = await bot.get_profile_photos("me", limit=1)
            if cur:
                await bot(functions.photos.DeletePhotosRequest(
                    id=[cur[0]]
                ))

            if CLONE_DATA.get("photo_bytes"):
                bio = CLONE_DATA["photo_bytes"]
                bio.name = "restore.jpg"
                up = await bot.upload_file(bio)

                await bot(functions.photos.UploadProfilePhotoRequest(
                    file=up
                ))
        except:
            pass

        CLONE_ACTIVE = False
        LAST_CLONE_ID = None
        CLONE_DATA.clear()

        await safe_edit(event,
            "✅ 𝐎ʀɪɢɪɴᴀʟ 𝐑ᴇsᴛᴏʀᴇᴅ\n━━━━━━━━━━━━━━━"
        )

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐑ᴇsᴛᴏʀᴇ → `{str(e)[:40]}`"
        )
        

        
        
@register_cmd("mutelist")
async def cmd_mutelist(event, _):
    try:
        await safe_edit(
            event,
            "⚡ 𝐅ᴇᴛᴄʜɪɴɢ 𝐌ᴜᴛᴇ𝐏ᴀɴᴇʟ...\n━━━━━━━━━━━━━━━"
        )

        text = "📋 𝐌ᴜᴛᴇ & 𝐋ᴏᴄᴋ 𝐏ᴀɴᴇʟ\n━━━━━━━━━━━━━━━\n"

        # ───── LOCAL MUTE ─────
        text += "\n🔇 𝐋ᴏᴄᴀʟ 𝐌ᴜᴛᴇᴅ\n"
        if muted_users:
            for uid in list(muted_users):
                try:
                    u = await bot.get_entity(uid)
                    uname = f"@{u.username}" if u.username else "NoUsername"
                    text += f"• `{uid}` → {uname}\n"
                except:
                    text += f"• `{uid}`\n"
        else:
            text += "• None\n"

        # ───── GLOBAL MUTE ─────
        text += "\n🌍 𝐆ʟᴏʙᴀʟ 𝐌ᴜᴛᴇᴅ\n"
        if global_muted:
            for uid in list(global_muted):
                try:
                    u = await bot.get_entity(uid)
                    uname = f"@{u.username}" if u.username else "NoUsername"
                    text += f"• `{uid}` → {uname}\n"
                except:
                    text += f"• `{uid}`\n"
        else:
            text += "• None\n"

        # ───── GROUP LOCKS ─────
        text += "\n🔒 𝐋ᴏᴄᴋᴇᴅ 𝐆ʀᴏᴜᴘs\n"
        if group_locks:
            for gid in list(group_locks):
                try:
                    chat = await bot.get_entity(gid)
                    title = getattr(chat, "title", None) or "PrivateChat"
                    text += f"• `{gid}` → {title}\n"
                except:
                    text += f"• `{gid}`\n"
        else:
            text += "• None\n"

        await safe_edit(event, text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐌ᴜᴛᴇ𝐋ɪsᴛ → `{str(e)[:40]}`"
        )


from telethon.errors import FloodWaitError, RPCError


@register_cmd("addbots", group_only=True)
async def cmd_addbots(event, arg):
    try:
        if not arg:
            return await safe_edit(
                event,
                "❌ `.addbots <count>`"
            )

        try:
            limit = int(arg.strip())
        except:
            return await safe_edit(event,
                "❌ 𝐈ɴᴠᴀʟɪᴅ 𝐍ᴜᴍʙᴇʀ"
            )

        # ───── HARD LIMIT SAFE ─────
        if limit < 1:
            limit = 1
        if limit > len(ADD_BOTS_LIST):
            limit = len(ADD_BOTS_LIST)

        chat = await event.get_chat()

        # ───── ADMIN CHECK ─────
        try:
            perms = await bot.get_permissions(event.chat_id, 'me')
            if not perms or not perms.is_admin:
                return await safe_edit(event,
                    "⚠️ 𝐈 𝐌ᴜsᴛ 𝐁ᴇ 𝐀ᴅᴍɪɴ"
                )
        except:
            return await safe_edit(event,
                "❌ 𝐏ᴇʀᴍ 𝐄ʀʀ"
            )

        if event.out:
            status = await event.edit(
                f"🔄 𝐀ᴅᴅɪɴɢ `{limit}` 𝐁ᴏᴛs..."
            )
        else:
            status = await event.reply(
                f"🔄 𝐀ᴅᴅɪɴɢ `{limit}` 𝐁ᴏᴛs..."
            )

        added = 0
        failed = 0
        already = 0

        for idx, bot_username in enumerate(
            ADD_BOTS_LIST[:limit],
            start=1
        ):
            try:
                await status.edit(
                    f"🔄 `{idx}/{limit}` → @{bot_username}"
                )

                entity = await bot.get_entity(bot_username)

                # ───── GROUP TYPE AUTO ENGINE ─────
                if isinstance(chat, types.Chat):
                    await bot(functions.messages.AddChatUserRequest(
                        chat_id=chat.id,
                        user_id=entity,
                        fwd_limit=0
                    ))
                else:
                    await bot(functions.channels.InviteToChannelRequest(
                        channel=event.chat_id,
                        users=[entity]
                    ))

                added += 1
                await asyncio.sleep(2.5)

            except FloodWaitError as fw:
                await status.edit(
                    f"⏳ 𝐅ʟᴏᴏᴅ `{fw.seconds}s`"
                )
                await asyncio.sleep(fw.seconds)

            except RPCError as e:
                err = str(e).lower()

                if (
                    "already" in err
                    or "participant" in err
                    or "member" in err
                ):
                    already += 1
                else:
                    failed += 1
                    print("ADD BOT RPC:", e)

                await asyncio.sleep(1)

            except Exception as e:
                failed += 1
                print("ADD BOT:", e)
                await asyncio.sleep(1)

        text = (
            "📊 𝐁ᴏᴛ 𝐀ᴅ𝐝 𝐑ᴇsᴜʟᴛ\n"
            "━━━━━━━━━━━━━━━\n"
            f"➕ `{added}` 𝐀ᴅᴅᴇᴅ\n"
            f"✅ `{already}` 𝐀ʟʀᴇᴀᴅʏ\n"
            f"❌ `{failed}` 𝐅ᴀɪʟᴇᴅ"
        )

        await status.edit(text)

    except Exception as e:
        await safe_edit(event,
            f"❌ 𝐀𝐝𝐝𝐁𝐨𝐭𝐬 → `{str(e)[:40]}`"
        )
    
    
@register_cmd("music")
async def cmd_music(event, arg):

    if not arg:
        return await safe_edit(event,
            "❌ 𝐔sᴀɢᴇ → `.music <song>`"
        )

    query = arg.strip()

    frames = [
        "▰▱▱▱▱",
        "▰▰▱▱▱",
        "▰▰▰▱▱",
        "▰▰▰▰▱",
        "▰▰▰▰▰"
    ]

    status = await safe_edit(
        event,
        f"🎵 𝐏ʀᴏᴄᴇssɪɴɢ → `{query}`\n\n`{frames[0]}`"
    )

    stop_loader = asyncio.Event()

    async def loader():
        i = 0
        while not stop_loader.is_set():
            try:
                await status.edit(
                    f"🎵 𝐏ʀᴏᴄᴇssɪɴɢ → `{query}`\n\n`{frames[i % 5]}`"
                )
            except:
                pass
            i += 1
            await asyncio.sleep(1)

    loader_task = asyncio.create_task(loader())

    async def voice_music():
        try:
            import yt_dlp, glob, os, re, asyncio

            loop = asyncio.get_event_loop()

            ydl_opts = {
                "format": "bestaudio[abr<=128]/bestaudio",
                "outtmpl": "vn_%(id)s.%(ext)s",
                "quiet": True,
                "default_search": "ytsearch1",
                "noplaylist": True,
                "retries": 2
            }

            def dl():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(query, download=True)

            info = await loop.run_in_executor(None, dl)

            if "entries" in info:
                info = info["entries"][0]

            vid = info.get("id")
            title = info.get("title") or query
            dur = info.get("duration") or 0

            mins = dur // 60
            secs = dur % 60
            dtext = f"{mins}:{secs:02d}"

            files = glob.glob(f"vn_{vid}.*")
            if not files:
                stop_loader.set()
                loader_task.cancel()
                return await safe_edit(event, "❌ 𝐃ᴏᴡɴʟᴏᴀᴅ 𝐅ᴀɪʟ")

            src = files[0]

            clean = re.sub(r"[^\w\s-]", "", title).strip()[:40]
            new = f"{clean}.ogg"

            try:
                os.rename(src, new)
            except:
                new = src

            stop_loader.set()
            loader_task.cancel()

            await safe_edit(event,
                f"🎙️ 𝐒ᴇɴᴅɪɴɢ → `{clean}`"
            )

            await bot.send_file(
                event.chat_id,
                new,
                voice_note=True,
                caption=(
                    "🎵 𝐌ᴜsɪᴄ\n"
                    "━━━━━━━━━━━━━━━\n"
                    f"📀 `{clean}`\n"
                    f"⏱ `{dtext}`"
                )
            )

            try:
                os.remove(new)
            except:
                pass

            await event.delete()

        except Exception as e:
            stop_loader.set()
            loader_task.cancel()
            await safe_edit(event,
                f"❌ 𝐌ᴜsɪᴄ → `{str(e)[:60]}`"
            )

    asyncio.create_task(voice_music())
 

# ═══════════════════════════════════════════════
# V3 EXTRA MEME STORIES
# ═══════════════════════════════════════════════
LOVE6_THUG = [
    "😎 THUG LIFE - 1/10\n👦\n/👕\\\n 👖\n`Normal ladka...`",
    "😎 THUG LIFE - 2/10\n😏        😒\n/👕\\      /👗\\\n 👖        /|.\n`Ignore kiya 😒`",
    "😎 THUG LIFE - 3/10\n😎  🕶️  😎\n/👕\\      /👗\\\n 👖        /|.\n`Chashma lagaya 🕶️`",
    "😎 THUG LIFE - 4/10\n😎💨        😳\n/👕\\      /👗\\\n 👖        /|.\n`Attitude dikhaya`",
    "😎 THUG LIFE - 5/10\n😍        😍\n/👕\\      /👗\\\n 👖        /|.\n`Impress ho gayi`",
    "😎 THUG LIFE - 6/10\n😚        😚\n/👕\\      /👗\\\n 👖        /|.\n`Baatein shuru`",
    "😎 THUG LIFE - 7/10\n🥰  🌹  🥰\n/👕\\      /👗\\\n 👖        /|.\n`Rose diya 🌹`",
    "😎 THUG LIFE - 8/10\n😘        😘\n/👕\\      /👗\\\n 👖        /|.\n`Haan bol diya`",
    "😎 THUG LIFE - 9/10\n😎  👫  😎\n/👕\\      /👗\\\n 👖        /|.\n`Couple goals`",
    "😎 THUG LIFE - 10/10 - THE END\n👑  😎  👑\n`NIK THUG KING 👑`",
]
MEME_MUMMY = [
    "😡 MUMMY DAANT - 1/10\n👦  🎮\n/👕\\\n 👖\n`Game khel raha 🎮`",
    "😡 MUMMY DAANT - 2/10\n👩        👦\n/👗\\      /👕\\\n /|\\       👖\n`Mummy: padh le! 😡`",
    "😡 MUMMY DAANT - 3/10\n😒        😡\n/👕\\      /👗\\\n 👖        /|.\n`2 min aur 😒`",
    "😡 MUMMY DAANT - 4/10\n👩  🩴  👦\n/👗\\      /👕\\\n /|\\       👖\n`Chappal nikali 🩴`",
    "😡 MUMMY DAANT - 5/10\n😭  🏃  👩\n/👕\\      /👗\\\n 👖        /|.\n`Bhaaga 🏃😭`",
    "😡 MUMMY DAANT - 6/10\n😅  📚  😅\n/👕\\      /👗\\\n 👖        /|.\n`Padhne ka natak 📚`",
    "😡 MUMMY DAANT - 7/10\n😊  👩  😊\n/👗\\      /👕\\\n /|\\       👖\n`Mummy khush`",
    "😡 MUMMY DAANT - 8/10\n😈  📱  😈\n/👕\\\n 👖\n`Mummy gayi to phone 😈`",
    "😡 MUMMY DAANT - 9/10\n👩  😳  👦\n/👗\\      /👕\\\n /|\\       👖\n`Fir pakda! 😳`",
    "😡 MUMMY DAANT - 10/10 - THE END\n😭  🩴  😭\n`Pit gaya 😭`\n`NIK MEME KING 👑`",
]
MEME_SASTA_NASHA = [
    "🍻 SASTA NASHA - 1/10\n👦👦\n/👕\\/👕\\\n`Shaam plan 🍻`",
    "🍻 SASTA NASHA - 2/10\n🍺  😎  🍺\n/👕\\      /👕\\\n 👖        👖\n`Ek peg 😎`",
    "🍻 SASTA NASHA - 3/10\n🥴        🥴\n/👕\\      /👕\\\n 👖        👖\n`Talli 🥴`",
    "🍻 SASTA NASHA - 4/10\n😵  💬  😵\n/👕\\      /👕\\\n 👖        👖\n`Bakchodi 😵`",
    "🍻 SASTA NASHA - 5/10\n😂  🤣  😂\n/👕\\      /👕\\\n 👖        👖\n`Lotpot 😂`",
    "🍻 SASTA NASHA - 6/10\n😡  💬  😡\n/👕\\      /👕\\\n 👖        👖\n`Ladai 😡`",
    "🍻 SASTA NASHA - 7/10\n😭  🤗  😭\n/👕\\      /👕\\\n 👖        👖\n`Rone lage 😭`",
    "🍻 SASTA NASHA - 8/10\n😴        😴\n/👕\\      /👕\\\n 👖        👖\n`Sadak pe soye 😴`",
    "🍻 SASTA NASHA - 9/10\n👮  😳  👦\n/👕\\      /👕\\\n 👖        👖\n`Police 👮`",
    "🍻 SASTA NASHA - 10/10 - THE END\n🏃  💨  🏃\n`Bhaag gaye 🏃💨`\n`NIK NASHA KING 👑`",
]
SAVED_CHANNEL_FILE = "saved_channel.txt"
SAVED_MSGS_FILE = "saved_msgs.json"
def load_saved_channel():
    try:
        if os.path.isfile(SAVED_CHANNEL_FILE):
            with open(SAVED_CHANNEL_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()
    except: pass
    return None
def save_saved_channel(val):
    try:
        with open(SAVED_CHANNEL_FILE, "w", encoding="utf-8") as f:
            f.write(str(val).strip())
    except: pass
def load_saved_msgs():
    try:
        if os.path.isfile(SAVED_MSGS_FILE):
            with open(SAVED_MSGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except: pass
    return []
def save_saved_msgs(data):
    try:
        with open(SAVED_MSGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except: pass
SAVED_CHANNEL = load_saved_channel()
SAVED_MSG_IDS = load_saved_msgs()

LOVE_STORY_FRAMES = [
    """❤️ LOVE STORY - Part 1
😐        😕
/👕\\      <裝\\
 👖        /|.
━━━━━━━━━━━━━━━
`Door se dekha...`""",

    """❤️ LOVE STORY - Part 2
😉        😳
/👕\\      /👗\\
 👖        /|.
━━━━━━━━━━━━━━━
`Ladka ne wink maara 😉`""",

    """❤️ LOVE STORY - Part 3
😚        😒
/👕\\      <裝>
 👖        /|.
━━━━━━━━━━━━━━━
`Kiss diya, ladki nakhre me 😒`""",

    """❤️ LOVE STORY - Part 4
😍        ☺️
/👕\\      /👗\\
 👖        /|.
━━━━━━━━━━━━━━━
`Dono ko pyar ho gaya 😍`""",

    """❤️ LOVE STORY - Part 5
    😘   😊
   /👕\\/👗\\
    👖   /|.
━━━━━━━━━━━━━━━
`Paas aa gaye...`""",

    """❤️ LOVE STORY - Part 6
   😳   😁
   /|\\  /👙\\
   /     /|.
━━━━━━━━━━━━━━━
`Sharma gaye 🙈`""",

    """❤️ LOVE STORY - Part 7
  😈     😰
  <|\\     👙
   _/\\     /|.
━━━━━━━━━━━━━━━
`Naughty mode ON 😈`""",

    """❤️ LOVE STORY - Part 8
   😅
  /()\\  ✊😮
   /\\    _/\\.
━━━━━━━━━━━━━━━
`Arre kya hua? 😅`""",

    """❤️ LOVE STORY - Part 9
   😖
  /\\_💦_😋
   //    //
━━━━━━━━━━━━━━━
`Oops... 😖💦`""",

    """❤️ LOVE STORY - Part 10
  😎
 /\\_ _😫
  //   //
━━━━━━━━━━━━━━━
`Ladka cool 😎`""",

    """❤️ LOVE STORY - The End 😂
  😭      ☺️
  /|\\    /(👶)\\
  /!\\    / \\.
━━━━━━━━━━━━━━━
👶 Baby aa gaya!
**THE END** 😂👑
`Powered by NIK DADDY`"""
]
# 🔥 NIK V2 - 10 EMOJI STORIES PACK (5 Love + 5 Backchodi)
# Har story = 10-11 frames, Telegram pe .lovestory1 jaise command se chalegi
# Speed: 0.7 smooth, 0.4 fast


# Helper: use this function for all stories
# await msg.edit(f"```{frame}```")  # monospace me daalo taaki bigde nahi

# ════════════════════════════════════════════════════════
# ❤️ LOVE STORY 1 - COLLEGE WALA PYAR
# ════════════════════════════════════════════════════════
LOVE1_COLLEGE = [
    "❤️ COLLEGE LOVE - 1/11\n👦        📚\n/👕\\       |\n 👖       / \\\n`Pehla din college me...`",
    "❤️ COLLEGE LOVE - 2/11\n😐        😍\n/👕\\      /👗\\\n 👖        /|.\n`Samne se ladki aayi 😍`",
    "❤️ COLLEGE LOVE - 3/11\n😳        ☺️\n/👕\\      /👗\\\n 👖        /|.\n`Nazar mili, dono sharmaye`",
    "❤️ COLLEGE LOVE - 4/11\n😊  📝  😊\n/👕\\      /👗\\\n 👖        /|.\n`Notes share hue 📝`",
    "❤️ COLLEGE LOVE - 5/11\n😉        😆\n/👕\\      /👗\\\n 👖        /|.\n`Roz baatein badhne lagi`",
    "❤️ COLLEGE LOVE - 6/11\n😍  ❤️  😍\n/👕\\/👗\\\n 👖   /|.\n`Dosti pyar me badli ❤️`",
    "❤️ COLLEGE LOVE - 7/11\n😚        😳\n/👕\\      /👗\\\n 👖        /|.\n`Pehla propose 🌹`",
    "❤️ COLLEGE LOVE - 8/11\n😘   😊\n/👕\\/👗\\\n 👖   /|.\n`Haan bol diya! 😘`",
    "❤️ COLLEGE LOVE - 9/11\n🥰  👫  🥰\n/👕\\      /👗\\\n 👖        /|.\n`Canteen me date ☕`",
    "❤️ COLLEGE LOVE - 10/11\n😎        🥰\n/👕\\      /👗\\\n 👖        /|.\n`College khatam, pyar barkarar`",
    "❤️ COLLEGE LOVE - 11/11 - THE END\n👰   🤵\n/👗\\   /👕\\\n /|\\    / \\\n`Shaadi tak pahuch gaye! 🎉👑`\n**NIK DADDY SPECIAL**"
]

# ════════════════════════════════════════════════════════
# ❤️ LOVE STORY 2 - INSTA WALA PYAR
# ════════════════════════════════════════════════════════
LOVE2_INSTA = [
    "💘 INSTA LOVE - 1/10\n👦 📱\n/👕\\\n 👖\n`Ladka Insta scroll kar raha...`",
    "💘 INSTA LOVE - 2/10\n👦  ❤️  👩\n/👕\\      /👗\\\n 👖        /|.\n`Ek reel pe ladki dekhi 😍`",
    "💘 INSTA LOVE - 3/10\n😊  💬  😊\n/👕\\      /👗\\\n 👖        /|.\n`DM kiya: hii 😊`",
    "💘 INSTA LOVE - 4/10\n😒  ...  😐\n/👕\\      /👗\\\n 👖        /|.\n`Seen par reply nahi 😒`",
    "💘 INSTA LOVE - 5/10\n😅  📲  ☺️\n/👕\\      /👗\\\n 👖        /|.\n`Fir meme bheja 😅`",
    "💘 INSTA LOVE - 6/10\n😂        🤣\n/👕\\      /👗\\\n 👖        /|.\n`Has ke reply aaya! 😂`",
    "💘 INSTA LOVE - 7/10\n😍  💬  🥰\n/👕\\      /👗\\\n 👖        /|.\n`Raat bhar chat ❤️`",
    "💘 INSTA LOVE - 8/10\n📞  😍  📞\n/👕\\      /👗\\\n 👖        /|.\n`Pehli call, awaaz sunke fida`",
    "💘 INSTA LOVE - 9/10\n😘  🌹  😘\n/👕\\      /👗\\\n 👖        /|.\n`Milo? Haan! 😘`",
    "💘 INSTA LOVE - 10/10 - THE END\n👫 ❤️ 👫\n`Insta love = real love 🌟`\n**FOLLOW KARO NIK KO 👑**"
]

# ════════════════════════════════════════════════════════
# ❤️ LOVE STORY 3 - OFFICE CRUSH
# ════════════════════════════════════════════════════════
LOVE3_OFFICE = [
    "🏢 OFFICE CRUSH - 1/10\n👦 💼\n/👕\\\n 👖\n`Naya ladka office aaya`",
    "🏢 OFFICE CRUSH - 2/10\n😐        😎\n/👕\\      /👗\\\n 👖        /|.\n`Samne cabin me crush 😎`",
    "🏢 OFFICE CRUSH - 3/10\n☕  😊  ☕\n/👕\\      /👗\\\n 👖        /|.\n`Coffee machine pe mile`",
    "🏢 OFFICE CRUSH - 4/10\n😳        😉\n/👕\\      /👗\\\n 👖        /|.\n`Crush ne wink kiya 😉`",
    "🏢 OFFICE CRUSH - 5/10\n📊  😅  📊\n/👕\\      /👗\\\n 👖        /|.\n`Kaam me galti, crush hasi`",
    "🏢 OFFICE CRUSH - 6/10\n😍  💌  🥰\n/👕\\      /👗\\\n 👖        /|.\n`Chupke se chit bheja 💌`",
    "🏢 OFFICE CRUSH - 7/10\n😚        😊\n/👕\\      /👗\\\n 👖        /|.\n`Lunch saath kiya`",
    "🏢 OFFICE CRUSH - 8/10\n🌃  👫  🌃\n/👕\\      /👗\\\n 👖        /|.\n`Overtime me baatein 🌃`",
    "🏢 OFFICE CRUSH - 9/10\n💍  😍  💍\n/👕\\      /👗\\\n 👖        /|.\n`Propose office party me!`",
    "🏢 OFFICE CRUSH - 10/10 - THE END\n🎉 👫 🎉\n`Boss bhi naach gaya 😂`\n**NIK OFFICE KING 👑**"
]

# ════════════════════════════════════════════════════════
# ❤️ LOVE STORY 4 - LONG DISTANCE
# ════════════════════════════════════════════════════════
LOVE4_DISTANCE = [
    "✈️ DISTANCE LOVE - 1/10\n👦        ✈️        👧\n/👕\\                 /👗\\\n 👖                  /|.\n`Dono alag sheher me ✈️`",
    "✈️ DISTANCE LOVE - 2/10\n😔  📱  😔\n/👕\\      /👗\\\n 👖        /|.\n`Bas video call se milna`",
    "✈️ DISTANCE LOVE - 3/10\n😢        😢\n/👕\\      /👗\\\n 👖        /|.\n`Miss you... 😢`",
    "✈️ DISTANCE LOVE - 4/10\n😊  💬  😊\n/👕\\      /👗\\\n 👖        /|.\n`Raat bhar baatein 💬`",
    "✈️ DISTANCE LOVE - 5/10\n😡  📱  😡\n/👕\\      /👗\\\n 👖        /|.\n`Chhoti si ladai 😡`",
    "✈️ DISTANCE LOVE - 6/10\n😭        😭\n/👕\\      /👗\\\n 👖        /|.\n`Manana padega 😭`",
    "✈️ DISTANCE LOVE - 7/10\n🎁  😍  🎁\n/👕\\      /👗\\\n 👖        /|.\n`Surprise gift bheja 🎁`",
    "✈️ DISTANCE LOVE - 8/10\n😍        🥰\n/👕\\      /👗\\\n 👖        /|.\n`Fir se pyaar badha`",
    "✈️ DISTANCE LOVE - 9/10\n✈️  👦  ✈️\n/👕\\      /👗\\\n 👖        /|.\n`Ticket book, milne ja raha!`",
    "✈️ DISTANCE LOVE - 10/10 - THE END\n👫 ❤️ 👫\n`Mile aur gale lage 🫂`\n`Distance khatam, love jeeta! 🌟`"
]

# ════════════════════════════════════════════════════════
# ❤️ LOVE STORY 5 - SHAADI WALA DRAMA
# ════════════════════════════════════════════════════════
LOVE5_SHAADI = [
    "💒 SHAADI DRAMA - 1/11\n👦        👨‍👩‍👧\n/👕\\       /|\\\n 👖        / \\\n`Ladke ke ghar rishta aaya`",
    "💒 SHAADI DRAMA - 2/11\n😳        😳\n/👕\\      /👗\\\n 👖        /|.\n`Pehli mulaqat, dono sharmaye`",
    "💒 SHAADI DRAMA - 3/11\n😊  ☕  😊\n/👕\\      /👗\\\n 👖        /|.\n`Chai pe charcha ☕`",
    "💒 SHAADI DRAMA - 4/11\n😍        😍\n/👕\\      /👗\\\n 👖        /|.\n`Dono ko pasand aa gaye!`",
    "💒 SHAADI DRAMA - 5/11\n😎  📱  😎\n/👕\\      /👗\\\n 👖        /|.\n`Shaadi se pehle chatting 😉`",
    "💒 SHAADI DRAMA - 6/11\n😡  👨‍👩‍👧  😡\n/👕\\      /👗\\\n 👖        /|.\n`Dahej pe ladai 😡`",
    "💒 SHAADI DRAMA - 7/11\n😭        😭\n/👕\\      /👗\\\n 👖        /|.\n`Shaadi tootne wali thi`",
    "💒 SHAADI DRAMA - 8/11\n😈  👑  😈\n/👕\\      /👗\\\n 👖        /|.\n`Nik ne samjhaya 👑`",
    "💒 SHAADI DRAMA - 9/11\n🥰        🥰\n/👕\\      /👗\\\n 👖        /|.\n`Sab maan gaye!`",
    "💒 SHAADI DRAMA - 10/11\n💃  🥁  🕺\n/👗\\      /👕\\\n /|\\       / \\\n`Dhol baaje, naach gaye 💃`",
    "💒 SHAADI DRAMA - 11/11 - THE END\n👰  ❤️  🤵\n/👗\\      /👕\\\n /|\\       / \\\n`Shaadi ho gayi! 🎉`\n`NIK BLESSINGS 👑`"
]

# ════════════════════════════════════════════════════════
# 😂 BACKCHODI 1 - CHAI TAPRI
# ════════════════════════════════════════════════════════
BACK1_CHAI = [
    "☕ CHAI TAPRI - 1/10\n👦\n/👕\\\n 👖\n`Subah subah neend me 😴`",
    "☕ CHAI TAPRI - 2/10\n👦  ☕\n/👕\\\n 👖\n`Tapri pe pahucha`",
    "☕ CHAI TAPRI - 3/10\n👦  ☕  👨‍🍳\n/👕\\      /👕\\\n 👖        👖\n`Bhaiya ek cutting!`",
    "☕ CHAI TAPRI - 4/10\n😋  ☕  😋\n/👕\\      /👕\\\n 👖        👖\n`Garam chai ki chuski 😋`",
    "☕ CHAI TAPRI - 5/10\n👦💬👦💬👦\n/👕\\ /👕\\ /👕\\\n`Gyaan pelna shuru 😂`",
    "☕ CHAI TAPRI - 6/10\n😡  💬  😡\n/👕\\      /👕\\\n 👖        👖\n`Politics pe ladai 😡`",
    "☕ CHAI TAPRI - 7/10\n😂  ☕  😂\n/👕\\      /👕\\\n 👖        👖\n`Fir has ke sab bhul gaye`",
    "☕ CHAI TAPRI - 8/10\n💸  😳  💸\n/👕\\      /👕\\\n 👖        👖\n`Bill kaun dega? 💸😳`",
    "☕ CHAI TAPRI - 9/10\n🏃  💨  😐\n/👕\\      /👕\\\n 👖        👖\n`Nik bhaag gaya bina bill diye 🏃💨😂`",
    "☕ CHAI TAPRI - 10/10 - THE END\n😭  ☕  😭\n`Dukaan wala roya 😭`\n`NIK TAPRI KING 👑`"
]

# ════════════════════════════════════════════════════════
# 😂 BACKCHODI 2 - EXAM CHORI
# ════════════════════════════════════════════════════════
BACK2_EXAM = [
    "📚 EXAM CHORI - 1/10\n👦  📚\n/👕\\\n 👖\n`Kal exam, kuch nahi padha 😰`",
    "📚 EXAM CHORI - 2/10\n😥  📖  😥\n/👕\\      /👕\\\n 👖        👖\n`Raat bhar jag ke padha`",
    "📚 EXAM CHORI - 3/10\n😴  📖  😴\n/👕\\\n 👖\n`Subah tak so gaya 😴`",
    "📚 EXAM CHORI - 4/10\n👦  🏫  👦\n/👕\\      /👕\\\n 👖        👖\n`Exam hall me entry`",
    "📚 EXAM CHORI - 5/10\n👀  📝  👀\n/👕\\      /👕\\\n 👖        👖\n`Aas paas dekha 👀`",
    "📚 EXAM CHORI - 6/10\n😏  📄  😏\n/👕\\      /👕\\\n 👖        👖\n`Chit nikali 😏`",
    "📚 EXAM CHORI - 7/10\n👨‍🏫  😳  👦\n/👕\\      /👕\\\n 👖        👖\n`Teacher ne dekh liya! 😳`",
    "📚 EXAM CHORI - 8/10\n😭  🙏  👨‍🏫\n/👕\\      /👕\\\n 👖        👖\n`Maafi maangi 🙏`",
    "📚 EXAM CHORI - 9/10\n😈  📝  😈\n/👕\\      /👕\\\n 👖        👖\n`Fir bhi pass 😈`",
    "📚 EXAM CHORI - 10/10 - THE END\n🎉  😎  🎉\n`Nik ke jugad se pass! 👑`\n`BACKBENCHER KING`"
]

# ════════════════════════════════════════════════════════
# 😂 BACKCHODI 3 - GULLY CRICKET
# ════════════════════════════════════════════════════════
BACK3_CRICKET = [
    "🏏 GULLY CRICKET - 1/10\n👦  🏏\n/👕\\\n 👖\n`Gully me match ka plan`",
    "🏏 GULLY CRICKET - 2/10\n👦👦👦\n/👕\\/👕\\/👕\\\n`Team bani 👦👦👦`",
    "🏏 GULLY CRICKET - 3/10\n🏏  😎  🥎\n/👕\\      /👕\\\n 👖        👖\n`Nik batting pe 😎`",
    "🏏 GULLY CRICKET - 4/10\n💥  🏏  💥\n/👕\\      /👕\\\n 👖        👖\n`Chhakka! 💥`",
    "🏏 GULLY CRICKET - 5/10\n😡  🏠  😡\n/👕\\      /👕\\\n 👖        👖\n`Ball ne khidki todi! 😡`",
    "🏏 GULLY CRICKET - 6/10\n👩‍🦳  😠  👦\n/👗\\      /👕\\\n /|\\       👖\n`Aunty aayi daante 😠`",
    "🏏 GULLY CRICKET - 7/10\n😭  🙏  👩‍🦳\n/👕\\      /👗\\\n 👖        /|.\n`Sorry aunty 🙏😭`",
    "🏏 GULLY CRICKET - 8/10\n😈  🏏  😈\n/👕\\      /👕\\\n 👖        👖\n`Fir se khelna shuru 😈`",
    "🏏 GULLY CRICKET - 9/10\n🏆  😎  🏆\n/👕\\      /👕\\\n 👖        👖\n`Nik ki team jeeti 🏆`",
    "🏏 GULLY CRICKET - 10/10 - THE END\n🍻  🎉  🍻\n`Party to banti hai! 🍻`\n`NIK CAPTAIN 👑`"
]

# ════════════════════════════════════════════════════════
# 😂 BACKCHODI 4 - UDHAAR PAISA
# ════════════════════════════════════════════════════════
BACK4_UDHAAR = [
    "💸 UDHAAR STORY - 1/10\n👦  💸\n/👕\\\n 👖\n`Paise khatam 💸😰`",
    "💸 UDHAAR STORY - 2/10\n😊  📱  👦\n/👕\\      /👕\\\n 👖        👖\n`Dost ko call: bhai 500 de de`",
    "💸 UDHAAR STORY - 3/10\n😎  💸  😎\n/👕\\      /👕\\\n 👖        👖\n`Dost ne de diye 😎`",
    "💸 UDHAAR STORY - 4/10\n😍  🍔  😍\n/👕\\      /👕\\\n 👖        👖\n`Burger party 🍔`",
    "💸 UDHAAR STORY - 5/10\n📅  ...  📅\n`1 mahina baad 📅`",
    "💸 UDHAAR STORY - 6/10\n👦  📱  😒\n/👕\\      /👕\\\n 👖        👖\n`Dost: paise kab dega? 😒`",
    "💸 UDHAAR STORY - 7/10\n😅  🙈  😅\n/👕\\\n 👖\n`Seen karke ignore 😅🙈`",
    "💸 UDHAAR STORY - 8/10\n😡  📱  😡\n/👕\\      /👕\\\n 👖        👖\n`Dost gussa 😡`",
    "💸 UDHAAR STORY - 9/10\n🏃  💨  👦\n/👕\\\n 👖\n`Nik block karke bhaag gaya 🏃💨😂`",
    "💸 UDHAAR STORY - 10/10 - THE END\n😭  💸  😭\n`Dost abhi tak rota hai 😭`\n`NIK UDHAAR KING 👑`"
]

# ════════════════════════════════════════════════════════
# 😜 BACKCHODI 5 - NAUGHTY FLIRT (Clean 18+ hint, no explicit)
# ════════════════════════════════════════════════════════
# Note: Ye sirf flirty comedy hai, explicit nahi - Telegram safe
BACK5_FLIRT = [
    "😜 FLIRT STORY - 1/10\n😎        😍\n/👕\\      /👗\\\n 👖        /|.\n`Ladka ladki ko dekha 😎😍`",
    "😜 FLIRT STORY - 2/10\n😉        ☺️\n/👕\\      /👗\\\n 👖        /|.\n`Ladke ne line maari 😉`",
    "😜 FLIRT STORY - 3/10\n😏        😳\n/👕\\      /👗\\\n 👖        /|.\n`Ladki sharmayi 😳`",
    "😜 FLIRT STORY - 4/10\n😍  ☕  😍\n/👕\\      /👗\\\n 👖        /|.\n`Coffee date fix ☕`",
    "😜 FLIRT STORY - 5/10\n😘        😘\n/👕\\      /👗\\\n 👖        /|.\n`Baatein gehraayi 😘`",
    "😜 FLIRT STORY - 6/10\n🥰  🌃  🥰\n/👕\\      /👗\\\n 👖        /|.\n`Raat ko long drive 🌃`",
    "😜 FLIRT STORY - 7/10\n🙈        🙈\n/👕\\      /👗\\\n 👖        /|.\n`Thoda close aaye 🙈`",
    "😜 FLIRT STORY - 8/10\n😳        😳\n/👕\\      /👗\\\n 👖        /|.\n`Dil tez dhadka 💓`",
    "😜 FLIRT STORY - 9/10\n😈        😈\n/👕\\      /👗\\\n 👖        /|.\n`Nik bola: control 😈😂`",
    "😜 FLIRT STORY - 10/10 - THE END\n😂  ❤️  😂\n/👕\\      /👗\\\n 👖        /|.\n`Pyar me izzat hai boss ❤️`\n`NIK FLIRT GURU 👑`"
]

# ════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════
# V3 EXTRA MEME STORIES
# ═══════════════════════════════════════════════
LOVE6_THUG = [
    "😎 THUG LIFE - 1/10\n👦\n/👕\\\n 👖\n`Normal ladka...`",
    "😎 THUG LIFE - 2/10\n😏        😒\n/👕\\      /👗\\\n 👖        /|.\n`Ignore kiya 😒`",
    "😎 THUG LIFE - 3/10\n😎  🕶️  😎\n/👕\\      /👗\\\n 👖        /|.\n`Chashma lagaya 🕶️`",
    "😎 THUG LIFE - 4/10\n😎💨        😳\n/👕\\      /👗\\\n 👖        /|.\n`Attitude dikhaya`",
    "😎 THUG LIFE - 5/10\n😍        😍\n/👕\\      /👗\\\n 👖        /|.\n`Impress ho gayi`",
    "😎 THUG LIFE - 6/10\n😚        😚\n/👕\\      /👗\\\n 👖        /|.\n`Baatein shuru`",
    "😎 THUG LIFE - 7/10\n🥰  🌹  🥰\n/👕\\      /👗\\\n 👖        /|.\n`Rose diya 🌹`",
    "😎 THUG LIFE - 8/10\n😘        😘\n/👕\\      /👗\\\n 👖        /|.\n`Haan bol diya`",
    "😎 THUG LIFE - 9/10\n😎  👫  😎\n/👕\\      /👗\\\n 👖        /|.\n`Couple goals`",
    "😎 THUG LIFE - 10/10 - THE END\n👑  😎  👑\n`NIK THUG KING 👑`",
]
MEME_MUMMY = [
    "😡 MUMMY DAANT - 1/10\n👦  🎮\n/👕\\\n 👖\n`Game khel raha 🎮`",
    "😡 MUMMY DAANT - 2/10\n👩        👦\n/👗\\      /👕\\\n /|\\       👖\n`Mummy: padh le! 😡`",
    "😡 MUMMY DAANT - 3/10\n😒        😡\n/👕\\      /👗\\\n 👖        /|.\n`2 min aur 😒`",
    "😡 MUMMY DAANT - 4/10\n👩  🩴  👦\n/👗\\      /👕\\\n /|\\       👖\n`Chappal nikali 🩴`",
    "😡 MUMMY DAANT - 5/10\n😭  🏃  👩\n/👕\\      /👗\\\n 👖        /|.\n`Bhaaga 🏃😭`",
    "😡 MUMMY DAANT - 6/10\n😅  📚  😅\n/👕\\      /👗\\\n 👖        /|.\n`Padhne ka natak 📚`",
    "😡 MUMMY DAANT - 7/10\n😊  👩  😊\n/👗\\      /👕\\\n /|\\       👖\n`Mummy khush`",
    "😡 MUMMY DAANT - 8/10\n😈  📱  😈\n/👕\\\n 👖\n`Mummy gayi to phone 😈`",
    "😡 MUMMY DAANT - 9/10\n👩  😳  👦\n/👗\\      /👕\\\n /|\\       👖\n`Fir pakda! 😳`",
    "😡 MUMMY DAANT - 10/10 - THE END\n😭  🩴  😭\n`Pit gaya 😭`\n`NIK MEME KING 👑`",
]
MEME_SASTA_NASHA = [
    "🍻 SASTA NASHA - 1/10\n👦👦\n/👕\\/👕\\\n`Shaam plan 🍻`",
    "🍻 SASTA NASHA - 2/10\n🍺  😎  🍺\n/👕\\      /👕\\\n 👖        👖\n`Ek peg 😎`",
    "🍻 SASTA NASHA - 3/10\n🥴        🥴\n/👕\\      /👕\\\n 👖        👖\n`Talli 🥴`",
    "🍻 SASTA NASHA - 4/10\n😵  💬  😵\n/👕\\      /👕\\\n 👖        👖\n`Bakchodi 😵`",
    "🍻 SASTA NASHA - 5/10\n😂  🤣  😂\n/👕\\      /👕\\\n 👖        👖\n`Lotpot 😂`",
    "🍻 SASTA NASHA - 6/10\n😡  💬  😡\n/👕\\      /👕\\\n 👖        👖\n`Ladai 😡`",
    "🍻 SASTA NASHA - 7/10\n😭  🤗  😭\n/👕\\      /👕\\\n 👖        👖\n`Rone lage 😭`",
    "🍻 SASTA NASHA - 8/10\n😴        😴\n/👕\\      /👕\\\n 👖        👖\n`Sadak pe soye 😴`",
    "🍻 SASTA NASHA - 9/10\n👮  😳  👦\n/👕\\      /👕\\\n 👖        👖\n`Police 👮`",
    "🍻 SASTA NASHA - 10/10 - THE END\n🏃  💨  🏃\n`Bhaag gaye 🏃💨`\n`NIK NASHA KING 👑`",
]
SAVED_CHANNEL_FILE = "saved_channel.txt"
SAVED_MSGS_FILE = "saved_msgs.json"
def load_saved_channel():
    try:
        if os.path.isfile(SAVED_CHANNEL_FILE):
            with open(SAVED_CHANNEL_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()
    except: pass
    return None
def save_saved_channel(val):
    try:
        with open(SAVED_CHANNEL_FILE, "w", encoding="utf-8") as f:
            f.write(str(val).strip())
    except: pass
def load_saved_msgs():
    try:
        if os.path.isfile(SAVED_MSGS_FILE):
            with open(SAVED_MSGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except: pass
    return []
def save_saved_msgs(data):
    try:
        with open(SAVED_MSGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except: pass
SAVED_CHANNEL = load_saved_channel()
SAVED_MSG_IDS = load_saved_msgs()

# 🔥 NIK V2 - 10 EMOJI STORIES PACK (5 Love + 5 Backchodi)
# Har story = 10-11 frames, Telegram pe .lovestory1 jaise command se chalegi
# Speed: 0.7 smooth, 0.4 fast


# Helper: use this function for all stories
# await msg.edit(f"```{frame}```")  # monospace me daalo taaki bigde nahi

# ════════════════════════════════════════════════════════
# ❤️ LOVE STORY 1 - COLLEGE WALA PYAR
# ════════════════════════════════════════════════════════
LOVE1_COLLEGE = [
    "❤️ COLLEGE LOVE - 1/11\n👦        📚\n/👕\\       |\n 👖       / \\\n`Pehla din college me...`",
    "❤️ COLLEGE LOVE - 2/11\n😐        😍\n/👕\\      /👗\\\n 👖        /|.\n`Samne se ladki aayi 😍`",
    "❤️ COLLEGE LOVE - 3/11\n😳        ☺️\n/👕\\      /👗\\\n 👖        /|.\n`Nazar mili, dono sharmaye`",
    "❤️ COLLEGE LOVE - 4/11\n😊  📝  😊\n/👕\\      /👗\\\n 👖        /|.\n`Notes share hue 📝`",
    "❤️ COLLEGE LOVE - 5/11\n😉        😆\n/👕\\      /👗\\\n 👖        /|.\n`Roz baatein badhne lagi`",
    "❤️ COLLEGE LOVE - 6/11\n😍  ❤️  😍\n/👕\\/👗\\\n 👖   /|.\n`Dosti pyar me badli ❤️`",
    "❤️ COLLEGE LOVE - 7/11\n😚        😳\n/👕\\      /👗\\\n 👖        /|.\n`Pehla propose 🌹`",
    "❤️ COLLEGE LOVE - 8/11\n😘   😊\n/👕\\/👗\\\n 👖   /|.\n`Haan bol diya! 😘`",
    "❤️ COLLEGE LOVE - 9/11\n🥰  👫  🥰\n/👕\\      /👗\\\n 👖        /|.\n`Canteen me date ☕`",
    "❤️ COLLEGE LOVE - 10/11\n😎        🥰\n/👕\\      /👗\\\n 👖        /|.\n`College khatam, pyar barkarar`",
    "❤️ COLLEGE LOVE - 11/11 - THE END\n👰   🤵\n/👗\\   /👕\\\n /|\\    / \\\n`Shaadi tak pahuch gaye! 🎉👑`\n**NIK DADDY SPECIAL**"
]

# ════════════════════════════════════════════════════════
# ❤️ LOVE STORY 2 - INSTA WALA PYAR
# ════════════════════════════════════════════════════════
LOVE2_INSTA = [
    "💘 INSTA LOVE - 1/10\n👦 📱\n/👕\\\n 👖\n`Ladka Insta scroll kar raha...`",
    "💘 INSTA LOVE - 2/10\n👦  ❤️  👩\n/👕\\      /👗\\\n 👖        /|.\n`Ek reel pe ladki dekhi 😍`",
    "💘 INSTA LOVE - 3/10\n😊  💬  😊\n/👕\\      /👗\\\n 👖        /|.\n`DM kiya: hii 😊`",
    "💘 INSTA LOVE - 4/10\n😒  ...  😐\n/👕\\      /👗\\\n 👖        /|.\n`Seen par reply nahi 😒`",
    "💘 INSTA LOVE - 5/10\n😅  📲  ☺️\n/👕\\      /👗\\\n 👖        /|.\n`Fir meme bheja 😅`",
    "💘 INSTA LOVE - 6/10\n😂        🤣\n/👕\\      /👗\\\n 👖        /|.\n`Has ke reply aaya! 😂`",
    "💘 INSTA LOVE - 7/10\n😍  💬  🥰\n/👕\\      /👗\\\n 👖        /|.\n`Raat bhar chat ❤️`",
    "💘 INSTA LOVE - 8/10\n📞  😍  📞\n/👕\\      /👗\\\n 👖        /|.\n`Pehli call, awaaz sunke fida`",
    "💘 INSTA LOVE - 9/10\n😘  🌹  😘\n/👕\\      /👗\\\n 👖        /|.\n`Milo? Haan! 😘`",
    "💘 INSTA LOVE - 10/10 - THE END\n👫 ❤️ 👫\n`Insta love = real love 🌟`\n**FOLLOW KARO NIK KO 👑**"
]

# ════════════════════════════════════════════════════════
# ❤️ LOVE STORY 3 - OFFICE CRUSH
# ════════════════════════════════════════════════════════
LOVE3_OFFICE = [
    "🏢 OFFICE CRUSH - 1/10\n👦 💼\n/👕\\\n 👖\n`Naya ladka office aaya`",
    "🏢 OFFICE CRUSH - 2/10\n😐        😎\n/👕\\      /👗\\\n 👖        /|.\n`Samne cabin me crush 😎`",
    "🏢 OFFICE CRUSH - 3/10\n☕  😊  ☕\n/👕\\      /👗\\\n 👖        /|.\n`Coffee machine pe mile`",
    "🏢 OFFICE CRUSH - 4/10\n😳        😉\n/👕\\      /👗\\\n 👖        /|.\n`Crush ne wink kiya 😉`",
    "🏢 OFFICE CRUSH - 5/10\n📊  😅  📊\n/👕\\      /👗\\\n 👖        /|.\n`Kaam me galti, crush hasi`",
    "🏢 OFFICE CRUSH - 6/10\n😍  💌  🥰\n/👕\\      /👗\\\n 👖        /|.\n`Chupke se chit bheja 💌`",
    "🏢 OFFICE CRUSH - 7/10\n😚        😊\n/👕\\      /👗\\\n 👖        /|.\n`Lunch saath kiya`",
    "🏢 OFFICE CRUSH - 8/10\n🌃  👫  🌃\n/👕\\      /👗\\\n 👖        /|.\n`Overtime me baatein 🌃`",
    "🏢 OFFICE CRUSH - 9/10\n💍  😍  💍\n/👕\\      /👗\\\n 👖        /|.\n`Propose office party me!`",
    "🏢 OFFICE CRUSH - 10/10 - THE END\n🎉 👫 🎉\n`Boss bhi naach gaya 😂`\n**NIK OFFICE KING 👑**"
]

# ════════════════════════════════════════════════════════
# ❤️ LOVE STORY 4 - LONG DISTANCE
# ════════════════════════════════════════════════════════
LOVE4_DISTANCE = [
    "✈️ DISTANCE LOVE - 1/10\n👦        ✈️        👧\n/👕\\                 /👗\\\n 👖                  /|.\n`Dono alag sheher me ✈️`",
    "✈️ DISTANCE LOVE - 2/10\n😔  📱  😔\n/👕\\      /👗\\\n 👖        /|.\n`Bas video call se milna`",
    "✈️ DISTANCE LOVE - 3/10\n😢        😢\n/👕\\      /👗\\\n 👖        /|.\n`Miss you... 😢`",
    "✈️ DISTANCE LOVE - 4/10\n😊  💬  😊\n/👕\\      /👗\\\n 👖        /|.\n`Raat bhar baatein 💬`",
    "✈️ DISTANCE LOVE - 5/10\n😡  📱  😡\n/👕\\      /👗\\\n 👖        /|.\n`Chhoti si ladai 😡`",
    "✈️ DISTANCE LOVE - 6/10\n😭        😭\n/👕\\      /👗\\\n 👖        /|.\n`Manana padega 😭`",
    "✈️ DISTANCE LOVE - 7/10\n🎁  😍  🎁\n/👕\\      /👗\\\n 👖        /|.\n`Surprise gift bheja 🎁`",
    "✈️ DISTANCE LOVE - 8/10\n😍        🥰\n/👕\\      /👗\\\n 👖        /|.\n`Fir se pyaar badha`",
    "✈️ DISTANCE LOVE - 9/10\n✈️  👦  ✈️\n/👕\\      /👗\\\n 👖        /|.\n`Ticket book, milne ja raha!`",
    "✈️ DISTANCE LOVE - 10/10 - THE END\n👫 ❤️ 👫\n`Mile aur gale lage 🫂`\n`Distance khatam, love jeeta! 🌟`"
]

# ════════════════════════════════════════════════════════
# ❤️ LOVE STORY 5 - SHAADI WALA DRAMA
# ════════════════════════════════════════════════════════
LOVE5_SHAADI = [
    "💒 SHAADI DRAMA - 1/11\n👦        👨‍👩‍👧\n/👕\\       /|\\\n 👖        / \\\n`Ladke ke ghar rishta aaya`",
    "💒 SHAADI DRAMA - 2/11\n😳        😳\n/👕\\      /👗\\\n 👖        /|.\n`Pehli mulaqat, dono sharmaye`",
    "💒 SHAADI DRAMA - 3/11\n😊  ☕  😊\n/👕\\      /👗\\\n 👖        /|.\n`Chai pe charcha ☕`",
    "💒 SHAADI DRAMA - 4/11\n😍        😍\n/👕\\      /👗\\\n 👖        /|.\n`Dono ko pasand aa gaye!`",
    "💒 SHAADI DRAMA - 5/11\n😎  📱  😎\n/👕\\      /👗\\\n 👖        /|.\n`Shaadi se pehle chatting 😉`",
    "💒 SHAADI DRAMA - 6/11\n😡  👨‍👩‍👧  😡\n/👕\\      /👗\\\n 👖        /|.\n`Dahej pe ladai 😡`",
    "💒 SHAADI DRAMA - 7/11\n😭        😭\n/👕\\      /👗\\\n 👖        /|.\n`Shaadi tootne wali thi`",
    "💒 SHAADI DRAMA - 8/11\n😈  👑  😈\n/👕\\      /👗\\\n 👖        /|.\n`Nik ne samjhaya 👑`",
    "💒 SHAADI DRAMA - 9/11\n🥰        🥰\n/👕\\      /👗\\\n 👖        /|.\n`Sab maan gaye!`",
    "💒 SHAADI DRAMA - 10/11\n💃  🥁  🕺\n/👗\\      /👕\\\n /|\\       / \\\n`Dhol baaje, naach gaye 💃`",
    "💒 SHAADI DRAMA - 11/11 - THE END\n👰  ❤️  🤵\n/👗\\      /👕\\\n /|\\       / \\\n`Shaadi ho gayi! 🎉`\n`NIK BLESSINGS 👑`"
]

# ════════════════════════════════════════════════════════
# 😂 BACKCHODI 1 - CHAI TAPRI
# ════════════════════════════════════════════════════════
BACK1_CHAI = [
    "☕ CHAI TAPRI - 1/10\n👦\n/👕\\\n 👖\n`Subah subah neend me 😴`",
    "☕ CHAI TAPRI - 2/10\n👦  ☕\n/👕\\\n 👖\n`Tapri pe pahucha`",
    "☕ CHAI TAPRI - 3/10\n👦  ☕  👨‍🍳\n/👕\\      /👕\\\n 👖        👖\n`Bhaiya ek cutting!`",
    "☕ CHAI TAPRI - 4/10\n😋  ☕  😋\n/👕\\      /👕\\\n 👖        👖\n`Garam chai ki chuski 😋`",
    "☕ CHAI TAPRI - 5/10\n👦💬👦💬👦\n/👕\\ /👕\\ /👕\\\n`Gyaan pelna shuru 😂`",
    "☕ CHAI TAPRI - 6/10\n😡  💬  😡\n/👕\\      /👕\\\n 👖        👖\n`Politics pe ladai 😡`",
    "☕ CHAI TAPRI - 7/10\n😂  ☕  😂\n/👕\\      /👕\\\n 👖        👖\n`Fir has ke sab bhul gaye`",
    "☕ CHAI TAPRI - 8/10\n💸  😳  💸\n/👕\\      /👕\\\n 👖        👖\n`Bill kaun dega? 💸😳`",
    "☕ CHAI TAPRI - 9/10\n🏃  💨  😐\n/👕\\      /👕\\\n 👖        👖\n`Nik bhaag gaya bina bill diye 🏃💨😂`",
    "☕ CHAI TAPRI - 10/10 - THE END\n😭  ☕  😭\n`Dukaan wala roya 😭`\n`NIK TAPRI KING 👑`"
]

# ════════════════════════════════════════════════════════
# 😂 BACKCHODI 2 - EXAM CHORI
# ════════════════════════════════════════════════════════
BACK2_EXAM = [
    "📚 EXAM CHORI - 1/10\n👦  📚\n/👕\\\n 👖\n`Kal exam, kuch nahi padha 😰`",
    "📚 EXAM CHORI - 2/10\n😥  📖  😥\n/👕\\      /👕\\\n 👖        👖\n`Raat bhar jag ke padha`",
    "📚 EXAM CHORI - 3/10\n😴  📖  😴\n/👕\\\n 👖\n`Subah tak so gaya 😴`",
    "📚 EXAM CHORI - 4/10\n👦  🏫  👦\n/👕\\      /👕\\\n 👖        👖\n`Exam hall me entry`",
    "📚 EXAM CHORI - 5/10\n👀  📝  👀\n/👕\\      /👕\\\n 👖        👖\n`Aas paas dekha 👀`",
    "📚 EXAM CHORI - 6/10\n😏  📄  😏\n/👕\\      /👕\\\n 👖        👖\n`Chit nikali 😏`",
    "📚 EXAM CHORI - 7/10\n👨‍🏫  😳  👦\n/👕\\      /👕\\\n 👖        👖\n`Teacher ne dekh liya! 😳`",
    "📚 EXAM CHORI - 8/10\n😭  🙏  👨‍🏫\n/👕\\      /👕\\\n 👖        👖\n`Maafi maangi 🙏`",
    "📚 EXAM CHORI - 9/10\n😈  📝  😈\n/👕\\      /👕\\\n 👖        👖\n`Fir bhi pass 😈`",
    "📚 EXAM CHORI - 10/10 - THE END\n🎉  😎  🎉\n`Nik ke jugad se pass! 👑`\n`BACKBENCHER KING`"
]

# ════════════════════════════════════════════════════════
# 😂 BACKCHODI 3 - GULLY CRICKET
# ════════════════════════════════════════════════════════
BACK3_CRICKET = [
    "🏏 GULLY CRICKET - 1/10\n👦  🏏\n/👕\\\n 👖\n`Gully me match ka plan`",
    "🏏 GULLY CRICKET - 2/10\n👦👦👦\n/👕\\/👕\\/👕\\\n`Team bani 👦👦👦`",
    "🏏 GULLY CRICKET - 3/10\n🏏  😎  🥎\n/👕\\      /👕\\\n 👖        👖\n`Nik batting pe 😎`",
    "🏏 GULLY CRICKET - 4/10\n💥  🏏  💥\n/👕\\      /👕\\\n 👖        👖\n`Chhakka! 💥`",
    "🏏 GULLY CRICKET - 5/10\n😡  🏠  😡\n/👕\\      /👕\\\n 👖        👖\n`Ball ne khidki todi! 😡`",
    "🏏 GULLY CRICKET - 6/10\n👩‍🦳  😠  👦\n/👗\\      /👕\\\n /|\\       👖\n`Aunty aayi daante 😠`",
    "🏏 GULLY CRICKET - 7/10\n😭  🙏  👩‍🦳\n/👕\\      /👗\\\n 👖        /|.\n`Sorry aunty 🙏😭`",
    "🏏 GULLY CRICKET - 8/10\n😈  🏏  😈\n/👕\\      /👕\\\n 👖        👖\n`Fir se khelna shuru 😈`",
    "🏏 GULLY CRICKET - 9/10\n🏆  😎  🏆\n/👕\\      /👕\\\n 👖        👖\n`Nik ki team jeeti 🏆`",
    "🏏 GULLY CRICKET - 10/10 - THE END\n🍻  🎉  🍻\n`Party to banti hai! 🍻`\n`NIK CAPTAIN 👑`"
]

# ════════════════════════════════════════════════════════
# 😂 BACKCHODI 4 - UDHAAR PAISA
# ════════════════════════════════════════════════════════
BACK4_UDHAAR = [
    "💸 UDHAAR STORY - 1/10\n👦  💸\n/👕\\\n 👖\n`Paise khatam 💸😰`",
    "💸 UDHAAR STORY - 2/10\n😊  📱  👦\n/👕\\      /👕\\\n 👖        👖\n`Dost ko call: bhai 500 de de`",
    "💸 UDHAAR STORY - 3/10\n😎  💸  😎\n/👕\\      /👕\\\n 👖        👖\n`Dost ne de diye 😎`",
    "💸 UDHAAR STORY - 4/10\n😍  🍔  😍\n/👕\\      /👕\\\n 👖        👖\n`Burger party 🍔`",
    "💸 UDHAAR STORY - 5/10\n📅  ...  📅\n`1 mahina baad 📅`",
    "💸 UDHAAR STORY - 6/10\n👦  📱  😒\n/👕\\      /👕\\\n 👖        👖\n`Dost: paise kab dega? 😒`",
    "💸 UDHAAR STORY - 7/10\n😅  🙈  😅\n/👕\\\n 👖\n`Seen karke ignore 😅🙈`",
    "💸 UDHAAR STORY - 8/10\n😡  📱  😡\n/👕\\      /👕\\\n 👖        👖\n`Dost gussa 😡`",
    "💸 UDHAAR STORY - 9/10\n🏃  💨  👦\n/👕\\\n 👖\n`Nik block karke bhaag gaya 🏃💨😂`",
    "💸 UDHAAR STORY - 10/10 - THE END\n😭  💸  😭\n`Dost abhi tak rota hai 😭`\n`NIK UDHAAR KING 👑`"
]

# ════════════════════════════════════════════════════════
# 😜 BACKCHODI 5 - NAUGHTY FLIRT (Clean 18+ hint, no explicit)
# ════════════════════════════════════════════════════════
# Note: Ye sirf flirty comedy hai, explicit nahi - Telegram safe
BACK5_FLIRT = [
    "😜 FLIRT STORY - 1/10\n😎        😍\n/👕\\      /👗\\\n 👖        /|.\n`Ladka ladki ko dekha 😎😍`",
    "😜 FLIRT STORY - 2/10\n😉        ☺️\n/👕\\      /👗\\\n 👖        /|.\n`Ladke ne line maari 😉`",
    "😜 FLIRT STORY - 3/10\n😏        😳\n/👕\\      /👗\\\n 👖        /|.\n`Ladki sharmayi 😳`",
    "😜 FLIRT STORY - 4/10\n😍  ☕  😍\n/👕\\      /👗\\\n 👖        /|.\n`Coffee date fix ☕`",
    "😜 FLIRT STORY - 5/10\n😘        😘\n/👕\\      /👗\\\n 👖        /|.\n`Baatein gehraayi 😘`",
    "😜 FLIRT STORY - 6/10\n🥰  🌃  🥰\n/👕\\      /👗\\\n 👖        /|.\n`Raat ko long drive 🌃`",
    "😜 FLIRT STORY - 7/10\n🙈        🙈\n/👕\\      /👗\\\n 👖        /|.\n`Thoda close aaye 🙈`",
    "😜 FLIRT STORY - 8/10\n😳        😳\n/👕\\      /👗\\\n 👖        /|.\n`Dil tez dhadka 💓`",
    "😜 FLIRT STORY - 9/10\n😈        😈\n/👕\\      /👗\\\n 👖        /|.\n`Nik bola: control 😈😂`",
    "😜 FLIRT STORY - 10/10 - THE END\n😂  ❤️  😂\n/👕\\      /👗\\\n 👖        /|.\n`Pyar me izzat hai boss ❤️`\n`NIK FLIRT GURU 👑`"
]

# ════════════════════════════════════════════════════════

# ────────────────────────────────────────────────
# V3 CHANNEL + STORY COMMANDS (20+ features)
# ────────────────────────────────────────────────
@register_cmd("setchannel")
async def cmd_setchannel(event, arg):
    global SAVED_CHANNEL
    try:
        if not arg:
            cur = SAVED_CHANNEL or "Not set"
            return await safe_edit(event, f"📌 Current: `{cur}`\n👉 `.setchannel @channel`")
        try:
            ent = await bot.get_entity(arg)
            if getattr(ent, "username", None):
                SAVED_CHANNEL = f"@{ent.username}"
            else:
                SAVED_CHANNEL = str(ent.id)
        except:
            SAVED_CHANNEL = arg.strip()
        save_saved_channel(SAVED_CHANNEL)
        await safe_edit(event, f"✅ Channel Set → `{SAVED_CHANNEL}`\n📤 `.save` se save karo")
    except Exception as e:
        await safe_edit(event, f"❌ SetChannel → `{e}`")

@register_cmd("save")
async def cmd_save(event, _):
    try:
        if not SAVED_CHANNEL:
            return await safe_edit(event, "❌ Pehle `.setchannel @channel`")
        if not event.is_reply:
            return await safe_edit(event, "❌ Reply karke `.save` karo")
        reply = await event.get_reply_message()
        await safe_edit(event, "💾 Saving...")
        try:
            saved = await bot.forward_messages(SAVED_CHANNEL, reply)
            if isinstance(saved, list): saved = saved[0]
            entry = {"chat_id": saved.chat_id, "msg_id": saved.id, "text": (reply.text or "")[:30]}
            S = load_saved_msgs(); S.append(entry)
            if len(S) > 50: S = S[-50:]
            save_saved_msgs(S)
            await safe_edit(event, f"✅ Saved → `{SAVED_CHANNEL}` 🆔 `{saved.id}`\n💬 `.fwd` se anywhere forward")
        except Exception as e:
            try:
                if reply.media:
                    f = await reply.download_media(file=bytes)
                    bio = BytesIO(f); bio.name="saved"
                    saved = await bot.send_file(SAVED_CHANNEL, bio, caption=reply.text or "")
                else:
                    saved = await bot.send_message(SAVED_CHANNEL, reply.text or "saved")
                await safe_edit(event, f"✅ Saved fallback → `{SAVED_CHANNEL}`")
            except Exception as e2:
                await safe_edit(event, f"❌ Save Fail `{str(e)[:50]}`")
    except Exception as e:
        await safe_edit(event, f"❌ Save → `{e}`")

@register_cmd("savelist")
async def cmd_savelist(event, _):
    try:
        lst = load_saved_msgs()
        if not lst: return await safe_edit(event, "📭 Empty, `.save` karo")
        txt = "💾 **Saved**\n━━━━━━━━━━━━━━━\n"
        for i, e in enumerate(lst[-10:], 1):
            txt += f"{i}. `{e.get('msg_id')}` → `{e.get('text','')[:20]}`\n"
        txt += f"\n📌 `{SAVED_CHANNEL}` → `.fwd`"
        await safe_edit(event, txt)
    except Exception as e:
        await safe_edit(event, f"❌ → `{e}`")

@register_cmd("fwd")
async def cmd_fwd(event, arg):
    try:
        lst = load_saved_msgs()
        if not lst: return await safe_edit(event, "❌ Koi saved nahi")
        last = lst[-1]
        msg = await bot.get_messages(SAVED_CHANNEL, ids=last["msg_id"])
        if not msg: return await safe_edit(event, "❌ Not found")
        if event.is_reply:
            reply = await event.get_reply_message()
            await bot.send_message(event.chat_id, msg, reply_to=reply.id)
        else:
            await bot.send_message(event.chat_id, msg)
        try: await event.delete()
        except: pass
        work = await bot.send_message(event.chat_id, "✅ **WorkDone** 🦫 `Forwarded from @Nikkkwa channel`")
        await asyncio.sleep(2)
        try: await work.delete()
        except: pass
    except Exception as e:
        await safe_edit(event, f"❌ Fwd → `{str(e)[:60]}`")

@register_cmd("delsave")
async def cmd_delsave(event, arg):
    try:
        lst = load_saved_msgs()
        if not arg: return await safe_edit(event, "👉 `.delsave <id>/all`")
        if arg.lower()=="all":
            save_saved_msgs([]); return await safe_edit(event, "🧹 Cleared")
        mid=int(arg); new=[x for x in lst if x.get("msg_id")!=mid]
        save_saved_msgs(new); await safe_edit(event, f"🗑️ Deleted `{mid}` left `{len(new)}`")
    except Exception as e:
        await safe_edit(event, f"❌ → `{e}`")

@register_cmd("alive")
async def cmd_alive(event, _):
    try:
        uptime = time.time() - START_TIME; hrs, rem = divmod(int(uptime), 3600); mins, secs = divmod(rem, 60)
        me = await bot.get_me()
        text = f"╭━━━〔 👑 NIK V3 ALIVE 〕━━━╮\n┃ 👤 {me.first_name} | `{me.id}`\n┃ 🆔 @Nikkkwa\n┃ ⚡ V3 FINAL | {hrs}h {mins}m {secs}s\n┃ 🛡 Muted:{len(muted_users)+len(global_muted)} Raids:{len(reply_users)+len(rr_users)}\n┃ 💾 Saved:{len(load_saved_msgs())} Chan:{SAVED_CHANNEL or 'None'}\n╰━━━━━━━━━━━━━━━━━━━━╯\n✅ ONLINE 🔥"
        await safe_edit(event, text)
    except Exception as e:
        await safe_edit(event, f"❌ Alive → `{e}`")

@register_cmd("help")
async def cmd_help(event, arg):
    await safe_edit(event, "📚 **V3 Help** → `.menu` dekho full 70+ cmds\n💾 `.setchannel` → `.save` → `.fwd` 🦫")

@register_cmd("afk")
async def cmd_afk(event, arg):
    AFK_STATE["active"]=True; AFK_STATE["reason"]=arg or "AFK"; AFK_STATE["since"]=time.time()
    await safe_edit(event, f"💤 AFK ON → `{AFK_STATE['reason']}`")

@register_cmd("unafk")
async def cmd_unafk(event, _):
    AFK_STATE["active"]=False; await safe_edit(event, "✅ AFK OFF")

@register_cmd("ghost")
async def cmd_ghost(event, arg):
    global GHOST_MODE
    if not arg: return await safe_edit(event, f"👻 Ghost: `{'ON' if GHOST_MODE else 'OFF'}`")
    GHOST_MODE = arg.lower() in ["on","enable","start"]
    await safe_edit(event, f"👻 Ghost → `{'ON' if GHOST_MODE else 'OFF'}`")

@register_cmd("echo")
async def cmd_echo(event, arg):
    targets = await get_targets(event, arg)
    for uid in targets: ECHO_USERS.add(uid)
    await safe_edit(event, f"🔁 Echo ON → `{', '.join(map(str, targets))}`")

@register_cmd("unecho")
async def cmd_unecho(event, arg):
    targets = await get_targets(event, arg)
    for uid in targets: ECHO_USERS.discard(uid)
    await safe_edit(event, f"🔕 Echo OFF")

@register_cmd("raidstopall")
async def cmd_raidstopall(event, _):
    cleared=0
    for s in [reply_users, rr_users, flag_users, hrr_users, replygod_users, ECHO_USERS]:
        cleared+=len(s); s.clear()
    replyyorichi_users.clear(); replyking_users.clear()
    for task in list(spray_tasks.values()):
        try: task.cancel()
        except: pass
    spray_tasks.clear()
    await safe_edit(event, f"🧹 All Stopped ✅ Cleared `{cleared}`")

@register_cmd("spam")
async def cmd_spam_v2(event, arg):
    if not arg: return await safe_edit(event, "❌ `.spam <count> <text>`")
    parts=arg.split(maxsplit=1)
    if len(parts)<2: return await safe_edit(event, "❌ Text de")
    count=int(parts[0]); txt=parts[1]
    if count>100: count=100
    await safe_edit(event, f"💣 Spamming `{count}x`...")
    for i in range(count):
        try: await event.reply(txt); await asyncio.sleep(0.7)
        except FloodWaitError as fw: await asyncio.sleep(fw.seconds)
        except: pass
    await event.reply(f"✅ Done `{count}`")

@register_cmd("mspam")
async def cmd_mspam(event, arg):
    if not event.is_reply: return await safe_edit(event, "❌ Reply media `.mspam <n>`")
    reply=await event.get_reply_message()
    count=int(arg) if arg and arg.isdigit() else 5
    if count>30: count=30
    await safe_edit(event, f"📸 Media {count}x...")
    for _ in range(count):
        try: await bot.send_file(event.chat_id, reply.media); await asyncio.sleep(1.2)
        except FloodWaitError as fw: await asyncio.sleep(fw.seconds)
        except: pass
    await safe_edit(event, "✅ Media done")

@register_cmd("delayspam")
async def cmd_delayspam(event, arg):
    parts=arg.split(maxsplit=2)
    if len(parts)<3: return await safe_edit(event, "❌ `.delayspam <delay> <count> <text>`")
    delay=float(parts[0]); count=int(parts[1]); txt=parts[2]
    if delay<0.5: delay=0.5
    await safe_edit(event, f"⏱ {delay}s x {count}")
    for _ in range(count):
        try: await event.reply(txt); await asyncio.sleep(delay)
        except FloodWaitError as fw: await asyncio.sleep(fw.seconds)
        except: pass

@register_cmd("bomb")
async def cmd_bomb(event, arg):
    targets=await get_targets(event, arg)
    if not targets and not event.is_reply:
        msg=await safe_edit(event, "💣 Loading...")
        for f in ["💣.", "💣..", "💣...", "💥 BOOM!", "🔥 Nik bomb 💥", "💀 Bhag bsdk 💀"]:
            try: await msg.edit(f); await asyncio.sleep(0.6)
            except: break
        return
    if targets:
        for uid in targets:
            reply_users.add(uid); rr_users.add(uid)
        await safe_edit(event, f"💣 Bomb → `{', '.join(map(str, targets))}`")

@register_cmd("love")
async def cmd_love(event, arg):
    msg=await safe_edit(event, "❤️ Starting...")
    for f in ["❤️","💖","💝","💞","💓","💗","❤️‍🔥","💘","❤️ Nik loves you ❤️"]:
        try: await msg.edit(f" {f} "*5); await asyncio.sleep(0.5)
        except: break

@register_cmd("gali")
async def cmd_gali(event, arg):
    count=int(arg) if arg and arg.isdigit() else 5
    if count>20: count=20
    await safe_edit(event, f"🔥 Gali {count}x...")
    for _ in range(count):
        try: await event.reply(random.choice(reply_list)); await asyncio.sleep(0.8)
        except FloodWaitError as fw: await asyncio.sleep(fw.seconds)
        except: pass

@register_cmd("tagall")
async def cmd_tagall(event, arg):
    global TAGALL_ACTIVE
    if not event.is_group: return await safe_edit(event, "❌ Group only")
    msg=arg if arg else "📢 Attention!"
    await safe_edit(event, "⚡ Tagging...")
    TAGALL_ACTIVE=True; mentions=[]
    async for user in bot.iter_participants(event.chat_id):
        if not TAGALL_ACTIVE: break
        if user.bot or user.deleted: continue
        mentions.append(f"[{user.first_name}](tg://user?id={user.id})")
        if len(mentions)==5:
            try: await bot.send_message(event.chat_id, msg+"\n"+" ".join(mentions)); mentions=[]; await asyncio.sleep(1.5)
            except FloodWaitError as fw: await asyncio.sleep(fw.seconds)
            except: pass
    if mentions:
        try: await bot.send_message(event.chat_id, msg+"\n"+" ".join(mentions))
        except: pass
    TAGALL_ACTIVE=False; await event.reply("✅ Tag done")

@register_cmd("stop")
async def cmd_stop_tag(event, _):
    global TAGALL_ACTIVE; TAGALL_ACTIVE=False; await safe_edit(event, "🛑 Stopped")

@register_cmd("id")
async def cmd_id_v2(event, arg):
    if event.is_reply:
        reply=await event.get_reply_message(); uid=reply.sender_id
        try: ent=await bot.get_entity(uid)
        except: ent=None
        name=getattr(ent,'first_name','Unknown') if ent else 'Unknown'
        await safe_edit(event, f"🆔 Name:`{name}` ID:`{uid}` Chat:`{event.chat_id}`")
    elif arg:
        try: ent=await bot.get_entity(arg); await safe_edit(event, f"🆔 `{arg}` → `{ent.id}`")
        except Exception as e: await safe_edit(event, f"❌ `{e}`")
    else:
        me=await bot.get_me(); await safe_edit(event, f"🆔 You:`{me.id}` Chat:`{event.chat_id}`")

@register_cmd("purgeall")
async def cmd_purgeall(event, arg):
    count=int(arg) if arg and arg.isdigit() else 10
    if count>100: count=100
    await safe_edit(event, f"🧹 Purging {count}...")
    msgs=[]
    async for msg in bot.iter_messages(event.chat_id, limit=count): msgs.append(msg.id)
    try: await bot.delete_messages(event.chat_id, msgs); await safe_edit(event, f"✅ Purged {len(msgs)}"); await asyncio.sleep(1); await event.delete()
    except Exception as e: await safe_edit(event, f"❌ `{e}`")

# Love/Fun story cmds
@register_cmd("love1")
async def cmd_love1(event, _):
    msg=await safe_edit(event, "🎬 love1...")
    for f in LOVE1_COLLEGE:
        try: await msg.edit(f); await asyncio.sleep(0.65)
        except FloodWaitError as fw: await asyncio.sleep(fw.seconds)
        except: break
@register_cmd("love2")
async def cmd_love2(event, _):
    msg=await safe_edit(event, "🎬 love2...")
    for f in LOVE2_INSTA:
        try: await msg.edit(f); await asyncio.sleep(0.65)
        except: break
@register_cmd("love3")
async def cmd_love3(event, _):
    msg=await safe_edit(event, "🎬 love3...")
    for f in LOVE3_OFFICE:
        try: await msg.edit(f); await asyncio.sleep(0.65)
        except: break
@register_cmd("love4")
async def cmd_love4(event, _):
    msg=await safe_edit(event, "🎬 love4...")
    for f in LOVE4_DISTANCE:
        try: await msg.edit(f); await asyncio.sleep(0.65)
        except: break
@register_cmd("love5")
async def cmd_love5(event, _):
    msg=await safe_edit(event, "🎬 love5...")
    for f in LOVE5_SHAADI:
        try: await msg.edit(f); await asyncio.sleep(0.65)
        except: break
@register_cmd("fun1")
async def cmd_fun1(event, _):
    msg=await safe_edit(event, "😂 fun1...")
    for f in BACK1_CHAI:
        try: await msg.edit(f); await asyncio.sleep(0.6)
        except: break
@register_cmd("fun2")
async def cmd_fun2(event, _):
    msg=await safe_edit(event, "😂 fun2...")
    for f in BACK2_EXAM:
        try: await msg.edit(f); await asyncio.sleep(0.6)
        except: break
@register_cmd("fun3")
async def cmd_fun3(event, _):
    msg=await safe_edit(event, "😂 fun3...")
    for f in BACK3_CRICKET:
        try: await msg.edit(f); await asyncio.sleep(0.6)
        except: break
@register_cmd("fun4")
async def cmd_fun4(event, _):
    msg=await safe_edit(event, "😂 fun4...")
    for f in BACK4_UDHAAR:
        try: await msg.edit(f); await asyncio.sleep(0.6)
        except: break
@register_cmd("fun5")
async def cmd_fun5(event, _):
    msg=await safe_edit(event, "😜 fun5...")
    for f in BACK5_FLIRT:
        try: await msg.edit(f); await asyncio.sleep(0.65)
        except: break
@register_cmd("fun6")
async def cmd_fun6(event, _):
    msg=await safe_edit(event, "😎 thug...")
    for f in LOVE6_THUG:
        try: await msg.edit(f); await asyncio.sleep(0.6)
        except: break
@register_cmd("fun7")
async def cmd_fun7(event, _):
    msg=await safe_edit(event, "😡 mummy...")
    for f in MEME_MUMMY:
        try: await msg.edit(f); await asyncio.sleep(0.6)
        except: break
@register_cmd("fun8")
async def cmd_fun8(event, _):
    msg=await safe_edit(event, "🍻 nasha...")
    for f in MEME_SASTA_NASHA:
        try: await msg.edit(f); await asyncio.sleep(0.6)
        except: break
@register_cmd("lovestory")
async def cmd_lovestory_old(event, _):
    msg=await safe_edit(event, "🎬 classic...")
    src = LOVE_STORY_FRAMES if 'LOVE_STORY_FRAMES' in globals() else LOVE1_COLLEGE
    for f in src:
        try: await msg.edit(f); await asyncio.sleep(0.65)
        except: break

# ────────────────────────────────────────────────
#                   AUTO HANDLER
# ────────────────────────────────────────────────
@bot.on(events.NewMessage)
async def auto_handler(event):

    # ⭐ ignore self messages fast
    if event.out:
        return

    sender = event.sender_id
    chat = event.chat_id

    # ⭐ null safety
    if not sender:
        return

    # 👑 OWNER PROTECT
    if sender == OWNER_ID:
        return

    # ⭐ GLOBAL / LOCAL MUTE ENGINE
    if sender in global_muted or sender in muted_users:
        try:
            await event.delete()
        except:
            pass
        return

    # ⭐ GROUP LOCK ENGINE
    if chat in group_locks:
        try:
            if not is_admin(sender):
                try:
                    await event.delete()
                except:
                    pass
                return
        except:
            pass

    # ⭐ MAIN AUTO ACTION ENGINE
    try:

        # 🔥 REPLY RAID
        if sender in reply_users:
            try:
                await event.reply(random.choice(reply_list))
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
            except:
                pass

        # 💥 REPLY GOD (multi burst)
        if sender in replygod_users:
            try:
                for _ in range(3):
                    await event.reply(random.choice(reply_texts))
                    await asyncio.sleep(0.5)
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
            except:
                pass

        # 🌊 FLAG RAID
        if sender in flag_users:
            try:
                await event.reply(random.choice(flag_texts))
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
            except:
                pass

        # 💜 HEART RAID
        if sender in hrr_users:
            try:
                await event.reply(random.choice(heart_replies))
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
            except:
                pass

        # 🤣 RR RAID (GLOBAL)
        if sender in rr_users:
            try:
                bot_msg = await event.reply(
                    random.choice(fun_texts)
                )

                try:
                    await bot(functions.messages.SendReactionRequest(
                        peer=chat,
                        msg_id=bot_msg.id,
                        reaction=[types.ReactionEmoji(
                            emoticon="🤣"
                        )]
                    ))
                except:
                    pass

            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
            except:
                pass

        # ☄️ REPLY Nik (LIMITED COUNT)
        if sender in replyking_users:
            try:
                data = replyking_users.get(sender)

                if not data:
                    return

                count = int(data.get("count", 0))
                text = data.get("text", "")

                if count > 0:
                    await event.reply(text)
                    data["count"] = count - 1
                else:
                    replyking_users.pop(sender, None)

            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
            except:
                pass

    except Exception as e:
        print(f"[AUTO_HANDLER_ERR] {str(e)[:80]}")


@bot.on(events.NewMessage(outgoing=True))
async def auto_react(event):

    # ⭐ FAST EXIT
    emoji = auto_react_emoji
    if not emoji:
        return

    # ⭐ MESSAGE VALIDATION
    msg_id = event.id
    chat = event.chat_id

    if not msg_id or not chat:
        return

    try:

        # ⭐ REACTION ENGINE
        await bot(functions.messages.SendReactionRequest(
            peer=chat,
            msg_id=msg_id,
            reaction=[
                types.ReactionEmoji(
                    emoticon=emoji
                )
            ]
        ))

    except FloodWaitError as fw:
        try:
            await asyncio.sleep(fw.seconds)
        except:
            pass

    except RPCError:
        # ⭐ silent rpc fail safe
        pass

    except Exception:
        # ⭐ unknown crash isolation
        pass

# ────────────────────────────────────────────────
#                   COMMAND HANDLER
# ────────────────────────────────────────────────
@bot.on(events.NewMessage)
async def dispatcher(event):

    text = event.raw_text

    # ⭐ basic validation ultra fast
    if not text:
        return

    if not text.startswith("."):
        return

    # ⭐ safe split engine (never IndexError)
    body = text[1:].strip()

    if not body:
        return

    parts = body.split(maxsplit=1)

    cmd = parts[0].lower().strip()
    arg = parts[1].strip() if len(parts) > 1 else ""

    # ⭐ command lookup safety
    cmd_data = commands.get(cmd)
    if not cmd_data:
        return

    sender = event.sender_id

    # ⭐ null sender protection (channel / anon admin)
    if not sender:
        return

    # ⚡ permission branch
    if sender != OWNER_ID:

        if sender not in admins:
            try:
                await event.reply(
                    "👑 𝐍ɪᴋ 𝐃ᴀᴅᴅ𝐘 👑  𝐊ᴏ 𝐁ᴀᴀᴘ 𝐁ᴀɴᴀ 𝐑ᴀɴᴅɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐋ᴀᴅᴋᴇ 🤩🖕🏻"
                )
            except:
                pass
            return

        if cmd in {"copy", "normal", "addadmin", "deladmin", "admins"}:
            await safe_edit(event, "❌ 𝐎ᴡɴᴇʀ 𝐎ɴʟʏ 𝐂ᴍᴅ")
            return

    # ⭐ group restriction engine
    if cmd_data.get("group_only"):
        try:
            if not event.is_group:
                await safe_edit(event, "⚠️ 𝐆ʀᴏᴜᴘ 𝐎ɴʟʏ 𝐂ᴏᴍᴍᴀɴᴅ")
                return
        except:
            return

    # ⭐ reply requirement engine
    if cmd_data.get("needs_reply"):
        try:
            if not event.is_reply and not arg:
                await safe_edit(
                    event,
                    f"❌ 𝐑ᴇᴘʟʏ 𝐎ʀ 𝐏ᴀss 𝐓ᴀʀɢᴇᴛ\n👉 .{cmd} @user / id"
                )
                return
        except:
            return

    # ⭐ command execution core
    try:

        await cmd_data["func"](event, arg)

    except FloodWaitError as e:
        try:
            await safe_edit(
                event,
                f"⏳ 𝐅ʟᴏᴏᴅ𝐖ᴀɪᴛ → `{e.seconds}s`"
            )
        except:
            pass

    except Exception as e:
        try:
            await safe_edit(
                event,
                f"❌ 𝐄ʀʀᴏʀ → `{str(e)[:50]}`"
            )
        except:
            pass
# ────────────────────────────────────────────────
#                   START
# ────────────────────────────────────────────────
async def main():

    try:
        # ⭐ start engine
        await bot.start()

        me = await bot.get_me()

        uname = f"@{me.username}" if me.username else "NoUsername"

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🤖 USERBOT STARTED SUCCESSFULLY")
        print(f"👤 Logged in as → {me.first_name} ({uname})")
        print(f"🆔 User ID → {me.id}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # ⭐ connection watchdog
        while True:
            try:
                await bot.run_until_disconnected()
                break
            except (ConnectionError, OSError):
                print("⚠️ Connection Lost → Reconnecting...")
                await asyncio.sleep(3)

    except KeyboardInterrupt:
        print("\n🛑 Userbot stopped manually")

    except Exception as e:
        print(f"\n❌ Startup Error → {str(e)[:80]}")

    finally:
        try:
            if bot.is_connected():
                await bot.disconnect()
        except:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:
        # ⭐ event loop reuse fix (pydroid / termux)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())