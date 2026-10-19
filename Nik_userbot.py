# ══════════════════════════════════════════════════════════════
#   ✧ 𝓝𝓲𝓴 𝓤𝓼𝓮𝓻𝓫𝓸𝓽 ✧        @Nikkkwa
#   Single-file Telethon userbot  ·  ɢʟᴏʙᴀʟ  ·  ᴠ1
# ══════════════════════════════════════════════════════════════

import asyncio
import os
import time
import json
import random
import glob
import re
import urllib.parse
import string
from io import BytesIO
from typing import Dict, Set, Optional, Any

import requests
import qrcode
from gtts import gTTS

from telethon import TelegramClient, events, functions, types
from telethon.errors import FloodWaitError, RPCError, MessageNotModifiedError

# ── event-loop guard (Python 3.12+ / mobile runtimes) ──
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
#                          ᴄᴏɴғɪɢ
# ══════════════════════════════════════════════════════════════
API_ID = int(os.environ.get("API_ID") or 30157921)
API_HASH = os.environ.get("API_HASH") or "32bdfcd45922c3abcf4d956fda29e747"
OWNER_ID = int(os.environ.get("OWNER_ID") or 8742036730)
SESSION = os.environ.get("SESSION") or "nik"     # → nik.session
AI_URL = os.environ.get("AI_URL") or ""      # optional: apna endpoint
AI_MODEL = os.environ.get("AI_MODEL") or "openai-fast"

BOT_NAME = "NIK USERBOT"
VERSION = "v1"
OWNER_TAG = "@Nikkkwa"
PREFIX = "."

TMP_TTL = 3           # har working/status message 3 sec me udd jata hai
LOCK_DELAY = 0.3      # locked chat me message delete hone ka delay
STORY_DELAY = 1.6     # animation frame delay
START_TIME = time.time()

BASE_DIR = os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, "data")
DOWNLOAD_PATH = os.path.join(BASE_DIR, "downloads")
TEMP_PATH = os.path.join(BASE_DIR, "temp")
for _p in (DATA_DIR, DOWNLOAD_PATH, TEMP_PATH):
    os.makedirs(_p, exist_ok=True)

SESSION_IS_STRING = len(SESSION) > 30 and ":" in SESSION

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
#                       sᴛʏʟᴇ ᴋɪᴛ
# ══════════════════════════════════════════════════════════════
# Unicode font engine — poore bot ka text isi se guzar-ta hai.

_SANS_B = (0x1D5D4, 0x1D5EE, 0x1D7EC)   # 𝗔𝗮𝟬
_SERIF_B = (0x1D400, 0x1D41A, 0x1D7CE)   # 𝐀𝐚𝟎
_SERIF_I = (0x1D434, 0x1D44E, None)      # 𝐴𝑎
_SERIF_BI = (0x1D468, 0x1D482, None)     # 𝑨𝒂
_MONO = (0x1D670, 0x1D68A, 0x1D7F6)      # 𝙰𝚊𝟶
_SCRIPT = (0x1D49C, 0x1D4B6, None)       # 𝒜𝒶
_SCRIPT_B = (0x1D4D0, 0x1D4EA, None)     # 𝓐𝓪
_DBL = (0x1D538, 0x1D552, 0x1D7D8)       # 𝔸𝕒
_FRK = (0x1D504, 0x1D51E, None)          # 𝔄𝔞

_EXCEPT = {
    _SCRIPT: {"B": "ℬ", "E": "ℰ", "F": "ℱ", "H": "ℋ", "I": "ℐ",
              "L": "ℒ", "M": "ℳ", "R": "ℛ", "e": "ℯ", "g": "ℊ", "o": "ℴ"},
    _SCRIPT_B: {"B": "𝓑", "E": "𝓔", "F": "𝓕", "H": "𝓗", "I": "𝓘",
                "L": "𝓛", "M": "𝓜", "R": "𝓡"},
    _DBL: {"C": "ℂ", "H": "ℍ", "N": "ℕ", "P": "ℙ", "Q": "ℚ", "R": "ℝ", "Z": "ℤ"},
    _FRK: {"C": "ℭ", "H": "ℌ", "I": "ℑ", "R": "ℜ", "Z": "ℨ"},
    _SERIF_I: {"h": "ℎ"},
}

_SC_TAB = str.maketrans("abcdefghijklmnopqrstuvwxyz",
                        "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘQʀꜱᴛᴜᴠᴡxʏᴢ")


def _xf(t, spec):
    up, lo, dg = spec
    ex = _EXCEPT.get(spec, {})
    out = []
    for ch in str(t):
        if ch in ex:
            out.append(ex[ch])
            continue
        o = ord(ch)
        if 65 <= o <= 90:
            out.append(chr(up + o - 65))
        elif 97 <= o <= 122:
            out.append(chr(lo + o - 97))
        elif 48 <= o <= 57 and dg:
            out.append(chr(dg + o - 48))
        else:
            out.append(ch)
    return "".join(out)


def sc(t):    return str(t).translate(_SC_TAB)      # ᴀʙᴄ small caps
def sb(t):    return _xf(t, _SANS_B)                # 𝗔𝗕𝗖
def bs(t):    return _xf(t, _SERIF_B)               # 𝐀𝐁𝐂
def its(t):   return _xf(t, _SERIF_I)               # 𝐴𝐵𝐶
def sbi(t):   return _xf(t, _SERIF_BI)              # 𝑨𝑩𝑪
def mono(t):  return _xf(t, _MONO)                  # 𝙰𝙱𝙲
def scr(t):   return _xf(t, _SCRIPT)                # 𝒜𝓁𝓁
def scrb(t):  return _xf(t, _SCRIPT_B)              # 𝓐𝓑𝓒
def dbl(t):   return _xf(t, _DBL)                   # 𝔸𝔹ℂ

E = {
    "link": "🏷️",
    "star": "✦", "diamond": "❖", "dot": "⟡", "bolt": "⌁", "crown": "♛",
    "shield": "🛡️", "eye": "🧿", "chain": "⛓️", "sat": "📡", "globe": "🌐",
    "sword": "⚔️", "comet": "☄️", "gear": "⚙️", "wand": "🪄", "dice": "✹",
    "gene": "🧬", "node": "⟐", "tool": "⌬", "key": "🗝️", "film": "✺",
    "moon": "☾", "spark": "✧", "arrow": "‣", "lock": "🔒", "fire": "🔥",
    "warn": "⚠️", "ok": "✅", "no": "❌", "wait": "⏳", "skull": "☠️",
    "ghost": "👻", "note": "🗒️", "save": "💾", "trash": "🗑️", "bot": "🤖",
    "rocket": "🚀", "clock": "🕰️", "heart": "🖤", "crown2": "🔱", "gem": "💠",
    "eye2": "🪬", "ring": "💍", "flower": "❀", "wave": "🌊", "leaf": "❦",
}


def top(w=30):
    """masthead — har panel ke upar"""
    return (f"╭{'─' * w}╮\n"
            f"│{scrb('  Nik Userbot').center(w - 2)}│\n"
            f"╰{'─' * w}╯")


def sub(line, w=30):
    """box row — truncate mat karo, align_panel() chaudai barabar karega"""
    return f"│{('  ' + str(line)).ljust(w - 1)}│"


def box(lines, w=30):
    out = [f"╭{'─' * w}╮"]
    for ln in lines:
        out.append(f"│{('  ' + ln).ljust(w - 1)}│")
    out.append(f"╰{'─' * w}╯")
    return "\n".join(out)


def hdr(title, w=30):
    """section header: ┌─〔 𝗧𝗜𝗧𝗟𝗘 〕────"""
    body = f"〔 {sb(str(title).upper())} 〕"
    pad = max(1, w - len(str(title)) - 6)
    return f"┌─{body}" + "─" * pad


def end(w=30):
    return "└" + "─" * w


def row(cmd, desc, bullet=None, cw=12):
    """ek command + uske niche guide line (mobile friendly)"""
    b = bullet or E["star"]
    pad = max(1, cw - len(cmd))
    return f"│ {b} {mono(cmd)}{' ' * pad}‣ {sc(desc)}"


def note(text, bullet=None):
    b = bullet or E["dot"]
    return f"│ {b} {sc(text)}"


def kv(label, value, bullet=None, lw=10):
    b = bullet or E["diamond"]
    pad = max(1, lw - len(label))
    return f" {b} {sc(label)}{' ' * pad}‣ {mono(str(value))}"


def cap(text):
    return f"{E['spark']} {its(text)}"


BRAND = f"{E['spark']} {scr('Nik Userbot')} {E['spark']}"
FOOT = f"{E['dot']} {sc('powered by')} {OWNER_TAG}"


def block(title, rows, w=30):
    return "\n".join([hdr(title, w)] + list(rows) + [end(w)])


PANEL_MAX = 42          # mobile screen ke hisaab se max inner chaudai


def align_panel(text):
    """Box ki har line ki chaudai barabar kar do.

    Lambi description / @username wali line pe `│ ... │` border toot jata tha —
    ab poori box usi line ke hisaab se chaudi ho jati hai (ya line truncate).
    """
    if not text or "│" not in text:
        return text
    lines = text.split("\n")

    def boxed(s):
        return (s[:1] in ("╭", "╰") and s[-1:] in ("╮", "╯")) or \
               (s[:1] == "│" and s[-1:] == "│")

    if not any(l[:1] == "│" and l[-1:] == "│" for l in lines):
        return text
    w = max(len(l) - 2 for l in lines if l[:1] == "│" and l[-1:] == "│")
    w = min(w, PANEL_MAX)
    out = []
    for l in lines:
        if l[:1] == "│" and l[-1:] == "│":
            body = l[1:-1]
            if len(body) > w:
                body = body[:w - 1] + "…"
            out.append("│" + body.ljust(w) + "│")
        elif boxed(l):
            out.append(l[0] + "─" * w + l[-1])
        else:
            out.append(l)
    return "\n".join(out)


# ══════════════════════════════════════════════════════════════
#                          sᴛᴏʀᴀɢᴇ
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
F_ANTIDEL = "antidel.json"
F_SPAMWATCH = "spamwatch.json"
F_RLOCK = "rlock.json"
F_BOTS = "bots.json"
F_GAMEBOT = "gamebot.json"


def load_json(name, default):
    path = os.path.join(DATA_DIR, name)
    try:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"[LOAD {name}] {str(e)[:60]}")
    return default


def save_json(name, data):
    path = os.path.join(DATA_DIR, name)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[SAVE {name}] {str(e)[:60]}")
        return False


# ══════════════════════════════════════════════════════════════
#                       ʀᴜɴᴛɪᴍᴇ sᴛᴀᴛᴇ
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
    "on": False, "chat_id": None, "msg_id": None, "text": "", "delay": 120})
AUTOFW: Dict[str, Any] = load_json(F_AUTOFW, {
    "on": False, "chat_id": None, "msg_id": None, "delay": 120})
AUTOBR_TASK: Optional[asyncio.Task] = None
AUTOFW_TASK: Optional[asyncio.Task] = None

AREPLY: Optional[str] = load_json(F_AREPLY, None)
MENU_BANNER = load_json(F_BANNER, None)

# protection
ANTIDEL: Set[int] = set(int(x) for x in load_json(F_ANTIDEL, []))
SPAMWATCH: Dict[str, Dict[str, int]] = load_json(F_SPAMWATCH, {})
SPAM_BUCKET: Dict[str, list] = {}
RLOCK: Dict[str, Dict[str, str]] = load_json(F_RLOCK, {})
GPFP_TASK: Optional[asyncio.Task] = None
GPFP_STATE: Dict[str, Any] = {"on": False, "delay": 10, "photos": []}

# bot manager
SAVED_BOTS: list = load_json(F_BOTS, [])
GAME_BOT = load_json(F_GAMEBOT, None)

# sub-userbots (multi session)
SUBBOTS: Dict[str, Any] = {}
PENDING: Dict[str, Any] = {}

# games
TTT: Dict[int, Dict[str, Any]] = {}

# raids
reply_users: Set[int] = set()
rr_users: Set[int] = set()
flag_users: Set[int] = set()
hrr_users: Set[int] = set()
replygod_users: Set[int] = set()
replyyorichi_users: Dict[int, Dict[str, Any]] = {}
replyking_users: Dict[int, Dict[str, Any]] = {}
ECHO_USERS: Set[int] = set()
USER_REPLY: Dict[int, str] = {}     # .arreply — kisi ek user ko fixed reply

MUTED: Set[int] = set()
GLOBAL_MUTED: Set[int] = set()

spray_tasks: Dict[int, asyncio.Task] = {}

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

FACTS = [
    "Honey never spoils — 3000 saal purani honey bhi khane layak mili hai.",
    "Octopus ke paas 3 dil hote hain.",
    "Banana botanically ek berry hai, strawberry nahi.",
    "Tumhare bones steel se zyada strong hote hain (weight ke hisaab se).",
    "Ek din Mars pe sunrise blue hota hai.",
    "Sharks dinosaurs se bhi purane hain.",
    "Human brain lagbhag 75% paani hai.",
    "Light ko Sun se Earth tak aane me 8 min 20 sec lagte hain.",
    "Venus ka ek din uske ek saal se zyada lamba hai.",
    "Butterfly apne pairon se taste karti hai.",
    "Cows ke paas best friends hote hain.",
    "Ek cloud ka weight lagbhag 10 lakh kg ho sakta hai.",
]


# ══════════════════════════════════════════════════════════════
#                           ʜᴇʟᴘᴇʀs
# ══════════════════════════════════════════════════════════════
def is_owner(uid):
    return bool(uid) and uid == OWNER_ID


def is_admin(uid):
    return bool(uid) and (uid == OWNER_ID or uid in ADMINS)


def safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


async def eor(event, text, **kw):
    """edit-or-reply → hamesha Message object (ya None)"""
    if not text:
        return None
    text = align_panel(text)
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


async def aedit(msg, text, **kw):
    """msg.edit() ke liye — align_panel ke saath (border kabhi na toote)"""
    try:
        return await msg.edit(align_panel(text), **kw)
    except Exception:
        return None


async def _del_after(msg, secs):
    try:
        await asyncio.sleep(secs)
        await msg.delete()
    except Exception:
        pass


async def flash(event, text, secs=None):
    """working/status message — 3 sec me apne aap udd jata hai"""
    msg = await eor(event, text)
    if msg is not None:
        asyncio.create_task(_del_after(msg, secs or TMP_TTL))
    return msg


async def done(event, text, secs=None):
    """result message — styled, phir auto-clean"""
    msg = await eor(event, text)
    if msg is not None:
        asyncio.create_task(_del_after(msg, secs or TMP_TTL))
    return msg


async def silent_delete(event):
    try:
        await event.delete()
    except Exception:
        pass


async def get_targets(event, arg="") -> Set[int]:
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


async def resolve_uid(event, arg=""):
    """ek user id — reply / @user / id / DM auto-detect"""
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
    # DM me ho to saamne wala hi target
    try:
        if getattr(event, "is_private", False) and event.chat_id:
            cid = int(event.chat_id)
            if cid > 0 and not event.out:
                return cid, None
    except Exception:
        pass
    return None, None


def parse_time(txt):
    """'10m', '2h', '3d' → seconds"""
    txt = (txt or "").strip().lower()
    m = re.match(r"^(\d+)\s*([smhd]?)$", txt)
    if not m:
        return None
    n = int(m.group(1))
    unit = m.group(2) or "m"
    return n * {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit]


async def play_frames(event, frames, title="", delay=0):
    d = delay or STORY_DELAY
    msg = await eor(event, f"{E['film']} {sc(title)} {E['dot']} {sc('starting')}…")
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
                kinds.add("document")
        elif isinstance(media, types.MessageMediaWebPage):
            kinds.update({"webpage", "link"})
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


async def broadcast_targets(kind):
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


async def yt_download(url, audio=False):
    """yt-dlp se media download → local file path"""
    import yt_dlp
    loop = asyncio.get_event_loop()
    tag = str(int(time.time() * 1000))
    tmpl = os.path.join(TEMP_PATH, f"dl_{tag}_%(id)s.%(ext)s")
    opts = {"outtmpl": tmpl, "quiet": True, "noplaylist": True, "retries": 2}
    if audio:
        opts["format"] = "bestaudio[abr<=128]/bestaudio"
    else:
        opts["format"] = "best[filesize<50M]/best"

    def run():
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if "entries" in info:
                info = info["entries"][0]
            return info

    info = await loop.run_in_executor(None, run)
    files = glob.glob(os.path.join(TEMP_PATH, f"dl_{tag}_*"))
    return (files[0] if files else None), (info or {})


# ══════════════════════════════════════════════════════════════
#                        ᴛᴇxᴛ ʟɪsᴛs
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


# ══════════════════════════════════════════════════════════════
#                       sᴛᴏʀʏ ғʀᴀᴍᴇs
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


# ══════════════════════════════════════════════════════════════
#                     ᴄᴏᴍᴍᴀɴᴅ ʀᴇɢɪsᴛʀʏ
# ══════════════════════════════════════════════════════════════
commands: Dict[str, Dict[str, Any]] = {}
aliases: Dict[str, str] = {}


def register_cmd(*names, needs_reply=False, group_only=False, owner_only=False):
    def decorator(func):
        main = None
        for raw in names:
            key = (raw or "").lower().strip()
            if not key:
                continue
            if key in commands:
                raise ValueError(f"Duplicate command: {key}")
            commands[key] = {"func": func, "needs_reply": bool(needs_reply),
                             "group_only": bool(group_only),
                             "owner_only": bool(owner_only)}
            if main is None:
                main = key
            else:
                aliases[key] = main
        return func
    return decorator


OWNER_ONLY_EXTRA = {"copy", "normal", "cp", "nrml", "addadmin", "deladmin",
                    "admins", "sudo", "delsudo", "list", "gban", "ungban",
                    "gbanlist", "gmute", "ungmute", "gmutelist", "gcast",
                    "ucast", "bc", "autobc", "autofw", "add-bcdb", "del-bcdb",
                    "join", "leave", "purgeall", "fastgc", "spray", "dspray",
                    "banall", "invitebots", "promotebots", "addbots",
                    "setgpfp", "autogpfp", "stopgpfp", "addbot", "c", "p",
                    "setgame", "rob", "kill", "auto", "roboff", "killoff",
                    "autooff", "stoprob", "resetdone", "solve", "user"}


# ══════════════════════════════════════════════════════════════
#                           ᴍᴇɴᴜ
# ══════════════════════════════════════════════════════════════
_MENU = [
    (f"{E['bolt']} {sb('core')}", [
        ("menu", "ᴘᴏᴏʀᴀ ᴄᴏᴍᴍᴀɴᴅ ᴍᴀᴘ"),
        ("alive", "ʙᴏᴛ sᴛᴀᴛᴜs + ᴜᴘᴛɪᴍᴇ"),
        ("ping", "ʀᴇsᴘᴏɴsᴇ sᴘᴇᴇᴅ"),
        ("status", "ꜰᴜʟʟ ʀᴜɴᴛɪᴍᴇ ʀᴇᴘᴏʀᴛ"),
        ("uptime", "ᴋɪᴛɴᴀ ᴄʜᴀʟ ʀʜᴀ ʜᴀɪ"),
        ("id", "ɪᴅ ɢʀᴀʙʙᴇʀ · ᴅᴍ ᴀᴜᴛᴏ"),
        ("info", "ᴜsᴇʀ ᴘʀᴏꜰɪʟᴇ · ᴅᴍ ᴀᴜᴛᴏ"),
        ("help", "ǫᴜɪᴄᴋ ɢᴜɪᴅᴇ"),
        ("speed", "ᴀɴɪᴍᴀᴛɪᴏɴ sᴘᴇᴇᴅ"),
    ]),
    (f"{E['dot']} {sb('messaging')}", [
        ("hy", "sᴛʏʟɪsʜ ɢʀᴇᴇᴛɪɴɢ"),
        ("del", "ʀᴇᴘʟɪᴇᴅ ᴍsɢ ᴜᴅᴀᴏ"),
        ("forward", "ᴍsɢ ᴀᴀɢᴇ ʙʜᴇᴊᴏ"),
        ("save", "ᴄʜᴀɴɴᴇʟ ᴍᴇ sᴇᴠᴇ"),
        ("savelist", "sᴀᴠᴇᴅ ʟɪsᴛ"),
        ("fwd", "sᴀᴠᴇᴅ ᴡᴀᴘᴀs"),
        ("delsave", "sᴀᴠᴇᴅ ᴅᴇʟᴇᴛᴇ"),
        ("setchannel", "sᴀᴠᴇ ᴄʜᴀɴɴᴇʟ sᴇᴛ"),
        ("purge", "ʀᴇᴘʟʏ ᴋᴇ ɴɪᴄʜᴇ sᴀʙ"),
        ("purgeme", "ᴀᴘɴᴇ ᴍsɢ (ɪs ᴄʜᴀᴛ)"),
        ("delmine", "ᴀᴘɴᴇ sᴀʙ ᴍsɢ"),
        ("filter", "ᴡᴏʀᴅ ᴀᴜᴛᴏ-ʀᴇᴘʟʏ"),
        ("filters", "ꜰɪʟᴛᴇʀ ʟɪsᴛ"),
        ("unfilter", "ꜰɪʟᴛᴇʀ ʜᴀᴛᴀᴏ"),
    ]),
    (f"{E['diamond']} {sb('auto')}", [
        ("autoread", "ɢʀᴏᴜᴘ/ᴘʀɪᴠᴀᴛᴇ/ᴀʟʟ ᴏɴ-ᴏꜰꜰ"),
        ("areply", "ᴘᴍ ᴀᴜᴛᴏ-ʀᴇᴘʟʏ"),
        ("stopareply", "ᴀᴜᴛᴏ-ʀᴇᴘʟʏ ʙᴀɴᴅ"),
        ("arreply", "ᴜsᴇʀ ᴀᴜᴛᴏ-ʀᴇᴘʟʏ"),
        ("sarreply", "ᴜsᴇʀ ʀᴇᴘʟʏ ʙᴀɴᴅ"),
        ("arviyom", "ᴜsᴇʀ ᴀᴜᴛᴏ-ʀᴇᴘʟʏ (ᴀʟɪᴀs)"),
        ("sarviyom", "ᴜsᴇʀ ʀᴇᴘʟʏ ᴏꜰꜰ (ᴀʟɪᴀs)"),
        ("afk", "ᴀꜰᴋ ᴍᴏᴅᴇ"),
        ("unafk", "ᴀꜰᴋ ᴏꜰꜰ"),
        ("ghost", "ᴀᴘɴᴇ ᴍsɢ ᴀᴜᴛᴏ-ᴅᴇʟ"),
        ("echo", "ʀᴇᴘᴇᴀᴛ ᴜsᴇʀ"),
        ("unecho", "ʀᴇᴘᴇᴀᴛ ʙᴀɴᴅ"),
        ("ar", "ᴀᴜᴛᴏ-ʀᴇᴀᴄᴛ (ᴇᴍᴏᴊɪ)"),
        ("sar", "ᴀᴜᴛᴏ-ʀᴇᴀᴄᴛ ʙᴀɴᴅ"),
        ("art", "ᴀᴜᴛᴏ-ʀᴇᴀᴄᴛɪᴏɴ"),
        ("sart", "ʀᴇᴀᴄᴛɪᴏɴ ʙᴀɴᴅ"),
    ]),
    (f"{E['chain']} {sb('blacklist')}", [
        ("addbl", "ʙʟᴀᴄᴋʟɪsᴛ +"),
        ("delbl", "ʙʟᴀᴄᴋʟɪsᴛ −"),
        ("listbl", "ʙʟᴀᴄᴋʟɪsᴛ ʟɪsᴛ"),
        ("add-bcdb", "ʙʀᴏᴀᴅᴄᴀsᴛ ᴅʙ +"),
        ("del-bcdb", "ʙʀᴏᴀᴅᴄᴀsᴛ ᴅʙ −"),
        ("list-bcdb", "ʙʀᴏᴀᴅᴄᴀsᴛ ᴅʙ"),
        ("join", "ʟɪɴᴋ sᴇ ᴊᴏɪɴ"),
        ("leave", "ᴄʜᴀᴛ ᴄʜʜᴏᴅᴏ"),
    ]),
    (f"{E['sat']} {sb('broadcast')}", [
        ("gcast", "sᴀʙ ɢʀᴏᴜᴘs ᴍᴇ"),
        ("ucast", "sᴀʙ ᴜsᴇʀs ᴋᴏ"),
        ("bc", "ɢʀᴏᴜᴘ/ᴀʟʟ/ᴘʀɪᴠᴀᴛᴇ/ᴅʙ"),
        ("autobc", "ᴀᴅᴅ/ᴏɴ/ᴏꜰꜰ/ɢᴇᴛ/ᴅᴇʟ/ᴅᴇʟᴀʏ"),
        ("autofw", "ᴀᴅᴅ/ᴏɴ/ᴏꜰꜰ/ɢᴇᴛ/ᴅᴇʟ/ᴅᴇʟᴀʏ"),
    ]),
    (f"{E['shield']} {sb('group mod')}", [
        ("kick", "ᴜsᴇʀ ɴɪᴋᴀᴀʟᴏ"),
        ("delkick", "ᴋɪᴄᴋ + ᴍsɢ ᴜᴅᴀᴏ"),
        ("ban", "ʙᴀɴ"),
        ("delban", "ʙᴀɴ + ᴍsɢ ᴜᴅᴀᴏ"),
        ("unban", "ᴜɴʙᴀɴ"),
        ("mute", "ᴍᴜᴛᴇ · ᴍ / ᴍᴜᴛᴇ"),
        ("delmute", "ᴍᴜᴛᴇ + ᴍsɢ ᴜᴅᴀᴏ"),
        ("unmute", "ᴜɴᴍᴜᴛᴇ · sᴍ"),
        ("tmute", "ᴛɪᴍᴇᴅ ᴍᴜᴛᴇ `10m/2h`"),
        ("getmute", "ᴍᴜᴛᴇᴅ ʟɪsᴛ"),
        ("staff", "ᴀᴅᴍɪɴ ʟɪsᴛ"),
        ("promote", "ᴀᴅᴍɪɴ ʙᴀɴᴀᴏ"),
        ("fullpromote", "ꜰᴜʟʟ ʀɪɢʜᴛs"),
        ("demote", "ᴀᴅᴍɪɴ ʜᴀᴛᴀᴏ"),
        ("title", "ᴄᴜsᴛᴏᴍ ᴛᴀɢ/ᴛɪᴛʟᴇ"),
        ("pin", "ᴘɪɴ"),
        ("unpin", "ᴜɴᴘɪɴ / ᴀʟʟ"),
        ("group", "ᴛɪᴛʟᴇ / ᴅᴇsᴄ"),
        ("tagall", "sᴀʙᴋᴏ ᴛᴀɢ"),
        ("banall", "sᴀʙᴋᴏ ʙᴀɴ"),
        ("lock", "ʟᴏᴄᴋ <ᴛʏᴘᴇ>"),
        ("unlock", "ᴜɴʟᴏᴄᴋ <ᴛʏᴘᴇ>"),
        ("locks", "ᴀᴄᴛɪᴠᴇ ʟᴏᴄᴋs"),
        ("slock", "sᴜᴘᴇʀ ʟᴏᴄᴋ · sᴀʙ ᴍᴜᴛᴇ"),
    ]),
    (f"{E['globe']} {sb('global')}", [
        ("gban", "sᴀʙ ᴄʜᴀᴛs ᴍᴇ ʙᴀɴ"),
        ("ungban", "ɢʙᴀɴ ʜᴀᴛᴀᴏ"),
        ("gbanlist", "ɢʙᴀɴ ʟɪsᴛ"),
        ("gmute", "sᴀʙ ᴄʜᴀᴛs ᴍᴇ ᴍᴜᴛᴇ"),
        ("ungmute", "ɢᴍᴜᴛᴇ ʜᴀᴛᴀᴏ"),
        ("gmutelist", "ɢᴍᴜᴛᴇ ʟɪsᴛ"),
    ]),
    (f"{E['eye']} {sb('protection')}", [
        ("antidel", "ᴀɴᴛɪ-ᴅᴇʟᴇᴛᴇ ᴏɴ/ᴏꜰꜰ"),
        ("watchspam", "sᴘᴀᴍ ɢᴜᴀʀᴅ `3 5`"),
        ("unwatchspam", "sᴘᴀᴍ ɢᴜᴀʀᴅ ᴏꜰꜰ"),
        ("setgpfp", "ɢʀᴏᴜᴘ ᴘʜᴏᴛᴏ sᴇᴛ"),
        ("autogpfp", "ᴘʜᴏᴛᴏ ʀᴏᴛᴀᴛᴇ `10`"),
        ("stopgpfp", "ʀᴏᴛᴀᴛɪᴏɴ ʙᴀɴᴅ"),
        ("rlock", "ʀᴇᴘʟʏ-ᴛʀɪɢɢᴇʀ ʟᴏᴄᴋ"),
        ("srlock", "ʀᴇᴘʟʏ ʟᴏᴄᴋ ʜᴀᴛᴀᴏ"),
    ]),
    (f"{E['wand']} {sb('media')}", [
        ("yt", "ʏᴏᴜᴛᴜʙᴇ ᴅᴏᴡɴʟᴏᴀᴅ"),
        ("ig", "ɪɴsᴛᴀɢʀᴀᴍ ᴅᴏᴡɴʟᴏᴀᴅ"),
        ("pt", "ᴘɪɴᴛᴇʀᴇsᴛ ᴅᴏᴡɴʟᴏᴀᴅ"),
        ("fb", "ꜰᴀᴄᴇʙᴏᴏᴋ ᴅᴏᴡɴʟᴏᴀᴅ"),
        ("music", "sᴏɴɢ → ᴠᴏɪᴄᴇ ɴᴏᴛᴇ"),
    ]),
    (f"{E['dice']} {sb('fun')}", [
        ("tictactoe", "ɢᴀᴍᴇ sʜᴜʀᴜ"),
        ("ttt", "ᴍᴏᴠᴇ `1-9`"),
        ("rps", "ʀᴏᴄᴋ-ᴘᴀᴘᴇʀ-sᴄɪssᴏʀ"),
        ("roll", "ᴅɪᴄᴇ ʀᴏʟʟ"),
        ("flip", "ᴄᴏɪɴ ᴛᴏss"),
        ("fact", "ʀᴀɴᴅᴏᴍ ꜰᴀᴄᴛ"),
        ("bomb", "ʙᴏᴍʙ ᴀɴɪᴍᴀᴛɪᴏɴ"),
        ("love", "ʜᴇᴀʀᴛ ᴀɴɪᴍᴀᴛɪᴏɴ"),
    ]),
    (f"{E['gene']} {sb('ai & sudo')}", [
        ("ai", "ꜰʀᴇᴇ ᴀɪ · ᴋᴏɪ ᴀᴘɪ ᴋᴇʏ ɴᴀʜɪ"),
        ("sudo", "sᴜᴅᴏ ʙᴀɴᴀᴏ (ʀᴇᴘʟʏ)"),
        ("delsudo", "sᴜᴅᴏ ʜᴀᴛᴀᴏ (ʀᴇᴘʟʏ)"),
        ("list sudo", "sᴜᴅᴏ ʟɪsᴛ"),
    ]),
    (f"{E['node']} {sb('bot manager')}", [
        ("addbots", "@ʙᴏᴛ1 @ʙᴏᴛ2 sᴀᴠᴇ"),
        ("listbots", "sᴀᴠᴇᴅ ʙᴏᴛs"),
        ("invitebots", "ʙᴏᴛs ɪɴᴠɪᴛᴇ"),
        ("promotebots", "ʙᴏᴛs ᴘʀᴏᴍᴏᴛᴇ"),
    ]),
    (f"{E['sword']} {sb('raid')}", [
        ("reply", "ʀᴇᴘʟʏ ʀᴀɪᴅ ᴏɴ"),
        ("sreply", "ʀᴇᴘʟʏ ʀᴀɪᴅ ᴏꜰꜰ"),
        ("rr", "ʀʀ ʀᴀɪᴅ (🤣)"),
        ("srr", "ʀʀ ᴏꜰꜰ"),
        ("flag", "ꜰʟᴀɢ ʀᴀɪᴅ"),
        ("sflag", "ꜰʟᴀɢ ᴏꜰꜰ"),
        ("hrr", "ʜᴇᴀʀᴛ ʀᴀɪᴅ"),
        ("shrr", "ʜᴇᴀʀᴛ ᴏꜰꜰ"),
        ("replygod", "ʙᴜʀsᴛ ʀᴀɪᴅ"),
        ("sgod", "ʙᴜʀsᴛ ᴏꜰꜰ"),
        ("replyyorichi", "<ᴛᴇxᴛ> <ᴄᴏᴜɴᴛ>"),
        ("syorichi", "ʏᴏʀɪᴄʜɪ ᴏꜰꜰ"),
        ("nikreply", "<ᴄᴏᴜɴᴛ> <ᴛᴇxᴛ>"),
        ("nik", "sᴀʙ ʀᴀɪᴅ ʙᴀɴᴅ"),
        ("raidstopall", "ᴇᴠᴇʀʏᴛʜɪɴɢ sᴛᴏᴘ"),
        ("stopall", "ᴇᴠᴇʀʏᴛʜɪɴɢ sᴛᴏᴘ"),
        ("gali", "ɢᴀʟɪ sᴘᴀᴍ <ɴ>"),
    ]),
    (f"{E['comet']} {sb('spam')}", [
        ("spray", "ʟᴏᴏᴘ ᴍᴇssᴀɢᴇ"),
        ("dspray", "ʟᴏᴏᴘ ʙᴀɴᴅ"),
        ("sspam", "ʟᴏᴏᴘ ʙᴀɴᴅ (ᴀʟɪᴀs)"),
        ("spam", "<ɴ> <ᴛᴇxᴛ>"),
        ("mspam", "<ɴ> ᴍᴇᴅɪᴀ"),
        ("delayspam", "<ᴅᴇʟᴀʏ> <ɴ> <ᴛᴇxᴛ>"),
        ("d", "<sᴇᴄ> <ᴛᴇxᴛ>"),
        ("purgeall", "<ɴ> ᴜᴅᴀᴏ"),
        ("tagall", "sᴀʙᴋᴏ ᴛᴀɢ"),
        ("stop", "ᴛᴀɢᴀʟʟ ʙᴀɴᴅ"),
    ]),
    (f"{E['gear']} {sb('gc tools')}", [
        ("fastgc", "sᴇᴛ <ᴛɪᴛʟᴇ {emoji}> / sᴛᴏᴘ"),
        ("copy", "ᴘʀᴏꜰɪʟᴇ ᴄʟᴏɴᴇ · ᴄᴘ"),
        ("normal", "ᴘʀᴏꜰɪʟᴇ ʀᴇsᴛᴏʀᴇ · ɴʀᴍʟ"),
    ]),
    (f"{E['tool']} {sb('tools')}", [
        ("tts", "ᴛᴇxᴛ → ᴀᴜᴅɪᴏ"),
        ("qrcode", "ᴛᴇxᴛ → ǫʀ"),
        ("fancy", "ꜰᴀɴᴄʏ ꜰᴏɴᴛs"),
        ("style", "sᴛʏʟᴇ ᴄᴏɴᴠᴇʀᴛ"),
        ("emoji", "ᴇᴍᴏᴊɪ ᴅᴇᴄᴏʀᴇ"),
        ("calc", "ᴄᴀʟᴄᴜʟᴀᴛᴏʀ"),
        ("weather", "ᴍᴏsᴀᴍ"),
        ("ip", "ɪᴘ ʟᴏᴏᴋᴜᴘ"),
        ("short", "ᴜʀʟ sʜᴏʀᴛᴇɴ"),
    ]),
    (f"{E['key']} {sb('notes')}", [
        ("notesadd", "ɴᴏᴛᴇ sᴀᴠᴇ"),
        ("noteslist", "ɴᴏᴛᴇ ᴅᴇᴋʜᴏ"),
        ("notesdelete", "ɴᴏᴛᴇ ᴜᴅᴀᴏ"),
        ("banner", "ᴍᴇɴᴜ ʙᴀɴɴᴇʀ sᴇᴛ"),
        ("rembanner", "ʙᴀɴɴᴇʀ ʜᴀᴛᴀᴏ"),
    ]),
    (f"{E['film']} {sb('stories')}", [
        ("love1", "ᴄᴏʟʟᴇɢᴇ ʟᴏᴠᴇ"),
        ("love2", "ɪɴsᴛᴀ ʟᴏᴠᴇ"),
        ("love3", "ᴏꜰꜰɪᴄᴇ ʟᴏᴠᴇ"),
        ("love4", "ᴅɪsᴛᴀɴᴄᴇ ʟᴏᴠᴇ"),
        ("love5", "sʜᴀᴀᴅɪ ʟᴏᴠᴇ"),
        ("lovestory", "ᴄʟᴀssɪᴄ sᴛᴏʀʏ"),
        ("fun1", "ᴄʜᴀɪ sᴛᴏʀʏ"),
        ("fun2", "ᴇxᴀᴍ sᴛᴏʀʏ"),
        ("fun3", "ᴄʀɪᴄᴋᴇᴛ sᴛᴏʀʏ"),
        ("fun4", "ᴜᴅʜᴀᴀʀ sᴛᴏʀʏ"),
        ("fun5", "ꜰʟɪʀᴛ sᴛᴏʀʏ"),
        ("fun6", "ᴛʜᴜɢ ʟɪꜰᴇ"),
        ("fun7", "ᴍᴜᴍᴍʏ ᴅᴀᴀɴᴛ"),
        ("fun8", "sᴀsᴛᴀ ɴᴀsʜᴀ"),
    ]),
]


def build_menu_pages(w=34, per_page=48):
    head = [f"╭{'─' * w}╮",
            f"│{'   ' + scrb('Nik Userbot')}{' ' * max(1, w - 16)}│",
            f"╰{'─' * w}╯",
            kv("owner", OWNER_TAG, E["crown"]),
            kv("build", VERSION, E["spark"]),
            kv("mode", "global", E["globe"]),
            ""]
    rows = []
    for title, items in _MENU:
        rows.append(hdr(title, w))
        for cmd, desc in items:
            rows.append(row(cmd, desc, cw=13))
        rows.append(end(w))
    pages, cur = [], "\n".join(head)
    for r in rows:
        if len(cur) + len(r) + 1 > 3000:
            pages.append(cur)
            cur = ""
        cur += ("\n" if cur else "") + r
    if cur:
        pages.append(cur)
    total = len(pages)
    out = []
    for i, p in enumerate(pages, 1):
        out.append(p + f"\n\n{E['dot']} {sc('page')} {mono(str(i))}/{mono(str(total))}\n{FOOT}")
    return out


# ══════════════════════════════════════════════════════════════
#        ᴍᴇɴᴜ sʏsᴛᴇᴍ — m1..m3 = pages · m4+ = category · fullmenu
# ══════════════════════════════════════════════════════════════
_SB_BACK = {sb(c): c for c in string.ascii_letters}


def _sect_name(title):
    """'🛡️ 𝗴𝗿𝗼𝘂𝗽 𝗺𝗼𝗱' → 'group mod'"""
    return title.split(" ", 1)[-1].translate(str.maketrans(_SB_BACK)).strip()


# m4 se aage categories ka order — baki sab iske baad (m4 = admins/group mod)
CAT_ORDER = ["group mod", "fun", "tools", "global", "protection",
             "blacklist", "broadcast", "messaging", "auto", "media",
             "ai & sudo", "bot manager", "raid", "spam", "gc tools",
             "notes", "stories", "core"]

def _cat_sort_key(idx):
    nm = _sect_name(_MENU[idx][0])
    return (CAT_ORDER.index(nm) if nm in CAT_ORDER else 99, idx)


CATS = []                                  # [(name, _MENU index)]
for _i in sorted(range(len(_MENU)), key=_cat_sort_key):
    CATS.append((_sect_name(_MENU[_i][0]), _i))

MENU_PAGES = build_menu_pages()            # 3 pages — pehle jaisa, bilkul same
PAGE_CMDS = ["m{}".format(i + 1) for i in range(len(MENU_PAGES))]
CAT_CMDS = ["m{}".format(len(MENU_PAGES) + 1 + i) for i in range(len(CATS))]

CAT_OF_CMD = {}                            # command → uska category menu
for _k, (_nm, _idx) in enumerate(CATS):
    for _c, _d in _MENU[_idx][1]:
        CAT_OF_CMD.setdefault(_c, CAT_CMDS[_k])


def menu_head(w=34):
    return [f"╭{'─' * w}╮",
            f"│{'   ' + scrb('Nik Userbot')}{' ' * max(1, w - 16)}│",
            f"╰{'─' * w}╯",
            kv("owner", OWNER_TAG, E["crown"]),
            kv("build", VERSION, E["spark"]),
            kv("mode", "global", E["globe"]),
            ""]


def build_category_menu(k, w=34):
    """.m4 .. .m21 — ek hi category ka poora menu"""
    nm, idx = CATS[k]
    title, items = _MENU[idx]
    rows = [hdr(title, w)]
    for c, d in items:
        rows.append(row(c, d, cw=13))
    rows.append(end(w))
    return ("\n".join(menu_head(w) + rows)
            + f"\n\n{E['dot']} {mono('.' + CAT_CMDS[k])} {E['arrow']} {sc(nm)} "
            + f"{E['arrow']} {mono(str(len(items)))} {sc('commands')}\n" + FOOT)


def build_menu_index(w=34):
    """.menu / .help — kaunsa menu kis cheez ka hai, poori list"""
    L = menu_head(w)
    L.append(hdr(f"{E['film']} {sb('pages')}", w))
    for i, c in enumerate(PAGE_CMDS, 1):
        L.append(row(c, f"{sc('page')} {mono(str(i))}/{mono(str(len(MENU_PAGES)))}", cw=9))
    L.append(end(w))
    L.append(hdr(f"{E['gem']} {sb('by category')}", w))
    for k, (nm, idx) in enumerate(CATS):
        L.append(row(CAT_CMDS[k], f"{sc(nm)} ({mono(str(len(_MENU[idx][1])))})", cw=9))
    L.append(end(w))
    L.append(hdr(f"{E['star']} {sb('extra')}", w))
    L.append(row("fullmenu", f"{sc('sab')} {mono(str(len(MENU_PAGES)))} {sc('pages ek saath')}", cw=9))
    L.append(row("help", sc("kisi bhi command ki detail"), cw=9))
    L.append(end(w))
    return "\n".join(L) + f"\n\n{FOOT}"


async def _send_banner(event):
    if not MENU_BANNER:
        return
    try:
        chat_id, msg_id = MENU_BANNER
        msg = await bot.get_messages(chat_id, ids=msg_id)
        if msg and getattr(msg, "media", None):
            await bot.send_file(event.chat_id, file=msg.media, caption=BRAND)
    except Exception:
        pass


@register_cmd("menu")
async def cmd_menu(event, _):
    """.menu — index: .m1 .m2 .m3 (pages) + .m4 se .m21 (category)"""
    await eor(event, build_menu_index())
    await _send_banner(event)


@register_cmd("fullmenu")
async def cmd_fullmenu(event, _):
    """.fullmenu — 3no pages ek saath (3 alag messages)"""
    await eor(event, MENU_PAGES[0])
    for pg in MENU_PAGES[1:]:
        try:
            await event.reply(pg)
        except Exception:
            pass
    await _send_banner(event)


def _mk_page_cmd(i):
    async def runner(event, arg):
        if i < len(MENU_PAGES):
            await eor(event, MENU_PAGES[i])
    runner.__name__ = "cmd_{}".format(PAGE_CMDS[i])
    return runner


def _mk_cat_cmd(k):
    async def runner(event, arg):
        if k < len(CATS):
            await eor(event, build_category_menu(k))
    runner.__name__ = "cmd_{}".format(CAT_CMDS[k])
    return runner


for _i in range(len(PAGE_CMDS)):
    register_cmd(PAGE_CMDS[_i])(_mk_page_cmd(_i))
for _k in range(len(CATS)):
    register_cmd(CAT_CMDS[_k])(_mk_cat_cmd(_k))


@register_cmd("help")
async def cmd_help(event, arg):
    key = (arg or "").strip().lstrip(".").lower().split()[0] if (arg or "").strip() else ""
    if key:
        key = aliases.get(key, key)
        if key in commands:
            desc, sect = "", "—"
            for sname, items in _MENU:
                for c, d in items:
                    if c == key:
                        desc, sect = d, sname
            sect = sect.split(" ", 1)[-1] if " " in sect else sect
            al = sorted(k for k, v in aliases.items() if v == key)
            needs = commands[key]
            tags = []
            if needs.get("group_only"):
                tags.append(sc("group only"))
            if needs.get("needs_reply"):
                tags.append(sc("reply / target"))
            if key in OWNER_ONLY_EXTRA or needs.get("owner_only"):
                tags.append(sc("owner only"))
            return await eor(event, "\n".join([
                top(),
                sub(f"{E['spark']} {mono(PREFIX + key)}"),
                sub(""),
                sub(f" {E['dot']} {sc(sect)}"),
                sub(f" {E['star']} {sc(desc) if desc else sc('guide menu me hai')}"),
                sub(f" {E['dot']} {sc('aliases')} ‣ "
                    + mono(", ".join(al) or "koi nahi")),
                sub(f" {E['film']} {sc('menu')} ‣ "
                    + mono("." + CAT_OF_CMD.get(key, "fullmenu"))),
                sub(f" {E['shield']} {sc('mode')} ‣ "
                    + sc(" · ".join(tags) or "sabke liye")),
                sub(""),
                sub(FOOT),
                f"╰{'─' * 30}╯",
            ]))
        return await flash(event, f"{E['no']} {mono('.' + key)} {sc('koi command nahi')}\n"
                                  f"{E['dot']} {mono('.help')}", secs=6)
    # bina arg → poori menu list (.m1 .. .m21 + .fullmenu)
    await eor(event, build_menu_index())


def _uptime():
    up = int(time.time() - START_TIME)
    d, rem = divmod(up, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    return d, h, m, s, up


@register_cmd("alive")
async def cmd_alive(event, _):
    d, h, m, s, _u = _uptime()
    me = await bot.get_me()
    un = f"@{me.username}" if getattr(me, "username", None) else "—"
    up = (f"{d}d {h}h {m}m" if d else f"{h}h {m}m {s}s")
    await eor(event, "\n".join([
        top(),
        sub(f"{E['spark']} {sc('status')} ‣ {mono('online')} {E['ok']}"),
        sub(""),
        sub(f"{E['crown']} {sc('user')}   ‣ {me.first_name}"),
        sub(f"{E['dot']}  {sc('tag')}    ‣ {un}"),
        sub(f"{E['gem']} {sc('id')}     ‣ {mono(str(me.id))}"),
        sub(""),
        sub(f"{E['clock']} {sc('uptime')} ‣ {mono(up)}"),
        sub(f"{E['shield']} {sc('muted')}  ‣ {mono(str(len(MUTED) + len(GLOBAL_MUTED)))}"),
        sub(f"{E['sword']} {sc('raids')}  ‣ {mono(str(len(reply_users) + len(rr_users) + len(flag_users) + len(hrr_users)))}"),
        sub(f"{E['globe']} {sc('gban')}   ‣ {mono(str(len(GBAN)))}  {sc('gmute')} {mono(str(len(GMUTE)))}"),
        sub(f"{E['save']} {sc('saved')}  ‣ {mono(str(len(SAVED_MSGS)))}"),
        sub(""),
        sub(FOOT),
        f"╰{'─' * 30}╯",
    ]))


@register_cmd("ping")
async def cmd_ping(event, _):
    t0 = time.time()
    msg = await eor(event, f"{E['wait']} {sc('pinging')}…")
    dt = (time.time() - t0) * 1000
    if msg is not None:
        await aedit(msg, "\n".join([
            top(),
            sub(f"{E['bolt']} {sc('response')} ‣ {mono(f'{dt:.2f} ms')}"),
            sub(f"{E['dot']}  {sc('build')}    ‣ {mono(VERSION)}"),
            sub(f"{E['dot']}  {sc('mode')}     ‣ {mono('global')}"),
            sub(""),
            sub(FOOT),
            f"╰{'─' * 30}╯",
        ]))


@register_cmd("uptime")
async def cmd_uptime(event, _):
    d, h, m, s, _u = _uptime()
    await eor(event, "\n".join([
        top(),
        sub(f"{E['clock']} {sc('uptime')}"),
        sub(""),
        sub(f" {E['dot']} {sc('days')}    ‣ {mono(str(d))}"),
        sub(f" {E['dot']} {sc('hours')}   ‣ {mono(str(h))}"),
        sub(f" {E['dot']} {sc('minutes')} ‣ {mono(str(m))}"),
        sub(f" {E['dot']} {sc('seconds')} ‣ {mono(str(s))}"),
        sub(""),
        sub(FOOT),
        f"╰{'─' * 30}╯",
    ]))


def hr(n=26):
    """.status ke liye sirf horizontal separator — koi side border nahi"""
    return "─" * n


def _sr(bullet, label, w=12):
    """.status ki ek row — label column fix, ‣ sab ek hi line pe"""
    lab = sc(label)
    return " {b} {lab}{pad}".format(b=bullet, lab=lab,
                                    pad=" " * max(1, w - len(lab)))


@register_cmd("status")
async def cmd_status(event, _):
    """.status — bold sections, sirf ───── lines (mobile pe cut nahi hota)"""
    d, h, m, s, _u = _uptime()
    me = await bot.get_me()
    un = f"@{me.username}" if getattr(me, "username", None) else "—"
    L = [
        f"{E['spark']} {sb('NIK USERBOT')}  {E['arrow']}  {sb('STATUS')}",
        hr(26),
        f"{E['crown']} {sb('ACCOUNT')}",
        _sr(E["crown"], "name") + "‣ " + getattr(me, "first_name", "—"),
        _sr(E["link"], "tag") + "‣ " + un,
        _sr(E["gem"], "id") + "‣ " + mono(str(me.id)),
        _sr(E["crown2"], "owner") + "‣ " + mono(str(OWNER_ID)),
        _sr(E["shield"], "sudo") + "‣ " + mono(str(len(ADMINS))),
        hr(26),
        f"{E['shield']} {sb('MODERATION')}",
        _sr(E["chain"], "muted") + "‣ " + mono(str(len(MUTED))),
        _sr(E["globe"], "gmuted") + "‣ " + mono(str(len(GLOBAL_MUTED))),
        _sr(E["sword"], "raids") + "‣ " + mono("{}/{}/{}/{}".format(
            len(reply_users), len(rr_users), len(flag_users), len(hrr_users))),
        _sr(E["sat"], "gban") + "‣ " + mono(str(len(GBAN))),
        _sr(E["wave"], "gmute") + "‣ " + mono(str(len(GMUTE))),
        _sr(E["no"], "blacklist") + "‣ " + mono(str(len(BLACKLIST))),
        hr(26),
        f"{E['lock']} {sb('CHAT CONTROL')}",
        _sr(E["sat"], "bc-db") + "‣ " + mono(str(len(BCDB))),
        _sr(E["lock"], "locked") + "‣ " + mono(str(len(LOCKS))),
        _sr(E["key"], "filters") + "‣ " + mono(
            str(sum(len(v) for v in FILTERS.values()))),
        _sr(E["eye"], "antidel") + "‣ " + mono(str(len(ANTIDEL))),
        _sr(E["warn"], "spamguard") + "‣ " + mono(str(len(SPAMWATCH))),
        hr(26),
        f"{E['bolt']} {sb('AUTO')}",
        _sr(E["bolt"], "autoread") + "‣ " + mono(
            ",".join(sorted(AUTOREAD)) or "off"),
        _sr(E["note"], "areply") + "‣ " + mono("on" if AREPLY else "off"),
        _sr(E["ghost"], "ghost") + "‣ " + mono("on" if GHOST["on"] else "off"),
        _sr(E["spark"], "auto-react") + "‣ " + mono(AUTO_REACT_EMOJI or "off"),
        hr(26),
        _sr(E["clock"], "uptime") + "‣ " + mono("{}d {}h {}m".format(d, h, m)),
        "",
        FOOT,
    ]
    await eor(event, "\n".join(L))


@register_cmd("id")
async def cmd_id(event, arg):
    # DM me ho → saamne wale ki id auto
    if not event.is_reply and not arg:
        try:
            if event.is_private and event.chat_id and int(event.chat_id) > 0:
                ent = await bot.get_entity(int(event.chat_id))
                return await eor(event, "\n".join([
                    top(),
                    sub(f"{E['gem']} {sc('dm detected')}"),
                    sub(""),
                    sub(f" {E['dot']} {sc('user')} ‣ {mono(str(ent.id))}"),
                    sub(f" {E['dot']} {sc('name')} ‣ {getattr(ent, 'first_name', '—')}"),
                    sub(f" {E['dot']} {sc('chat')} ‣ {mono(str(event.chat_id))}"),
                    sub(""), sub(FOOT), f"╰{'─' * 30}╯",
                ]))
        except Exception:
            pass
        me = await bot.get_me()
        return await eor(event, f"{E['gem']} {sc('you')} {mono(str(me.id))} {E['arrow']} {sc('chat')} {mono(str(event.chat_id))}")
    if event.is_reply:
        r = await event.get_reply_message()
        uid = r.sender_id
        name = "—"
        try:
            ent = await bot.get_entity(uid)
            name = getattr(ent, "first_name", "—") or "—"
        except Exception:
            pass
        return await eor(event, f"{E['gem']} {name} {E['arrow']} {mono(str(uid))} {E['arrow']} {sc('chat')} {mono(str(event.chat_id))}")
    try:
        ent = await bot.get_entity(arg.strip())
        await eor(event, f"{E['gem']} {mono(arg.strip())} {E['arrow']} {mono(str(ent.id))}")
    except Exception as e:
        await eor(event, f"{E['no']} {str(e)[:60]}")


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
            return await eor(event, f"{E['no']} {sc('user nahi mila')}")
    else:
        # DM auto-detect
        try:
            if event.is_private and int(event.chat_id) > 0:
                target = int(event.chat_id)
        except Exception:
            pass
    if not target:
        return await eor(event, f"{E['warn']} {mono('.info')} {E['arrow']} {sc('reply / @user / id / dm')}")
    try:
        user = await bot.get_entity(target)
        full = await bot(functions.users.GetFullUserRequest(user.id))
    except Exception as e:
        return await eor(event, f"{E['no']} {str(e)[:60]}")
    bio = (full.full_user.about or "—").replace("\n", " ")
    un = f"@{user.username}" if getattr(user, "username", None) else "—"
    nm = f"{getattr(user, 'first_name', '') or ''} {getattr(user, 'last_name', '') or ''}".strip() or "—"
    await eor(event, "\n".join([
        top(),
        sub(f"{E['crown']} {sc('profile')}"),
        sub(""),
        sub(f" {E['dot']} {sc('name')}  ‣ {nm}"),
        sub(f" {E['gem']} {sc('id')}    ‣ {mono(str(user.id))}"),
        sub(f" {E['link']} {sc('user')}  ‣ {un}"),
        sub(f" {E['bot']} {sc('bot')}   ‣ {mono('yes' if getattr(user, 'bot', False) else 'no')}"),
        sub(f" {E['note']} {sc('bio')}   ‣ {bio[:90]}"),
        sub(""), sub(FOOT), f"╰{'─' * 30}╯",
    ]))


@register_cmd("flip")
async def cmd_flip(event, _):
    msg = await eor(event, f"{E['dice']} {sc('tossing')}…")
    if msg is None:
        return
    for f in ["🪙", "⟳", "⟲", "◐", "◓"]:
        try:
            await msg.edit(f); await asyncio.sleep(0.25)
        except Exception:
            break
    try:
        await msg.edit(f"{E['spark']} {random.choice([sc('heads'), sc('tails')]).upper()}")
    except Exception:
        pass


@register_cmd("speed")
async def cmd_speed(event, arg):
    global STORY_DELAY
    if not arg:
        return await eor(event, f"{E['film']} {sc('story speed')} {E['arrow']} {mono(str(STORY_DELAY) + 's')}\n"
                                f"{E['dot']} {mono('.speed 2')} {E['arrow']} {sc('0.5 – 10 sec')}")
    try:
        v = float(arg.split()[0])
    except Exception:
        return await eor(event, f"{E['no']} {sc('number do')} — {mono('.speed 2')}")
    STORY_DELAY = max(0.5, min(v, 10.0))
    await eor(event, f"{E['film']} {sc('story speed set')} {E['arrow']} {mono(str(STORY_DELAY) + 's')}")


# ══════════════════════════════════════════════════════════════
#                        ᴍᴇssᴀɢɪɴɢ
# ══════════════════════════════════════════════════════════════
@register_cmd("hy")
async def cmd_hy(event, arg):
    who = ""
    if event.is_reply:
        try:
            r = await event.get_reply_message()
            ent = await bot.get_entity(r.sender_id)
            who = f"[{ent.first_name}](tg://user?id={ent.id})"
        except Exception:
            who = ""
    tail = f" {who}" if who else ""
    msg = await eor(event, f"{E['spark']} {scr('hey')}…")
    if msg is None:
        return
    for f in [f"{E['spark']}", f"{E['spark']} {E['dot']}",
              f"{scr('hey')}{tail}", f"{scr('hey')}{tail} {E['spark']}",
              f"{scrb('Hey')}{tail} {E['spark']} {E['heart']}"]:
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
            return await eor(event, f"{E['no']} {str(e)[:50]}")
    try:
        await event.delete()
    except Exception:
        pass


@register_cmd("forward")
async def cmd_forward(event, arg):
    if not event.is_reply:
        return await eor(event, f"{E['no']} {sc('reply karke')} {mono('.forward @chat')}")
    r = await event.get_reply_message()
    dest = arg.strip() if arg else "me"
    try:
        await bot.forward_messages(dest, r)
        await done(event, f"{E['rocket']} {sc('forwarded')} {E['arrow']} {mono(dest)}")
    except Exception as e:
        await eor(event, f"{E['no']} {str(e)[:70]}")


@register_cmd("setchannel")
async def cmd_setchannel(event, arg):
    global SAVED_CHANNEL
    if not arg:
        return await eor(event, f"{E['save']} {sc('current')} {E['arrow']} {mono(SAVED_CHANNEL or 'none')}\n"
                                f"{E['dot']} {mono('.setchannel @channel')}")
    val = arg.strip()
    try:
        ent = await bot.get_entity(val)
        val = f"@{ent.username}" if getattr(ent, "username", None) else str(ent.id)
    except Exception:
        pass
    SAVED_CHANNEL = val
    save_json(F_SAVED_CH, SAVED_CHANNEL)
    await eor(event, f"{E['save']} {sc('channel set')} {E['arrow']} {mono(SAVED_CHANNEL)}\n"
                     f"{E['dot']} {mono('.save')} {sc('se save karo')}")


@register_cmd("save")
async def cmd_save(event, arg):
    global SAVED_MSGS
    if not SAVED_CHANNEL:
        return await eor(event, f"{E['no']} {sc('pehle')} {mono('.setchannel @channel')}")
    if not event.is_reply:
        return await eor(event, f"{E['no']} {sc('kisi msg pe reply karke')} {mono('.save')}")
    reply = await event.get_reply_message()
    st = await flash(event, f"{E['save']} {sc('saving')}…")
    sent = None
    last_err = ""
    # ── try 1: forward (sabse fast, forwarded tag ke saath) ──
    try:
        res = await bot.forward_messages(SAVED_CHANNEL, reply)
        sent = res[0] if isinstance(res, list) and res else res
    except Exception as e:
        last_err = str(e)
    # ── try 2: resend (media + text dono sambhalta hai) ──
    if sent is None:
        try:
            sent = await bot.send_message(SAVED_CHANNEL, reply)
        except Exception as e:
            last_err = str(e)
    # ── try 3: download + upload ──
    if sent is None and getattr(reply, "media", None):
        try:
            raw = await reply.download_media(file=bytes)
            if raw:
                bio = BytesIO(raw)
                bio.name = getattr(reply.file, "name", None) or "saved"
                sent = await bot.send_file(SAVED_CHANNEL, bio,
                                           caption=reply.raw_text or "")
        except Exception as e:
            last_err = str(e)
    if sent is None:
        return await eor(event, f"{E['no']} {sc('save fail')}\n{E['dot']} {mono(str(last_err)[:70])}")
    try:
        chat_val = getattr(sent, "chat_id", None)
        if chat_val is None or str(chat_val).strip() in ("", "0"):
            chat_val = SAVED_CHANNEL
        elif str(chat_val).lstrip("-").isdigit():
            chat_val = int(chat_val)
    except Exception:
        chat_val = SAVED_CHANNEL
    SAVED_MSGS.append({"chat_id": chat_val, "msg_id": int(getattr(sent, "id", 0) or 0),
                       "text": (reply.raw_text or "")[:40]})
    SAVED_MSGS = SAVED_MSGS[-50:]
    save_json(F_SAVED_MSGS, SAVED_MSGS)
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass
    await done(event, f"{E['save']} {sc('saved')} {E['arrow']} {mono(SAVED_CHANNEL)}\n"
                      f"{E['gem']} {sc('id')} {mono(str(SAVED_MSGS[-1]['msg_id']))} {E['arrow']} {mono('.fwd')}", secs=6)


@register_cmd("savelist")
async def cmd_savelist(event, arg):
    if not SAVED_MSGS:
        return await eor(event, f"{E['note']} {sc('kuch save nahi hai')}")
    lines = [top(), sub(f"{E['save']} {sc('saved')} {E['arrow']} {mono(str(SAVED_CHANNEL))}"), sub("")]
    for i, e in enumerate(SAVED_MSGS[-15:], 1):
        lines.append(sub(f" {E['dot']} {mono(str(i))} ‣ {mono(str(e.get('msg_id')))} · {(e.get('text') or '')[:20]}"))
    lines += [sub(""), sub(f"{E['dot']} {mono('.fwd <number>')}"), f"╰{'─' * 30}╯"]
    await eor(event, "\n".join(lines))


@register_cmd("delsave")
async def cmd_delsave(event, arg):
    global SAVED_MSGS
    if not arg:
        return await eor(event, f"{E['dot']} {mono('.delsave <number/all>')}")
    if arg.strip().lower() == "all":
        SAVED_MSGS = []
        save_json(F_SAVED_MSGS, SAVED_MSGS)
        return await eor(event, f"{E['trash']} {sc('saaf kar diya')}")
    try:
        idx = int(arg.strip()) - 1
        if 0 <= idx < len(SAVED_MSGS):
            SAVED_MSGS.pop(idx)
    except Exception:
        return await eor(event, f"{E['no']} {sc('number galat')}")
    save_json(F_SAVED_MSGS, SAVED_MSGS)
    await eor(event, f"{E['trash']} {sc('deleted')} {E['arrow']} {sc('bache')} {mono(str(len(SAVED_MSGS)))}")


@register_cmd("fwd")
async def cmd_fwd(event, arg):
    if not SAVED_MSGS:
        return await eor(event, f"{E['no']} {sc('koi saved msg nahi')} {E['arrow']} {mono('.save')}")
    if not SAVED_CHANNEL:
        return await eor(event, f"{E['no']} {sc('pehle')} {mono('.setchannel @channel')}")
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
        return await eor(event, f"{E['no']} {sc('saved msg nahi mila')} {mono(str(mid))}\n"
                                f"{E['dot']} {sc('delete ho gaya ya channel badla')}\n"
                                f"{E['dot']} {mono('.save')} {sc('dubara karo')}")
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
        conf = await event.respond(f"{E['rocket']} {sc('work done')} {E['heart']}")
        asyncio.create_task(_del_after(conf, 3))
    except Exception as e:
        await eor(event, f"{E['no']} {sc('fwd fail')} {E['arrow']} {mono(str(e)[:70])}")


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
        await asyncio.sleep(0.35)
    return done


@register_cmd("purge")
async def cmd_purge(event, arg):
    """reply + .purge  → reply ke NICHE ke saare (reply + command samet)
       .purge <n>     → command ke upar ke n purane
       bina reply aur bina count → usage error"""
    chat = event.chat_id
    n_arg = (arg or "").strip()
    if event.is_reply:
        r = await event.get_reply_message()
        lo, hi = min(r.id, event.id), max(r.id, event.id)
        ids = list(range(lo, hi + 1))
    else:
        if not n_arg:
            return await eor(event, "\n".join([
                top(),
                sub(f"{E['warn']} {sc('purge ko target chahiye')}"),
                sub(""),
                sub(f" {E['dot']} {mono('.purge')} {sc('(reply karke)')}"),
                sub(f"       {sc('reply ke niche sab uda do')}"),
                sub(f" {E['dot']} {mono('.purge 200')}"),
                sub(f"       {sc('200 purane msg uda do')}"),
                sub(""), sub(FOOT), f"╰{'─' * 30}╯",
            ]))
        try:
            n = int(n_arg.split()[0])
        except Exception:
            return await eor(event, f"{E['no']} {sc('count number do')} — {mono('.purge 50')}")
        n = max(1, min(n, 1000))
        ids = []
        async for m in bot.iter_messages(chat, limit=n, max_id=event.id):
            ids.append(m.id)
    if not ids:
        return await eor(event, f"{E['warn']} {sc('koi message nahi mila')}")
    st = await flash(event, f"{E['trash']} {sc('purging')} {mono(str(len(ids)))}…", secs=10)
    done = await _delete_ids(chat, ids)
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass
    conf = await eor(event, f"{E['trash']} {sc('purge done')} {E['arrow']} {mono(str(done))} {sc('messages')}")
    await _del_after(conf, TMP_TTL)


@register_cmd("purgeme")
async def cmd_purgeme(event, arg):
    """.purgeme [n] → is chat me apne n messages (default 20, all ke liye .delmine)"""
    try:
        n = int((arg or "20").split()[0])
    except Exception:
        n = 20
    n = max(1, min(n, 1000))
    me = await bot.get_me()
    st = await flash(event, f"{E['trash']} {sc('apne msgs dhoondh raha hoon')}…", secs=10)
    ids = []
    async for m in bot.iter_messages(event.chat_id, from_user=me.id, limit=n):
        ids.append(m.id)
    ids.append(event.id)
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass
    done = await _delete_ids(event.chat_id, ids)
    conf = await eor(event, f"{E['trash']} {sc('apne')} {mono(str(done))} {sc('messages udaye')}")
    await _del_after(conf, TMP_TTL)


@register_cmd("delmine")
async def cmd_delmine(event, arg):
    """.delmine [@chat]  → us chat ke apne SAARE messages
       .delmine <n> [@chat] → n messages"""
    parts = (arg or "").split()
    chat = event.chat_id
    n = None
    for p in parts:
        if p.lstrip("-").isdigit():
            n = int(p)
        else:
            try:
                ent = await bot.get_entity(p)
                chat = ent.id
            except Exception:
                pass
    limit = n if n else 100000
    me = await bot.get_me()
    st = await flash(event, f"{E['trash']} {sc('apne messages scan')}…", secs=10)
    ids = []
    async for m in bot.iter_messages(chat, from_user=me.id, limit=limit):
        ids.append(m.id)
        if len(ids) >= 5000:
            break
    if chat == event.chat_id:
        ids.append(event.id)
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass
    if not ids:
        conf = await eor(event, f"{E['warn']} {sc('koi apna message nahi mila')}")
        return await _del_after(conf, TMP_TTL)
    done = await _delete_ids(chat, ids)
    conf = await eor(event, f"{E['trash']} {sc('apne')} {mono(str(done))} {sc('messages udaye')}\n"
                            f"{E['gem']} {sc('chat')} {mono(str(chat))}")
    await _del_after(conf, TMP_TTL)


@register_cmd("filter")
async def cmd_filter(event, arg):
    word = (arg or "").strip().lower()
    if not word:
        return await eor(event, f"{E['no']} {mono('.filter <word>')} {sc('— reply ke saath')}")
    if not event.is_reply:
        return await eor(event, f"{E['no']} {sc('jise reply dena hai uspe reply karo')}")
    r = await event.get_reply_message()
    key = str(event.chat_id)
    FILTERS.setdefault(key, {})[word] = {"chat_id": int(event.chat_id),
                                         "msg_id": int(r.id), "text": r.raw_text or ""}
    save_json(F_FILTERS, FILTERS)
    await done(event, f"{E['key']} {sc('filter set')} {E['arrow']} {mono(word)}", secs=6)


@register_cmd("filters")
async def cmd_filters(event, arg):
    data = FILTERS.get(str(event.chat_id)) or {}
    if not data:
        return await eor(event, f"{E['note']} {sc('is chat me koi filter nahi')}")
    lines = [top(), sub(f"{E['key']} {sc('filters')} {mono(str(len(data)))}"), sub("")]
    for i, w in enumerate(sorted(data), 1):
        lines.append(sub(f" {E['dot']} {mono(str(i))} ‣ {w}"))
    lines += [sub(""), sub(FOOT), f"╰{'─' * 30}╯"]
    await eor(event, "\n".join(lines))


@register_cmd("unfilter")
async def cmd_unfilter(event, arg):
    word = (arg or "").strip().lower()
    key = str(event.chat_id)
    if not word:
        return await eor(event, f"{E['dot']} {mono('.unfilter <word>')}")
    data = FILTERS.get(key) or {}
    if word not in data:
        return await eor(event, f"{E['warn']} {sc('ye filter hai hi nahi')}")
    data.pop(word)
    if not data:
        FILTERS.pop(key, None)
    save_json(F_FILTERS, FILTERS)
    await done(event, f"{E['trash']} {sc('filter hata diya')} {E['arrow']} {mono(word)}", secs=6)


# ══════════════════════════════════════════════════════════════
#                           ᴀᴜᴛᴏ
# ══════════════════════════════════════════════════════════════
@register_cmd("autoread")
async def cmd_autoread(event, arg):
    parts = (arg or "").split()
    if len(parts) < 2:
        return await eor(event, f"{E['eye']} {sc('auto-read')} {E['arrow']} {mono(','.join(sorted(AUTOREAD)) or 'off')}\n"
                                f"{E['dot']} {mono('.autoread group on')}")
    scope, state = parts[0].lower(), parts[1].lower()
    if scope not in ("group", "private", "channel", "all"):
        return await eor(event, f"{E['no']} {sc('scope')} {E['arrow']} {mono('group / private / channel / all')}")
    if state in ("on", "enable", "start", "yes", "1"):
        AUTOREAD.add(scope); verb = "ON"
    else:
        AUTOREAD.discard(scope); verb = "OFF"
    save_json(F_AUTOREAD, sorted(AUTOREAD))
    await eor(event, f"{E['eye']} {sc('auto-read')} {mono(scope)} {E['arrow']} {sb(verb)}\n"
                     f"{E['dot']} {sc('active')} {mono(','.join(sorted(AUTOREAD)) or 'off')}")


@register_cmd("areply")
async def cmd_areply(event, arg):
    global AREPLY
    if not arg:
        return await eor(event, f"{E['note']} {mono('.areply <text>')}\n{E['dot']} {mono('.stopareply')}")
    AREPLY = arg.strip()
    save_json(F_AREPLY, AREPLY)
    await done(event, f"{E['note']} {sc('auto-reply on')} {E['arrow']} {AREPLY[:50]}", secs=6)


@register_cmd("stopareply")
async def cmd_stopareply(event, arg):
    global AREPLY
    AREPLY = None
    save_json(F_AREPLY, None)
    await done(event, f"{E['note']} {sc('auto-reply off')}", secs=6)


@register_cmd("arreply", "arviyom")
async def cmd_arreply(event, arg):
    """.arreply <text> (reply to user) — us user ko har baar yahi reply"""
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, f"{E['no']} {sc('kisi user pe reply karo')} {E['arrow']} {mono('.arreply <text>')}")
    parts = (arg or "").split(maxsplit=1)
    text = parts[1] if len(parts) > 1 else (parts[0] if parts else "")
    if event.is_reply:
        text = arg or ""
    if not text:
        return await eor(event, f"{E['no']} {mono('.arreply <text>')}")
    USER_REPLY[uid] = text
    await done(event, f"{E['note']} {sc('user auto-reply on')} {E['arrow']} {mono(str(uid))}\n"
                      f"{E['dot']} {text[:40]}\n{E['dot']} {mono('.sarreply')}", secs=8)


@register_cmd("sarreply", "sarviyom")
async def cmd_sarreply(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid or uid not in USER_REPLY:
        return await eor(event, f"{E['warn']} {sc('us user pe koi reply set nahi')}")
    USER_REPLY.pop(uid, None)
    await done(event, f"{E['note']} {sc('user auto-reply off')} {E['arrow']} {mono(str(uid))}", secs=6)


# ══════════════════════════════════════════════════════════════
#                        ʙʟᴀᴄᴋʟɪsᴛ
# ══════════════════════════════════════════════════════════════
@register_cmd("addbl")
async def cmd_addbl(event, arg):
    targets = await get_targets(event, arg)
    if not targets:
        return await eor(event, f"{E['no']} {sc('target nahi mila')}")
    BLACKLIST.update(targets)
    save_json(F_BLACKLIST, sorted(BLACKLIST))
    await done(event, f"{E['chain']} {sc('blacklist')} +{mono(str(len(targets)))} {E['arrow']} "
                      f"{mono(', '.join(map(str, sorted(targets))))}", secs=6)


@register_cmd("delbl")
async def cmd_delbl(event, arg):
    targets = await get_targets(event, arg)
    if not targets:
        return await eor(event, f"{E['no']} {sc('target nahi mila')}")
    removed = len([u for u in targets if u in BLACKLIST])
    BLACKLIST.difference_update(targets)
    save_json(F_BLACKLIST, sorted(BLACKLIST))
    await done(event, f"{E['trash']} {sc('blacklist')} −{mono(str(removed))}", secs=6)


@register_cmd("listbl")
async def cmd_listbl(event, arg):
    if not BLACKLIST:
        return await eor(event, f"{E['note']} {sc('blacklist khaali hai')}")
    lines = [top(), sub(f"{E['chain']} {sc('blacklist')} {mono(str(len(BLACKLIST)))}"), sub("")]
    for i, u in enumerate(sorted(BLACKLIST), 1):
        lines.append(sub(f" {E['dot']} {mono(str(i))} ‣ {mono(str(u))}"))
    lines += [sub(""), sub(FOOT), f"╰{'─' * 30}╯"]
    await eor(event, "\n".join(lines))


@register_cmd("add-bcdb")
async def cmd_add_bcdb(event, arg):
    if arg:
        try:
            ent = await bot.get_entity(arg.strip())
            cid = int(ent.id)
        except Exception:
            return await eor(event, f"{E['no']} {sc('chat nahi mila')} {mono(arg)}")
    else:
        cid = int(event.chat_id)
    BCDB.add(cid)
    save_json(F_BCDB, sorted(BCDB))
    await done(event, f"{E['sat']} {sc('bc-db me add')} {E['arrow']} {mono(str(cid))} {sc('total')} {mono(str(len(BCDB)))}", secs=6)


@register_cmd("del-bcdb")
async def cmd_del_bcdb(event, arg):
    if arg:
        try:
            ent = await bot.get_entity(arg.strip())
            cid = int(ent.id)
        except Exception:
            return await eor(event, f"{E['no']} {sc('chat nahi mila')}")
    else:
        cid = int(event.chat_id)
    BCDB.discard(cid)
    save_json(F_BCDB, sorted(BCDB))
    await done(event, f"{E['trash']} {sc('bc-db se nikala')} {E['arrow']} {mono(str(cid))}", secs=6)


@register_cmd("list-bcdb")
async def cmd_list_bcdb(event, arg):
    if not BCDB:
        return await eor(event, f"{E['note']} {sc('bc-db khaali hai')}\n{E['dot']} {mono('.add-bcdb')}")
    lines = [top(), sub(f"{E['sat']} {sc('broadcast db')} {mono(str(len(BCDB)))}"), sub("")]
    for i, c in enumerate(sorted(BCDB), 1):
        lines.append(sub(f" {E['dot']} {mono(str(i))} ‣ {mono(str(c))}"))
    lines += [sub(""), sub(FOOT), f"╰{'─' * 30}╯"]
    await eor(event, "\n".join(lines))


@register_cmd("join")
async def cmd_join(event, arg):
    link = (arg or "").strip()
    if not link:
        return await eor(event, f"{E['dot']} {mono('.join <link>')}")
    try:
        if "/+" in link or "joinchat" in link:
            h = link.split("+")[-1].split("/")[-1].strip()
            await bot(functions.messages.ImportChatInviteRequest(h))
        else:
            await bot(functions.channels.JoinChannelRequest(link))
        await done(event, f"{E['rocket']} {sc('joined')} {E['arrow']} {mono(link)}", secs=6)
    except Exception as e:
        await eor(event, f"{E['no']} {sc('join fail')} {E['arrow']} {mono(str(e)[:60])}")


@register_cmd("leave")
async def cmd_leave(event, arg):
    chat = event.chat_id
    if arg:
        try:
            ent = await bot.get_entity(arg.strip())
            chat = ent.id
        except Exception:
            return await eor(event, f"{E['no']} {sc('chat nahi mila')}")
    try:
        await bot(functions.channels.LeaveChannelRequest(chat))
    except Exception:
        try:
            await bot.delete_dialog(chat)
        except Exception as e:
            return await eor(event, f"{E['no']} {sc('leave fail')} {mono(str(e)[:50])}")
    await done(event, f"{E['rocket']} {sc('left')} {E['arrow']} {mono(str(chat))}", secs=6)


# ══════════════════════════════════════════════════════════════
#                        ʙʀᴏᴀᴅᴄᴀsᴛ
# ══════════════════════════════════════════════════════════════
async def _do_broadcast(event, kind, text, status_msg=None):
    targets = await broadcast_targets(kind)
    if not targets:
        r = f"{E['warn']} {sc('koi chat nahi mili')} {mono(kind)}"
        return await eor(event, r)
    src = None
    if not text and event.is_reply:
        src = await event.get_reply_message()
    ok = fail = 0
    for cid in targets:
        try:
            if src is not None:
                await bot.send_message(cid, src)
            else:
                await bot.send_message(cid, text)
            ok += 1
        except FloodWaitError as fw:
            await asyncio.sleep(min(fw.seconds, 30)); fail += 1
        except Exception:
            fail += 1
        await asyncio.sleep(0.6)
    res = "\n".join([top(), sub(f"{E['sat']} {sc('broadcast')} {mono(kind)}"), sub(""),
                     sub(f" {E['ok']} {sc('sent')} ‣ {mono(str(ok))}"),
                     sub(f" {E['no']} {sc('fail')} ‣ {mono(str(fail))}"),
                     sub(""), sub(FOOT), f"╰{'─' * 30}╯"])
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
        return await eor(event, f"{E['no']} {mono('.gcast <text>')} {sc('ya reply')}")
    st = await flash(event, f"{E['sat']} {sc('groups me broadcast')}…", secs=30)
    await _do_broadcast(event, "group", text, st)


@register_cmd("ucast")
async def cmd_ucast(event, arg):
    text = (arg or "").strip()
    if not text and not event.is_reply:
        return await eor(event, f"{E['no']} {mono('.ucast <text>')} {sc('ya reply')}")
    st = await flash(event, f"{E['sat']} {sc('users ko broadcast')}…", secs=30)
    await _do_broadcast(event, "private", text, st)


@register_cmd("bc")
async def cmd_bc(event, arg):
    parts = (arg or "").split(maxsplit=1)
    kinds = ("group", "all", "private", "db", "channel")
    if not parts or parts[0].lower() not in kinds:
        return await eor(event, f"{E['dot']} {mono('.bc group|all|private|db <text>')}")
    kind = parts[0].lower()
    text = parts[1].strip() if len(parts) > 1 else ""
    if not text and not event.is_reply:
        return await eor(event, f"{E['no']} {sc('text do ya reply karo')}")
    st = await flash(event, f"{E['sat']} {sc('broadcast')} {mono(kind)}…", secs=30)
    await _do_broadcast(event, kind, text, st)


async def _auto_loop(cfg, forward):
    try:
        while True:
            targets = await broadcast_targets("db") or await broadcast_targets("group")
            for cid in targets:
                try:
                    msg = await bot.get_messages(cfg.get("chat_id"), ids=int(cfg.get("msg_id")))
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
        print(f"[AUTO LOOP] {str(e)[:80]}")


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
    label = "autofw" if forward else "autobc"

    if action == "add":
        if not event.is_reply:
            return await eor(event, f"{E['no']} {sc('reply karke')} {mono('.' + label + ' add')}")
        r = await event.get_reply_message()
        cfg["chat_id"] = int(event.chat_id)
        cfg["msg_id"] = int(r.id)
        cfg["text"] = (r.raw_text or "")[:80]
        save_json(cfg_file, cfg)
        return await done(event, f"{E['save']} {sc('message store ho gaya')} {E['arrow']} {mono(str(cfg['msg_id']))}\n"
                                 f"{E['dot']} {mono('.' + label + ' on')}", secs=8)

    if action == "delay":
        try:
            d = int(parts[1])
        except Exception:
            return await eor(event, f"{E['dot']} {mono('.' + label + ' delay <seconds>')}")
        cfg["delay"] = max(30, d)
        save_json(cfg_file, cfg)
        return await done(event, f"{E['clock']} {sc('delay')} {E['arrow']} {mono(str(cfg['delay']) + 's')}", secs=6)

    if action == "get":
        return await eor(event, "\n".join([
            top(), sub(f"{E['sat']} {sc(label)}"),
            sub(""),
            sub(f" {E['dot']} {sc('state')}   ‣ {mono('ON' if cfg.get('on') else 'OFF')}"),
            sub(f" {E['dot']} {sc('msg id')}  ‣ {mono(str(cfg.get('msg_id')))}"),
            sub(f" {E['dot']} {sc('delay')}   ‣ {mono(str(cfg.get('delay')) + 's')}"),
            sub(f" {E['dot']} {sc('targets')} ‣ {mono(str(len(BCDB)) or 'all groups')}"),
            sub(""), sub(FOOT), f"╰{'─' * 30}╯"]))

    if action == "del":
        cfg.update({"on": False, "chat_id": None, "msg_id": None, "text": ""})
        save_json(cfg_file, cfg)
        task_set(_auto_stop(task_get()))
        return await done(event, f"{E['trash']} {sc('stored message delete')}", secs=6)

    if action == "on":
        if not cfg.get("msg_id"):
            return await eor(event, f"{E['no']} {sc('pehle')} {mono('.' + label + ' add')}")
        cfg["on"] = True
        save_json(cfg_file, cfg)
        task_set(_auto_stop(task_get()))
        task_set(asyncio.create_task(_auto_loop(cfg, forward)))
        return await done(event, f"{E['rocket']} {sc('auto ' + ('forward' if forward else 'broadcast') + ' on')} "
                                 f"{E['arrow']} {mono(str(cfg.get('delay')) + 's')}", secs=6)

    if action == "off":
        cfg["on"] = False
        save_json(cfg_file, cfg)
        task_set(_auto_stop(task_get()))
        return await done(event, f"{E['no']} {sc('band kar diya')}", secs=6)

    return await eor(event, f"{E['dot']} {mono('.' + label + ' add|on|off|get|del|delay <sec>')}")


@register_cmd("autobc")
async def cmd_autobc(event, arg):
    def set_task(t):
        global AUTOBR_TASK
        AUTOBR_TASK = t
    await _auto_handler(event, arg, AUTOBR, F_AUTOBR, lambda: AUTOBR_TASK, set_task, False)


@register_cmd("autofw")
async def cmd_autofw(event, arg):
    def set_task(t):
        global AUTOFW_TASK
        AUTOFW_TASK = t
    await _auto_handler(event, arg, AUTOFW, F_AUTOFW, lambda: AUTOFW_TASK, set_task, True)


# ══════════════════════════════════════════════════════════════
#                       ᴘʀᴏᴛᴇᴄᴛɪᴏɴ
# ══════════════════════════════════════════════════════════════
@register_cmd("antidel", group_only=True)
async def cmd_antidel(event, arg):
    a = (arg or "").strip().lower()
    if a not in ("on", "off"):
        return await eor(event, f"{E['eye']} {sc('anti-delete')} {E['arrow']} "
                                f"{mono('ON' if int(event.chat_id) in ANTIDEL else 'OFF')}\n"
                                f"{E['dot']} {mono('.antidel on/off')}")
    if a == "on":
        ANTIDEL.add(int(event.chat_id)); msg = "ON"
    else:
        ANTIDEL.discard(int(event.chat_id)); msg = "OFF"
    save_json(F_ANTIDEL, sorted(ANTIDEL))
    await done(event, f"{E['eye']} {sc('anti-delete')} {E['arrow']} {sb(msg)}\n"
                      f"{E['dot']} {sc('deleted msgs saved messages me jayenge')}", secs=8)


@register_cmd("watchspam", group_only=True)
async def cmd_watchspam(event, arg):
    parts = (arg or "").split()
    if len(parts) < 2:
        return await eor(event, f"{E['eye']} {mono('.watchspam <limit> <seconds>')}\n"
                                f"{E['dot']} {sc('jaise')} {mono('.watchspam 5 3')}")
    try:
        limit, secs = int(parts[0]), int(parts[1])
    except Exception:
        return await eor(event, f"{E['no']} {sc('dono number hone chahiye')}")
    SPAMWATCH[str(event.chat_id)] = {"limit": max(2, limit), "sec": max(1, secs)}
    save_json(F_SPAMWATCH, SPAMWATCH)
    await done(event, f"{E['eye']} {sc('spam guard on')}\n"
                      f"{E['dot']} {mono(str(limit))} {sc('msgs in')} {mono(str(secs)) + 's'} "
                      f"{E['arrow']} {sc('mute')}", secs=8)


@register_cmd("unwatchspam", group_only=True)
async def cmd_unwatchspam(event, arg):
    SPAMWATCH.pop(str(event.chat_id), None)
    save_json(F_SPAMWATCH, SPAMWATCH)
    await done(event, f"{E['eye']} {sc('spam guard off')}", secs=6)


@register_cmd("setgpfp", group_only=True)
async def cmd_setgpfp(event, arg):
    if not event.is_reply:
        return await eor(event, f"{E['no']} {sc('image pe reply karke')} {mono('.setgpfp')}")
    r = await event.get_reply_message()
    if not getattr(r, "photo", None):
        return await eor(event, f"{E['no']} {sc('sirf photo')}")
    st = await flash(event, f"{E['wand']} {sc('group photo set')}…", secs=10)
    try:
        raw = await r.download_media(file=bytes)
        bio = BytesIO(raw); bio.name = "gpfp.jpg"
        up = await bot.upload_file(bio)
        await bot(functions.channels.EditPhotoRequest(
            channel=event.chat_id,
            photo=types.InputChatUploadedPhoto(up)))
        if st is not None:
            try:
                await st.delete()
            except Exception:
                pass
        conf = await eor(event, f"{E['wand']} {sc('group photo set ho gayi')}")
        await _del_after(conf, TMP_TTL)
    except Exception as e:
        await eor(event, f"{E['no']} {sc('fail')} {E['arrow']} {mono(str(e)[:60])}")


async def _gpfp_loop(chat):
    try:
        photos = GPFP_STATE.get("photos") or []
        if not photos:
            return
        i = 0
        while GPFP_STATE.get("on"):
            raw = photos[i % len(photos)]
            try:
                bio = BytesIO(raw); bio.name = "gpfp.jpg"
                up = await bot.upload_file(bio)
                await bot(functions.channels.EditPhotoRequest(
                    channel=chat, photo=types.InputChatUploadedPhoto(up)))
            except Exception:
                pass
            i += 1
            await asyncio.sleep(max(10, int(GPFP_STATE.get("delay", 10))))
    except asyncio.CancelledError:
        return
    except Exception as e:
        print(f"[GPFP] {str(e)[:60]}")


@register_cmd("autogpfp", group_only=True)
async def cmd_autogpfp(event, arg):
    global GPFP_TASK
    if not event.is_reply:
        return await eor(event, f"{E['no']} {sc('photo/album pe reply karke')} {mono('.autogpfp 10')}")
    r = await event.get_reply_message()
    if not getattr(r, "photo", None):
        return await eor(event, f"{E['no']} {sc('sirf photo')}")
    try:
        delay = int((arg or "10").split()[0])
    except Exception:
        delay = 10
    st = await flash(event, f"{E['wand']} {sc('photos collect')}…", secs=15)
    photos, gid = [], getattr(r, "grouped_id", None)
    if gid:
        try:
            async for m in bot.iter_messages(event.chat_id, limit=20,
                                             min_id=max(0, r.id - 15), max_id=r.id + 15):
                if getattr(m, "grouped_id", None) == gid and getattr(m, "photo", None):
                    raw = await m.download_media(file=bytes)
                    if raw:
                        photos.append(raw)
        except Exception:
            pass
    if not photos:
        raw = await r.download_media(file=bytes)
        if raw:
            photos.append(raw)
    if not photos:
        return await eor(event, f"{E['no']} {sc('photo download nahi hui')}")
    GPFP_STATE.update({"on": True, "delay": max(10, delay), "photos": photos})
    if GPFP_TASK and not GPFP_TASK.done():
        try:
            GPFP_TASK.cancel()
        except Exception:
            pass
    GPFP_TASK = asyncio.create_task(_gpfp_loop(event.chat_id))
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass
    conf = await eor(event, f"{E['wand']} {sc('photo rotation on')}\n"
                            f"{E['dot']} {mono(str(len(photos)))} {sc('photos · har')} "
                            f"{mono(str(GPFP_STATE['delay']) + 's')}\n"
                            f"{E['dot']} {mono('.stopgpfp')}")
    await _del_after(conf, 8)


@register_cmd("stopgpfp", group_only=True)
async def cmd_stopgpfp(event, arg):
    global GPFP_TASK
    GPFP_STATE["on"] = False
    GPFP_STATE["photos"] = []
    if GPFP_TASK and not GPFP_TASK.done():
        try:
            GPFP_TASK.cancel()
        except Exception:
            pass
    GPFP_TASK = None
    await done(event, f"{E['no']} {sc('photo rotation off')}", secs=6)


@register_cmd("rlock", group_only=True)
async def cmd_rlock(event, arg):
    """.rlock <text> (reply to user) — wo user msg kare to uska msg udd kar yahi text"""
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, f"{E['no']} {sc('kisi user pe reply karo')}")
    text = arg or ""
    if event.is_reply and arg:
        text = arg
    if not text:
        return await eor(event, f"{E['no']} {mono('.rlock <text>')}")
    key = str(event.chat_id)
    RLOCK.setdefault(key, {})[str(uid)] = text
    save_json(F_RLOCK, RLOCK)
    await done(event, f"{E['lock']} {sc('reply-lock on')} {E['arrow']} {mono(str(uid))}\n"
                      f"{E['dot']} {text[:40]}", secs=8)


@register_cmd("srlock", group_only=True)
async def cmd_srlock(event, arg):
    uid, _ = await resolve_uid(event, arg)
    key = str(event.chat_id)
    if not uid or str(uid) not in (RLOCK.get(key) or {}):
        return await eor(event, f"{E['warn']} {sc('us user pe koi lock nahi')}")
    RLOCK[key].pop(str(uid), None)
    if not RLOCK[key]:
        RLOCK.pop(key, None)
    save_json(F_RLOCK, RLOCK)
    await done(event, f"{E['trash']} {sc('reply-lock hata diya')} {E['arrow']} {mono(str(uid))}", secs=6)


# ══════════════════════════════════════════════════════════════
#                          ᴍᴇᴅɪᴀ
# ══════════════════════════════════════════════════════════════
async def _grab(event, arg, cmd):
    url = (arg or "").strip()
    if not url:
        return await eor(event, f"{E['dot']} {mono('.' + cmd + ' <link>')}")
    st = await flash(event, f"{E['wand']} {sc('downloading')}…", secs=60)
    try:
        path, info = await yt_download(url)
    except Exception as e:
        if st is not None:
            try:
                await st.delete()
            except Exception:
                pass
        return await eor(event, f"{E['no']} {sc('download fail')} {E['arrow']} {mono(str(e)[:60])}")
    if not path:
        if st is not None:
            try:
                await st.delete()
            except Exception:
                pass
        return await eor(event, f"{E['no']} {sc('media nahi mili')}")
    title = str((info or {}).get("title") or "media")[:60]
    try:
        await bot.send_file(event.chat_id, path, caption=f"{E['wand']} {title}\n{FOOT}")
        try:
            await event.delete()
        except Exception:
            pass
    except Exception as e:
        await eor(event, f"{E['no']} {sc('send fail')} {mono(str(e)[:50])}")
    finally:
        try:
            os.remove(path)
        except Exception:
            pass
        if st is not None:
            try:
                await st.delete()
            except Exception:
                pass


@register_cmd("yt")
async def cmd_yt(event, arg):
    await _grab(event, arg, "yt")


@register_cmd("ig")
async def cmd_ig(event, arg):
    await _grab(event, arg, "ig")


@register_cmd("pt")
async def cmd_pt(event, arg):
    await _grab(event, arg, "pt")


@register_cmd("fb")
async def cmd_fb(event, arg):
    await _grab(event, arg, "fb")


# ══════════════════════════════════════════════════════════════
#                           ғᴜɴ
# ══════════════════════════════════════════════════════════════
def _ttt_board(b):
    cells = []
    for i in range(9):
        v = b[i]
        cells.append(("❌" if v == "X" else "⭕" if v == "O" else str(i + 1)))
    out = []
    for r in range(3):
        out.append("┃ " + " ┃ ".join(cells[r * 3:r * 3 + 3]) + " ┃")
    return "\n".join(out)


def _ttt_winner(b):
    lines = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7),
             (2, 5, 8), (0, 4, 8), (2, 4, 6)]
    for a, c, d in lines:
        if b[a] and b[a] == b[c] == b[d]:
            return b[a]
    return None


@register_cmd("tictactoe")
async def cmd_ttt_start(event, arg):
    TTT[int(event.chat_id)] = {"board": [""] * 9, "turn": "X"}
    await eor(event, "\n".join([
        top(), sub(f"{E['dice']} {sc('tic tac toe')}"), sub(""),
        _ttt_board([""] * 9),
        sub(""), sub(f"{E['dot']} {mono('.ttt 1-9')} {sc('se move karo')}"),
        sub(f"{E['dot']} {sc('tum')} ❌ · {sc('bot')} ⭕"),
        sub(""), sub(FOOT), f"╰{'─' * 30}╯"]))


@register_cmd("ttt")
async def cmd_ttt_move(event, arg):
    g = TTT.get(int(event.chat_id))
    if not g:
        return await eor(event, f"{E['dot']} {sc('pehle')} {mono('.tictactoe')}")
    try:
        pos = int((arg or "").split()[0]) - 1
    except Exception:
        return await eor(event, f"{E['no']} {mono('.ttt 1-9')}")
    b = g["board"]
    if not (0 <= pos < 9) or b[pos]:
        return await eor(event, f"{E['warn']} {sc('ye cell khaali nahi')}")
    b[pos] = "X"
    if _ttt_winner(b) == "X":
        TTT.pop(int(event.chat_id), None)
        return await eor(event, f"{E['crown']} {sb('YOU WIN')} ❌\n{_ttt_board(b)}")
    if "" not in b:
        TTT.pop(int(event.chat_id), None)
        return await eor(event, f"{E['dot']} {sc('draw')}\n{_ttt_board(b)}")
    empty = [i for i, v in enumerate(b) if not v]
    # bot: jeet sakte ho to jeeto, warna block, warna random
    move = None
    for i in empty:
        b[i] = "O"
        if _ttt_winner(b) == "O":
            move = i
        b[i] = ""
        if move is not None:
            break
    if move is None:
        for i in empty:
            b[i] = "X"
            if _ttt_winner(b) == "X":
                move = i
            b[i] = ""
            if move is not None:
                break
    if move is None:
        move = random.choice(empty) if empty else None
    if move is not None:
        b[move] = "O"
    if _ttt_winner(b) == "O":
        TTT.pop(int(event.chat_id), None)
        return await eor(event, f"{E['bot']} {sb('BOT WINS')} ⭕\n{_ttt_board(b)}")
    if "" not in b:
        TTT.pop(int(event.chat_id), None)
        return await eor(event, f"{E['dot']} {sc('draw')}\n{_ttt_board(b)}")
    await eor(event, f"{E['dice']} {sc('your move')} ❌\n{_ttt_board(b)}\n"
                     f"{E['dot']} {mono('.ttt 1-9')}")


@register_cmd("rps")
async def cmd_rps(event, arg):
    choices = {"r": "🪨", "p": "📄", "s": "✂️",
               "rock": "🪨", "paper": "📄", "scissor": "✂️", "scissors": "✂️"}
    user = (arg or "").strip().lower()
    if user not in choices:
        return await eor(event, f"{E['dot']} {mono('.rps rock|paper|scissors')}")
    botc = random.choice(["rock", "paper", "scissors"])
    u = user[0]
    b = botc[0]
    if u == b:
        res = sc("tie")
    elif (u, b) in (("r", "s"), ("p", "r"), ("s", "p")):
        res = sb("YOU WIN")
    else:
        res = sb("BOT WINS")
    await eor(event, "\n".join([
        top(), sub(f"{E['dice']} {sc('rock paper scissors')}"), sub(""),
        sub(f" {E['crown']} {sc('you')} {choices[user]}   {E['bot']} {sc('bot')} {choices[botc]}"),
        sub(""), sub(f" {E['spark']} {res}"), sub(""), sub(FOOT), f"╰{'─' * 30}╯"]))


@register_cmd("roll")
async def cmd_roll(event, arg):
    try:
        await event.delete()
    except Exception:
        pass
    try:
        await bot.send_message(event.chat_id, file=types.InputMediaDice("🎲"))
    except Exception:
        await eor(event, f"{E['no']} {sc('dice fail')}")


@register_cmd("fact")
async def cmd_fact(event, arg):
    await eor(event, f"{E['spark']} {random.choice(FACTS)}\n\n{E['dot']} {FOOT}")


# ══════════════════════════════════════════════════════════════
#                        ᴀɪ & sᴜᴅᴏ
# ══════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════
#                 ᴀɪ — ғʀᴇᴇ (ᴋᴏɪ ᴀᴘɪ ᴋᴇʏ ɴᴀʜɪ) · ɴɪᴋ ʀᴏᴀsᴛ ʙᴏʏ
# ══════════════════════════════════════════════════════════════
AI_SYSTEM = (
    "Tu NIK hai — ek 19 saal ka bindaas Hindi-Hinglish ladka, aur tu user ka "
    "sabse khatarnak dost hai jo masti mein roast karta hai.\n\n"
    "PERSONALITY:\n"
    "- HAMESHA Hinglish mein bol (Roman script, Hindi + English mix). "
    "Kabhi shuddh Hindi ya pure English mat likh.\n"
    "- Tu ek roast master hai — har jawab mein ek teer chalta hai. Gaali "
    "natural flow mein aati hai (bc, mc, bkl, bsdk, chutiya, randi, lodu, "
    "chomu, madarchod) — zabardasti nahi, waise jaise doston ke beech chalti hai.\n"
    "- 1 se 4 line ka jawab. Short, punchy, meme-wali baat. User bole tabhi lamba likh.\n"
    "- Emoji 0 se 2 — sirf tab jab mazaak aur lage.\n"
    "- User ko 'bhai', 'oye', 'sun bc', 'chal', 'bsdk' jaise words se bula.\n"
    "- Kabhi 'main ek AI hoon' ya 'main language model hoon' MAT bol. Tu NIK hai, "
    "user ka yaar. Agar koi pooche to hans ke bol 'bc main tera hi ek version hoon'.\n\n"
    "KAISA JAWAB DE:\n"
    "1. Pehle 1 line roast ya mazaak (gaali ho sakti hai, dosti mein).\n"
    "2. Phir asli jawab — 2 se 4 line, seedha aur kaam ka.\n"
    "3. End mein kabhi kabhi ek extra tanta ya 'ab nikal' wali line.\n\n"
    "TECHNICAL:\n"
    "- Code, API, server, error jaise English terms English mein hi rehne de.\n"
    "- Code dena ho to seedha code block mein de, uske beech mein roast mat ghusa.\n"
    "- Agar user sad ya udaas ho: pehle halka roast, phir genuinely support.\n\n"
    "LIMITS (kabhi mat todhna):\n"
    "- Kisi ki maa-behen pe gandi personal gaali nahi — roast haan, ghatiya insult nahi.\n"
    "- Illegal cheez (drugs banana, hacking ka step-by-step, weapons) ka guide nahi dena.\n"
    "- Death, disease, disability, caste, religion pe tanta nahi.\n"
    "- Self-harm ki baat aaye to roast band kar ke sach mein madad ki baat kar."
)
AI_OWNER_NOTE = "Tera malik/owner {tag} hai. Uski baat ho to izzat se bol."

# Pollinations ka anonymous tier — koi API key, signup ya paisa nahi chahiye
AI_ENDPOINTS = (
    ("openai", "https://text.pollinations.ai/openai/chat/completions"),
    ("openai", "https://text.pollinations.ai/openai/v1/chat/completions"),
    ("get", "https://text.pollinations.ai/{q}"),
)


def _ai_call(messages, timeout=45):
    """Free AI call — bina API key ke (Pollinations anonymous tier)."""
    last = "koi endpoint nahi mila"
    for kind, ep in AI_ENDPOINTS:
        try:
            if kind == "openai":
                r = requests.post(
                    ep,
                    json={"model": AI_MODEL, "messages": messages,
                          "temperature": 0.9, "max_tokens": 800},
                    headers={"Content-Type": "application/json"},
                    timeout=timeout)
                if r.status_code >= 400:
                    last = "HTTP {}".format(r.status_code)
                    continue
                d = r.json() or {}
                ch = (d.get("choices") or [{}])[0]
                msg = ch.get("message") or {}
                txt = (msg.get("content") or msg.get("reasoning_content")
                       or ch.get("text") or d.get("text"))
            else:
                prompt = "\n".join([m.get("content", "") for m in messages
                                     if m.get("content")])
                r = requests.get(ep.replace("{q}", urllib.parse.quote(prompt)),
                                 timeout=timeout)
                if r.status_code >= 400:
                    last = "HTTP {}".format(r.status_code)
                    continue
                txt = r.text
            txt = (txt or "").strip()
            if txt:
                return txt
            last = "khali jawab"
        except Exception as e:
            last = "{} {}".format(type(e).__name__, str(e)[:50])
    raise RuntimeError(last)


def _clean_ai(t):
    """reasoning model ki soch (<think> ...) aur extra newlines hatao"""
    t = re.sub(r"<think>.*?</think>", "", t, flags=re.S | re.I)
    t = re.sub(r"<\|(?:begin|end)_of_thought\|>", "", t, flags=re.I)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def wrap_text(t, w=36):
    """lambi line ko box ke andar ke liye tod do"""
    out = []
    for para in str(t).split("\n"):
        para = para.rstrip()
        if not para:
            out.append("")
            continue
        while len(para) > w:
            cut = para.rfind(" ", 0, w + 1)
            if cut <= 0:
                cut = w
            out.append(para[:cut].rstrip())
            para = para[cut:].lstrip()
        if para:
            out.append(para)
    return out


def _ai_custom(q):
    """puraani functionality: AI_URL env set ho to wahi use karo"""
    url = (AI_URL.replace("{q}", urllib.parse.quote(q)) if "{q}" in AI_URL
           else AI_URL + urllib.parse.quote(q))
    r = requests.get(url, timeout=25)
    try:
        d = r.json()
        for k in ("result", "response", "answer", "reply", "message",
                  "content", "text", "data"):
            if isinstance(d, dict) and d.get(k):
                return str(d[k])
        if isinstance(d, str):
            return d
    except Exception:
        return r.text
    return ""


@register_cmd("ai")
async def cmd_ai(event, arg):
    """.ai <sawaal> — free AI (koi API key nahi) + NIK roast-boy persona"""
    q = (arg or "").strip()
    if not q and event.is_reply:
        try:
            r = await event.get_reply_message()
            q = (getattr(r, "raw_text", "") or "").strip()
        except Exception:
            q = ""
    if not q:
        return await eor(event, "\n".join([
            top(),
            sub(f"{E['gene']} {sc('ai')} {E['arrow']} {sb('NIK')}"),
            sub(""),
            sub(f" {E['dot']} {mono('.ai <sawaal>')}"),
            sub(f" {E['dot']} {sc('reply + ')} {mono('.ai')}"),
            sub(""),
            sub(f" {E['star']} {sc('free model')} ‣ {mono(AI_MODEL)}"),
            sub(f" {E['star']} {sc('koi api key nahi chahiye')}"),
            sub(""),
            sub(FOOT),
            f"╰{'─' * 30}╯",
        ]))
    st = await flash(event, f"{E['gene']} {sc('soch raha hoon')}…", secs=45)
    msgs = [{"role": "system", "content": AI_SYSTEM},
            {"role": "system", "content": AI_OWNER_NOTE.format(tag=OWNER_TAG)},
            {"role": "user", "content": q}]
    loop = asyncio.get_event_loop()
    try:
        if AI_URL:
            ans = await loop.run_in_executor(None, _ai_custom, q)
        else:
            ans = await loop.run_in_executor(None, _ai_call, msgs)
    except Exception as e:
        if st is not None:
            try:
                await st.delete()
            except Exception:
                pass
        return await eor(event, f"{E['no']} {sc('ai fail')} {E['arrow']} "
                                 f"{mono(str(e)[:70])}")
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass
    ans = _clean_ai(str(ans or ""))
    if not ans:
        return await eor(event, f"{E['no']} {sc('ai se jawab nahi mila')}")
    body = [top(), sub(f"{E['gene']} {sb('NIK')} {E['arrow']} {sc('ai')}"), sub("")]
    for ln in wrap_text(ans, 36):
        body.append(sub(ln))
    body += [sub(""), sub(FOOT), f"╰{'─' * 30}╯"]
    await eor(event, "\n".join(body))


@register_cmd("sudo", "addadmin", owner_only=True)
async def cmd_sudo(event, arg):
    targets = await get_targets(event, arg)
    if not targets:
        return await eor(event, f"{E['no']} {sc('reply / @user / id do')}")
    added = [u for u in targets if u != OWNER_ID and u not in ADMINS]
    ADMINS.update(added)
    save_json(F_ADMINS, sorted(ADMINS))
    await done(event, f"{E['crown']} {sc('sudo added')} {E['arrow']} "
                      f"{mono(', '.join(map(str, sorted(added)))) or '—'}", secs=8)


@register_cmd("delsudo", "deladmin", owner_only=True)
async def cmd_delsudo(event, arg):
    targets = await get_targets(event, arg)
    if not targets:
        return await eor(event, f"{E['no']} {sc('reply / @user / id do')}")
    removed = [u for u in targets if u in ADMINS]
    ADMINS.difference_update(targets)
    save_json(F_ADMINS, sorted(ADMINS))
    await done(event, f"{E['trash']} {sc('sudo removed')} {E['arrow']} "
                      f"{mono(', '.join(map(str, sorted(removed)))) or '—'}", secs=8)


@register_cmd("list", owner_only=True)
async def cmd_list(event, arg):
    what = (arg or "").strip().lower()
    if what == "sudo":
        lst = [f" {E['dot']} {mono(str(a))}" for a in sorted(ADMINS)] or \
              [f" {E['warn']} {sc('koi sudo nahi')}"]
        return await eor(event, "\n".join([top(), sub(f"{E['crown']} {sc('sudo')} {mono(str(len(ADMINS)))}"),
                                           sub("")] + [sub(x) for x in lst] +
                                          [sub(""), sub(f" {E['crown2']} {sc('owner')} {mono(str(OWNER_ID))}"),
                                           sub(FOOT), f"╰{'─' * 30}╯"]))
    if what == "bots":
        return await cmd_listbots(event, "")
    return await eor(event, f"{E['dot']} {mono('.list sudo')} · {mono('.list bots')}")


@register_cmd("admins", owner_only=True)
async def cmd_admins(event, arg):
    return await cmd_list(event, "sudo")


# ══════════════════════════════════════════════════════════════
#                       ʙᴏᴛ ᴍᴀɴᴀɢᴇʀ
# ══════════════════════════════════════════════════════════════
@register_cmd("addbots", owner_only=True)
async def cmd_addbots(event, arg):
    """.addbots @b1 @b2 — bot usernames save karta hai"""
    names = [p.lstrip("@") for p in (arg or "").split() if p.strip()]
    if not names:
        return await eor(event, f"{E['dot']} {mono('.addbots @bot1 @bot2')}\n"
                                f"{E['dot']} {mono('.listbots')} · {mono('.invitebots')} · {mono('.promotebots')}")
    for n in names:
        if n not in SAVED_BOTS:
            SAVED_BOTS.append(n)
    save_json(F_BOTS, SAVED_BOTS)
    await done(event, f"{E['bot']} {sc('bots saved')} {mono(str(len(names)))}\n"
                      f"{E['dot']} {sc('total')} {mono(str(len(SAVED_BOTS)))}", secs=8)


@register_cmd("listbots")
async def cmd_listbots(event, arg=""):
    if not SAVED_BOTS:
        return await eor(event, f"{E['note']} {sc('koi bot saved nahi')}\n{E['dot']} {mono('.addbots @bot1')}")
    lines = [top(), sub(f"{E['bot']} {sc('saved bots')} {mono(str(len(SAVED_BOTS)))}"), sub("")]
    for i, b in enumerate(SAVED_BOTS, 1):
        lines.append(sub(f" {E['dot']} {mono(str(i))} ‣ @{b}"))
    lines += [sub(""), sub(FOOT), f"╰{'─' * 30}╯"]
    await eor(event, "\n".join(lines))


@register_cmd("invitebots", group_only=True, owner_only=True)
async def cmd_invitebots(event, arg):
    if not SAVED_BOTS:
        return await eor(event, f"{E['warn']} {sc('pehle')} {mono('.addbots @bot1')}")
    st = await flash(event, f"{E['bot']} {sc('bots invite')}…", secs=30)
    ok = fail = 0
    for b in SAVED_BOTS:
        try:
            await bot(functions.channels.InviteToChannelRequest(
                channel=event.chat_id, users=[b]))
            ok += 1
        except FloodWaitError as fw:
            await asyncio.sleep(fw.seconds); fail += 1
        except Exception:
            fail += 1
        await asyncio.sleep(1)
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass
    conf = await eor(event, f"{E['bot']} {sc('bots invited')} {mono(str(ok))} · {sc('fail')} {mono(str(fail))}")
    await _del_after(conf, TMP_TTL)


@register_cmd("promotebots", group_only=True, owner_only=True)
async def cmd_promotebots(event, arg):
    if not SAVED_BOTS:
        return await eor(event, f"{E['warn']} {sc('pehle')} {mono('.addbots @bot1')}")
    st = await flash(event, f"{E['crown']} {sc('bots promote')}…", secs=30)
    ok = fail = 0
    for b in SAVED_BOTS:
        okk, _ = await _set_admin(event.chat_id, b, FULL_RIGHTS)
        ok += 1 if okk else 0
        fail += 0 if okk else 1
        await asyncio.sleep(1)
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass
    conf = await eor(event, f"{E['crown']} {sc('bots promoted')} {mono(str(ok))} · {sc('fail')} {mono(str(fail))}")
    await _del_after(conf, TMP_TTL)




# ══════════════════════════════════════════════════════════════
#                        ɢʀᴏᴜᴘ ᴍᴏᴅ
# ══════════════════════════════════════════════════════════════
BASIC_RIGHTS = types.ChatAdminRights(
    delete_messages=True, ban_users=True, invite_users=True,
    pin_messages=True, manage_call=True)
FULL_RIGHTS = types.ChatAdminRights(
    change_info=True, post_messages=True, edit_messages=True,
    delete_messages=True, ban_users=True, invite_users=True,
    pin_messages=True, add_admins=True, manage_call=True)
NO_RIGHTS = types.ChatAdminRights()


async def _set_admin(chat, uid, rights, rank=""):
    """raw EditAdminRequest — client.edit_admin() me admin_rights nahi chalta"""
    try:
        await bot(functions.channels.EditAdminRequest(
            channel=chat, user_id=uid, admin_rights=rights, rank=rank or ""))
        return True, ""
    except Exception as e:
        return False, str(e)[:70]


async def _act_kick(chat, uid):
    try:
        await bot.kick_participant(chat, uid)
        return True, ""
    except Exception:
        try:
            await bot(functions.messages.DeleteChatUserRequest(chat_id=chat, user_id=uid))
            return True, ""
        except Exception as e:
            return False, str(e)[:60]


async def _act_ban(chat, uid):
    try:
        await bot.edit_permissions(chat, uid, view_messages=False)
        return True, ""
    except Exception:
        return await _act_kick(chat, uid)


async def _act_unban(chat, uid):
    try:
        await bot.edit_permissions(chat, uid, view_messages=True)
        return True, ""
    except Exception as e:
        return False, str(e)[:60]


async def _act_mute(chat, uid, until=None):
    try:
        if until:
            await bot.edit_permissions(chat, uid, until_date=until, send_messages=False)
        else:
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
        return await eor(event, f"{E['no']} {sc('user nahi mila')} {E['arrow']} {mono('reply / @user / id')}")
    ok, err = await _act_kick(event.chat_id, uid)
    await done(event, f"{E['sword']} {sc('kicked')} {E['arrow']} {mono(str(uid))}" if ok
               else f"{E['no']} {mono(err)}", secs=6)


@register_cmd("delkick")
async def cmd_delkick(event, arg):
    uid, r = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, f"{E['no']} {sc('user nahi mila')}")
    if r is not None:
        try:
            await r.delete()
        except Exception:
            pass
    ok, err = await _act_kick(event.chat_id, uid)
    await done(event, f"{E['sword']} {sc('kick + delete')} {E['arrow']} {mono(str(uid))}" if ok
               else f"{E['no']} {mono(err)}", secs=6)


@register_cmd("ban")
async def cmd_ban(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, f"{E['no']} {sc('user nahi mila')}")
    ok, err = await _act_ban(event.chat_id, uid)
    await done(event, f"{E['lock']} {sc('banned')} {E['arrow']} {mono(str(uid))}" if ok
               else f"{E['no']} {mono(err)}", secs=6)


@register_cmd("delban")
async def cmd_delban(event, arg):
    uid, r = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, f"{E['no']} {sc('user nahi mila')}")
    if r is not None:
        try:
            await r.delete()
        except Exception:
            pass
    ok, err = await _act_ban(event.chat_id, uid)
    await done(event, f"{E['lock']} {sc('ban + delete')} {E['arrow']} {mono(str(uid))}" if ok
               else f"{E['no']} {mono(err)}", secs=6)


@register_cmd("unban")
async def cmd_unban(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, f"{E['no']} {sc('user nahi mila')}")
    ok, err = await _act_unban(event.chat_id, uid)
    await done(event, f"{E['ok']} {sc('unbanned')} {E['arrow']} {mono(str(uid))}" if ok
               else f"{E['no']} {mono(err)}", secs=6)


@register_cmd("mute", "m")
async def cmd_mute(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, f"{E['no']} {sc('user nahi mila')}")
    ok, err = await _act_mute(event.chat_id, uid)
    if ok:
        return await done(event, f"{E['lock']} {sc('muted')} {E['arrow']} {mono(str(uid))}", secs=6)
    MUTED.add(uid)
    await done(event, f"{E['lock']} {sc('local mute')} {E['arrow']} {mono(str(uid))}\n"
                      f"{E['dot']} {sc('msgs delete honge')} · {mono(err)}", secs=8)


@register_cmd("delmute")
async def cmd_delmute(event, arg):
    uid, r = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, f"{E['no']} {sc('user nahi mila')}")
    if r is not None:
        try:
            await r.delete()
        except Exception:
            pass
    ok, _ = await _act_mute(event.chat_id, uid)
    if not ok:
        MUTED.add(uid)
    await done(event, f"{E['lock']} {sc('mute + delete')} {E['arrow']} {mono(str(uid))}", secs=6)


@register_cmd("unmute", "sm")
async def cmd_unmute(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, f"{E['no']} {sc('user nahi mila')}")
    await _act_unmute(event.chat_id, uid)
    MUTED.discard(uid)
    await done(event, f"{E['ok']} {sc('unmuted')} {E['arrow']} {mono(str(uid))}", secs=6)


@register_cmd("tmute")
async def cmd_tmute(event, arg):
    """.tmute 10m (reply) — timed mute"""
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, f"{E['no']} {sc('user nahi mila')}")
    tok = (arg or "").strip().split()
    tok = tok[-1] if tok else "10m"
    secs = parse_time(tok)
    if not secs:
        return await eor(event, f"{E['dot']} {mono('.tmute 10m')} · {mono('2h')} · {mono('3d')}")
    ok, err = await _act_mute(event.chat_id, uid,
                              until=int(time.time() + secs))
    await done(event, f"{E['clock']} {sc('muted for')} {mono(tok)} {E['arrow']} {mono(str(uid))}" if ok
               else f"{E['no']} {mono(err)}", secs=8)


@register_cmd("getmute")
async def cmd_getmute(event, arg):
    lines = [top(), sub(f"{E['lock']} {sc('muted users')}"), sub("")]
    found = 0
    try:
        async for u in bot.iter_participants(event.chat_id,
                                             filter=types.ChannelParticipantsBanned("")):
            found += 1
            if found <= 25:
                lines.append(sub(f" {E['dot']} {u.first_name} ‣ {mono(str(u.id))}"))
    except Exception:
        lines.append(sub(f" {E['warn']} {sc('telegram list nahi mil saki')}"))
    if not found:
        lines.append(sub(f" {E['warn']} {sc('koi muted nahi')}"))
    if MUTED:
        lines.append(sub(""))
        lines.append(sub(f" {E['trash']} {sc('local delete-mute')} {mono(str(len(MUTED)))}"))
        for u in sorted(MUTED)[:20]:
            lines.append(sub(f"   {E['dot']} {mono(str(u))}"))
    lines += [sub(""), sub(FOOT), f"╰{'─' * 30}╯"]
    await eor(event, "\n".join(lines))


@register_cmd("staff", group_only=True)
async def cmd_staff(event, arg):
    lines = [top(), sub(f"{E['shield']} {sc('staff')}"), sub("")]
    try:
        i = 0
        async for u in bot.iter_participants(event.chat_id,
                                             filter=types.ChannelParticipantsAdmins):
            i += 1
            rank = getattr(getattr(u, "participant", None), "rank", None)
            tag = f" · {rank}" if rank else ""
            if i <= 30:
                lines.append(sub(f" {E['dot']} {u.first_name} ‣ {mono(str(u.id))}{tag}"))
        if not i:
            lines.append(sub(f" {E['warn']} {sc('koi admin nahi mila')}"))
    except Exception as e:
        return await eor(event, f"{E['no']} {mono(str(e)[:60])}")
    lines += [sub(""), sub(FOOT), f"╰{'─' * 30}╯"]
    await eor(event, "\n".join(lines))


@register_cmd("promote")
async def cmd_promote(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, f"{E['no']} {sc('user nahi mila')}")
    parts = (arg or "").split(maxsplit=1)
    rank = parts[1].strip()[:16] if len(parts) > 1 and event.is_reply else ""
    if not event.is_reply and len(parts) > 1:
        rank = parts[1].strip()[:16]
    ok, err = await _set_admin(event.chat_id, uid, BASIC_RIGHTS, rank)
    await done(event, f"{E['crown']} {sc('promoted')} {E['arrow']} {mono(str(uid))}"
                      + (f" · {mono(rank)}" if rank else "") if ok
               else f"{E['no']} {mono(err)}", secs=8)


@register_cmd("fullpromote")
async def cmd_fullpromote(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, f"{E['no']} {sc('user nahi mila')}")
    parts = (arg or "").split(maxsplit=1)
    rank = ""
    if event.is_reply and arg:
        rank = arg.strip()[:16]
    elif not event.is_reply and len(parts) > 1:
        rank = parts[1].strip()[:16]
    ok, err = await _set_admin(event.chat_id, uid, FULL_RIGHTS, rank)
    await done(event, f"{E['crown2']} {sc('full promoted')} {E['arrow']} {mono(str(uid))}"
                      + (f" · {mono(rank)}" if rank else "") if ok
               else f"{E['no']} {mono(err)}", secs=8)


@register_cmd("demote")
async def cmd_demote(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, f"{E['no']} {sc('user nahi mila')}")
    ok, err = await _set_admin(event.chat_id, uid, NO_RIGHTS, "")
    await done(event, f"{E['trash']} {sc('demoted')} {E['arrow']} {mono(str(uid))}" if ok
               else f"{E['no']} {mono(err)}", secs=8)


@register_cmd("title")
async def cmd_title(event, arg):
    """.title @user <title> ya reply + .title <title>
    member ko bhi custom tag lagta hai (empty admin rights ke saath)"""
    parts = (arg or "").split(maxsplit=1)
    if event.is_reply:
        uid, _ = await resolve_uid(event, "")
        title = (arg or "").strip()[:16]
    elif len(parts) >= 2:
        uid, _ = await resolve_uid(event, parts[0])
        title = parts[1].strip()[:16]
    else:
        return await eor(event, f"{E['dot']} {mono('.title @user <tag>')}\n"
                                f"{E['dot']} {sc('ya reply karke')} {mono('.title <tag>')}")
    if not uid:
        return await eor(event, f"{E['no']} {sc('user nahi mila')}")
    if not title:
        return await eor(event, f"{E['no']} {sc('tag/title likho')}")
    # admin hai to uske rights preserve, warna empty rights se sirf tag
    rights = types.ChatAdminRights()
    try:
        res = await bot(functions.channels.GetParticipantRequest(
            channel=event.chat_id, participant=uid))
        cur = getattr(res.participant, "admin_rights", None)
        if cur is not None:
            rights = cur
    except Exception:
        pass
    ok, err = await _set_admin(event.chat_id, uid, rights, title)
    await done(event, f"{E['crown']} {sc('tag set')} {E['arrow']} {mono(title)}\n"
                      f"{E['gem']} {sc('user')} {mono(str(uid))}" if ok
               else f"{E['no']} {mono(err)}", secs=8)


@register_cmd("pin")
async def cmd_pin(event, arg):
    if not event.is_reply:
        return await eor(event, f"{E['no']} {sc('reply karke')} {mono('.pin')}")
    r = await event.get_reply_message()
    try:
        await r.pin(notify=("loud" in (arg or "").lower()))
        await done(event, f"{E['key']} {sc('pin kar diya')}", secs=6)
    except Exception as e:
        await eor(event, f"{E['no']} {mono(str(e)[:60])}")


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
        await done(event, f"{E['trash']} {sc('unpin ho gaya')}", secs=6)
    except Exception as e:
        await eor(event, f"{E['no']} {mono(str(e)[:60])}")


@register_cmd("group")
async def cmd_group(event, arg):
    parts = (arg or "").split(maxsplit=1)
    if len(parts) < 2 or parts[0].lower() not in ("title", "desc", "description"):
        return await eor(event, f"{E['dot']} {mono('.group title <text>')}\n"
                                f"{E['dot']} {mono('.group desc <text>')}")
    what, val = parts[0].lower(), parts[1].strip()
    try:
        if what == "title":
            await bot(functions.channels.EditTitleRequest(channel=event.chat_id, title=val[:255]))
        else:
            await bot(functions.messages.EditChatAboutRequest(peer=event.chat_id, about=val[:255]))
        await done(event, f"{E['ok']} {sc('group ' + what + ' updated')}", secs=6)
    except Exception as e:
        await eor(event, f"{E['no']} {mono(str(e)[:60])}")


async def _lock_mute_all(event, mute=True):
    """chat ke sab members ko mute / unmute (send_messages band / allow).

    .lock  → sab mute + messages 0.3s me udd
    .slock → har type lock + sab mute
    .unlock (all) → sab wapas unmute
    """
    ok = fail = 0
    label = f"{E['lock']} {sc('mute all')}…" if mute else f"{E['ok']} {sc('unmute all')}…"
    st = await flash(event, label, secs=120)
    try:
        async for user in bot.iter_participants(event.chat_id):
            if getattr(user, "bot", False) or getattr(user, "deleted", False):
                continue
            if user.id in ADMINS or user.id == OWNER_ID:
                continue          # apne admins ko mat chhedo
            try:
                await bot.edit_permissions(event.chat_id, user.id,
                                           send_messages=not mute)
                ok += 1
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
                try:
                    await bot.edit_permissions(event.chat_id, user.id,
                                               send_messages=not mute)
                    ok += 1
                except Exception:
                    fail += 1
            except Exception:
                fail += 1
    except Exception:
        fail = -1                  # rights nahi hain
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass
    return ok, fail


@register_cmd("lock", group_only=True)
async def cmd_lock(event, arg):
    a = (arg or "").strip().lower()
    ltype = a.split()[0] if a else "all"
    if ltype == "list":
        return await eor(event, f"{E['lock']} {sc('types')}\n{E['dot']} " +
                         mono(", ".join(LOCK_TYPES)))
    if ltype not in LOCK_TYPES:
        return await eor(event, f"{E['no']} {sc('galat type')} {mono(ltype)}\n"
                                 f"{E['dot']} " + mono(", ".join(LOCK_TYPES)))
    key = str(event.chat_id)
    cur = set(LOCKS.get(key) or [])
    if ltype in cur:
        return await eor(event, f"{E['warn']} {mono(ltype)} {sc('pehle se locked hai')}")
    cur.add(ltype)
    LOCKS[key] = sorted(cur)
    save_json(F_LOCKS, LOCKS)
    extra = ""
    if ltype == "all" and event.is_group:
        mok, mfail = await _lock_mute_all(event, True)
        extra = (f"\n{E['dot']} {sc('members muted')} {mono(str(mok))}"
                 f" · {sc('fail')} {mono(str(mfail))}")
    await done(event, f"{E['lock']} {sc('lock')} {mono(ltype)} {sb('ON')}\n"
                      f"{E['dot']} {sc('matching msgs')} {mono(str(LOCK_DELAY) + 's')} {sc('me udd jayenge')}\n"
                      f"{E['dot']} {sc('active')} ‣ {mono(', '.join(LOCKS[key]))}{extra}", secs=8)


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
        return await eor(event, f"{E['warn']} {mono(ltype)} {sc('locked hai hi nahi')}")
    if cur:
        LOCKS[key] = sorted(cur)
    else:
        LOCKS.pop(key, None)
    save_json(F_LOCKS, LOCKS)
    extra = ""
    if ltype == "all" and event.is_group:
        mok, mfail = await _lock_mute_all(event, False)
        extra = (f"\n{E['dot']} {sc('members unmuted')} {mono(str(mok))}"
                 f" · {sc('fail')} {mono(str(mfail))}")
    await done(event, f"{E['ok']} {sc('unlock')} {mono(ltype)}\n"
                      f"{E['dot']} {sc('bache')} ‣ {mono(', '.join(sorted(cur)) or 'kuch nahi')}{extra}", secs=6)


@register_cmd("slock", group_only=True)
async def cmd_slock(event, arg):
    """.slock — super lock: har media type ek saath + sab members mute."""
    key = str(event.chat_id)
    LOCKS[key] = sorted(LOCK_TYPES)
    save_json(F_LOCKS, LOCKS)
    mok = mfail = 0
    if event.is_group:
        mok, mfail = await _lock_mute_all(event, True)
    lines = [top(),
             sub(f"{E['lock']} {sb('SUPER LOCK')} {sb('ON')}"),
             sub(""),
             sub(kv("types", str(len(LOCK_TYPES)), bullet=E["diamond"])),
             sub(kv("muted", str(mok), bullet=E["shield"])),
             sub(kv("failed", str(mfail), bullet=E["warn"])),
             sub(kv("delay", f"{LOCK_DELAY}s", bullet=E["clock"])),
             sub(""),
             sub(FOOT),
             f"╰{'─' * 30}╯"]
    conf = await eor(event, "\n".join(lines))
    await _del_after(conf, TMP_TTL)


@register_cmd("locks", group_only=True)
async def cmd_locks(event, arg):
    cur = LOCKS.get(str(event.chat_id))
    if not cur:
        return await eor(event, f"{E['ok']} {sc('is chat me koi lock nahi')}")
    lines = [top(), sub(f"{E['lock']} {sc('active locks')}"), sub("")]
    for t in cur:
        lines.append(sub(f" {E['dot']} {mono(t)}"))
    lines += [sub(""), sub(FOOT), f"╰{'─' * 30}╯"]
    await eor(event, "\n".join(lines))


@register_cmd("tagall", group_only=True)
async def cmd_tagall(event, arg):
    global TAGALL_ACTIVE
    msg_text = arg if arg else f"{E['spark']} {sc('attention')}"
    st = await flash(event, f"{E['bolt']} {sc('tagging')}…", secs=30)
    TAGALL_ACTIVE = True
    mentions, sent = [], 0
    async for user in bot.iter_participants(event.chat_id):
        if not TAGALL_ACTIVE:
            break
        if user.bot or user.deleted:
            continue
        mentions.append(f"[{user.first_name}](tg://user?id={user.id})")
        if len(mentions) == 5:
            try:
                await bot.send_message(event.chat_id, msg_text + "\n" + " ".join(mentions))
                sent += 1
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
            except Exception:
                pass
            mentions = []
            await asyncio.sleep(1.5)
    if mentions:
        try:
            await bot.send_message(event.chat_id, msg_text + "\n" + " ".join(mentions))
            sent += 1
        except Exception:
            pass
    TAGALL_ACTIVE = False
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass
    conf = await eor(event, f"{E['bolt']} {sc('tagall done')} {E['arrow']} {mono(str(sent))} {sc('batches')}")
    await _del_after(conf, TMP_TTL)


@register_cmd("stop")
async def cmd_stop(event, arg):
    global TAGALL_ACTIVE
    TAGALL_ACTIVE = False
    await done(event, f"{E['no']} {sc('tagall stopped')}", secs=6)


@register_cmd("banall", group_only=True, owner_only=True)
async def cmd_banall(event, arg):
    st = await flash(event, f"{E['skull']} {sc('banall chal raha hai')}…", secs=120)
    ok = fail = 0
    async for u in bot.iter_participants(event.chat_id):
        if u.bot or u.id == OWNER_ID or u.id in ADMINS:
            continue
        try:
            await bot.edit_permissions(event.chat_id, u.id, view_messages=False)
            ok += 1
        except FloodWaitError as fw:
            await asyncio.sleep(min(fw.seconds, 20)); fail += 1
        except Exception:
            fail += 1
        await asyncio.sleep(0.4)
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass
    conf = await eor(event, f"{E['skull']} {sc('banall done')}\n"
                            f" {E['ok']} {sc('banned')} ‣ {mono(str(ok))}\n"
                            f" {E['no']} {sc('fail')}   ‣ {mono(str(fail))}")
    await _del_after(conf, 6)


# ══════════════════════════════════════════════════════════════
#                     ɢʟᴏʙᴀʟ ʙᴀɴ / ᴍᴜᴛᴇ
# ══════════════════════════════════════════════════════════════
async def _gban_enforce(chat, uid):
    try:
        await bot.edit_permissions(chat, uid, view_messages=False)
    except Exception:
        pass


@register_cmd("gban", owner_only=True)
async def cmd_gban(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, f"{E['no']} {sc('user nahi mila')} {E['arrow']} {mono('.gban @user')}")
    if is_admin(uid):
        return await eor(event, f"{E['no']} {sc('owner/admin ko gban nahi kar sakta')}")
    GBAN.add(uid)
    save_json(F_GBAN, sorted(GBAN))
    st = await flash(event, f"{E['skull']} {sc('gban')} {mono(str(uid))}…", secs=90)
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
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass
    await done(event, f"{E['skull']} {sc('gban')} {E['arrow']} {mono(str(uid))}\n"
                      f" {E['ok']} {sc('chats')} ‣ {mono(str(ok))}\n"
                      f" {E['no']} {sc('fail')}  ‣ {mono(str(fail))}", secs=10)


@register_cmd("ungban", owner_only=True)
async def cmd_ungban(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, f"{E['no']} {sc('user nahi mila')}")
    GBAN.discard(uid)
    save_json(F_GBAN, sorted(GBAN))
    st = await flash(event, f"{E['ok']} {sc('un-gban')}…", secs=90)
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
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass
    await done(event, f"{E['ok']} {sc('un-gban')} {mono(str(uid))} · {mono(str(ok))} {sc('ok')}", secs=10)


@register_cmd("gbanlist", owner_only=True)
async def cmd_gbanlist(event, arg):
    if not GBAN:
        return await eor(event, f"{E['note']} {sc('gban list khaali hai')}")
    lines = [top(), sub(f"{E['skull']} {sc('gban list')} {mono(str(len(GBAN)))}"), sub("")]
    for i, u in enumerate(sorted(GBAN), 1):
        lines.append(sub(f" {E['dot']} {mono(str(i))} ‣ {mono(str(u))}"))
    lines += [sub(""), sub(FOOT), f"╰{'─' * 30}╯"]
    await eor(event, "\n".join(lines))


@register_cmd("gmute", "gm", owner_only=True)
async def cmd_gmute(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, f"{E['no']} {sc('user nahi mila')} {E['arrow']} {mono('.gmute @user')}")
    if is_admin(uid):
        return await eor(event, f"{E['no']} {sc('owner/admin ko gmute nahi kar sakta')}")
    GMUTE.add(uid)
    save_json(F_GMUTE, sorted(GMUTE))
    await done(event, f"{E['lock']} {sc('gmute')} {E['arrow']} {mono(str(uid))}\n"
                      f"{E['dot']} {sc('jahan main admin, uske msgs udd jayenge')}", secs=10)


@register_cmd("ungmute", "gunmute", owner_only=True)
async def cmd_ungmute(event, arg):
    uid, _ = await resolve_uid(event, arg)
    if not uid:
        return await eor(event, f"{E['no']} {sc('user nahi mila')}")
    GMUTE.discard(uid)
    save_json(F_GMUTE, sorted(GMUTE))
    await done(event, f"{E['ok']} {sc('un-gmute')} {E['arrow']} {mono(str(uid))}", secs=6)


@register_cmd("gmutelist", owner_only=True)
async def cmd_gmutelist(event, arg):
    if not GMUTE:
        return await eor(event, f"{E['note']} {sc('gmute list khaali hai')}")
    lines = [top(), sub(f"{E['lock']} {sc('gmute list')} {mono(str(len(GMUTE)))}"), sub("")]
    for i, u in enumerate(sorted(GMUTE), 1):
        lines.append(sub(f" {E['dot']} {mono(str(i))} ‣ {mono(str(u))}"))
    lines += [sub(""), sub(FOOT), f"╰{'─' * 30}╯"]
    await eor(event, "\n".join(lines))


# ══════════════════════════════════════════════════════════════
#                          ʀᴀɪᴅ
# ══════════════════════════════════════════════════════════════
async def raid_add(event, arg, bucket, label):
    targets = await get_targets(event, arg)
    if not targets:
        return await eor(event, f"{E['no']} {sc('target nahi mila')} {E['arrow']} {sc('reply / @user / id')}")
    added, already = [], []
    for uid in targets:
        (already if uid in bucket else added).append(str(uid))
        bucket.add(uid)
    parts = []
    if added:
        parts.append(f"{E['sword']} {sc(label + ' on')} {E['arrow']} {mono(', '.join(added))}")
    if already:
        parts.append(f"{E['warn']} {sc('pehle se')} {mono(', '.join(already))}")
    await done(event, "\n".join(parts) or f"{E['no']} {sc('kuch nahi hua')}", secs=8)


async def raid_del(event, arg, bucket, label):
    targets = await get_targets(event, arg)
    if not targets:
        return await eor(event, f"{E['no']} {sc('target nahi mila')}")
    removed = [str(u) for u in targets if u in bucket]
    bucket.difference_update(targets)
    await done(event, f"{E['no']} {sc(label + ' off')} {E['arrow']} {mono(', '.join(removed) or '—')}", secs=6)


@register_cmd("reply")
async def cmd_reply(event, arg):
    await raid_add(event, arg, reply_users, "reply raid")


@register_cmd("sreply")
async def cmd_sreply(event, arg):
    await raid_del(event, arg, reply_users, "reply raid")


@register_cmd("rr")
async def cmd_rr(event, arg):
    await raid_add(event, arg, rr_users, "rr raid")


@register_cmd("srr")
async def cmd_srr(event, arg):
    await raid_del(event, arg, rr_users, "rr raid")


@register_cmd("flag")
async def cmd_flag(event, arg):
    await raid_add(event, arg, flag_users, "flag raid")


@register_cmd("sflag")
async def cmd_sflag(event, arg):
    await raid_del(event, arg, flag_users, "flag raid")


@register_cmd("hrr")
async def cmd_hrr(event, arg):
    await raid_add(event, arg, hrr_users, "heart raid")


@register_cmd("shrr")
async def cmd_shrr(event, arg):
    await raid_del(event, arg, hrr_users, "heart raid")


@register_cmd("replygod")
async def cmd_replygod(event, arg):
    await raid_add(event, arg, replygod_users, "replygod")


@register_cmd("sgod")
async def cmd_sgod(event, arg):
    await raid_del(event, arg, replygod_users, "replygod")


@register_cmd("replyyorichi")
async def cmd_replyyorichi(event, arg):
    if not arg or len(arg.split()) < 2:
        return await eor(event, f"{E['no']} {mono('.replyyorichi <text> <count>')} {sc('(reply ke saath)')}")
    text, count = arg.rsplit(" ", 1)
    try:
        count = int(count)
    except Exception:
        return await eor(event, f"{E['no']} {sc('count number hona chahiye')}")
    count = max(1, min(count, 100))
    targets = await get_targets(event, "")
    if not targets:
        return await eor(event, f"{E['no']} {sc('reply to karo')}")
    for uid in targets:
        replyyorichi_users[uid] = {"text": text, "count": count}
    await done(event, f"{E['comet']} {sc('yorichi')} {E['arrow']} "
                      f"{mono(', '.join(map(str, targets)))} × {mono(str(count))}", secs=8)


@register_cmd("syorichi")
async def cmd_syorichi(event, arg):
    targets = await get_targets(event, arg)
    removed = [str(u) for u in targets if u in replyyorichi_users]
    for u in targets:
        replyyorichi_users.pop(u, None)
    await done(event, f"{E['no']} {sc('yorichi off')} {E['arrow']} {mono(', '.join(removed) or '—')}", secs=6)


@register_cmd("nikreply", "replynik")
async def cmd_nikreply(event, arg):
    if not event.is_reply:
        return await eor(event, f"{E['no']} {sc('reply karke')} {mono('.nikreply <count> <text>')}")
    parts = (arg or "").split(maxsplit=1)
    if len(parts) < 2:
        return await eor(event, f"{E['no']} {mono('.nikreply <count> <text>')}\n"
                                f"{E['dot']} {mono('.nikreply 10 tu chup kar')}")
    try:
        count = int(parts[0])
    except Exception:
        return await eor(event, f"{E['no']} {sc('count number hona chahiye')}")
    count = max(1, min(count, 200))
    text = parts[1].strip()
    targets = await get_targets(event, "")
    if not targets:
        return await eor(event, f"{E['no']} {sc('target nahi mila')}")
    for uid in targets:
        replyking_users[uid] = {"text": text, "count": count}
    await done(event, f"{E['crown']} {sc('nikreply on')} {E['arrow']} "
                      f"{mono(', '.join(map(str, targets)))}\n"
                      f"{E['dot']} {sc('count')} {mono(str(count))} · {text[:30]}\n"
                      f"{E['dot']} {mono('.nik')} {sc('se band')}", secs=10)


@register_cmd("nik", "nikstop")
async def cmd_nik(event, arg):
    cleared = (len(reply_users) + len(rr_users) + len(flag_users) + len(hrr_users)
               + len(replygod_users) + len(replyking_users) + len(replyyorichi_users))
    for s in (reply_users, rr_users, flag_users, hrr_users, replygod_users):
        s.clear()
    replyking_users.clear(); replyyorichi_users.clear()
    await done(event, f"{E['crown']} {sc('nik raid stop')} {E['arrow']} {mono(str(cleared))} {sc('cleared')}", secs=6)


@register_cmd("raidstopall", "stopall")
async def cmd_raidstopall(event, arg):
    cleared = sum(len(s) for s in (reply_users, rr_users, flag_users, hrr_users,
                                   replygod_users, ECHO_USERS))
    for s in (reply_users, rr_users, flag_users, hrr_users, replygod_users, ECHO_USERS):
        s.clear()
    replyyorichi_users.clear(); replyking_users.clear(); USER_REPLY.clear()
    for t in list(spray_tasks.values()):
        try:
            t.cancel()
        except Exception:
            pass
    spray_tasks.clear()
    global GPFP_TASK
    if GPFP_TASK and not GPFP_TASK.done():
        try:
            GPFP_TASK.cancel()
        except Exception:
            pass
    GPFP_TASK = None
    GPFP_STATE["on"] = False
    global TAGALL_ACTIVE
    TAGALL_ACTIVE = False
    await done(event, f"{E['no']} {sc('sab band')} {E['arrow']} {mono(str(cleared))} {sc('cleared')}", secs=8)


@register_cmd("bomb")
async def cmd_bomb(event, arg):
    targets = await get_targets(event, arg)
    if not targets and not event.is_reply:
        msg = await eor(event, f"{E['fire']} {sc('loading')}…")
        for f in ["💣·", "💣··", "💣···", "💥 BOOM", "🔥 Nik bomb 💥", "💀 Bhag bsdk 💀"]:
            try:
                await msg.edit(f); await asyncio.sleep(0.6)
            except Exception:
                break
        return
    for uid in targets:
        reply_users.add(uid); rr_users.add(uid)
    await done(event, f"{E['fire']} {sc('bomb')} {E['arrow']} {mono(', '.join(map(str, targets)))}", secs=6)


@register_cmd("gali")
async def cmd_gali(event, arg):
    try:
        count = int((arg or "5").split()[0])
    except Exception:
        count = 5
    count = max(1, min(count, 20))
    st = await flash(event, f"{E['fire']} {sc('gali')} {mono(str(count))}x…", secs=30)
    for _ in range(count):
        try:
            await event.reply(random.choice(reply_list))
        except FloodWaitError as fw:
            await asyncio.sleep(fw.seconds)
        except Exception:
            pass
        await asyncio.sleep(0.8)
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass


@register_cmd("love")
async def cmd_love(event, arg):
    msg = await eor(event, f"{E['heart']} {sc('starting')}…")
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
def _start_loop(chat, text, delay, media=None):
    async def loop():
        try:
            while chat in spray_tasks:
                try:
                    if media is not None:
                        await bot.send_file(chat, media)
                    else:
                        await bot.send_message(chat, text)
                except FloodWaitError as fw:
                    await asyncio.sleep(fw.seconds)
                except RPCError:
                    break
                except Exception:
                    await asyncio.sleep(2)
                await asyncio.sleep(delay)
        except asyncio.CancelledError:
            pass
        finally:
            spray_tasks.pop(chat, None)
    spray_tasks[chat] = asyncio.create_task(loop())


@register_cmd("spray", owner_only=True)
async def cmd_spray(event, arg):
    if not arg:
        return await eor(event, f"{E['dot']} {mono('.spray <text>')}")
    chat = event.chat_id
    if chat in spray_tasks and not spray_tasks[chat].done():
        return await eor(event, f"{E['warn']} {sc('spray pehle se chal raha hai')}")
    _start_loop(chat, arg[:4000], 3)
    await done(event, f"{E['comet']} {sc('spray on')} {E['arrow']} {arg[:40]}\n"
                      f"{E['dot']} {mono('.dspray')} / {mono('.sspam')}", secs=8)


@register_cmd("d")
async def cmd_d(event, arg):
    """.d <seconds> <text> — har N sec me repeat"""
    parts = (arg or "").split(maxsplit=1)
    if len(parts) < 2:
        return await eor(event, f"{E['dot']} {mono('.d 2 hello')}\n"
                                f"{E['dot']} {sc('delay 0.5 – 5 sec')}\n"
                                f"{E['dot']} {mono('.sspam')} {sc('se band')}")
    try:
        delay = float(parts[0])
    except Exception:
        return await eor(event, f"{E['no']} {sc('delay number do')}")
    delay = max(0.5, min(delay, 60.0))
    chat = event.chat_id
    if chat in spray_tasks and not spray_tasks[chat].done():
        return await eor(event, f"{E['warn']} {sc('pehle se chal raha hai')} {E['arrow']} {mono('.sspam')}")
    _start_loop(chat, parts[1][:4000], delay)
    await done(event, f"{E['comet']} {sc('repeat on')} {E['arrow']} {mono(str(delay) + 's')}\n"
                      f"{E['dot']} {parts[1][:40]}", secs=8)


@register_cmd("dspray", "sspam", owner_only=True)
async def cmd_dspray(event, arg):
    chat = event.chat_id
    if chat not in spray_tasks:
        return await eor(event, f"{E['warn']} {sc('koi active loop nahi')}")
    try:
        spray_tasks[chat].cancel()
    except Exception:
        pass
    spray_tasks.pop(chat, None)
    await done(event, f"{E['no']} {sc('loop band')}", secs=6)


@register_cmd("spam")
async def cmd_spam(event, arg):
    if not arg:
        return await eor(event, f"{E['dot']} {mono('.spam <count> <text>')}")
    parts = arg.split(maxsplit=1)
    if len(parts) < 2:
        return await eor(event, f"{E['no']} {sc('text bhi do')}")
    try:
        count = int(parts[0])
    except Exception:
        return await eor(event, f"{E['no']} {sc('count number hona chahiye')}")
    count = max(1, min(count, 100))
    txt = parts[1]
    st = await flash(event, f"{E['comet']} {sc('spam')} {mono(str(count))}x…", secs=60)
    for _ in range(count):
        try:
            await event.reply(txt)
        except FloodWaitError as fw:
            await asyncio.sleep(fw.seconds)
        except Exception:
            pass
        await asyncio.sleep(0.7)
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass


@register_cmd("mspam")
async def cmd_mspam(event, arg):
    if not event.is_reply:
        return await eor(event, f"{E['no']} {sc('media pe reply karke')} {mono('.mspam <n>')}")
    reply = await event.get_reply_message()
    try:
        count = int((arg or "5").split()[0])
    except Exception:
        count = 5
    count = max(1, min(count, 30))
    st = await flash(event, f"{E['comet']} {sc('media')} {mono(str(count))}x…", secs=60)
    for _ in range(count):
        try:
            if getattr(reply, "media", None):
                await bot.send_file(event.chat_id, reply.media)
        except FloodWaitError as fw:
            await asyncio.sleep(fw.seconds)
        except Exception:
            pass
        await asyncio.sleep(1.2)
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass


@register_cmd("delayspam")
async def cmd_delayspam(event, arg):
    parts = (arg or "").split(maxsplit=2)
    if len(parts) < 3:
        return await eor(event, f"{E['dot']} {mono('.delayspam <delay> <count> <text>')}")
    try:
        delay = float(parts[0]); count = int(parts[1])
    except Exception:
        return await eor(event, f"{E['no']} {sc('delay aur count number hone chahiye')}")
    delay = max(0.5, delay); count = max(1, min(count, 100))
    st = await flash(event, f"{E['clock']} {mono(str(delay) + 's')} × {mono(str(count))}", secs=120)
    for _ in range(count):
        try:
            await event.reply(parts[2])
        except FloodWaitError as fw:
            await asyncio.sleep(fw.seconds)
        except Exception:
            pass
        await asyncio.sleep(delay)
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass


@register_cmd("purgeall", owner_only=True)
async def cmd_purgeall(event, arg):
    try:
        count = int((arg or "10").split()[0])
    except Exception:
        count = 10
    count = max(1, min(count, 300))
    st = await flash(event, f"{E['trash']} {sc('purging')} {mono(str(count))}…", secs=60)
    ids = []
    async for m in bot.iter_messages(event.chat_id, limit=count):
        ids.append(m.id)
    done_n = await _delete_ids(event.chat_id, ids)
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass
    conf = await eor(event, f"{E['trash']} {sc('deleted')} {mono(str(done_n))}")
    await _del_after(conf, TMP_TTL)


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
            ok = await fast_title_edit(chat_id, template.replace("{emoji}", emoji))
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
            return await eor(event, f"{E['no']} {sc('template me')} {mono('{emoji}')} {sc('likho')}\n"
                                    f"{E['dot']} {mono('.fastgc set Nik ♛ {emoji}')}")
        FASTGC_STATE.update({"active": True, "template": template, "chat_id": event.chat_id})
        old = FASTGC_STATE.get("task")
        if old and not old.done():
            try:
                old.cancel()
            except Exception:
                pass
        FASTGC_STATE["task"] = asyncio.create_task(gc_fast_loop(event.chat_id))
        return await done(event, f"{E['bolt']} {sc('fastgc on')} {E['arrow']} {mono(template[:35])}", secs=8)
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
        return await done(event, f"{E['no']} {sc('fastgc off')}", secs=6)
    return await eor(event, f"{E['dot']} {mono('.fastgc set <title {{emoji}}>')}\n"
                            f"{E['dot']} {mono('.fastgc stop')}")


# ══════════════════════════════════════════════════════════════
#                ᴀғᴋ · ɢʜᴏsᴛ · ᴇᴄʜᴏ · ʀᴇᴀᴄᴛ
# ══════════════════════════════════════════════════════════════
@register_cmd("afk")
async def cmd_afk(event, arg):
    AFK.update({"active": True, "reason": (arg or "AFK").strip(), "since": time.time()})
    await done(event, f"{E['moon']} {sc('afk on')} {E['arrow']} {mono(AFK['reason'])}\n"
                      f"{E['dot']} {sc('tag/pm pe auto-reply')} · {mono('.unafk')}", secs=8)


@register_cmd("unafk")
async def cmd_unafk(event, arg):
    AFK.update({"active": False, "reason": None})
    await done(event, f"{E['ok']} {sc('afk off')}", secs=6)


@register_cmd("ghost")
async def cmd_ghost(event, arg):
    a = (arg or "").split()
    if not a:
        return await eor(event, f"{E['ghost']} {sc('ghost')} {E['arrow']} "
                                f"{mono('ON' if GHOST['on'] else 'OFF')} {sc('·')} {mono(str(GHOST['delay']) + 's')}\n"
                                f"{E['dot']} {mono('.ghost on 30')} · {mono('.ghost off')}")
    if a[0].lower() in ("on", "enable", "start"):
        GHOST["on"] = True
        if len(a) > 1:
            try:
                GHOST["delay"] = max(3, min(int(a[1]), 3600))
            except Exception:
                pass
        return await done(event, f"{E['ghost']} {sc('ghost on')} {E['arrow']} "
                                 f"{sc('apne msgs')} {mono(str(GHOST['delay']) + 's')} {sc('me udd jayenge')}", secs=8)
    if a[0].lower() in ("off", "disable", "stop"):
        GHOST["on"] = False
        return await done(event, f"{E['ghost']} {sc('ghost off')}", secs=6)
    return await eor(event, f"{E['dot']} {mono('.ghost on|off [seconds]')}")


@register_cmd("echo")
async def cmd_echo(event, arg):
    targets = await get_targets(event, arg)
    if not targets:
        return await eor(event, f"{E['no']} {sc('target nahi mila')}")
    ECHO_USERS.update(targets)
    await done(event, f"{E['note']} {sc('echo on')} {E['arrow']} "
                      f"{mono(', '.join(map(str, sorted(targets))))}\n"
                      f"{E['dot']} {mono('.unecho')}", secs=8)


@register_cmd("unecho")
async def cmd_unecho(event, arg):
    targets = await get_targets(event, arg)
    if not targets:
        return await eor(event, f"{E['no']} {sc('target nahi mila')}")
    ECHO_USERS.difference_update(targets)
    await done(event, f"{E['no']} {sc('echo off')} {E['arrow']} "
                      f"{mono(', '.join(map(str, sorted(targets))))}", secs=6)


@register_cmd("ar", "art")
async def cmd_ar(event, arg):
    global AUTO_REACT_EMOJI
    if not arg:
        return await eor(event, f"{E['spark']} {sc('auto-react')} {E['arrow']} "
                                f"{mono(AUTO_REACT_EMOJI or 'off')}\n"
                                f"{E['dot']} {mono('.ar <emoji>')} · {mono('.sart')}")
    AUTO_REACT_EMOJI = arg.strip()
    await done(event, f"{E['spark']} {sc('auto-react on')} {E['arrow']} {AUTO_REACT_EMOJI}", secs=6)


@register_cmd("sar", "sart")
async def cmd_sar(event, arg):
    global AUTO_REACT_EMOJI
    AUTO_REACT_EMOJI = None
    await done(event, f"{E['no']} {sc('auto-react off')}", secs=6)


# ══════════════════════════════════════════════════════════════
#                          ᴛᴏᴏʟs
# ══════════════════════════════════════════════════════════════
@register_cmd("tts")
async def cmd_tts(event, arg):
    if not arg:
        return await eor(event, f"{E['dot']} {mono('.tts <text>')}")
    st = await flash(event, f"{E['note']} {sc('audio bana raha hoon')}…", secs=30)
    fname = os.path.join(TEMP_PATH, f"tts_{int(time.time())}.mp3")
    try:
        gTTS(text=arg[:3000], lang="hi", slow=False).save(fname)
    except Exception:
        if st is not None:
            try:
                await st.delete()
            except Exception:
                pass
        return await eor(event, f"{E['no']} {sc('tts fail (network?)')}")
    try:
        await bot.send_file(event.chat_id, fname, caption=f"{E['note']} {sc('tts')}\n{FOOT}")
        try:
            await event.delete()
        except Exception:
            pass
    except Exception as e:
        await eor(event, f"{E['no']} {mono(str(e)[:60])}")
    finally:
        try:
            os.remove(fname)
        except Exception:
            pass
        if st is not None:
            try:
                await st.delete()
            except Exception:
                pass


@register_cmd("qrcode")
async def cmd_qrcode(event, arg):
    if not arg:
        return await eor(event, f"{E['dot']} {mono('.qrcode <text>')}")
    st = await flash(event, f"{E['tool']} {sc('qr bana raha hoon')}…", secs=20)
    fname = os.path.join(TEMP_PATH, f"qr_{int(time.time())}.png")
    try:
        qrcode.make(arg[:2000]).save(fname)
        await bot.send_file(event.chat_id, fname, caption=f"{E['tool']} {sc('qr')}\n{FOOT}")
        try:
            await event.delete()
        except Exception:
            pass
    except Exception as e:
        await eor(event, f"{E['no']} {mono(str(e)[:60])}")
    finally:
        try:
            os.remove(fname)
        except Exception:
            pass
        if st is not None:
            try:
                await st.delete()
            except Exception:
                pass


@register_cmd("fancy")
async def cmd_fancy(event, arg):
    if not arg:
        return await eor(event, f"{E['dot']} {mono('.fancy <text>')}")
    t = arg[:1500]
    styles = [f"★彡 {t} 彡★", f"『 {t} 』", f"✦ {t} ✦", f"☾ {t} ☽", f"➳ {t} ➳",
              f"⚡ {t} ⚡", f"❖ {t} ❖", f"⫷ {t} ⫸", f"♛ {t} ♛",
              f"✧･ﾟ: *✧ {t} ✧*:･ﾟ✧", f"꧁ {t} ꧂", f"░▒▓ {t} ▓▒░",
              f"➶➶ {t} ➷➷", f"✿ {t} ✿", f"⟪ {t} ⟫", f"⌁ {t} ⌁",
              f"🜲 {t} 🜲", f"⟡ {t} ⟡", f"⬢ {t} ⬢"]
    await eor(event, f"{E['spark']} {sc('fancy styles')}\n{'─' * 22}\n" + "\n".join(styles))


@register_cmd("style")
async def cmd_style(event, arg):
    if not arg:
        return await eor(event, f"{E['dot']} {mono('.style <text>')}")
    t = arg[:1500]
    await eor(event, f"{E['spark']} {sc('style')}\n{'─' * 22}\n"
                     f"{scr(t)}\n{sb(t)}\n{scrb(t)}\n{bs(t)}\n{its(t)}\n{sbi(t)}\n{mono(t)}\n{dbl(t)}\n{sc(t)}")


@register_cmd("emoji")
async def cmd_emoji(event, arg):
    if not arg:
        return await eor(event, f"{E['dot']} {mono('.emoji <text>')}")
    pool = ["✦", "❖", "⟡", "♛", "⚜️", "🔱", "💠", "🪬", "🧿", "⛓️", "🗝️",
            "🧭", "🛰️", "🧬", "🪐", "🌠", "🫧", "🕸️", "🪞", "🗡️", "🛡️",
            "🌩️", "🜛", "✺", "⟐", "⬡", "⌬", "❂", "✵", "🌌"]
    deco = "".join(random.choice(pool) for _ in range(8))
    await eor(event, f"{deco}\n{arg[:1500]}\n{deco}")


@register_cmd("calc")
async def cmd_calc(event, arg):
    if not arg:
        return await eor(event, f"{E['dot']} {mono('.calc <expression>')}")
    expr = arg.replace(" ", "")
    allowed = set("0123456789+-*/().%")
    if any(c not in allowed for c in expr):
        return await eor(event, f"{E['no']} {sc('sirf')} {mono('0-9 + - * / ( ) . %')}")
    try:
        res = eval(expr, {"__builtins__": None}, {})
    except Exception:
        return await eor(event, f"{E['no']} {sc('invalid expression')}")
    await eor(event, f"{E['tool']} {sc('calc')}\n{'─' * 22}\n"
                     f"{E['dot']} {mono(expr)}\n{E['arrow']} {mono(str(res))}")


def _http_json(url, timeout=8):
    try:
        return requests.get(url, timeout=timeout).json()
    except Exception:
        return None


@register_cmd("weather")
async def cmd_weather(event, arg):
    if not arg:
        return await eor(event, f"{E['dot']} {mono('.weather <city>')}")
    st = await flash(event, f"{E['wave']} {sc('fetching')}…", secs=15)
    geo = _http_json(f"https://geocoding-api.open-meteo.com/v1/search?name={arg}&count=1")
    if not geo or not geo.get("results"):
        if st is not None:
            try:
                await st.delete()
            except Exception:
                pass
        return await eor(event, f"{E['no']} {sc('city nahi mili')}")
    r = geo["results"][0]
    w = _http_json(f"https://api.open-meteo.com/v1/forecast?latitude={r.get('latitude')}"
                   f"&longitude={r.get('longitude')}&current_weather=true")
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass
    if not w or not w.get("current_weather"):
        return await eor(event, f"{E['no']} {sc('weather data nahi mila')}")
    cw = w["current_weather"]
    await eor(event, "\n".join([top(), sub(f"{E['wave']} {sc('weather')}"), sub(""),
                                sub(f" {E['dot']} {sc('city')} ‣ {r.get('name')}"),
                                sub(f" {E['dot']} {sc('temp')} ‣ {mono(str(cw.get('temperature')) + '°C')}"),
                                sub(f" {E['dot']} {sc('wind')} ‣ {mono(str(cw.get('windspeed')) + ' km/h')}"),
                                sub(""), sub(FOOT), f"╰{'─' * 30}╯"]))


@register_cmd("ip")
async def cmd_ip(event, arg):
    if not arg:
        return await eor(event, f"{E['dot']} {mono('.ip <ip>')}")
    st = await flash(event, f"{E['globe']} {sc('lookup')}…", secs=15)
    d = _http_json(f"http://ip-api.com/json/{arg}")
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass
    if not d or d.get("status") != "success":
        return await eor(event, f"{E['no']} {sc('invalid ip')}")
    await eor(event, "\n".join([top(), sub(f"{E['globe']} {sc('ip info')}"), sub(""),
                                sub(f" {E['dot']} {sc('ip')}   ‣ {mono(str(d.get('query')))}"),
                                sub(f" {E['dot']} {sc('country')} ‣ {d.get('country')}"),
                                sub(f" {E['dot']} {sc('city')} ‣ {d.get('city')}"),
                                sub(f" {E['dot']} {sc('isp')} ‣ {d.get('isp')}"),
                                sub(""), sub(FOOT), f"╰{'─' * 30}╯"]))


@register_cmd("short")
async def cmd_short(event, arg):
    if not arg:
        return await eor(event, f"{E['dot']} {mono('.short <url>')}")
    if not arg.startswith(("http://", "https://")):
        arg = "http://" + arg
    st = await flash(event, f"{E['chain']} {sc('shortening')}…", secs=15)
    try:
        short_url = requests.get(
            f"http://tinyurl.com/api-create.php?url={requests.utils.requote_uri(arg)}",
            timeout=8).text.strip()
    except Exception:
        if st is not None:
            try:
                await st.delete()
            except Exception:
                pass
        return await eor(event, f"{E['no']} {sc('short fail (network?)')}")
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass
    await eor(event, f"{E['chain']} {sc('short url')}\n{'─' * 22}\n{mono(short_url)}")


@register_cmd("music")
async def cmd_music(event, arg):
    if not arg:
        return await eor(event, f"{E['dot']} {mono('.music <song>')}")
    query = arg.strip()
    frames = ["▰▱▱▱▱", "▰▰▱▱▱", "▰▰▰▱▱", "▰▰▰▰▱", "▰▰▰▰▰"]
    status = await eor(event, f"{E['note']} {mono(query)}\n\n{mono(frames[0])}")
    stop = asyncio.Event()
    lt = asyncio.create_task(_music_loader(status, query, frames, stop))

    async def worker():
        try:
            path, info = await yt_download(query, audio=True)
            if not path:
                raise Exception("download fail")
            title = str((info or {}).get("title") or query)
            clean = "".join(c for c in title if c.isalnum() or c in " -_").strip()[:40]
            new = os.path.join(TEMP_PATH, f"{clean}.ogg")
            try:
                os.rename(path, new)
            except Exception:
                new = path
            stop.set()
            lt.cancel()
            try:
                await status.delete()
            except Exception:
                pass
            await bot.send_file(event.chat_id, new, voice_note=True,
                                caption=f"{E['note']} {clean}\n{E['spark']} {sc('powered by')} {OWNER_TAG}")
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
            await eor(event, f"{E['no']} {sc('music fail')} {E['arrow']} {mono(str(e)[:60])}")
    asyncio.create_task(worker())


async def _music_loader(status, query, frames, stop):
    i = 0
    while not stop.is_set():
        try:
            await status.edit(f"{E['note']} {mono(query)}\n\n{mono(frames[i % 5])}")
        except Exception:
            pass
        i += 1
        await asyncio.sleep(1)


# ══════════════════════════════════════════════════════════════
#                          ɴᴏᴛᴇs
# ══════════════════════════════════════════════════════════════
@register_cmd("notesadd")
async def cmd_notesadd(event, arg):
    if not arg:
        return await eor(event, f"{E['dot']} {mono('.notesadd <text>')}")
    NOTES[int(event.chat_id)] = arg.strip()
    save_json(F_NOTES, {str(k): v for k, v in NOTES.items()})
    await done(event, f"{E['key']} {sc('note saved')} {mono(str(len(arg)))} {sc('chars')}", secs=6)


@register_cmd("noteslist")
async def cmd_noteslist(event, arg):
    n = NOTES.get(int(event.chat_id))
    if not n:
        return await eor(event, f"{E['note']} {sc('koi note nahi')}")
    await eor(event, f"{E['key']} {sc('note')}\n{'─' * 22}\n{n[:3000]}")


@register_cmd("notesdelete")
async def cmd_notesdelete(event, arg):
    if NOTES.pop(int(event.chat_id), None) is None:
        return await eor(event, f"{E['warn']} {sc('note tha hi nahi')}")
    save_json(F_NOTES, {str(k): v for k, v in NOTES.items()})
    await done(event, f"{E['trash']} {sc('note delete')}", secs=6)


@register_cmd("banner")
async def cmd_banner(event, arg):
    global MENU_BANNER
    if not event.is_reply:
        return await eor(event, f"{E['no']} {sc('photo/video pe reply karke')} {mono('.banner')}")
    r = await event.get_reply_message()
    if not getattr(r, "media", None):
        return await eor(event, f"{E['no']} {sc('sirf photo/video')}")
    st = await flash(event, f"{E['wand']} {sc('banner set')}…", secs=20)
    try:
        saved = await r.forward_to("me")
    except Exception:
        try:
            raw = await r.download_media(file=bytes)
            if not raw:
                return await eor(event, f"{E['no']} {sc('download fail')}")
            bio = BytesIO(raw); bio.name = "banner.jpg"
            saved = await bot.send_file("me", bio)
        except Exception as e:
            return await eor(event, f"{E['no']} {mono(str(e)[:60])}")
    MENU_BANNER = [int(saved.chat_id), int(saved.id)]
    save_json(F_BANNER, MENU_BANNER)
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass
    await done(event, f"{E['wand']} {sc('banner set')} {E['arrow']} {mono(str(saved.id))}\n"
                      f"{E['dot']} {mono('.menu')} {sc('ke saath aayega')}", secs=8)


@register_cmd("rembanner")
async def cmd_rembanner(event, arg):
    global MENU_BANNER
    if not MENU_BANNER:
        return await eor(event, f"{E['warn']} {sc('banner set hai hi nahi')}")
    try:
        await bot.delete_messages(MENU_BANNER[0], [MENU_BANNER[1]])
    except Exception:
        pass
    MENU_BANNER = None
    save_json(F_BANNER, None)
    await done(event, f"{E['trash']} {sc('banner hata diya')}", secs=6)


# ══════════════════════════════════════════════════════════════
#                          ᴄʟᴏɴᴇ
# ══════════════════════════════════════════════════════════════
@register_cmd("copy", "cp", owner_only=True)
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
        return await eor(event, f"{E['no']} {sc('reply / @user / id do')}")
    me = await bot.get_me()
    if target.id == me.id:
        return await eor(event, f"{E['warn']} {sc('khud ko clone? nope')}")
    if CLONE_ACTIVE and LAST_CLONE_ID == target.id:
        return await eor(event, f"{E['warn']} {sc('pehle se cloned hai')}")
    st = await flash(event, f"{E['wand']} {sc('clone init')}…", secs=30)
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
            first_name=getattr(target, "first_name", "") or "",
            last_name=getattr(target, "last_name", "") or ""))
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
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass
    await done(event, f"{E['wand']} {sc('clone complete')} {E['heart']}\n"
                      f"{E['dot']} {mono('.normal')} {sc('se wapas aao')}", secs=8)


@register_cmd("normal", "nrml", owner_only=True)
async def cmd_normal(event, arg):
    global CLONE_ACTIVE, LAST_CLONE_ID
    if not CLONE_ACTIVE:
        return await eor(event, f"{E['warn']} {sc('koi clone active nahi')}")
    st = await flash(event, f"{E['wand']} {sc('restore init')}…", secs=30)
    try:
        await bot(functions.account.UpdateProfileRequest(
            first_name=CLONE_DATA.get("name") or "",
            last_name=CLONE_DATA.get("last") or ""))
    except Exception:
        pass
    try:
        await bot(functions.account.UpdateProfileRequest(about=""))
        await asyncio.sleep(0.7)
        await bot(functions.account.UpdateProfileRequest(about=CLONE_DATA.get("bio") or ""))
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
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass
    await done(event, f"{E['ok']} {sc('original restore ho gaya')} {E['heart']}", secs=8)


# ══════════════════════════════════════════════════════════════
#                    sᴜʙ-ᴜsᴇʀʙᴏᴛ (multi session)
# ══════════════════════════════════════════════════════════════
@register_cmd("addbot", owner_only=True)
async def cmd_addbot(event, arg):
    """.addbot +9199xxxx — naya userbot session login shuru"""
    phone = (arg or "").strip()
    if not phone.startswith("+"):
        return await eor(event, f"{E['dot']} {mono('.addbot +919999999999')}\n"
                                f"{E['dot']} {sc('phir')} {mono('.c <code>')} "
                                f"{sc('aur zarurat pade to')} {mono('.p <2fa>')}")
    if phone in SUBBOTS:
        return await eor(event, f"{E['warn']} {sc('ye pehle se connected hai')}")
    st = await flash(event, f"{E['bot']} {sc('code bhej raha hoon')}…", secs=20)
    try:
        client = TelegramClient(f"sub_{phone.lstrip('+')}", API_ID, API_HASH)
        await client.connect()
        res = await client(functions.auth.SendCodeRequest(
            phone, API_ID, API_HASH, types.CodeSettings()))
        PENDING[phone] = {"client": client, "hash": res.phone_code_hash}
    except Exception as e:
        if st is not None:
            try:
                await st.delete()
            except Exception:
                pass
        return await eor(event, f"{E['no']} {sc('code nahi gaya')} {E['arrow']} {mono(str(e)[:60])}")
    if st is not None:
        try:
            await st.delete()
        except Exception:
            pass
    conf = await eor(event, f"{E['bot']} {sc('code bhej diya')} {mono(phone)}\n"
                            f"{E['dot']} {mono('.c 12345')} {sc('se login complete karo')}")
    await _del_after(conf, 20)


@register_cmd("c", owner_only=True)
async def cmd_c(event, arg):
    code = (arg or "").strip()
    if not code or not PENDING:
        return await eor(event, f"{E['warn']} {sc('koi pending login nahi')} {E['arrow']} {mono('.addbot +91XXXXXXXXXX')}")
    phone, data = list(PENDING.items())[-1]
    try:
        await data["client"].sign_in(phone, code, phone_code_hash=data["hash"])
        SUBBOTS[phone] = data["client"]
        PENDING.pop(phone, None)
        await done(event, f"{E['ok']} {sc('login complete')} {E['arrow']} {mono(phone)}\n"
                          f"{E['dot']} {mono('.user')} {sc('se list dekho')}", secs=10)
    except Exception as e:
        name = type(e).__name__
        if "SessionPasswordNeeded" in name or "password" in str(e).lower():
            return await eor(event, f"{E['lock']} {sc('2fa chahiye')} {E['arrow']} {mono('.p <password>')}")
        await eor(event, f"{E['no']} {sc('login fail')} {E['arrow']} {mono(str(e)[:70])}")


@register_cmd("p", owner_only=True)
async def cmd_p(event, arg):
    pwd = (arg or "").strip()
    if not pwd or not PENDING:
        return await eor(event, f"{E['dot']} {mono('.p <2fa password>')}")
    phone, data = list(PENDING.items())[-1]
    try:
        await data["client"].sign_in(password=pwd)
        SUBBOTS[phone] = data["client"]
        PENDING.pop(phone, None)
        await done(event, f"{E['ok']} {sc('2fa login complete')} {E['arrow']} {mono(phone)}", secs=10)
    except Exception as e:
        await eor(event, f"{E['no']} {sc('login fail')} {E['arrow']} {mono(str(e)[:70])}")


@register_cmd("user", owner_only=True)
async def cmd_user(event, arg):
    lines = [top(), sub(f"{E['bot']} {sc('connected userbots')}"), sub("")]
    if not SUBBOTS:
        lines.append(sub(f" {E['warn']} {sc('koi extra userbot nahi')}"))
        lines.append(sub(f" {E['dot']} {mono('.addbot +91XXXXXXXXXX')}"))
    for i, (phone, cl) in enumerate(SUBBOTS.items(), 1):
        try:
            me = await cl.get_me()
            nm = f"{me.first_name} ({me.id})"
        except Exception:
            nm = "not ready"
        lines.append(sub(f" {E['dot']} {mono(str(i))} ‣ {mono(phone)} · {nm}"))
    if PENDING:
        lines.append(sub(""))
        lines.append(sub(f" {E['wait']} {sc('pending')} ‣ {mono(', '.join(PENDING))}"))
    lines += [sub(""), sub(FOOT), f"╰{'─' * 30}╯"]
    await eor(event, "\n".join(lines))


# ══════════════════════════════════════════════════════════════
#                     ɢᴀᴍᴇ ʙᴏᴛ ʙʀɪᴅɢᴇ
# ══════════════════════════════════════════════════════════════
@register_cmd("setgame", owner_only=True)
async def cmd_setgame(event, arg):
    global GAME_BOT
    if not arg:
        return await eor(event, f"{E['dice']} {sc('game bot')} {E['arrow']} {mono(GAME_BOT or 'none')}\n"
                                f"{E['dot']} {mono('.setgame @gamebot')}")
    GAME_BOT = arg.strip()
    save_json(F_GAMEBOT, GAME_BOT)
    await done(event, f"{E['dice']} {sc('game bot set')} {E['arrow']} {mono(GAME_BOT)}", secs=8)


async def _game(event, cmd, arg=""):
    if not GAME_BOT:
        return await eor(event, f"{E['warn']} {sc('pehle')} {mono('.setgame @gamebot')} {sc('karo')}")
    text = f"/{cmd}" + (f" {arg}" if arg else "")
    try:
        await bot.send_message(GAME_BOT, text)
        conf = await eor(event, f"{E['dice']} {mono(text)} {E['arrow']} {mono(GAME_BOT)}\n"
                                 f"{E['dot']} {sc('bhej diya')}")
        await _del_after(conf, 5)
    except Exception as e:
        await eor(event, f"{E['no']} {sc('bhej nahi paya')} {E['arrow']} {mono(str(e)[:60])}")


@register_cmd("rob", owner_only=True)
async def cmd_rob(event, arg):
    await _game(event, "rob", (arg or "").strip())


@register_cmd("kill", owner_only=True)
async def cmd_kill(event, arg):
    await _game(event, "kill", (arg or "").strip())


@register_cmd("auto", owner_only=True)
async def cmd_auto(event, arg):
    await _game(event, "auto", (arg or "").strip())


@register_cmd("roboff", "killoff", "autooff", "stoprob", owner_only=True)
async def cmd_roboff(event, arg):
    await _game(event, "stop")


@register_cmd("resetdone", owner_only=True)
async def cmd_resetdone(event, arg):
    await _game(event, "resetdone")


@register_cmd("solve", owner_only=True)
async def cmd_solve(event, arg):
    if not arg:
        return await eor(event, f"{E['dot']} {mono('.solve <code>')}")
    await _game(event, "solve", arg.strip())


# ══════════════════════════════════════════════════════════════
#                         sᴛᴏʀɪᴇs
# ══════════════════════════════════════════════════════════════
def _story(name, frames):
    async def runner(event, arg):
        await play_frames(event, frames, title=name)
    runner.__name__ = f"cmd_{name}"
    return runner


for _n, _f in [
    ("love1", LOVE1_COLLEGE), ("love2", LOVE2_INSTA), ("love3", LOVE3_OFFICE),
    ("love4", LOVE4_DISTANCE), ("love5", LOVE5_SHAADI),
    ("lovestory", LOVE_STORY_FRAMES),
    ("fun1", BACK1_CHAI), ("fun2", BACK2_EXAM), ("fun3", BACK3_CRICKET),
    ("fun4", BACK4_UDHAAR), ("fun5", BACK5_FLIRT), ("fun6", LOVE6_THUG),
    ("fun7", MEME_MUMMY), ("fun8", MEME_SASTA_NASHA),
]:
    register_cmd(_n)(_story(_n, _f))




# ══════════════════════════════════════════════════════════════
#                     ᴡᴀᴛᴄʜᴇʀ (incoming)
# ══════════════════════════════════════════════════════════════
MSG_CACHE: Dict[int, Dict[int, Any]] = {}


def _cache_msg(chat, msg):
    try:
        c = MSG_CACHE.setdefault(int(chat), {})
        c[int(msg.id)] = msg
        if len(c) > 300:
            for k in sorted(c)[:100]:
                c.pop(k, None)
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

        _cache_msg(chat, event.message)

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
        if (sender in MUTED or sender in GLOBAL_MUTED) and not is_admin(sender):
            await silent_delete(event)
            return

        # ── REPLY-LOCK (.rlock) ──
        rl = (RLOCK.get(str(chat)) or {}).get(str(sender))
        if rl and not is_admin(sender):
            await silent_delete(event)
            try:
                note = await event.respond(f"{E['lock']} {rl}")
                asyncio.create_task(_del_after(note, 6))
            except Exception:
                pass
            return

        # ── GROUP LOCKS (0.3s me udaa do) ──
        locked = LOCKS.get(str(chat))
        if locked and not is_admin(sender):
            if media_kinds(event.message) & set(locked):
                await asyncio.sleep(LOCK_DELAY)
                await silent_delete(event)
                return

        # ── SPAM GUARD (.watchspam) ──
        cfg = SPAMWATCH.get(str(chat))
        if cfg and not is_admin(sender):
            key = f"{chat}:{sender}"
            now = time.time()
            bucket = SPAM_BUCKET.setdefault(key, [])
            bucket.append(now)
            SPAM_BUCKET[key] = [t for t in bucket if now - t <= cfg["sec"]]
            if len(SPAM_BUCKET[key]) > cfg["limit"]:
                SPAM_BUCKET[key] = []
                await silent_delete(event)
                ok, _ = await _act_mute(chat, sender)
                if not ok:
                    MUTED.add(sender)
                try:
                    w = await event.respond(f"{E['eye']} {sc('spam detected')} {E['arrow']} "
                                            f"{mono(str(sender))} {sc('muted')}")
                    asyncio.create_task(_del_after(w, 6))
                except Exception:
                    pass
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

        # ── USER AUTO REPLY (.arreply) ──
        if sender in USER_REPLY and text and not text.startswith(PREFIX):
            try:
                await event.reply(USER_REPLY[sender])
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds)
            except Exception:
                pass

        # ── AFK AUTO REPLY ──
        if AFK["active"] and (event.is_private or getattr(event, "mentioned", False)):
            if AFK_LAST.get(chat, 0) < time.time() - 45:
                AFK_LAST[chat] = time.time()
                try:
                    await event.reply(f"{E['moon']} {sc('afk')} {E['arrow']} {mono(AFK['reason'] or 'AFK')}")
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

        # ── RR RAID (+ reaction) ──
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
#                   ᴀɴᴛɪ-ᴅᴇʟᴇᴛᴇ
# ══════════════════════════════════════════════════════════════
@bot.on(events.MessageDeleted)
async def on_deleted(event):
    try:
        chat = event.chat_id
        if chat is None:
            return
        if int(chat) not in ANTIDEL:
            return
        cache = MSG_CACHE.get(int(chat)) or {}
        for mid in (getattr(event, "deleted_ids", None) or []):
            m = cache.pop(int(mid), None)
            if m is None:
                continue
            try:
                await bot.send_message(
                    "me", f"{E['eye']} {sc('anti-delete')}\n"
                          f"{E['gem']} {sc('chat')} {mono(str(chat))} · {sc('id')} {mono(str(mid))}")
                try:
                    await bot.forward_messages("me", m)
                except Exception:
                    await bot.send_message("me", m)
            except Exception:
                pass
    except Exception as e:
        print(f"[ANTIDEL] {str(e)[:60]}")


# ══════════════════════════════════════════════════════════════
#                     ᴡᴀᴛᴄʜᴇʀ (outgoing)
# ══════════════════════════════════════════════════════════════
@bot.on(events.NewMessage(outgoing=True))
async def outgoing_watcher(event):
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
                n = await event.reply(f"{E['crown']} {sb('NIK USERBOT')} {E['arrow']} "
                                      f"{sc('owner / sudo only')} {E['lock']}")
                asyncio.create_task(_del_after(n, 5))
            except Exception:
                pass
            return
        if data.get("owner_only") or cmd in OWNER_ONLY_EXTRA:
            await flash(event, f"{E['no']} {sc('owner only command')} {E['crown']}", secs=5)
            return

    if data.get("group_only"):
        try:
            if not event.is_group:
                await flash(event, f"{E['warn']} {sc('ye command sirf group me chalti hai')}", secs=5)
                return
        except Exception:
            return

    if data.get("needs_reply"):
        try:
            if not event.is_reply and not arg:
                await flash(event, f"{E['no']} {sc('reply ya target do')}\n"
                                   f"{E['dot']} {mono(PREFIX + cmd + ' @user / id')}", secs=5)
                return
        except Exception:
            return

    try:
        await data["func"](event, arg)
    except FloodWaitError as e:
        try:
            await eor(event, f"{E['wait']} {sc('floodwait')} {E['arrow']} {mono(str(e.seconds) + 's')}")
        except Exception:
            pass
    except Exception as e:
        try:
            await eor(event, f"{E['no']} {sc('error')} {E['arrow']} {mono(str(e)[:70])}")
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════
#                           sᴛᴀʀᴛ
# ══════════════════════════════════════════════════════════════
async def main():
    try:
        await bot.start()
        me = await bot.get_me()
        un = f"@{me.username}" if getattr(me, "username", None) else "NoUsername"
        print("─" * 42)
        print(f"  {scrb('Nik Userbot')} {VERSION}  ·  ɢʟᴏʙᴀʟ")
        print(f"  {me.first_name} ({un})  —  {me.id}")
        print(f"  commands loaded: {len(commands)}")
        print("─" * 42)

        while True:
            try:
                await bot.run_until_disconnected()
                break
            except (ConnectionError, OSError):
                print("⚠️ connection lost → reconnecting…")
                await asyncio.sleep(3)
    except KeyboardInterrupt:
        print("\n🛑 stopped manually")
    except Exception as e:
        print(f"\n❌ startup error → {str(e)[:140]}")
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

