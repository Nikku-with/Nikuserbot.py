# ♛ NIK USERBOT

Single-file Telethon userbot — **Global** mode.

## Setup

```bash
pip install -r requirements.txt
```

Config **env variables** se aata hai (hardcode karne ki zarurat nahi):

```bash
export API_ID=123456          # my.telegram.org
export API_HASH=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
export OWNER_ID=8742036730    # @userinfobot se apna id
export SESSION=aeris          # session file name ya StringSession
```

Agar env set nahi hai to file ke upar wale default values use honge.

```bash
python Nik_userbot.py
```

Pehli baar phone number + OTP maangega, phir `aeris.session` ban jayegi.
**Session file ko kabhi commit mat karna** (`.gitignore` me hai).

## Commands

Saare commands `.` se shuru hote hain. Poora list → `.menu`

| Group | Commands |
|---|---|
| Core | `.alive .ping .status .menu .id .info .help .speed` |
| Messaging | `.hy .del .forward .save .savelist .fwd .delsave .setchannel .purge .purgeme .delmine .filter .filters .unfilter` |
| Auto | `.autoread group/private/channel/all on/off` · `.areply .stopareply` · `.afk .unafk` · `.ghost on/off` · `.echo .unecho` · `.ar .sar` |
| Blacklist | `.addbl .delbl .listbl` · `.add-bcdb .del-bcdb .list-bcdb` · `.join .leave` |
| Broadcast | `.gcast .ucast .bc group/all/private/db` · `.autobc add/on/off/get/del/delay` · `.autofw add/on/off/get/del/delay` |
| Group mod | `.kick .delkick .ban .delban .unban .mute .delmute .unmute .getmute .staff .promote .fullpromote .demote .title .pin .unpin .group title/desc .lock .unlock .locks` |
| Global | `.gban .ungban .gbanlist` · `.gmute .ungmute .gmutelist` |
| Raid | `.reply .sreply .rr .srr .flag .sflag .hrr .shrr .replygod .sgod .replyyorichi .syorichi .nikreply .nik .raidstopall .bomb .gali` |
| Spam | `.spray .dspray .spam .mspam .delayspam .purgeall .tagall .stop` |
| GC tools | `.fastgc set <title {emoji}> / stop` · `.addbots` · `.addadmin .deladmin .admins` |
| Tools | `.tts .qrcode .fancy .style .emoji .calc .weather .ip .short .music .copy .normal` |
| Notes | `.notesadd .noteslist .notesdelete .banner .rembanner` |
| Stories | `.love1 … .love5 .lovestory` · `.fun1 … .fun8` |

## Notes

* **`.purge`** — reply ke saath: reply se command tak sab uda deta hai.
  Bina reply: `.purge 200` → command ke upar ke 200 purane messages.
* **`.purgeme <n>`** is chat me apne messages · **`.delmine <n> [@chat]`** specific chat me apne messages.
* **`.lock all`** — locked group me kisi bhi non-admin ka message `0.3s` me delete.
  Types: `all msg text media photo video document sticker gif audio voice link forward command inline poll contact location game dice webpage`
* **`.nikreply <count> <text>`** (reply ke saath) — us user ko N baar wo text bhejta hai. Band → `.nik`
* **`.ghost on 30`** — apne outgoing messages 30s me auto-delete (commands chhod kar).
* **`.speed <seconds>`** — story animation ki speed (default `1.6s`, pehle `0.5s` tha).
* Owner-only: `copy normal addadmin deladmin admins gban ungban gmute ungmute gcast ucast bc autobc autofw join leave purgeall fastgc addbots spray dspray` — baaki sab admin bhi chala sakta hai.

## Files

* `Nik_userbot.py` — poora bot (single file)
* `data/` — runtime state (admins, filters, blacklist, gban/gmute, locks, bcdb, saved msgs)
* `Nik_userbot_FINAL_V3*.py` — purane backups (ab use mat karna)
