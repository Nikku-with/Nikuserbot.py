# ══════════════════════════════════════════════════════════════
#   ♛  NIK USERBOT  ♛        @Nikkkwa
#   Single-file Telethon userbot  ·  Global mode  ·  v1
# ══════════════════════════════════════════════════════════════

import asyncio
import os
import time
import json
import random
import glob
from io import BytesIO
from typing import Dict, Set, Optional, Any

import requests
import qrcode
from gtts import gTTS

from telethon import TelegramClient, events, functions, types
from telethon.errors import FloodWaitError, RPCError, MessageNotModifiedError

# ── event-loop guard (Python 3.12+ / Termux / Pydroid) ──
try:
    asyncio.get_running_loop()
except RuntimeError:
    try:
        _loop = asyncio.get_event_loop()
        if _loop.is_closed():
            raise RuntimeError
    except Exception:
        asyncio.set_event_loop(asyncio.new_event_loop())


# ══════════════════════════════════════════════════════════════
#                          CONFIG
# ══════════════════════════════════════════════════════════════
# Credentials env se aayengi; fallback wahi purane values hain.
API_ID = int(os.environ.get("API_ID") or 30157921)
API_HASH = os.environ.get("API_HASH") or "32bdfcd45922c3abcf4d956fda29e747"
OWNER_ID = int(os.environ.get("OWNER_ID") or 8742036730)
SESSION = os.environ.get("SESSION") or "aeris"

BOT_NAME = "NIK USERBOT"
VERSION = "v1"
OWNER_TAG = "@Nikkkwa"
PREFIX = "."
LOCK_DELAY = 0.3          # locked chat me msg delete hone ka delay (seconds)
STORY_DELAY = 1.6         # animation frame delay (seconds)
START_TIME = time.time()

BASE_DIR = os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, "data")
DOWNLOAD_PATH = os.path.join(BASE_DIR, "downloads")
TEMP_PATH = os.path.join(BASE_DIR, "temp")
for _p in (DATA_DIR, DOWNLOAD_PATH, TEMP_PATH):
    os.makedirs(_p, exist_ok=True)

SESSION_IS_STRING = len(SESSION) > 30 and ":" in SESSION
print(f"♛ {BOT_NAME} {VERSION} | {OWNER_TAG} | session: {SESSION[:12]}...")

try:
    if SESSION_IS_STRING:
        from telethon.sessions import StringSession
        bot = TelegramClient(StringSession(SESSION), API_ID, API_HASH,
                             auto_reconnect=True, connection_retries=10,
                             retry_delay=3, flood_sleep_threshold=60)
    else:
        bot = TelegramClient(SESSION, API_ID, API_HASH,
                             auto_reconnect=True, connection_retries=10,
                             retry_delay=3, flood_sleep_threshold=60)
except Exception as _e:
    print(f"[CLIENT ERROR] {_e}")
    raise


# ══════════════════════════════════════════════════════════════
#                          STORAGE
# ══════════════════════════════════════════════════════════════
F_ADMINS = "admins.json"
F_NOTES = "notes.json"
F_BANNER = "banner.json"
F_FILTERS = "filters.json"
F_BLACKLIST = "blacklist.json"
F_BCDB = "bcdb.json"
F_GBAN = "gban.json"
F_GMUTE = "gmute.json"
F_LOCKS = "locks.json"
F_AUTOREAD = "autoread.json"
F_AREPLY = "areply.json"
F_SAVED_CH = "saved_channel.json"
F_SAVED_MSGS = "saved_msgs.json"
F_AUTOBR = "autobc.json"
F_AUTOFW = "autofw.json"


def load_json(name: str, default: Any):
    path = os.path.join(DATA_DIR, name)
    try:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"[LOAD {name}] {str(e)[:60]}")
    return default


def save_json(name: str, data: Any) -> bool:
    path = os.path.join(DATA_DIR, name)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[SAVE {name}] {str(e)[:60]}")
        return False


# ══════════════════════════════════════════════════════════════
#                        RUNTIME STATE
# ══════════════════════════════════════════════════════════════
ADMINS: Set[int] = set(int(x) for x in load_json(F_ADMINS, []))
NOTES: Dict[int, str] = {int(k): v for k, v in load_json(F_NOTES, {}).items()}

FILTERS: Dict[str, Dict[str, Any]] = load_json(F_FILTERS, {})
BLACKLIST: Set[int] = set(int(x) for x in load_json(F_BLACKLIST, []))
BCDB: Set[int] = set(int(x) for x in load_json(F_BCDB, []))
GBAN: Set[int] = set(int(x) for x in load_json(F_GBAN, []))
GMUTE: Set[int] = set(int(x) for x in load_json(F_GMUTE, []))
LOCKS: Dict[str, list] = load_json(F_LOCKS, {})
AUTOREAD: Set[str] = set(load_json(F_AUTOREAD, []))

SAVED_CHANNEL = load_json(F_SAVED_CH, None)
SAVED_MSGS: list = load_json(F_SAVED_MSGS, [])

AUTOBR: Dict[str, Any] = load_json(F_AUTOBR, {
    "on": False, "chat_id": None, "msg_id": None, "text": "", "delay": 120,
})
AUTOFW: Dict[str, Any] = load_json(F_AUTOFW, {
    "on": False, "chat_id": None, "msg_id": None, "delay": 120,
})
AUTOBR_TASK: Optional[asyncio.Task] = None
AUTOFW_TASK: Optional[asyncio.Task] = None

AREPLY: Optional[str] = load_json(F_AREPLY, None)
MENU_BANNER = load_json(F_BANNER, None)          # [chat_id, msg_id]

# raid sets
reply_users: Set[int] = set()
rr_users: Set[int] = set()
flag_users: Set[int] = set()
hrr_users: Set[int] = set()
replygod_users: Set[int] = set()
replyyorichi_users: Dict[int, Dict[str, Any]] = {}
replyking_users: Dict[int, Dict[str, Any]] = {}   # .nikreply
ECHO_USERS: Set[int] = set()

MUTED: Set[int] = set()          # local delete-mute (is chat)
GLOBAL_MUTED: Set[int] = set()   # local delete-mute (har jagah)

spray_tasks: Dict[int, asyncio.Task] = {}
spam_tasks: Dict[int, asyncio.Task] = {}

AFK = {"active": False, "reason": None, "since": None}
AFK_LAST: Dict[int, float] = {}
GHOST = {"on": False, "delay": 30}
AUTO_REACT_EMOJI: Optional[str] = None
TAGALL_ACTIVE = False
COMMAND_COOLDOWN: Dict[int, float] = {}

FASTGC_STATE: Dict[str, Any] = {"active": False, "template": None,
                                "task": None, "chat_id": None}
GC_FAST_EMOJIS = ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎",
                  "🩷", "🩵", "🩶", "💖", "💘", "💝", "💗", "💓", "💞",
                  "💕", "💟", "❣️", "❤️‍🔥", "❤️‍🩹"]

CLONE_ACTIVE = False
LAST_CLONE_ID: Optional[int] = None
CLONE_DATA: Dict[str, Any] = {}

ADD_BOTS_LIST = ["Nik6_bot", "Nik5bot", "Nik_3_bot", "Nik_2bot", "Nik7bot",
                 "Nik_8bot", "Nik1bot", "Nik_10ibot", "Nik4_bot", "Nik_6bot"]


# ══════════════════════════════════════════════════════════════
#                           HELPERS
# ══════════════════════════════════════════════════════════════
def is_owner(uid: Optional[int]) -> bool:
    return bool(uid) and uid == OWNER_ID


def is_admin(uid: Optional[int]) -> bool:
    return bool(uid) and (uid == OWNER_ID or uid in ADMINS)


async def eor(event, text: str, **kw):
    """edit-or-reply — hamesha ek Message object return karta hai (ya None)."""
    if not text:
        return None
    try:
        uid = event.sender_id
        now = time.time()
        if uid in COMMAND_COOLDOWN and now - COMMAND_COOLDOWN[uid] < 0.3:
            await asyncio.sleep(0.3)
        COMMAND_COOLDOWN[uid] = now
    except Exception:
        pass
    try:
        return await event.edit(text, **kw)
    except FloodWaitError as fw:
        try:
            await asyncio.sleep(min(fw.seconds, 10))
            return await event.edit(text, **kw)
        except Exception:
            pass
    except Exception:
        pass
    try:
        return await event.reply(text, **kw)
    except Exception:
        return None


async def silent_delete(event):
    try:
        await event.delete()
    except Exception:
        pass


def safe_int(value, default=0):
    """int() jo kabhi crash na kare (Telegram kabhi-kabhi peer string deta hai)."""
    try:
        return int(value)
    except Exception:
        return default


async def get_targets(event, arg: str = "") -> Set[int]:
    """reply + @user/id/username se user id nikalta hai (khud ko chhod kar)."""
    targets: Set[int] = set()
    if event.is_reply:
        try:
            r = await event.get_reply_message()
            if r and r.sender_id:
                targets.add(int(r.sender_id))
        except Exception:
            pass
    if arg:
        for part in arg.strip().split():
            if not part:
                continue
            if part.isdigit():
                targets.add(int(part))
                continue
            try:
                ent = await bot.get_entity(part)
                if ent and getattr(ent, "id", None):
                    targets.add(int(ent.id))
            except Exception:
                pass
    try:
        me = await bot.get_me()
        targets.discard(me.id)
    except Exception:
        pass
    return targets


async def resolve_uid(event, arg: str = ""):
    """ek single user id (reply / @user / id) + reply message."""
    if event.is_reply:
        try:
            r = await event.get_reply_message()
            if r and r.sender_id:
                return int(r.sender_id), r
        except Exception:
            pass
    tok = (arg or "").strip().split()[0] if arg else ""
    if tok:
        try:
            ent = await bot.get_entity(tok)
            if ent and getattr(ent, "id", None):
                return int(ent.id), None
        except Exception:
            if tok.lstrip("-").isdigit():
                return int(tok), None
    return None, None


async def play_frames(event, frames, title: str = "", delay: float = 0):
    """ASCII/emoji story ko frame-by-frame chalata hai.
    Har frame code-block me jaata hai (isliye art bigadti nahi)
    aur purane data me likha literal '\\n' bhi theek ho jaata hai."""
    d = delay or STORY_DELAY
    msg = await eor(event, f"❖ {title} ⟡ starting…")
    if msg is None:
        return
    for raw in frames:
        frame = raw.replace("\\n", "\n")
        body = f"```\n{frame}\n```"
        try:
            await msg.edit(body)
        except FloodWaitError as fw:
            await asyncio.sleep(min(fw.seconds + 1, 20))
            try:
                await msg.edit(body)
            except Exception:
                pass
        except MessageNotModifiedError:
            pass
        except Exception:
            break
        await asyncio.sleep(d)


def media_kinds(msg) -> Set[str]:
    """message ke liye lock-types ka set banata hai."""
    kinds = {"all", "msg"}
    media = getattr(msg, "media", None)
    if media is None:
        kinds.add("text")
    else:
        kinds.add("media")
        if isinstance(media, types.MessageMediaPhoto):
            kinds.add("photo")
        elif isinstance(media, types.MessageMediaDocument):
            doc = getattr(media, "document", None)
            if doc is not None:
                for attr in getattr(doc, "attributes", []) or []:
                    if isinstance(attr, types.DocumentAttributeSticker):
                        kinds.add("sticker")
                    elif isinstance(attr, types.DocumentAttributeAnimated):
                        kinds.add("gif")
                    elif isinstance(attr, types.DocumentAttributeVideo):
                        kinds.add("video")
                    elif isinstance(attr, types.DocumentAttributeAudio):
                        kinds.add("audio")
                        if getattr(attr, "voice", False):
                            kinds.add("voice")
                    elif isinstance(attr, types.DocumentAttributeFilename):
                        kinds.add("document")
                kinds.add("document")
        elif isinstance(media, types.MessageMediaWebPage):
            kinds.add("webpage")
            kinds.add("link")
        elif isinstance(media, types.MessageMediaContact):
            kinds.add("contact")
        elif isinstance(media, types.MessageMediaGeo):
            kinds.add("location")
        elif isinstance(media, types.MessageMediaPoll):
            kinds.add("poll")
        elif isinstance(media, types.MessageMediaDice):
            kinds.add("dice")
        elif isinstance(media, types.MessageMediaGame):
            kinds.add("game")
        elif isinstance(media, types.MessageMediaInvoice):
            kinds.add("invoice")
    if getattr(msg, "forward", None):
        kinds.add("forward")
    if getattr(msg, "via_bot_id", None):
        kinds.add("inline")
    txt = getattr(msg, "message", "") or ""
    if "http://" in txt or "https://" in txt or "t.me/" in txt or "www." in txt:
        kinds.add("link")
    if txt.startswith((".", "/", "!", "#", "$")):
        kinds.add("command")
    return kinds


LOCK_TYPES = ["all", "msg", "text", "media", "photo", "video", "document",
              "sticker", "gif", "audio", "voice", "link", "forward",
              "command", "inline", "poll", "contact", "location", "game",
              "dice", "webpage"]


def autoread_match(event) -> bool:
    if not AUTOREAD:
        return False
    if "all" in AUTOREAD:
        return True
    if event.is_group and "group" in AUTOREAD:
        return True
    if event.is_private and "private" in AUTOREAD:
        return True
    if getattr(event, "is_channel", False) and "channel" in AUTOREAD:
        return True
    return False


async def broadcast_targets(kind: str):
    if kind == "db":
        return list(BCDB)
    out = []
    try:
        async for d in bot.iter_dialogs():
            try:
                if d.is_group and kind in ("group", "all"):
                    out.append(d.id)
                elif d.is_user and kind in ("private", "all"):
                    out.append(d.id)
                elif getattr(d, "is_channel", False) and kind in ("channel", "all"):
                    out.append(d.id)
            except Exception:
                continue
    except Exception:
        pass
    return out


# ══════════════════════════════════════════════════════════════
#                        TEXT LISTS (raid)
# ══════════════════════════════════════════════════════════════
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
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन  𝐍ɪᴋ /\\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ  𝐍ɪᴋ बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके MOAN करती है ! 🛐","⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद  𝐍ɪᴋ बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ  𝐍ɪᴋ बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को  𝐍ɪᴋ बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन  𝐍ɪᴋ /\\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ  𝐍ɪᴋ बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके MOAN करती है ! 🛐","⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद  𝐍ɪᴋ बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ  𝐍ɪᴋ बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को  𝐍ɪᴋ बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन  𝐍ɪᴋ /\\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ  𝐍ɪᴋ बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके MOAN करती है ! 🛐","⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद  𝐍ɪᴋ  बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ  𝐍ɪᴋ बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को  𝐍ɪᴋ बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन  𝐍ɪᴋ /\\~ 👑 बाप से सही chudi 🥵🔥",
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


# ══════════════════════════════════════════════════════════════
#                        STORY FRAMES
# ══════════════════════════════════════════════════════════════
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


# ══════════════════════════════════════════════════════════════
#                       COMMAND REGISTRY
# ══════════════════════════════════════════════════════════════
commands: Dict[str, Dict[str, Any]] = {}
aliases: Dict[str, str] = {}


def register_cmd(*names, needs_reply: bool = False,
                 group_only: bool = False, owner_only: bool = False):
    def decorator(func):
        main_name = None
        for raw in names:
            key = (raw or "").lower().strip()
            if not key:
                continue
            if key in commands:
                raise ValueError(f"Duplicate command: {key}")
            commands[key] = {
                "func": func,
                "needs_reply": bool(needs_reply),
                "group_only": bool(group_only),
                "owner_only": bool(owner_only),
            }
            if main_name is None:
                main_name = key
            else:
                aliases[key] = main_name
        return func
    return decorator


OWNER_ONLY_EXTRA = {"copy", "normal", "addadmin", "deladmin", "admins",
                    "gban", "ungban", "gbanlist", "gmute", "ungmute",
                    "gmutelist", "gcast", "ucast", "bc", "autobc", "autofw",
                    "add-bcdb", "del-bcdb", "join", "leave", "purgeall",
                    "fastgc", "addbots", "spray", "dspray"}


# ══════════════════════════════════════════════════════════════
#                      ᴄᴏʀᴇ
# ══════════════════════════════════════════════════════════════
@register_cmd("menu")
async def cmd_menu(event, _):
    menu = f"""╭──────〔 ♛ 𝐍𝐈𝐊 𝐔𝐒𝐄𝐑𝐁𝐎𝐓 ♛ 〕──────╮
┃ 👑 Owner ◂ {OWNER_TAG}
┃ ❖ Build ◂ {VERSION}
┃ 🛰️ Mode ◂ Global
╰──────────────────────────╯

╭─〔 ⚜️ 𝐂𝐎𝐑𝐄 〕─╮
│ ⟡ .alive   ⟡ .ping
│ ⟡ .status  ⟡ .menu
│ ⟡ .id      ⟡ .info
│ ⟡ .help    ⟡ .speed
╰──────────╯

╭─〔 💬 𝐌𝐄𝐒𝐒𝐀𝐆𝐈𝐍𝐆 〕─╮
│ ➤ .hy .del .forward .save
│ ➤ .purge <count> / reply se
│ ➤ .purgeme <n> .delmine <n>
│ ➤ .filter <word> .filters .unfilter
│ ➤ .setchannel .savelist .fwd .delsave
╰──────────────╯

╭─〔 👁️ 𝐀𝐔𝐓𝐎 〕─╮
│ ➤ .autoread group/private/channel/all on/off
│ ➤ .areply <text> .stopareply
│ ➤ .afk .unafk  •  .ghost on/off
│ ➤ .echo .unecho  •  .ar .sar
╰────────╯

╭─〔 🚫 𝐁𝐋𝐀𝐂𝐊𝐋𝐈𝐒𝐓 〕─╮
│ ➤ .addbl .delbl .listbl
│ ➤ .add-bcdb .del-bcdb .list-bcdb
│ ➤ .join <link> .leave
╰─────────────╯

╭─〔 📣 𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓 〕─╮
│ ➤ .gcast .ucast
│ ➤ .bc group/all/private/db
│ ➤ .autobc add/on/off/get/del/delay
│ ➤ .autofw add/on/off/get/del/delay
╰────────────╯

╭─〔 🛡️ 𝐆𝐑𝐎𝐔𝐏 𝐌𝐎𝐃 〕─╮
│ ➤ .kick / .delkick @/reply/ID
│ ➤ .ban / .delban .unban
│ ➤ .mute / .delmute .unmute .getmute
│ ➤ .staff .promote .fullpromote .demote
│ ➤ .title @user <title> .pin .unpin
│ ➤ .group title/desc <text>
│ ➤ .lock <type> .unlock <type> .locks
╰──────────────╯

╭─〔 🌐 𝐆𝐋𝐎𝐁𝐀𝐋 〕─╮
│ ➤ .gban .ungban .gbanlist
│ ➤ .gmute .ungmute .gmutelist
╰─────────╯

╭─〔 🔥 𝐑𝐀𝐈𝐃 〕─╮
│ ➤ .reply .sreply  •  .rr .srr
│ ➤ .flag .sflag    •  .hrr .shrr
│ ➤ .replygod .sgod
│ ➤ .replyyorichi <text> <count> .syorichi
│ ➤ .nikreply <count> <text>  •  .nik
│ ➤ .raidstopall  •  .bomb .gali <n>
╰────────╯

╭─〔 💣 𝐒𝐏𝐀𝐌 〕─╮
│ ➤ .spray / .dspray
│ ➤ .spam <n> <text>  •  .mspam <n>
│ ➤ .delayspam <delay> <n> <text>
│ ➤ .purgeall <n>  •  .tagall .stop
╰────────╯

╭─〔 ⚡ 𝐆𝐂 𝐓𝐎𝐎𝐋𝐒 〕─╮
│ ➤ .fastgc set <title {{emoji}}> / stop
│ ➤ .addbots <n>  •  .addadmin .deladmin .admins
╰──────────╯

╭─〔 🛠️ 𝐓𝐎𝐎𝐋𝐒 〕─╮
│ ➤ .tts .qrcode .fancy .style .emoji
│ ➤ .calc .weather .ip .short
│ ➤ .music <song>  •  .copy .normal
╰────────╯

╭─〔 📝 𝐍𝐎𝐓𝐄𝐒 〕─╮
│ ➤ .notesadd .noteslist .notesdelete
│ ➤ .banner .rembanner
╰────────╯

╭─〔 🎬 𝐒𝐓𝐎𝐑𝐈𝐄𝐒 〕─╮
│ ⟡ Love  ◂ .love1 .love2 .love3 .love4 .love5
│ ⟡       ◂ .lovestory
│ ⟡ Fun   ◂ .fun1 .fun2 .fun3 .fun4
│ ⟡       ◂ .fun5 .fun6 .fun7 .fun8
│ ⟡ Speed ◂ .speed <seconds>
╰──────────╯
━━━━━━━━━━━━━━━━━━━━
✨ Powered by {OWNER_TAG} ♛
"""
    await eor(event, menu)
    if MENU_BANNER:
        try:
            chat_id, msg_id = MENU_BANNER
            msg = await bot.get_messages(chat_id, ids=msg_id)
            if msg and msg.media:
                await bot.send_file(event.chat_id, file=msg.media,
                                    caption=f"♛ {BOT_NAME} enters ✦")
        except Exception:
            pass


@register_cmd("alive")
async def cmd_alive(event, _):
    up = int(time.time() - START_TIME)
    h, rem = divmod(up, 3600)
    m, s = divmod(rem, 60)
    me = await bot.get_me()
    uname = f"@{me.username}" if getattr(me, "username", None) else "—"
    txt = (f"╭────〔 ♛ 𝐀𝐋𝐈𝐕𝐄 〕────╮\n"
           f"┃ 👤 {me.first_name} {uname}\n"
           f"┃ 🆔 `{me.id}`\n"
           f"┃ ❖ {BOT_NAME} {VERSION}\n"
           f"┃ 🛰️ Global\n"
           f"┃ ⏳ Uptime `{h}h {m}m {s}s`\n"
           f"┃ 🔇 Muted `{len(MUTED) + len(GLOBAL_MUTED)}`\n"
           f"┃ 🔥 Raids `{len(reply_users) + len(rr_users) + len(flag_users) + len(hrr_users)}`\n"
           f"┃ 🌐 Gban `{len(GBAN)}` Gmute `{len(GMUTE)}`\n"
           f"┃ 💾 Saved `{len(SAVED_MSGS)}`\n"
           f"╰──────────────╯\n"
           f"✅ Online ✦")
    await eor(event, txt)


@register_cmd("ping")
async def cmd_ping(event, _):
    t0 = time.time()
    msg = await eor(event, "⌁ Pinging…")
    dt = (time.time() - t0) * 1000
    if msg:
        try:
            await msg.edit(f"╭─〔 ⌁ 𝐏𝐈𝐍𝐆 〕─╮\n"
                           f"│ ⏱ `{dt:.2f} ms`\n"
                           f"│ ❖ {BOT_NAME} {VERSION}\n"
                           f"╰────────╯")
        except Exception:
            pass


@register_cmd("status")
async def cmd_status(event, _):
    up = int(time.time() - START_TIME)
    h, rem = divmod(up, 3600)
    m, s = divmod(rem, 60)
    me = await bot.get_me()
    txt = (f"╭────〔 ❖ 𝐒𝐓𝐀𝐓𝐔𝐒 〕────╮\n"
           f"┃ 👤 `{me.first_name}`\n"
           f"┃ 🆔 `{me.id}`\n"
           f"┃ 👑 Owner `{OWNER_ID}`\n"
           f"┃ 🛡️ Admins `{len(ADMINS)}`\n"
           f"┃ 🔇 Muted `{len(MUTED)}` Global `{len(GLOBAL_MUTED)}`\n"
           f"┃ 🔥 Raids `{len(reply_users)}/{len(rr_users)}/{len(flag_users)}/{len(hrr_users)}`\n"
           f"┃ 🌐 Gban `{len(GBAN)}` Gmute `{len(GMUTE)}`\n"
           f"┃ 🚫 Blacklist `{len(BLACKLIST)}`\n"
           f"┃ 📣 BC-DB `{len(BCDB)}`\n"
           f"┃ 🔒 Locked chats `{len(LOCKS)}`\n"
           f"┃ 🗝 Filters `{sum(len(v) for v in FILTERS.values())}`\n"
           f"┃ ⏳ Uptime `{h}h {m}m {s}s`\n"
           f"┃ 💬 Auto-reply `{'on' if AREPLY else 'off'}`\n"
           f"┃ 👁 Auto-read `{','.join(sorted(AUTOREAD)) or 'off'}`\n"
           f"┃ 👻 Ghost `{'on' if GHOST['on'] else 'off'}`\n"
           f"╰────────────╯")
    await eor(event, txt)


@register_cmd("help")
async def cmd_help(event, arg):
    await eor(event, f"📖 Poora list ke liye `.menu` dekho.\n"
                     f"❖ {BOT_NAME} {VERSION} · {OWNER_TAG}\n"
                     f"💡 Har command `{PREFIX}` se shuru hoti hai.")


@register_cmd("id")
async def cmd_id(event, arg):
    if event.is_reply:
        r = await event.get_reply_message()
        uid = r.sender_id
        name = "—"
        try:
            ent = await bot.get_entity(uid)
            name = getattr(ent, "first_name", "—") or "—"
        except Exception:
            pass
        return await eor(event, f"╭─〔 🆔 〕─╮\n│ 👤 `{name}`\n│ 🆔 `{uid}`\n│ 💬 `{event.chat_id}`\n╰──────╯")
    if arg:
        try:
            ent = await bot.get_entity(arg.strip())
            return await eor(event, f"🆔 `{arg}` → `{ent.id}`")
        except Exception as e:
            return await eor(event, f"❌ `{str(e)[:60]}`")
    me = await bot.get_me()
    await eor(event, f"🆔 You `{me.id}` · Chat `{event.chat_id}`")


@register_cmd("info")
async def cmd_info(event, arg):
    target = None
    if event.is_reply:
        r = await event.get_reply_message()
        target = r.sender_id if r else None
    elif arg:
        try:
            ent = await bot.get_entity(arg.strip())
            target = ent.id
        except Exception:
            return await eor(event, "❌ User nahi mila")
    if not target:
        return await eor(event, f"⚠️ `{PREFIX}info` — reply / @user / id")
    try:
        user = await bot.get_entity(target)
        full = await bot(functions.users.GetFullUserRequest(user.id))
    except Exception as e:
        return await eor(event, f"❌ `{str(e)[:60]}`")
    bio = (full.full_user.about or "—").replace("\n", " ")
    uname = f"@{user.username}" if getattr(user, "username", None) else "—"
    name = f"{user.first_name or ''} {user.last_name or ''}".strip() or "—"
    await eor(event, f"╭────〔 👤 𝐈𝐍𝐅𝐎 〕────╮\n"
                     f"┃ ❖ {name}\n"
                     f"┃ 🆔 `{user.id}`\n"
                     f"┃ 🔗 {uname}\n"
                     f"┃ 🤖 Bot `{'yes' if getattr(user, 'bot', False) else 'no'}`\n"
                     f"┃ 📝 {bio[:120]}\n"
                     f"╰────────────╯")


@register_cmd("flip")
async def cmd_flip(event, _):
    msg = await eor(event, "🪙 Tossing…")
    for f in ["🪙", "⟳", "⟲", "◐", "◓"]:
        try:
            await msg.edit(f); await asyncio.sleep(0.25)
        except Exception:
            break
    try:
        await msg.edit(random.choice(["⚜️ Heads", "❖ Tails"]))
    except Exception:
        pass


@register_cmd("dice")
async def cmd_dice(event, arg):
    try:
        await event.delete()
    except Exception:
        pass
    try:
        await bot.send_message(event.chat_id, file=types.InputMediaDice("🎲"))
    except Exception:
        await eor(event, "❌ Dice fail")


@register_cmd("speed")
async def cmd_speed(event, arg):
    global STORY_DELAY
    if not arg:
        return await eor(event, f"🎬 Story speed → `{STORY_DELAY}s`\n"
                                f"👉 `{PREFIX}speed <seconds>` (0.5 – 10)")
    try:
        v = float(arg.split()[0])
    except Exception:
        return await eor(event, "❌ Number do — `.speed 2`")
    v = max(0.5, min(v, 10.0))
    STORY_DELAY = v
    await eor(event, f"🎬 Story speed set → `{STORY_DELAY}s`")


# ══════════════════════════════════════════════════════════════
#                      ᴍᴇssᴀɢɪɴɢ
# ══════════════════════════════════════════════════════════════
@register_cmd("hy")
async def cmd_hy(event, arg):
    """stylish animated greeting — reply karke kisi ko bhi greet kar sakte ho."""
    who = ""
    if event.is_reply:
        try:
            r = await event.get_reply_message()
            ent = await bot.get_entity(r.sender_id)
            who = f"[{ent.first_name}](tg://user?id={ent.id})"
        except Exception:
            who = ""
    tail = f" {who}" if who else ""
    msg = await eor(event, "❖ hey…")
    if msg is None:
        return
    for f in ["❖", "❖ ⟡", "❖ ⟡ ❖", f"𝐇𝐄𝐘{tail} ⟡", f"𝐇𝐄𝐘{tail} ⟡ ✦",
              f"𝐇𝐄𝐘{tail} ⟡ ✦ ⚜️"]:
        try:
            await msg.edit(f); await asyncio.sleep(0.5)
        except Exception:
            break


@register_cmd("del")
async def cmd_del(event, arg):
    if event.is_reply:
        try:
            r = await event.get_reply_message()
            await r.delete()
        except Exception as e:
            return await eor(event, f"❌ Delete nahi hua → `{str(e)[:50]}`")
    try:
        await event.delete()
    except Exception:
        pass


@register_cmd("forward")
async def cmd_forward(event, arg):
    if not event.is_reply:
        return await eor(event, f"❌ Reply karke `{PREFIX}forward <@chat/id>` likho")
    r = await event.get_reply_message()
    dest = arg.strip() if arg else "me"
    try:
        await bot.forward_messages(dest, r)
        await eor(event, f"📤 Forwarded → `{dest}`")
    except Exception as e:
        await eor(event, f"❌ `{str(e)[:70]}`")


@register_cmd("setchannel")
async def cmd_setchannel(event, arg):
    global SAVED_CHANNEL
    if not arg:
        return await eor(event, f"📌 Current → `{SAVED_CHANNEL or 'set nahi'}`\n"
                                f"👉 `{PREFIX}setchannel @channel`")
    val = arg.strip()
    try:
        ent = await bot.get_entity(val)
        val = f"@{ent.username}" if getattr(ent, "username", None) else str(ent.id)
    except Exception:
        pass
    SAVED_CHANNEL = val
    save_json(F_SAVED_CH, SAVED_CHANNEL)
    await eor(event, f"📌 Channel set → `{SAVED_CHANNEL}`\n📤 `{PREFIX}save` se save karo")


@register_cmd("save")
async def cmd_save(event, arg):
    global SAVED_MSGS
    if not SAVED_CHANNEL:
        return await eor(event, f"❌ Pehle `{PREFIX}setchannel @channel` lagao")
    if not event.is_reply:
        return await eor(event, "❌ Kisi message pe reply karke `.save` likho")
    reply = await event.get_reply_message()
    await eor(event, "💾 Saving…")
    sent = None
    try:
        res = await bot.forward_messages(SAVED_CHANNEL, reply)
        sent = res[0] if isinstance(res, list) and res else res
    except Exception:
        sent = None
    if sent is None:
        try:
            sent = await bot.send_message(SAVED_CHANNEL, reply)
        except Exception as e:
            return await eor(event, f"❌ Save fail → `{str(e)[:70]}`")
    try:
        chat_val = getattr(sent, "chat_id", None)
        if chat_val is None or str(chat_val).strip() in ("", "0"):
            chat_val = SAVED_CHANNEL
        elif str(chat_val).lstrip("-").isdigit():
            chat_val = int(chat_val)
    except Exception:
        chat_val = SAVED_CHANNEL
    entry = {
        "chat_id": chat_val,
        "msg_id": int(getattr(sent, "id", 0) or 0),
        "text": (reply.raw_text or "")[:40],
    }
    SAVED_MSGS.append(entry)
    SAVED_MSGS = SAVED_MSGS[-50:]
    save_json(F_SAVED_MSGS, SAVED_MSGS)
    await eor(event, f"💾 Saved → `{SAVED_CHANNEL}` · id `{entry['msg_id']}`\n"
                     f"📤 `{PREFIX}fwd` se wapas bhejo")


@register_cmd("savelist")
async def cmd_savelist(event, arg):
    if not SAVED_MSGS:
        return await eor(event, "📭 Kuch save nahi hai")
    txt = f"💾 𝐒𝐀𝐕𝐄𝐃 (`{SAVED_CHANNEL}`)\n━━━━━━━━━━━━━━━\n"
    for i, e in enumerate(SAVED_MSGS[-15:], 1):
        txt += f"`{i}.` 🆔 `{e.get('msg_id')}` · {(e.get('text') or '')[:24]}\n"
    txt += f"\n📤 `{PREFIX}fwd <number>`"
    await eor(event, txt)


@register_cmd("delsave")
async def cmd_delsave(event, arg):
    global SAVED_MSGS
    if not arg:
        return await eor(event, f"👉 `{PREFIX}delsave <number/all>`")
    if arg.strip().lower() == "all":
        SAVED_MSGS = []
        save_json(F_SAVED_MSGS, SAVED_MSGS)
        return await eor(event, "🧹 Saaf kar diya")
    n = SAVED_MSGS
    try:
        idx = int(arg.strip()) - 1
        if 0 <= idx < len(n):
            n.pop(idx)
    except Exception:
        return await eor(event, "❌ Number galat")
    SAVED_MSGS = n
    save_json(F_SAVED_MSGS, SAVED_MSGS)
    await eor(event, f"🗑️ Deleted · bache `{len(SAVED_MSGS)}`")


@register_cmd("fwd")
async def cmd_fwd(event, arg):
    """saved message ko wapas bhejta hai — reply diya to usi ka reply ban kar."""
    if not SAVED_MSGS:
        return await eor(event, f"❌ Koi saved message nahi — pehle `{PREFIX}save` karo")
    if not SAVED_CHANNEL:
        return await eor(event, f"❌ Pehle `{PREFIX}setchannel @channel` lagao")

    entry = None
    a = (arg or "").strip()
    if a:
        if a.isdigit():
            n = int(a)
            if 1 <= n <= len(SAVED_MSGS):
                entry = SAVED_MSGS[n - 1]
            else:
                for e in SAVED_MSGS:
                    if str(e.get("msg_id")) == a:
                        entry = e
                        break
    if entry is None:
        entry = SAVED_MSGS[-1]

    src = entry.get("chat_id") or SAVED_CHANNEL
    mid = safe_int(entry.get("msg_id"), 0)
    msg = None
    try:
        msg = await bot.get_messages(src, ids=mid)
    except Exception:
        msg = None
    if msg is None:
        return await eor(
            event,
            f"❌ Saved message nahi mila (id `{entry.get('msg_id')}`)\n"
            f"Wajah: message delete ho gaya ya channel badal gaya.\n"
            f"👉 Dobara `{PREFIX}save` karo phir `{PREFIX}fwd`.")

    try:
        if event.is_reply:
            target = await event.get_reply_message()
            await bot.send_message(event.chat_id, msg, reply_to=target.id)
        else:
            try:
                await bot.forward_messages(event.chat_id, mid, from_peer=src)
            except Exception:
                await bot.send_message(event.chat_id, msg)
        try:
            await event.delete()
        except Exception:
            pass
    except Exception as e:
        await eor(event, f"❌ Fwd fail → `{str(e)[:80]}`")


async def _delete_ids(chat, ids):
    done = 0
    for i in range(0, len(ids), 100):
        batch = ids[i:i + 100]
        try:
            await bot.delete_messages(chat, batch)
            done += len(batch)
        except FloodWaitError as fw:
            await asyncio.sleep(min(fw.seconds, 20))
            try:
                await bot.delete_messages(chat, batch)
                done += len(batch)
            except Exception:
                pass
        except Exception:
            pass
        await asyncio.sleep(0.4)
    return done


@register_cmd("purge")
async def cmd_purge(event, arg):
    """reply ke saath → reply se lekar command tak sab uda do
    bina reply → command ke upar wale N purane message uda do"""
    chat = event.chat_id
    ids = []
    if event.is_reply:
        r = await event.get_reply_message()
        lo, hi = min(r.id, event.id), max(r.id, event.id)
        ids = list(range(lo, hi + 1))
    else:
        try:
            n = int((arg or "50").split()[0])
        except Exception:
            n = 50
        n = max(1, min(n, 500))
        async for m in bot.iter_messages(chat, limit=n, max_id=event.id):
            ids.append(m.id)
    if not ids:
        return await eor(event, "⚠️ Koi message nahi mila")
    await eor(event, f"🧹 Purging `{len(ids)}`…")
    done = await _delete_ids(chat, ids)
    conf = await eor(event, f"🧹 Purge done → `{done}` messages")
    await asyncio.sleep(4)
    try:
        await conf.delete()
    except Exception:
        pass


@register_cmd("purgeme", "delmine")
async def cmd_purgeme(event, arg):
    """apne hi messages delete karta hai.
    .purgeme <n>          → is chat me apne last N
    .delmine <n> [@chat]  → specific chat me apne last N"""
    parts = (arg or "").split()
    try:
        n = int(parts[0]) if parts else 20
    except Exception:
        n = 20
    n = max(1, min(n, 500))

    chat = event.chat_id
    if len(parts) > 1:
        tok = parts[1]
        try:
            ent = await bot.get_entity(tok)
            chat = ent.id
        except Exception:
            return await eor(event, f"❌ Chat nahi mila → `{tok}`")

    me = await bot.get_me()
    await eor(event, f"🧹 Apne `{n}` messages dhoondh raha hoon…")
    ids = []
    try:
        async for m in bot.iter_messages(chat, from_user=me.id, limit=n):
            ids.append(m.id)
    except Exception as e:
        return await eor(event, f"❌ `{str(e)[:60]}`")
    if chat == event.chat_id:
        ids.append(event.id)
    if not ids:
        return await eor(event, "⚠️ Koi apna message nahi mila")
    done = await _delete_ids(chat, ids)
    conf = await eor(event, f"🧹 `{done}` apne messages delete kiye")
    await asyncio.sleep(4)
    try:
        await conf.delete()
    except Exception:
        pass


@register_cmd("filter")
async def cmd_filter(event, arg):
    word = (arg or "").strip().lower()
    if not word:
        return await eor(event, f"❌ `{PREFIX}filter <word>` — reply ke saath")
    if not event.is_reply:
        return await eor(event, "❌ Jise reply dena hai us message pe reply karo")
    r = await event.get_reply_message()
    key = str(event.chat_id)
    FILTERS.setdefault(key, {})[word] = {
        "chat_id": int(event.chat_id),
        "msg_id": int(r.id),
        "text": r.raw_text or "",
    }
    save_json(F_FILTERS, FILTERS)
    await eor(event, f"🗝 Filter set → `{word}`")


@register_cmd("filters")
async def cmd_filters(event, arg):
    key = str(event.chat_id)
    data = FILTERS.get(key) or {}
    if not data:
        return await eor(event, "📭 Is chat me koi filter nahi")
    txt = f"🗝 𝐅𝐈𝐋𝐓𝐄𝐑𝐒 ({len(data)})\n━━━━━━━━━━━━━━━\n"
    for i, w in enumerate(sorted(data), 1):
        txt += f"`{i}.` {w}\n"
    await eor(event, txt)


@register_cmd("unfilter")
async def cmd_unfilter(event, arg):
    word = (arg or "").strip().lower()
    key = str(event.chat_id)
    if not word:
        return await eor(event, f"❌ `{PREFIX}unfilter <word>`")
    data = FILTERS.get(key) or {}
    if word not in data:
        return await eor(event, "⚠️ Ye filter hai hi nahi")
    data.pop(word)
    if not data:
        FILTERS.pop(key, None)
    save_json(F_FILTERS, FILTERS)
    await eor(event, f"🗑 Filter hata diya → `{word}`")


# ══════════════════════════════════════════════════════════════
#                         ᴀᴜᴛᴏ
# ══════════════════════════════════════════════════════════════
@register_cmd("autoread")
async def cmd_autoread(event, arg):
    parts = (arg or "").split()
    if len(parts) < 2:
        cur = ", ".join(sorted(AUTOREAD)) or "off"
        return await eor(event, f"👁 Auto-read → `{cur}`\n"
                                f"👉 `{PREFIX}autoread <group|private|channel|all> <on|off>`")
    scope, state = parts[0].lower(), parts[1].lower()
    if scope not in ("group", "private", "channel", "all"):
        return await eor(event, "❌ Scope galat — group / private / channel / all")
    if state in ("on", "enable", "start", "yes", "1"):
        AUTOREAD.add(scope)
        verb = "ON"
    else:
        AUTOREAD.discard(scope)
        verb = "OFF"
    save_json(F_AUTOREAD, sorted(AUTOREAD))
    await eor(event, f"👁 Auto-read `{scope}` → **{verb}**\n"
                     f"Active → `{', '.join(sorted(AUTOREAD)) or 'off'}`")


@register_cmd("areply")
async def cmd_areply(event, arg):
    global AREPLY
    if not arg:
        return await eor(event, f"❌ `{PREFIX}areply <text>`\n"
                                f"Band karne ke liye `{PREFIX}stopareply`")
    AREPLY = arg.strip()
    save_json(F_AREPLY, AREPLY)
    await eor(event, f"💬 Auto-reply ON → `{AREPLY[:60]}`")


@register_cmd("stopareply")
async def cmd_stopareply(event, arg):
    global AREPLY
    AREPLY = None
    save_json(F_AREPLY, None)
    await eor(event, "💬 Auto-reply OFF")


# ══════════════════════════════════════════════════════════════
#                       ʙʟᴀᴄᴋʟɪsᴛ
# ══════════════════════════════════════════════════════════════
@register_cmd("addbl")
async def cmd_addbl(event, arg):
    targets = await get_targets(event, arg)
    if not targets:
        return await eor(event, "❌ Target nahi mila")
    added = [u for u in targets if u not in BLACKLIST]
    BLACKLIST.update(targets)
    save_json(F_BLACKLIST, sorted(BLACKLIST))
    await eor(event, f"🚫 Blacklist +`{len(added)}` → `{', '.join(map(str, sorted(targets)))}`")


@register_cmd("delbl")
async def cmd_delbl(event, arg):
    targets = await get_targets(event, arg)
    if not targets:
        return await eor(event, "❌ Target nahi mila")
    removed = [u for u in targets if u in BLACKLIST]
    BLACKLIST.difference_update(targets)
    save_json(F_BLACKLIST, sorted(BLACKLIST))
    await eor(event, f"♻️ Blacklist −`{len(removed)}`")


@register_cmd("listbl")
async def cmd_listbl(event, arg):
    if not BLACKLIST:
        return await eor(event, "📭 Blacklist khaali hai")
    txt = f"🚫 𝐁𝐋𝐀𝐂𝐊𝐋𝐈𝐒𝐓 ({len(BLACKLIST)})\n━━━━━━━━━━━━━━━\n"
    for i, u in enumerate(sorted(BLACKLIST), 1):
        txt += f"`{i}.` `{u}`\n"
    await eor(event, txt)


@register_cmd("add-bcdb")
async def cmd_add_bcdb(event, arg):
    if arg:
        try:
            ent = await bot.get_entity(arg.strip())
            cid = int(ent.id)
        except Exception:
            return await eor(event, f"❌ Chat nahi mila → `{arg}`")
    else:
        cid = int(event.chat_id)
    BCDB.add(cid)
    save_json(F_BCDB, sorted(BCDB))
    await eor(event, f"📣 BC-DB me add → `{cid}` (total `{len(BCDB)}`)")


@register_cmd("del-bcdb")
async def cmd_del_bcdb(event, arg):
    if arg:
        try:
            ent = await bot.get_entity(arg.strip())
            cid = int(ent.id)
        except Exception:
            return await eor(event, f"❌ Chat nahi mila → `{arg}`")
    else:
        cid = int(event.chat_id)
    BCDB.discard(cid)
    save_json(F_BCDB, sorted(BCDB))
    await eor(event, f"🗑 BC-DB se nikala → `{cid}` (total `{len(BCDB)}`)")


@register_cmd("list-bcdb")
async def cmd_list_bcdb(event, arg):
    if not BCDB:
        return await eor(event, "📭 BC-DB khaali hai\n"
                                f"👉 `{PREFIX}add-bcdb` is chat ko add karega")
    txt = f"📣 𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓 𝐃𝐁 ({len(BCDB)})\n━━━━━━━━━━━━━━━\n"
    for i, c in enumerate(sorted(BCDB), 1):
        txt += f"`{i}.` `{c}`\n"
    await eor(event, txt)


@register_cmd("join")
async def cmd_join(event, arg):
    link = (arg or "").strip()
    if not link:
        return await eor(event, f"❌ `{PREFIX}join <link>`")
    try:
        if "/+" in link or "joinchat" in link:
            h = link.split("+")[-1].split("/")[-1].strip()
            await bot(functions.messages.ImportChatInviteRequest(h))
        else:
            await bot(functions.channels.JoinChannelRequest(link))
        await eor(event, f"📥 Joined → `{link}`")
    except Exception as e:
        await eor(event, f"❌ Join fail → `{str(e)[:70]}`")


@register_cmd("leave")
async def cmd_leave(event, arg):
    chat = event.chat_id
    if arg:
        try:
            ent = await bot.get_entity(arg.strip())
            chat = ent.id
        except Exception:
            return await eor(event, f"❌ Chat nahi mila → `{arg}`")
    try:
        await bot(functions.channels.LeaveChannelRequest(chat))
    except Exception:
        try:
            await bot.delete_dialog(chat)
        except Exception as e:
            return await eor(event, f"❌ Leave fail → `{str(e)[:60]}`")
    await eor(event, f"📤 Left → `{chat}`")


# ══════════════════════════════════════════════════════════════
#                       ʙʀᴏᴀᴅᴄᴀsᴛ
# ══════════════════════════════════════════════════════════════
async def _do_broadcast(event, kind, text, status_msg=None):
    targets = await broadcast_targets(kind)
    if not targets:
        return await eor(event, f"⚠️ `{kind}` ke liye koi chat nahi mili")
    src = None
    if not text and event.is_reply:
        src = await event.get_reply_message()
    ok, fail = 0, 0
    for cid in targets:
        try:
            if src is not None:
                await bot.send_message(cid, src)
            else:
                await bot.send_message(cid, text)
            ok += 1
        except FloodWaitError as fw:
            await asyncio.sleep(min(fw.seconds, 30))
            fail += 1
        except Exception:
            fail += 1
        await asyncio.sleep(0.6)
    res = (f"📣 𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓 [{kind}]\n━━━━━━━━━━━━━━━\n"
           f"✅ Sent `{ok}`\n❌ Fail `{fail}`")
    if status_msg:
        try:
            await status_msg.edit(res)
        except Exception:
            await eor(event, res)
    else:
        await eor(event, res)


@register_cmd("gcast")
async def cmd_gcast(event, arg):
    text = (arg or "").strip()
    if not text and not event.is_reply:
        return await eor(event, f"❌ `{PREFIX}gcast <text>` ya kisi message pe reply")
    st = await eor(event, "📣 Groups me broadcast shuru…")
    await _do_broadcast(event, "group", text, st)


@register_cmd("ucast")
async def cmd_ucast(event, arg):
    text = (arg or "").strip()
    if not text and not event.is_reply:
        return await eor(event, f"❌ `{PREFIX}ucast <text>` ya kisi message pe reply")
    st = await eor(event, "📣 Users ko broadcast shuru…")
    await _do_broadcast(event, "private", text, st)


@register_cmd("bc")
async def cmd_bc(event, arg):
    parts = (arg or "").split(maxsplit=1)
    if not parts or parts[0].lower() not in ("group", "all", "private", "db", "channel"):
        return await eor(event, f"❌ `{PREFIX}bc <group|all|private|db> <text>`")
    kind = parts[0].lower()
    text = parts[1].strip() if len(parts) > 1 else ""
    if not text and not event.is_reply:
        return await eor(event, "❌ Text do ya kisi message pe reply karo")
    st = await eor(event, f"📣 Broadcast `[{kind}]` shuru…")
    await _do_broadcast(event, kind, text, st)


async def _auto_loop(cfg, cfg_file, task_holder_key, forward: bool):
    """autobc / autofw ka background loop."""
    name = "AUTOFW" if forward else "AUTOBC"
    try:
        while True:
            targets = await broadcast_targets("db") or await broadcast_targets("group")
            for cid in targets:
                try:
                    msg = await bot.get_messages(cfg.get("chat_id"),
                                                 ids=int(cfg.get("msg_id")))
                    if msg is None:
                        continue
                    if forward:
                        await bot.forward_messages(cid, int(cfg["msg_id"]),
                                                   from_peer=cfg.get("chat_id"))
                    else:
                        await bot.send_message(cid, msg)
                except FloodWaitError as fw:
                    await asyncio.sleep(min(fw.seconds, 60))
                except Exception:
                    pass
                await asyncio.sleep(1.5)
            await asyncio.sleep(max(30, int(cfg.get("delay", 120))))
    except asyncio.CancelledError:
        return
    except Exception as e:
        print(f"[{name} CRASH] {str(e)[:80]}")


def _auto_stop(task):
    if task and not task.done():
        try:
            task.cancel()
        except Exception:
            pass
    return None


async def _auto_handler(event, sub, cfg, cfg_file, task_get, task_set, forward):
    parts = (sub or "").split()
    action = parts[0].lower() if parts else "get"

    if action == "add":
        if not event.is_reply:
            return await eor(event, f"❌ Jise broadcast karna hai us message pe reply karo\n"
                                    f"👉 `{PREFIX}autobc add`")
        r = await event.get_reply_message()
        cfg["chat_id"] = int(event.chat_id)
        cfg["msg_id"] = int(r.id)
        cfg["text"] = (r.raw_text or "")[:80]
        save_json(cfg_file, cfg)
        return await eor(event, f"💾 Message store ho gaya → id `{cfg['msg_id']}`\n"
                                f"👉 ab `{PREFIX}{'autofw' if forward else 'autobc'} on`")

    if action == "delay":
        try:
            d = int(parts[1])
        except Exception:
            return await eor(event, "❌ `.autobc delay <seconds>`")
        cfg["delay"] = max(30, d)
        save_json(cfg_file, cfg)
        return await eor(event, f"⏱ Delay → `{cfg['delay']}s` (min 30s)")

    if action == "get":
        return await eor(event, f"╭─〔 {'📣 AUTOFW' if forward else '📣 AUTOBC'} 〕─╮\n"
                                f"│ State `{'ON' if cfg.get('on') else 'OFF'}`\n"
                                f"│ Msg id `{cfg.get('msg_id')}`\n"
                                f"│ Delay `{cfg.get('delay')}s`\n"
                                f"│ Targets `{len(BCDB) or 'all groups'}`\n"
                                f"╰──────────╯\n"
                                f"{(cfg.get('text') or '')[:80]}")

    if action == "del":
        cfg.update({"on": False, "chat_id": None, "msg_id": None, "text": ""})
        save_json(cfg_file, cfg)
        task_set(_auto_stop(task_get()))
        return await eor(event, "🗑 Stored message delete kar diya")

    if action == "on":
        if not cfg.get("msg_id"):
            return await eor(event, f"❌ Pehle `{PREFIX}{'autofw' if forward else 'autobc'} add` karo")
        cfg["on"] = True
        save_json(cfg_file, cfg)
        task_set(_auto_stop(task_get()))
        task_set(asyncio.create_task(_auto_loop(cfg, cfg_file, "", forward)))
        return await eor(event, f"▶️ Auto-{'forward' if forward else 'broadcast'} ON "
                                f"(har `{cfg.get('delay')}s` me)")

    if action == "off":
        cfg["on"] = False
        save_json(cfg_file, cfg)
        task_set(_auto_stop(task_get()))
        return await eor(event, "⏹ Band kar diya")

    return await eor(event, "❌ `.autobc add|on|off|get|del|delay <sec>`")


@register_cmd("autobc")
async def cmd_autobc(event, arg):
    def set_task(t):
        global AUTOBR_TASK
        AUTOBR_TASK = t
    await _auto_handler(event, arg, AUTOBR, F_AUTOBR,
                        lambda: AUTOBR_TASK, set_task, False)


@register_cmd("autofw")
async def cmd_autofw(event, arg):
    def set_task(t):
        global AUTOFW_TASK
        AUTOFW_TASK = t
    await _auto_handler(event, arg, AUTOFW, F_AUTOFW,
                        lambda: AUTOFW_TASK, set_task, True)


# ══════════════════════════════════════════════════════════════
#                       ɢʀᴏᴜᴘ ᴍᴏᴅ
# ══════════════════════════════════════════════════════════════
BASIC_RIGHTS = types.ChatAdminRights(
    delete_messages=True, ban_users=True, invite_users=True,
    pin_messages=True, manage_call=True,
)
FULL_RIGHTS = types.ChatAdminRights(
    change_info=True, post_messages=True, edit_messages=True,
    delete_messages=True, ban_users=True, invite_users=True,
    pin_messages=True, add_admins=True, manage_call=True,
)
NO_RIGHTS = types.ChatAdminRights()


async def _act_kick(chat, uid):
    try:
        await bot.kick_participant(chat, uid)
        return True, ""
    except Exception:
        try:
            await bot(functions.messages.DeleteChatUserRequest(
                chat_id=chat, user_id=uid))
            return True, ""
        except Exception as e:
            return False, str(e)[:60]


async def _act_ban(chat, uid):
    try:
        await bot.edit_permissions(chat, uid, view_messages=False)
        return True, ""
    except Exception:
        ok, err = await _act_kick(chat, uid)
        return ok, err


async def _act_unban(chat, uid):
    try:
        await bot.edit_permissions(chat, uid, view_messages=True)
        return True, ""
    except Exception as e:
        return False, str(e)[:60]


async def _act_mute(chat, uid):
    try:
        await bot.edit_permissions(chat, uid, until_date=None, send_messages=False)
        return True, ""
    except Exception as e:
        return False, str(e)[:60]


async def _act_unmute(chat, uid):
    try:
        await bot.edit_permissions(chat, uid, send_messages=True)
        return True, ""
    except Exception as e:
        return False, str(e)[:60]


@register_cmd("kick")
async def cmd_kick(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, "❌ User nahi mila — reply / @user / id")
    ok, err = await _act_kick(event.chat_id, uid)
    await eor(event, f"👢 Kicked → `{uid}`" if ok else f"❌ `{err}`")


@register_cmd("delkick")
async def cmd_delkick(event, arg):
    uid, r = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, "❌ User nahi mila")
    if r is not None:
        try:
            await r.delete()
        except Exception:
            pass
    ok, err = await _act_kick(event.chat_id, uid)
    await eor(event, f"👢 Kick + delete → `{uid}`" if ok else f"❌ `{err}`")


@register_cmd("ban")
async def cmd_ban(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, "❌ User nahi mila")
    ok, err = await _act_ban(event.chat_id, uid)
    await eor(event, f"⛔ Banned → `{uid}`" if ok else f"❌ `{err}`")


@register_cmd("delban")
async def cmd_delban(event, arg):
    uid, r = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, "❌ User nahi mila")
    if r is not None:
        try:
            await r.delete()
        except Exception:
            pass
    ok, err = await _act_ban(event.chat_id, uid)
    await eor(event, f"⛔ Ban + delete → `{uid}`" if ok else f"❌ `{err}`")


@register_cmd("unban")
async def cmd_unban(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, "❌ User nahi mila")
    ok, err = await _act_unban(event.chat_id, uid)
    await eor(event, f"♻️ Unbanned → `{uid}`" if ok else f"❌ `{err}`")


@register_cmd("mute")
async def cmd_mute(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, "❌ User nahi mila")
    ok, err = await _act_mute(event.chat_id, uid)
    if ok:
        return await eor(event, f"🔇 Muted → `{uid}`")
    MUTED.add(uid)
    await eor(event, f"🔇 Admin right nahi → local mute laga diya (msgs delete honge) `{uid}`\n`{err}`")


@register_cmd("delmute")
async def cmd_delmute(event, arg):
    uid, r = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, "❌ User nahi mila")
    if r is not None:
        try:
            await r.delete()
        except Exception:
            pass
    ok, err = await _act_mute(event.chat_id, uid)
    if ok:
        return await eor(event, f"🔇 Mute + delete → `{uid}`")
    MUTED.add(uid)
    await eor(event, f"🔇 Local mute + delete → `{uid}`")


@register_cmd("unmute")
async def cmd_unmute(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, "❌ User nahi mila")
    ok, _ = await _act_unmute(event.chat_id, uid)
    MUTED.discard(uid)
    await eor(event, f"🔊 Unmuted → `{uid}`")


@register_cmd("getmute")
async def cmd_getmute(event, arg):
    txt = "🔇 𝐌𝐔𝐓𝐄𝐃\n━━━━━━━━━━━━━━━\n"
    try:
        found = []
        async for u in bot.iter_participants(event.chat_id,
                                             filter=types.ChannelParticipantsBanned("")):
            found.append(u)
        if found:
            for i, u in enumerate(found[:30], 1):
                txt += f"`{i}.` {u.first_name} — `{u.id}`\n"
        else:
            txt += "⚠️ Telegram me koi muted nahi\n"
    except Exception:
        txt += "⚠️ List nahi mil saki (admin right chahiye)\n"
    if MUTED:
        txt += f"\n🧹 Local delete-mute ({len(MUTED)})\n"
        for i, u in enumerate(sorted(MUTED), 1):
            txt += f"`{i}.` `{u}`\n"
    await eor(event, txt)


@register_cmd("staff")
async def cmd_staff(event, arg):
    if not event.is_group:
        return await eor(event, "❌ Group only")
    txt = "🛡 𝐒𝐓𝐀𝐅𝐅\n━━━━━━━━━━━━━━━\n"
    try:
        i = 0
        async for u in bot.iter_participants(event.chat_id,
                                             filter=types.ChannelParticipantsAdmins):
            i += 1
            rank = getattr(u.participant, "rank", None) if hasattr(u, "participant") else None
            tag = f" · {rank}" if rank else ""
            txt += f"`{i}.` {u.first_name} — `{u.id}`{tag}\n"
    except Exception as e:
        return await eor(event, f"❌ `{str(e)[:60]}`")
    await eor(event, txt)


@register_cmd("promote")
async def cmd_promote(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, "❌ User nahi mila")
    rest = (arg or "").split(maxsplit=1)
    rank = rest[1].strip()[:16] if len(rest) > 1 else ""
    try:
        await bot.edit_admin(event.chat_id, uid,
                             admin_rights=BASIC_RIGHTS, rank=rank)
        await eor(event, f"🛡 Promoted → `{uid}`" + (f" · `{rank}`" if rank else ""))
    except Exception as e:
        await eor(event, f"❌ `{str(e)[:70]}`")


@register_cmd("fullpromote")
async def cmd_fullpromote(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, "❌ User nahi mila")
    rest = (arg or "").split(maxsplit=1)
    rank = rest[1].strip()[:16] if len(rest) > 1 else ""
    try:
        await bot.edit_admin(event.chat_id, uid,
                             admin_rights=FULL_RIGHTS, rank=rank)
        await eor(event, f"👑 Full-promoted → `{uid}`" + (f" · `{rank}`" if rank else ""))
    except Exception as e:
        await eor(event, f"❌ `{str(e)[:70]}`")


@register_cmd("demote")
async def cmd_demote(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, "❌ User nahi mila")
    try:
        await bot.edit_admin(event.chat_id, uid, admin_rights=NO_RIGHTS, rank="")
        await eor(event, f"⬇️ Demoted → `{uid}`")
    except Exception as e:
        await eor(event, f"❌ `{str(e)[:70]}`")


@register_cmd("title")
async def cmd_title(event, arg):
    parts = (arg or "").split(maxsplit=1)
    if not event.is_reply and len(parts) < 2:
        return await eor(event, f"❌ `{PREFIX}title @user <title>` ya reply + `{PREFIX}title <title>`")
    if event.is_reply:
        uid, _ = await resolve_uid(event, "")
        title = (arg or "").strip()[:16]
    else:
        uid, _ = await resolve_uid(event, parts[0])
        title = parts[1].strip()[:16]
    if not uid:
        return await eor(event, "❌ User nahi mila")
    try:
        res = await bot(functions.channels.GetParticipantRequest(
            channel=event.chat_id, participant=uid))
        rights = getattr(res.participant, "admin_rights", None)
        if rights is None:
            return await eor(event, "❌ Ye admin hi nahi hai")
        await bot(functions.channels.EditAdminRequest(
            channel=event.chat_id, user_id=uid,
            admin_rights=rights, rank=title))
        await eor(event, f"🏷 Title set → `{title}`")
    except Exception as e:
        await eor(event, f"❌ `{str(e)[:70]}`")


@register_cmd("pin")
async def cmd_pin(event, arg):
    if not event.is_reply:
        return await eor(event, "❌ Reply karke `.pin` likho")
    r = await event.get_reply_message()
    try:
        await r.pin(notify=("loud" in (arg or "").lower()))
        await eor(event, "📌 Pin kar diya")
    except Exception as e:
        await eor(event, f"❌ `{str(e)[:70]}`")


@register_cmd("unpin")
async def cmd_unpin(event, arg):
    a = (arg or "").strip().lower()
    try:
        if a == "all":
            await bot.unpin_message(event.chat_id)
        elif event.is_reply:
            r = await event.get_reply_message()
            await r.unpin()
        else:
            await bot.unpin_message(event.chat_id)
        await eor(event, "📌 Unpin ho gaya")
    except Exception as e:
        await eor(event, f"❌ `{str(e)[:70]}`")


@register_cmd("group")
async def cmd_group(event, arg):
    parts = (arg or "").split(maxsplit=1)
    if len(parts) < 2 or parts[0].lower() not in ("title", "desc", "description"):
        return await eor(event, f"❌ `{PREFIX}group title <text>` / `{PREFIX}group desc <text>`")
    what, val = parts[0].lower(), parts[1].strip()
    try:
        if what == "title":
            await bot(functions.channels.EditTitleRequest(
                channel=event.chat_id, title=val[:255]))
        else:
            await bot(functions.messages.EditChatAboutRequest(
                peer=event.chat_id, about=val[:255]))
        await eor(event, f"✅ Group {what} update ho gaya")
    except Exception as e:
        await eor(event, f"❌ `{str(e)[:70]}`")


@register_cmd("lock", group_only=True)
async def cmd_lock(event, arg):
    a = (arg or "").strip().lower()
    ltype = a.split()[0] if a else "all"
    if ltype == "list":
        return await eor(event, "🔒 Types → `" + "`, `".join(LOCK_TYPES) + "`")
    if ltype not in LOCK_TYPES:
        return await eor(event, f"❌ Galat type `{ltype}`\n"
                                f"🔒 Types → `" + "`, `".join(LOCK_TYPES) + "`")
    key = str(event.chat_id)
    cur = set(LOCKS.get(key) or [])
    if ltype in cur:
        return await eor(event, f"⚠️ `{ltype}` pehle se locked hai")
    cur.add(ltype)
    LOCKS[key] = sorted(cur)
    save_json(F_LOCKS, LOCKS)
    await eor(event, f"🔒 Lock `{ltype}` ON\n"
                     f"Ab matching messages `{LOCK_DELAY}s` me delete honge\n"
                     f"Active → `{', '.join(LOCKS[key])}`")


@register_cmd("unlock", group_only=True)
async def cmd_unlock(event, arg):
    a = (arg or "").strip().lower()
    ltype = a.split()[0] if a else "all"
    key = str(event.chat_id)
    cur = set(LOCKS.get(key) or [])
    if ltype == "all":
        cur.clear()
    elif ltype in cur:
        cur.discard(ltype)
    else:
        return await eor(event, f"⚠️ `{ltype}` locked hai hi nahi")
    if cur:
        LOCKS[key] = sorted(cur)
    else:
        LOCKS.pop(key, None)
    save_json(F_LOCKS, LOCKS)
    await eor(event, f"🔓 Unlock `{ltype}`\n"
                     f"Bache → `{', '.join(sorted(cur)) or 'kuch nahi'}`")


@register_cmd("locks", group_only=True)
async def cmd_locks(event, arg):
    cur = LOCKS.get(str(event.chat_id))
    if not cur:
        return await eor(event, "🔓 Is chat me koi lock nahi")
    await eor(event, "🔒 𝐋𝐎𝐂𝐊𝐒\n━━━━━━━━━━━━━━━\n"
                     + "\n".join(f"⟡ `{t}`" for t in cur))


# ══════════════════════════════════════════════════════════════
#                     ɢʟᴏʙᴀʟ ʙᴀɴ / ᴍᴜᴛᴇ
# ══════════════════════════════════════════════════════════════
@register_cmd("gban", owner_only=True)
async def cmd_gban(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, f"❌ User nahi mila — `{PREFIX}gban <@user/id>` ya reply")
    if is_admin(uid):
        return await eor(event, "❌ Owner/admin ko gban nahi kar sakta")
    GBAN.add(uid)
    save_json(F_GBAN, sorted(GBAN))
    st = await eor(event, f"☠️ GBAN `{uid}` — saare chats me ban kar raha hoon…")
    ok = fail = 0
    async for d in bot.iter_dialogs():
        if not d.is_group:
            continue
        try:
            await bot.edit_permissions(d.id, uid, view_messages=False)
            ok += 1
        except Exception:
            fail += 1
        await asyncio.sleep(0.25)
    res = f"☠️ 𝐆𝐁𝐀𝐍\n━━━━━━━━━━━━━━━\n👤 `{uid}`\n✅ `{ok}` chats\n❌ `{fail}` fail"
    try:
        await st.edit(res)
    except Exception:
        await eor(event, res)


@register_cmd("ungban", owner_only=True)
async def cmd_ungban(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, "❌ User nahi mila")
    GBAN.discard(uid)
    save_json(F_GBAN, sorted(GBAN))
    st = await eor(event, "♻️ Un-gban kar raha hoon…")
    ok = fail = 0
    async for d in bot.iter_dialogs():
        if not d.is_group:
            continue
        try:
            await bot.edit_permissions(d.id, uid, view_messages=True)
            ok += 1
        except Exception:
            fail += 1
        await asyncio.sleep(0.25)
    res = f"♻️ 𝐔𝐍𝐆𝐁𝐀𝐍\n━━━━━━━━━━━━━━━\n👤 `{uid}`\n✅ `{ok}`\n❌ `{fail}`"
    try:
        await st.edit(res)
    except Exception:
        await eor(event, res)


@register_cmd("gbanlist", owner_only=True)
async def cmd_gbanlist(event, arg):
    if not GBAN:
        return await eor(event, "📭 Gban list khaali hai")
    txt = f"☠️ 𝐆𝐁𝐀𝐍 𝐋𝐈𝐒𝐓 ({len(GBAN)})\n━━━━━━━━━━━━━━━\n"
    for i, u in enumerate(sorted(GBAN), 1):
        txt += f"`{i}.` `{u}`\n"
    await eor(event, txt)


@register_cmd("gmute", owner_only=True)
async def cmd_gmute(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, f"❌ User nahi mila — `{PREFIX}gmute <@user/id>` ya reply")
    if is_admin(uid):
        return await eor(event, "❌ Owner/admin ko gmute nahi kar sakta")
    GMUTE.add(uid)
    save_json(F_GMUTE, sorted(GMUTE))
    await eor(event, f"🔇 GMUTE → `{uid}`\nAb jahan bhi main admin hoon, uske messages delete honge")


@register_cmd("ungmute", "gunmute", owner_only=True)
async def cmd_ungmute(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, "❌ User nahi mila")
    GMUTE.discard(uid)
    save_json(F_GMUTE, sorted(GMUTE))
    await eor(event, f"🔊 Un-gmute → `{uid}`")


@register_cmd("gmutelist", owner_only=True)
async def cmd_gmutelist(event, arg):
    if not GMUTE:
        return await eor(event, "📭 Gmute list khaali hai")
    txt = f"🔇 𝐆𝐌𝐔𝐓𝐄 𝐋𝐈𝐒𝐓 ({len(GMUTE)})\n━━━━━━━━━━━━━━━\n"
    for i, u in enumerate(sorted(GMUTE), 1):
        txt += f"`{i}.` `{u}`\n"
    await eor(event, txt)


# ══════════════════════════════════════════════════════════════
#                          ʀᴀɪᴅ
# ══════════════════════════════════════════════════════════════
async def raid_add(event, arg, bucket, label):
    targets = await get_targets(event, arg)
    if not targets:
        return await eor(event, "❌ Target nahi mila — reply / @user / id")
    added, already = [], []
    for uid in targets:
        if uid in bucket:
            already.append(str(uid))
        else:
            bucket.add(uid)
            added.append(str(uid))
    parts = []
    if added:
        parts.append(f"▶️ {label} ON → `{', '.join(added)}`")
    if already:
        parts.append(f"⚠️ Pehle se → `{', '.join(already)}`")
    await eor(event, "\n".join(parts) or "❌ Kuch nahi hua")


async def raid_del(event, arg, bucket, label):
    targets = await get_targets(event, arg)
    if not targets:
        return await eor(event, "❌ Target nahi mila")
    removed = [str(u) for u in targets if u in bucket]
    bucket.difference_update(targets)
    await eor(event, f"⏹ {label} OFF → `{', '.join(removed) or 'kuch nahi'}`")


@register_cmd("reply")
async def cmd_reply(event, arg):
    await raid_add(event, arg, reply_users, "Reply raid")


@register_cmd("sreply")
async def cmd_sreply(event, arg):
    await raid_del(event, arg, reply_users, "Reply raid")


@register_cmd("rr")
async def cmd_rr(event, arg):
    await raid_add(event, arg, rr_users, "RR raid")


@register_cmd("srr")
async def cmd_srr(event, arg):
    await raid_del(event, arg, rr_users, "RR raid")


@register_cmd("flag")
async def cmd_flag(event, arg):
    await raid_add(event, arg, flag_users, "Flag raid")


@register_cmd("sflag")
async def cmd_sflag(event, arg):
    await raid_del(event, arg, flag_users, "Flag raid")


@register_cmd("hrr")
async def cmd_hrr(event, arg):
    await raid_add(event, arg, hrr_users, "Heart raid")


@register_cmd("shrr")
async def cmd_shrr(event, arg):
    await raid_del(event, arg, hrr_users, "Heart raid")


@register_cmd("replygod")
async def cmd_replygod(event, arg):
    await raid_add(event, arg, replygod_users, "ReplyGod")


@register_cmd("sgod")
async def cmd_sgod(event, arg):
    await raid_del(event, arg, replygod_users, "ReplyGod")


@register_cmd("replyyorichi")
async def cmd_replyyorichi(event, arg):
    if not arg or len(arg.split()) < 2:
        return await eor(event, f"❌ `{PREFIX}replyyorichi <text> <count>` (reply ke saath)")
    text, count = arg.rsplit(" ", 1)
    try:
        count = int(count)
    except Exception:
        return await eor(event, "❌ Count number hona chahiye")
    count = max(1, min(count, 100))
    targets = await get_targets(event, "")
    if not targets:
        return await eor(event, "❌ Reply to karo")
    for uid in targets:
        replyyorichi_users[uid] = {"text": text, "count": count}
    await eor(event, f"☄️ ReplyYorichi → `{', '.join(map(str, targets))}` × `{count}`")


@register_cmd("syorichi")
async def cmd_syorichi(event, arg):
    targets = await get_targets(event, arg)
    removed = [str(u) for u in targets if u in replyyorichi_users]
    for u in targets:
        replyyorichi_users.pop(u, None)
    await eor(event, f"⏹ Yorichi OFF → `{', '.join(removed) or 'kuch nahi'}`")


@register_cmd("nikreply", "replynik")
async def cmd_nikreply(event, arg):
    """.nikreply <count> <text> — reply kiye gaye user ko N baar ye text bhejta hai"""
    if not event.is_reply:
        return await eor(event, f"❌ Reply karke `{PREFIX}nikreply <count> <text>` likho")
    parts = (arg or "").split(maxsplit=1)
    if len(parts) < 2:
        return await eor(event, f"❌ `{PREFIX}nikreply <count> <text>`\n"
                                f"jaise `{PREFIX}nikreply 10 tu chup kar`")
    try:
        count = int(parts[0])
    except Exception:
        return await eor(event, "❌ Count number hona chahiye")
    count = max(1, min(count, 200))
    text = parts[1].strip()
    targets = await get_targets(event, "")
    if not targets:
        return await eor(event, "❌ Target nahi mila")
    for uid in targets:
        replyking_users[uid] = {"text": text, "count": count}
    await eor(event, f"♛ NikReply ON → `{', '.join(map(str, targets))}`\n"
                     f"🔢 Count `{count}` · 💬 `{text[:40]}`\n"
                     f"⏹ Band → `{PREFIX}nik`")


@register_cmd("nik", "nikstop")
async def cmd_nik(event, arg):
    cleared = len(reply_users) + len(rr_users) + len(flag_users) + \
        len(hrr_users) + len(replygod_users) + len(replyking_users) + \
        len(replyyorichi_users)
    reply_users.clear(); rr_users.clear(); flag_users.clear()
    hrr_users.clear(); replygod_users.clear()
    replyking_users.clear(); replyyorichi_users.clear()
    await eor(event, f"♛ Nik raid stop → `{cleared}` targets clear")


@register_cmd("raidstopall")
async def cmd_raidstopall(event, arg):
    cleared = sum(len(s) for s in (reply_users, rr_users, flag_users,
                                   hrr_users, replygod_users, ECHO_USERS))
    for s in (reply_users, rr_users, flag_users, hrr_users,
              replygod_users, ECHO_USERS):
        s.clear()
    replyyorichi_users.clear(); replyking_users.clear()
    for t in list(spray_tasks.values()):
        try:
            t.cancel()
        except Exception:
            pass
    spray_tasks.clear()
    await eor(event, f"🧹 Sab raids band → `{cleared}` cleared")


@register_cmd("bomb")
async def cmd_bomb(event, arg):
    targets = await get_targets(event, arg)
    if not targets and not event.is_reply:
        msg = await eor(event, "💣 Loading…")
        for f in ["💣·", "💣··", "💣···", "💥 BOOM", "🔥 Nik bomb 💥", "💀 Bhag bsdk 💀"]:
            try:
                await msg.edit(f); await asyncio.sleep(0.6)
            except Exception:
                break
        return
    for uid in targets:
        reply_users.add(uid); rr_users.add(uid)
    await eor(event, f"💣 Bomb → `{', '.join(map(str, targets))}`")


@register_cmd("gali")
async def cmd_gali(event, arg):
    try:
        count = int((arg or "5").split()[0])
    except Exception:
        count = 5
    count = max(1, min(count, 20))
    await eor(event, f"🔥 Gali `{count}x`…")
    for _ in range(count):
        try:
            await event.reply(random.choice(reply_list))
        except FloodWaitError as fw:
            await asyncio.sleep(fw.seconds)
        except Exception:
            pass
        await asyncio.sleep(0.8)


@register_cmd("love")
async def cmd_love(event, arg):
    msg = await eor(event, "❤️ Starting…")
    if msg is None:
        return
    for f in ["❤️", "💖", "💝", "💞", "💓", "💗", "❤️‍🔥", "💘", "❤️ Nik loves you ❤️"]:
        try:
            await msg.edit(f" {f} " * 5); await asyncio.sleep(0.5)
        except Exception:
            break


# ══════════════════════════════════════════════════════════════
#                          sᴘᴀᴍ
# ══════════════════════════════════════════════════════════════
@register_cmd("spray", owner_only=True)
async def cmd_spray(event, arg):
    if not arg:
        return await eor(event, f"❌ `{PREFIX}spray <text>`")
    chat = event.chat_id
    if chat in spray_tasks and not spray_tasks[chat].done():
        return await eor(event, "⚠️ Spray pehle se chal raha hai")

    async def spray_loop():
        try:
            while True:
                if chat not in spray_tasks:
                    break
                try:
                    await bot.send_message(chat, arg[:4000])
                except FloodWaitError as fw:
                    await asyncio.sleep(fw.seconds)
                except RPCError:
                    break
                except Exception:
                    await asyncio.sleep(2)
                await asyncio.sleep(3)
        except asyncio.CancelledError:
            pass
        finally:
            spray_tasks.pop(chat, None)

    spray_tasks[chat] = asyncio.create_task(spray_loop())
    await eor(event, f"💣 Spray ON → `{arg[:40]}`\n⏹ `{PREFIX}dspray`")


@register_cmd("dspray", owner_only=True)
async def cmd_dspray(event, arg):
    chat = event.chat_id
    if chat not in spray_tasks:
        return await eor(event, "⚠️ Koi active spray nahi")
    try:
        spray_tasks[chat].cancel()
    except Exception:
        pass
    spray_tasks.pop(chat, None)
    await eor(event, "🛑 Spray OFF")


@register_cmd("spam")
async def cmd_spam(event, arg):
    if not arg:
        return await eor(event, f"❌ `{PREFIX}spam <count> <text>`")
    parts = arg.split(maxsplit=1)
    if len(parts) < 2:
        return await eor(event, "❌ Text bhi do")
    try:
        count = int(parts[0])
    except Exception:
        return await eor(event, "❌ Count number hona chahiye")
    count = max(1, min(count, 100))
    txt = parts[1]
    await eor(event, f"💣 Spam `{count}x`…")
    for _ in range(count):
        try:
            await event.reply(txt)
        except FloodWaitError as fw:
            await asyncio.sleep(fw.seconds)
        except Exception:
            pass
        await asyncio.sleep(0.7)


@register_cmd("mspam")
async def cmd_mspam(event, arg):
    if not event.is_reply:
        return await eor(event, "❌ Media pe reply karke `.mspam <n>`")
    reply = await event.get_reply_message()
    try:
        count = int((arg or "5").split()[0])
    except Exception:
        count = 5
    count = max(1, min(count, 30))
    await eor(event, f"📸 Media `{count}x`…")
    for _ in range(count):
        try:
            await bot.send_file(event.chat_id, reply.media)
        except FloodWaitError as fw:
            await asyncio.sleep(fw.seconds)
        except Exception:
            pass
        await asyncio.sleep(1.2)
    await eor(event, "✅ Media spam done")


@register_cmd("delayspam")
async def cmd_delayspam(event, arg):
    parts = (arg or "").split(maxsplit=2)
    if len(parts) < 3:
        return await eor(event, f"❌ `{PREFIX}delayspam <delay> <count> <text>`")
    try:
        delay = float(parts[0]); count = int(parts[1])
    except Exception:
        return await eor(event, "❌ Delay aur count number hone chahiye")
    delay = max(0.5, delay)
    count = max(1, min(count, 100))
    txt = parts[2]
    await eor(event, f"⏱ `{delay}s` × `{count}`")
    for _ in range(count):
        try:
            await event.reply(txt)
        except FloodWaitError as fw:
            await asyncio.sleep(fw.seconds)
        except Exception:
            pass
        await asyncio.sleep(delay)


@register_cmd("purgeall", owner_only=True)
async def cmd_purgeall(event, arg):
    try:
        count = int((arg or "10").split()[0])
    except Exception:
        count = 10
    count = max(1, min(count, 200))
    await eor(event, f"🧹 Purging `{count}`…")
    ids = []
    async for m in bot.iter_messages(event.chat_id, limit=count):
        ids.append(m.id)
    done = await _delete_ids(event.chat_id, ids)
    conf = await eor(event, f"🧹 Deleted `{done}`")
    await asyncio.sleep(3)
    try:
        await conf.delete()
    except Exception:
        pass


@register_cmd("tagall", group_only=True)
async def cmd_tagall(event, arg):
    global TAGALL_ACTIVE
    msg_text = arg if arg else "📢 Attention!"
    await eor(event, "⚡ Tagging…")
    TAGALL_ACTIVE = True
    mentions = []
    async for user in bot.iter_participants(event.chat_id):
        if not TAGALL_ACTIVE:
            break
        if user.bot or user.deleted:
            continue
        mentions.append(f"[{user.first_name}](tg://user?id={user.id})")
        if len(mentions) == 5:
            try:
                await bot.send_message(event.chat_id,
                                       msg_text + "\n" + " ".join(mentions))
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
            except Exception:
                pass
            mentions = []
            await asyncio.sleep(1.5)
    if mentions:
        try:
            await bot.send_message(event.chat_id,
                                   msg_text + "\n" + " ".join(mentions))
        except Exception:
            pass
    TAGALL_ACTIVE = False
    await eor(event, "✅ Tagall done")


@register_cmd("stop")
async def cmd_stop(event, arg):
    global TAGALL_ACTIVE
    TAGALL_ACTIVE = False
    await eor(event, "🛑 Tagall stopped")


# ══════════════════════════════════════════════════════════════
#                         ғᴀsᴛɢᴄ
# ══════════════════════════════════════════════════════════════
async def fast_title_edit(chat_id, title):
    safe = (title or "").strip()[:255]
    if not safe:
        return False
    try:
        await bot(functions.channels.EditTitleRequest(channel=chat_id, title=safe))
        return True
    except Exception:
        return False


async def gc_fast_loop(chat_id):
    try:
        while FASTGC_STATE.get("active"):
            template = FASTGC_STATE.get("template")
            if not template:
                await asyncio.sleep(2)
                continue
            emoji = random.choice(GC_FAST_EMOJIS)
            new_title = template.replace("{emoji}", emoji)
            ok = await fast_title_edit(chat_id, new_title)
            await asyncio.sleep(1 if ok else 5)
    except asyncio.CancelledError:
        return
    except Exception as e:
        print(f"[FastGC] {str(e)[:80]}")


@register_cmd("fastgc", owner_only=True)
async def cmd_fastgc(event, arg):
    a = (arg or "").strip()
    if a.startswith("set "):
        template = a[4:].strip()
        if "{emoji}" not in template:
            return await eor(event, "❌ Template me `{emoji}` likho\n"
                                    f"👉 `{PREFIX}fastgc set Nik ♛ {{emoji}}`")
        FASTGC_STATE.update({"active": True, "template": template,
                             "chat_id": event.chat_id})
        old = FASTGC_STATE.get("task")
        if old and not old.done():
            try:
                old.cancel()
            except Exception:
                pass
        FASTGC_STATE["task"] = asyncio.create_task(gc_fast_loop(event.chat_id))
        return await eor(event, f"⚡ FastGC ON → `{template[:40]}`")
    if a == "stop":
        FASTGC_STATE["active"] = False
        FASTGC_STATE["template"] = None
        t = FASTGC_STATE.get("task")
        if t and not t.done():
            try:
                t.cancel()
            except Exception:
                pass
        FASTGC_STATE["task"] = None
        return await eor(event, "🛑 FastGC OFF")
    return await eor(event, f"❌ `{PREFIX}fastgc set <title {{emoji}}>` / `{PREFIX}fastgc stop`")



# ══════════════════════════════════════════════════════════════
#                 ᴀғᴋ · ɢʜᴏsᴛ · ᴇᴄʜᴏ · ᴀᴜᴛᴏ-ʀᴇᴀᴄᴛ
# ══════════════════════════════════════════════════════════════
@register_cmd("afk")
async def cmd_afk(event, arg):
    AFK["active"] = True
    AFK["reason"] = (arg or "AFK").strip()
    AFK["since"] = time.time()
    await eor(event, f"💤 AFK ON → `{AFK['reason']}`\n"
                     f"Ab tag/PM pe auto-reply jayega · `{PREFIX}unafk` se band")


@register_cmd("unafk")
async def cmd_unafk(event, arg):
    AFK["active"] = False
    AFK["reason"] = None
    await eor(event, "✅ AFK OFF")


@register_cmd("ghost")
async def cmd_ghost(event, arg):
    """.ghost on [seconds] — apne outgoing messages apne aap delete (default 30s)"""
    a = (arg or "").split()
    if not a:
        state = "ON" if GHOST["on"] else "OFF"
        return await eor(event, f"👻 Ghost → `{state}` (delay `{GHOST['delay']}s`)\n"
                                f"👉 `{PREFIX}ghost on 30` / `{PREFIX}ghost off`")
    if a[0].lower() in ("on", "enable", "start"):
        GHOST["on"] = True
        if len(a) > 1:
            try:
                GHOST["delay"] = max(3, min(int(a[1]), 3600))
            except Exception:
                pass
        return await eor(event, f"👻 Ghost ON — apne messages `{GHOST['delay']}s` me delete honge")
    if a[0].lower() in ("off", "disable", "stop"):
        GHOST["on"] = False
        return await eor(event, "👻 Ghost OFF")
    return await eor(event, f"❌ `{PREFIX}ghost on|off [seconds]`")


@register_cmd("echo")
async def cmd_echo(event, arg):
    targets = await get_targets(event, arg)
    if not targets:
        return await eor(event, "❌ Target nahi mila — reply / @user / id")
    ECHO_USERS.update(targets)
    await eor(event, f"🔁 Echo ON → `{', '.join(map(str, sorted(targets)))}`\n"
                     f"Ab jo bhi ye bolega, main repeat karunga · `{PREFIX}unecho`")


@register_cmd("unecho")
async def cmd_unecho(event, arg):
    targets = await get_targets(event, arg)
    if not targets:
        return await eor(event, "❌ Target nahi mila")
    ECHO_USERS.difference_update(targets)
    await eor(event, f"🔕 Echo OFF → `{', '.join(map(str, sorted(targets)))}`")


@register_cmd("ar")
async def cmd_ar(event, arg):
    global AUTO_REACT_EMOJI
    if not arg:
        return await eor(event, f"❌ `{PREFIX}ar <emoji>` — apne har message pe auto-react")
    AUTO_REACT_EMOJI = arg.strip()
    await eor(event, f"✨ Auto-react ON → {AUTO_REACT_EMOJI}")


@register_cmd("sar")
async def cmd_sar(event, arg):
    global AUTO_REACT_EMOJI
    AUTO_REACT_EMOJI = None
    await eor(event, "⏹ Auto-react OFF")


# ══════════════════════════════════════════════════════════════
#                          ᴛᴏᴏʟs
# ══════════════════════════════════════════════════════════════
@register_cmd("tts")
async def cmd_tts(event, arg):
    if not arg:
        return await eor(event, f"❌ `{PREFIX}tts <text>`")
    await eor(event, "🎙 Ban raha hoon…")
    fname = os.path.join(TEMP_PATH, f"tts_{int(time.time())}.mp3")
    try:
        gTTS(text=arg[:3000], lang="hi", slow=False).save(fname)
    except Exception:
        return await eor(event, "❌ TTS fail (network?)")
    try:
        await bot.send_file(event.chat_id, fname, caption="🎙 TTS ♛")
        try:
            await event.delete()
        except Exception:
            pass
    except Exception as e:
        await eor(event, f"❌ `{str(e)[:60]}`")
    finally:
        try:
            os.remove(fname)
        except Exception:
            pass


@register_cmd("qrcode")
async def cmd_qrcode(event, arg):
    if not arg:
        return await eor(event, f"❌ `{PREFIX}qrcode <text>`")
    await eor(event, "⚡ QR bana raha hoon…")
    fname = os.path.join(TEMP_PATH, f"qr_{int(time.time())}.png")
    try:
        qrcode.make(arg[:2000]).save(fname)
        await bot.send_file(event.chat_id, fname, caption="🔳 QR ♛")
        try:
            await event.delete()
        except Exception:
            pass
    except Exception as e:
        await eor(event, f"❌ `{str(e)[:60]}`")
    finally:
        try:
            os.remove(fname)
        except Exception:
            pass


@register_cmd("fancy")
async def cmd_fancy(event, arg):
    if not arg:
        return await eor(event, f"❌ `{PREFIX}fancy <text>`")
    t = arg[:1500]
    styles = [
        f"★彡 {t} 彡★", f"『 {t} 』", f"✦ {t} ✦", f"☾ {t} ☽",
        f"➳ {t} ➳", f"⚡ {t} ⚡", f"❖ {t} ❖", f"⫷ {t} ⫸",
        f"♛ {t} ♛", f"✧･ﾟ: *✧ {t} ✧*:･ﾟ✧", f"꧁ {t} ꧂",
        f"░▒▓ {t} ▓▒░", f"➶➶ {t} ➷➷", f"✿ {t} ✿", f"⟪ {t} ⟫",
        f"⌁ {t} ⌁", f"🜲 {t} 🜲", f"⟡ {t} ⟡", f"⬢ {t} ⬢",
    ]
    await eor(event, "✨ 𝐅𝐀𝐍𝐂𝐘\n━━━━━━━━━━━━━━━\n" + "\n".join(styles))


@register_cmd("style")
async def cmd_style(event, arg):
    if not arg:
        return await eor(event, f"❌ `{PREFIX}style <text>`")
    t = arg[:1500]
    script = (t.replace('a', '𝒶').replace('b', '𝒷').replace('c', '𝒸')
              .replace('d', '𝒹').replace('e', '𝑒').replace('f', '𝒻')
              .replace('g', '𝑔').replace('h', '𝒽').replace('i', '𝒾')
              .replace('j', '𝒿').replace('k', '𝓀').replace('l', '𝓁')
              .replace('m', '𝓂').replace('n', '𝓃').replace('o', '𝑜')
              .replace('p', '𝓅').replace('q', '𝓆').replace('r', '𝓇')
              .replace('s', '𝓈').replace('t', '𝓉').replace('u', '𝓊')
              .replace('v', '𝓋').replace('w', '𝓌').replace('x', '𝓍')
              .replace('y', '𝓎').replace('z', '𝓏'))
    await eor(event, f"🎨 𝐒𝐓𝐘𝐋𝐄\n━━━━━━━━━━━━━━━\n"
                     f"𝒻𝒶𝓃𝒸𝓎 → {script}\n"
                     f"**Bold** → **{t}**\n"
                     f"__Italic__ → __{t}__\n"
                     f"`Mono` → `{t}`")


@register_cmd("emoji")
async def cmd_emoji(event, arg):
    if not arg:
        return await eor(event, f"❌ `{PREFIX}emoji <text>`")
    pool = ["🔥", "❤️", "✨", "⚡", "💥", "🌟", "💫", "🎯", "💎", "🦋",
            "🌈", "🧨", "🎆", "👑", "🌸", "🪄", "🌊", "❄️", "🍁", "🌙",
            "☀️", "💣", "🎵", "🧿", "✦", "❖", "⟡", "♛", "⚜️", "🔱"]
    deco = "".join(random.choice(pool) for _ in range(8))
    await eor(event, f"✨ 𝐄𝐌𝐎𝐉𝐈\n━━━━━━━━━━━━━━━\n{arg[:1500]} {deco}")


@register_cmd("calc")
async def cmd_calc(event, arg):
    if not arg:
        return await eor(event, f"❌ `{PREFIX}calc <expression>`")
    expr = arg.replace(" ", "")
    allowed = set("0123456789+-*/().%")
    if any(c not in allowed for c in expr):
        return await eor(event, "❌ Sirf 0-9 + - * / ( ) . % allowed")
    try:
        res = eval(expr, {"__builtins__": None}, {})
    except Exception:
        return await eor(event, "❌ Invalid expression")
    await eor(event, f"🧮 𝐂𝐀𝐋𝐂\n━━━━━━━━━━━━━━━\n📥 `{expr}`\n📤 `{res}`")


def _http_json(url, timeout=8):
    try:
        return requests.get(url, timeout=timeout).json()
    except Exception:
        return None


@register_cmd("weather")
async def cmd_weather(event, arg):
    if not arg:
        return await eor(event, f"❌ `{PREFIX}weather <city>`")
    await eor(event, "🌦 Fetching…")
    geo = _http_json(f"https://geocoding-api.open-meteo.com/v1/search?name={arg}&count=1")
    if not geo or not geo.get("results"):
        return await eor(event, "❌ City nahi mili")
    r = geo["results"][0]
    w = _http_json(f"https://api.open-meteo.com/v1/forecast?latitude={r.get('latitude')}"
                   f"&longitude={r.get('longitude')}&current_weather=true")
    if not w or not w.get("current_weather"):
        return await eor(event, "❌ Weather data nahi mila")
    cw = w["current_weather"]
    await eor(event, f"🌦 𝐖𝐄𝐀𝐓𝐇𝐄𝐑\n━━━━━━━━━━━━━━━\n"
                     f"📍 `{r.get('name')}`\n"
                     f"🌡 `{cw.get('temperature')}°C`\n"
                     f"💨 `{cw.get('windspeed')} km/h`")


@register_cmd("ip")
async def cmd_ip(event, arg):
    if not arg:
        return await eor(event, f"❌ `{PREFIX}ip <ip>`")
    await eor(event, "🌍 Looking up…")
    d = _http_json(f"http://ip-api.com/json/{arg}")
    if not d or d.get("status") != "success":
        return await eor(event, "❌ Invalid IP")
    await eor(event, f"🌍 𝐈𝐏 𝐈𝐍𝐅𝐎\n━━━━━━━━━━━━━━━\n"
                     f"📡 `{d.get('query')}`\n"
                     f"🌐 `{d.get('country')}`\n"
                     f"🏙 `{d.get('city')}`\n"
                     f"📍 `{d.get('isp')}`")


@register_cmd("short")
async def cmd_short(event, arg):
    if not arg:
        return await eor(event, f"❌ `{PREFIX}short <url>`")
    if not arg.startswith(("http://", "https://")):
        arg = "http://" + arg
    await eor(event, "🔗 Shortening…")
    try:
        short_url = requests.get(
            f"http://tinyurl.com/api-create.php?url={requests.utils.requote_uri(arg)}",
            timeout=8).text.strip()
    except Exception:
        return await eor(event, "❌ Short fail (network?)")
    await eor(event, f"🔗 𝐒𝐇𝐎𝐑𝐓\n━━━━━━━━━━━━━━━\n`{short_url}`")


@register_cmd("music")
async def cmd_music(event, arg):
    if not arg:
        return await eor(event, f"❌ `{PREFIX}music <song>`")
    query = arg.strip()
    frames = ["▰▱▱▱▱", "▰▰▱▱▱", "▰▰▰▱▱", "▰▰▰▰▱", "▰▰▰▰▰"]
    status = await eor(event, f"🎵 `{query}`\n\n`{frames[0]}`")
    stop = asyncio.Event()

    async def loader():
        i = 0
        while not stop.is_set():
            try:
                await status.edit(f"🎵 `{query}`\n\n`{frames[i % 5]}`")
            except Exception:
                pass
            i += 1
            await asyncio.sleep(1)

    lt = asyncio.create_task(loader())

    async def worker():
        try:
            import yt_dlp
            loop = asyncio.get_event_loop()
            opts = {"format": "bestaudio[abr<=128]/bestaudio",
                    "outtmpl": os.path.join(TEMP_PATH, "vn_%(id)s.%(ext)s"),
                    "quiet": True, "default_search": "ytsearch1",
                    "noplaylist": True, "retries": 2}

            def dl():
                with yt_dlp.YoutubeDL(opts) as ydl:
                    return ydl.extract_info(query, download=True)

            info = await loop.run_in_executor(None, dl)
            if "entries" in info:
                info = info["entries"][0]
            vid = info.get("id")
            title = info.get("title") or query
            files = glob.glob(os.path.join(TEMP_PATH, f"vn_{vid}.*"))
            if not files:
                raise Exception("download fail")
            src = files[0]
            clean = "".join(c for c in title if c.isalnum() or c in " -_").strip()[:40]
            new = os.path.join(TEMP_PATH, f"{clean}.ogg")
            try:
                os.rename(src, new)
            except Exception:
                new = src
            stop.set()
            lt.cancel()
            await eor(event, f"🎙 Sending → `{clean}`")
            await bot.send_file(event.chat_id, new, voice_note=True,
                                caption=f"🎵 {clean}")
            try:
                os.remove(new)
            except Exception:
                pass
            try:
                await event.delete()
            except Exception:
                pass
        except Exception as e:
            stop.set()
            lt.cancel()
            await eor(event, f"❌ Music → `{str(e)[:60]}`")

    asyncio.create_task(worker())


# ══════════════════════════════════════════════════════════════
#                          ɴᴏᴛᴇs
# ══════════════════════════════════════════════════════════════
@register_cmd("notesadd")
async def cmd_notesadd(event, arg):
    if not arg:
        return await eor(event, f"❌ `{PREFIX}notesadd <text>`")
    NOTES[int(event.chat_id)] = arg.strip()
    save_json(F_NOTES, {str(k): v for k, v in NOTES.items()})
    await eor(event, f"📝 Note saved ({len(arg)} chars)")


@register_cmd("noteslist")
async def cmd_noteslist(event, arg):
    n = NOTES.get(int(event.chat_id))
    if not n:
        return await eor(event, "📭 Is chat ka koi note nahi")
    await eor(event, f"📝 𝐍𝐎𝐓𝐄\n━━━━━━━━━━━━━━━\n{n[:3000]}")


@register_cmd("notesdelete")
async def cmd_notesdelete(event, arg):
    if NOTES.pop(int(event.chat_id), None) is None:
        return await eor(event, "⚠️ Note tha hi nahi")
    save_json(F_NOTES, {str(k): v for k, v in NOTES.items()})
    await eor(event, "🗑 Note delete kar diya")


@register_cmd("banner")
async def cmd_banner(event, arg):
    global MENU_BANNER
    if not event.is_reply:
        return await eor(event, "❌ Photo/video pe reply karke `.banner`")
    r = await event.get_reply_message()
    if not r.media:
        return await eor(event, "❌ Sirf photo/video")
    await eor(event, "⚡ Banner set kar raha hoon…")
    try:
        saved = await r.forward_to("me")
    except Exception:
        try:
            raw = await r.download_media(file=bytes)
            if not raw:
                return await eor(event, "❌ Download fail")
            bio = BytesIO(raw)
            bio.name = "banner.jpg"
            saved = await bot.send_file("me", bio)
        except Exception as e:
            return await eor(event, f"❌ `{str(e)[:60]}`")
    MENU_BANNER = [int(saved.chat_id), int(saved.id)]
    save_json(F_BANNER, MENU_BANNER)
    await eor(event, f"🖼 Banner set → id `{saved.id}`\n`.menu` ke saath aayega")


@register_cmd("rembanner")
async def cmd_rembanner(event, arg):
    global MENU_BANNER
    if not MENU_BANNER:
        return await eor(event, "⚠️ Banner set hai hi nahi")
    try:
        await bot.delete_messages(MENU_BANNER[0], [MENU_BANNER[1]])
    except Exception:
        pass
    MENU_BANNER = None
    save_json(F_BANNER, None)
    await eor(event, "🗑 Banner hata diya")


# ══════════════════════════════════════════════════════════════
#                          ᴄʟᴏɴᴇ
# ══════════════════════════════════════════════════════════════
@register_cmd("copy", owner_only=True)
async def cmd_copy(event, arg):
    global CLONE_ACTIVE, LAST_CLONE_ID
    target = None
    if event.is_reply:
        try:
            r = await event.get_reply_message()
            if r.sender_id:
                target = await bot.get_entity(r.sender_id)
        except Exception:
            pass
    if target is None and arg:
        try:
            target = await bot.get_entity(arg.strip())
        except Exception:
            pass
    if target is None:
        return await eor(event, "❌ Reply / @user / id do")
    me = await bot.get_me()
    if target.id == me.id:
        return await eor(event, "⚠️ Khud ko clone? nope")
    if CLONE_ACTIVE and LAST_CLONE_ID == target.id:
        return await eor(event, "⚠️ Pehle se cloned hai")

    await eor(event, "⚡ Clone init…")
    if not CLONE_ACTIVE:
        try:
            full = await bot(functions.users.GetFullUserRequest(me.id))
            CLONE_DATA.clear()
            CLONE_DATA["name"] = me.first_name
            CLONE_DATA["last"] = me.last_name
            CLONE_DATA["bio"] = full.full_user.about
            try:
                dp = await bot.download_profile_photo("me", file=bytes, download_big=True)
                if dp:
                    b = BytesIO(dp); b.name = "orig.jpg"
                    CLONE_DATA["photo_bytes"] = b
            except Exception:
                CLONE_DATA["photo_bytes"] = None
            CLONE_ACTIVE = True
        except Exception as e:
            print(f"[clone backup] {e}")

    try:
        await bot(functions.account.UpdateProfileRequest(
            first_name=target.first_name or "", last_name=target.last_name or ""))
    except FloodWaitError as fw:
        await asyncio.sleep(fw.seconds)

    try:
        tf = await bot(functions.users.GetFullUserRequest(target.id))
        bio = (tf.full_user.about or "").strip()[:70]
        await bot(functions.account.UpdateProfileRequest(about=""))
        await asyncio.sleep(0.7)
        await bot(functions.account.UpdateProfileRequest(about=bio))
    except Exception:
        pass

    try:
        raw = await bot.download_profile_photo(target, file=bytes, download_big=True)
        if raw:
            b = BytesIO(raw); b.name = "clone.jpg"
            up = await bot.upload_file(b)
            try:
                cur = await bot.get_profile_photos("me", limit=1)
                if cur:
                    await bot(functions.photos.DeletePhotosRequest(id=[cur[0]]))
            except Exception:
                pass
            await bot(functions.photos.UploadProfilePhotoRequest(file=up))
    except FloodWaitError as fw:
        await asyncio.sleep(fw.seconds)
    except Exception:
        pass

    LAST_CLONE_ID = target.id
    await eor(event, "✅ Clone complete ♛\n`.normal` se wapas aao")


@register_cmd("normal", owner_only=True)
async def cmd_normal(event, arg):
    global CLONE_ACTIVE, LAST_CLONE_ID
    if not CLONE_ACTIVE:
        return await eor(event, "⚠️ Koi clone active nahi")
    await eor(event, "⚡ Restore init…")
    try:
        await bot(functions.account.UpdateProfileRequest(
            first_name=CLONE_DATA.get("name") or "",
            last_name=CLONE_DATA.get("last") or ""))
    except Exception:
        pass
    try:
        await bot(functions.account.UpdateProfileRequest(about=""))
        await asyncio.sleep(0.7)
        await bot(functions.account.UpdateProfileRequest(
            about=CLONE_DATA.get("bio") or ""))
    except Exception:
        pass
    try:
        cur = await bot.get_profile_photos("me", limit=1)
        if cur:
            await bot(functions.photos.DeletePhotosRequest(id=[cur[0]]))
        if CLONE_DATA.get("photo_bytes"):
            b = CLONE_DATA["photo_bytes"]; b.name = "restore.jpg"
            up = await bot.upload_file(b)
            await bot(functions.photos.UploadProfilePhotoRequest(file=up))
    except Exception:
        pass
    CLONE_ACTIVE = False
    LAST_CLONE_ID = None
    CLONE_DATA.clear()
    await eor(event, "✅ Original restore ho gaya ♛")


# ══════════════════════════════════════════════════════════════
#                          ᴀᴅᴍɪɴ
# ══════════════════════════════════════════════════════════════
@register_cmd("addadmin", owner_only=True)
async def cmd_addadmin(event, arg):
    targets = await get_targets(event, arg)
    if not targets:
        return await eor(event, "❌ Target nahi mila")
    added, already = [], []
    for uid in targets:
        if uid == OWNER_ID:
            continue
        if uid in ADMINS:
            already.append(str(uid))
        else:
            ADMINS.add(uid); added.append(str(uid))
    save_json(F_ADMINS, sorted(ADMINS))
    parts = []
    if added:
        parts.append(f"✅ Admin added → `{', '.join(added)}`")
    if already:
        parts.append(f"⚠️ Pehle se → `{', '.join(already)}`")
    await eor(event, "\n".join(parts) or "❌ Kuch nahi hua")


@register_cmd("deladmin", owner_only=True)
async def cmd_deladmin(event, arg):
    targets = await get_targets(event, arg)
    if not targets:
        return await eor(event, "❌ Target nahi mila")
    removed = [str(u) for u in targets if u in ADMINS]
    ADMINS.difference_update(targets)
    save_json(F_ADMINS, sorted(ADMINS))
    await eor(event, f"🗑 Admin removed → `{', '.join(removed) or 'kuch nahi'}`")


@register_cmd("admins", owner_only=True)
async def cmd_admins(event, arg):
    lst = "\n".join(f"⟡ `{a}`" for a in sorted(ADMINS)) or "⚠️ Koi extra admin nahi"
    await eor(event, f"👑 𝐀𝐃𝐌𝐈𝐍𝐒\n━━━━━━━━━━━━━━━\n"
                     f"👑 Owner `{OWNER_ID}`\n{lst}\n\n📊 Total `{len(ADMINS)}`")


@register_cmd("addbots", group_only=True, owner_only=True)
async def cmd_addbots(event, arg):
    try:
        n = int((arg or "5").split()[0])
    except Exception:
        n = 5
    n = max(1, min(n, len(ADD_BOTS_LIST)))
    await eor(event, f"🤖 `{n}` bots add kar raha hoon…")
    ok = fail = 0
    for b in ADD_BOTS_LIST[:n]:
        try:
            await bot(functions.channels.InviteToChannelRequest(
                channel=event.chat_id, users=[b]))
            ok += 1
        except FloodWaitError as fw:
            await asyncio.sleep(fw.seconds)
            fail += 1
        except Exception:
            fail += 1
        await asyncio.sleep(1)
    await eor(event, f"🤖 Bots added `{ok}` · fail `{fail}`")


# ══════════════════════════════════════════════════════════════
#                         sᴛᴏʀɪᴇs
# ══════════════════════════════════════════════════════════════
def _story(name, frames):
    async def runner(event, arg):
        await play_frames(event, frames, title=name)
    runner.__name__ = f"cmd_{name}"
    return runner


for _name, _frames in [
    ("love1", LOVE1_COLLEGE), ("love2", LOVE2_INSTA), ("love3", LOVE3_OFFICE),
    ("love4", LOVE4_DISTANCE), ("love5", LOVE5_SHAADI),
    ("lovestory", LOVE_STORY_FRAMES),
    ("fun1", BACK1_CHAI), ("fun2", BACK2_EXAM), ("fun3", BACK3_CRICKET),
    ("fun4", BACK4_UDHAAR), ("fun5", BACK5_FLIRT), ("fun6", LOVE6_THUG),
    ("fun7", MEME_MUMMY), ("fun8", MEME_SASTA_NASHA),
]:
    register_cmd(_name)(_story(_name, _frames))


# ══════════════════════════════════════════════════════════════
#                      ᴡᴀᴛᴄʜᴇʀ (incoming)
# ══════════════════════════════════════════════════════════════
async def _gban_enforce(chat, uid):
    try:
        await bot.edit_permissions(chat, uid, view_messages=False)
    except Exception:
        pass


@bot.on(events.NewMessage)
async def watcher(event):
    try:
        if event.out:
            return
        sender = event.sender_id
        chat = event.chat_id
        if not sender:
            return
        text = event.raw_text or ""

        # ── GLOBAL BAN ──
        if sender in GBAN and not is_admin(sender):
            await silent_delete(event)
            asyncio.create_task(_gban_enforce(chat, sender))
            return

        # ── GLOBAL MUTE ──
        if sender in GMUTE and not is_admin(sender):
            await silent_delete(event)
            return

        # ── BLACKLIST ──
        if sender in BLACKLIST and not is_admin(sender):
            await silent_delete(event)
            return

        # ── LOCAL MUTE (delete engine) ──
        if sender in MUTED or sender in GLOBAL_MUTED:
            if not is_admin(sender):
                await silent_delete(event)
                return

        # ── GROUP LOCKS (0.3s me udaa do) ──
        locked = LOCKS.get(str(chat))
        if locked and not is_admin(sender):
            if media_kinds(event.message) & set(locked):
                await asyncio.sleep(LOCK_DELAY)
                await silent_delete(event)
                return

        # ── AUTO READ ──
        if autoread_match(event):
            try:
                await bot.send_read_acknowledge(chat, max_id=event.id)
            except Exception:
                pass

        # ── ECHO ──
        if sender in ECHO_USERS and text and not text.startswith(PREFIX):
            try:
                await event.reply(text)
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
            except Exception:
                pass

        # ── AFK AUTO REPLY ──
        if AFK["active"] and (event.is_private or getattr(event, "mentioned", False)):
            if AFK_LAST.get(chat, 0) < time.time() - 45:
                AFK_LAST[chat] = time.time()
                try:
                    await event.reply(f"💤 AFK — `{AFK['reason']}`")
                except Exception:
                    pass

        # ── AUTO REPLY (PM) ──
        if AREPLY and event.is_private and sender != OWNER_ID and sender not in ADMINS:
            try:
                await event.reply(AREPLY)
            except Exception:
                pass
            return

        # ── FILTERS ──
        fdata = FILTERS.get(str(chat))
        if fdata and text and not text.startswith(PREFIX):
            low = text.lower()
            for word, data in fdata.items():
                if word in low:
                    try:
                        src = await bot.get_messages(int(data["chat_id"]),
                                                     ids=int(data["msg_id"]))
                        if src is not None:
                            await bot.send_message(chat, src, reply_to=event.id)
                        elif data.get("text"):
                            await event.reply(data["text"])
                    except FloodWaitError as fw:
                        await asyncio.sleep(fw.seconds)
                    except Exception:
                        pass
                    break

        # ── REPLY RAID ──
        if sender in reply_users:
            try:
                await event.reply(random.choice(reply_list))
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
            except Exception:
                pass

        # ── REPLY GOD (burst) ──
        if sender in replygod_users:
            try:
                for _ in range(3):
                    await event.reply(random.choice(reply_texts))
                    await asyncio.sleep(0.5)
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
            except Exception:
                pass

        # ── FLAG RAID ──
        if sender in flag_users:
            try:
                await event.reply(random.choice(flag_texts))
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
            except Exception:
                pass

        # ── HEART RAID ──
        if sender in hrr_users:
            try:
                await event.reply(random.choice(heart_replies))
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
            except Exception:
                pass

        # ── RR RAID (+🤣 reaction) ──
        if sender in rr_users:
            try:
                bot_msg = await event.reply(random.choice(fun_texts))
                try:
                    await bot(functions.messages.SendReactionRequest(
                        peer=chat, msg_id=bot_msg.id,
                        reaction=[types.ReactionEmoji(emoticon="🤣")]))
                except Exception:
                    pass
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
            except Exception:
                pass

        # ── YORICHI (limited count) ──
        if sender in replyyorichi_users:
            data = replyyorichi_users.get(sender)
            if data:
                count = int(data.get("count", 0))
                if count > 0:
                    try:
                        await event.reply(data.get("text", ""))
                    except FloodWaitError as fw:
                        await asyncio.sleep(fw.seconds)
                    except Exception:
                        pass
                    data["count"] = count - 1
                else:
                    replyyorichi_users.pop(sender, None)

        # ── NIK REPLY (.nikreply) ──
        if sender in replyking_users:
            data = replyking_users.get(sender)
            if data:
                count = int(data.get("count", 0))
                if count > 0:
                    try:
                        await event.reply(data.get("text", ""))
                    except FloodWaitError as fw:
                        await asyncio.sleep(fw.seconds)
                    except Exception:
                        pass
                    data["count"] = count - 1
                else:
                    replyking_users.pop(sender, None)

    except Exception as e:
        print(f"[WATCHER] {str(e)[:80]}")


# ══════════════════════════════════════════════════════════════
#                      ᴡᴀᴛᴄʜᴇʀ (outgoing)
# ══════════════════════════════════════════════════════════════
@bot.on(events.NewMessage(outgoing=True))
async def outgoing_watcher(event):
    # auto react on own messages
    emoji = AUTO_REACT_EMOJI
    if emoji:
        try:
            await bot(functions.messages.SendReactionRequest(
                peer=event.chat_id, msg_id=event.id,
                reaction=[types.ReactionEmoji(emoticon=emoji)]))
        except FloodWaitError as fw:
            try:
                await asyncio.sleep(fw.seconds)
            except Exception:
                pass
        except Exception:
            pass

    # ghost mode — apne messages auto delete (commands chhod kar)
    if GHOST["on"]:
        if (event.raw_text or "").startswith(PREFIX):
            return
        try:
            await asyncio.sleep(GHOST["delay"])
            await event.delete()
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════
#                        ᴅɪsᴘᴀᴛᴄʜᴇʀ
# ══════════════════════════════════════════════════════════════
@bot.on(events.NewMessage)
async def dispatcher(event):
    text = event.raw_text or ""
    if not text or not text.startswith(PREFIX):
        return
    body = text[len(PREFIX):].strip()
    if not body:
        return
    parts = body.split(maxsplit=1)
    cmd = parts[0].lower().strip()
    arg = parts[1].strip() if len(parts) > 1 else ""

    data = commands.get(cmd)
    if not data:
        return

    sender = event.sender_id
    if not sender:
        return

    if sender != OWNER_ID:
        if sender not in ADMINS:
            try:
                await event.reply("♛ 𝐍𝐈𝐊 𝐔𝐒𝐄𝐑𝐁𝐎𝐓 — 𝐎𝐰𝐧𝐞𝐫/𝐀𝐝𝐦𝐢𝐧 𝐨𝐧𝐥𝐲 ❖")
            except Exception:
                pass
            return
        if data.get("owner_only") or cmd in OWNER_ONLY_EXTRA:
            await eor(event, "❌ Owner only command ♛")
            return

    if data.get("group_only"):
        try:
            if not event.is_group:
                await eor(event, "⚠️ Ye command sirf group me chalti hai")
                return
        except Exception:
            return

    if data.get("needs_reply"):
        try:
            if not event.is_reply and not arg:
                await eor(event, f"❌ Reply ya target do\n👉 `{PREFIX}{cmd} @user / id`")
                return
        except Exception:
            return

    try:
        await data["func"](event, arg)
    except FloodWaitError as e:
        try:
            await eor(event, f"⏳ FloodWait → `{e.seconds}s`")
        except Exception:
            pass
    except Exception as e:
        try:
            await eor(event, f"❌ Error → `{str(e)[:60]}`")
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════
#                           sᴛᴀʀᴛ
# ══════════════════════════════════════════════════════════════
async def main():
    try:
        await bot.start()
        me = await bot.get_me()
        uname = f"@{me.username}" if getattr(me, "username", None) else "NoUsername"
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"♛ {BOT_NAME} {VERSION} STARTED")
        print(f"👤 {me.first_name} ({uname})")
        print(f"🆔 {me.id}")
        print(f"❖ Commands loaded: {len(commands)}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        while True:
            try:
                await bot.run_until_disconnected()
                break
            except (ConnectionError, OSError):
                print("⚠️ Connection lost → reconnecting…")
                await asyncio.sleep(3)
    except KeyboardInterrupt:
        print("\n🛑 Stopped manually")
    except Exception as e:
        print(f"\n❌ Startup error → {str(e)[:120]}")
    finally:
        try:
            if bot.is_connected():
                await bot.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())

