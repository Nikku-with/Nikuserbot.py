# ♛ NIK USERBOT

Single-file Telethon userbot — **Global** mode · **193 commands** · styled output

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

Saare commands `.` se shuru hote hain. Har command ke saath guide line → `.menu`

| Group | Commands |
|---|---|
| core | .menu .alive .ping .status .uptime .id .info .help .speed |
| messaging | .hy .del .forward .save .savelist .fwd .delsave .setchannel .purge .purgeme .delmine .filter .filters .unfilter |
| auto | .autoread .areply .stopareply .arreply .sarreply .arviyom .sarviyom .afk .unafk .ghost .echo .unecho .ar .sar .art .sart |
| blacklist | .addbl .delbl .listbl .add-bcdb .del-bcdb .list-bcdb .join .leave |
| broadcast | .gcast .ucast .bc .autobc .autofw |
| group mod | .kick .delkick .ban .delban .unban .mute .delmute .unmute .tmute .getmute .staff .promote .fullpromote .demote .title .pin .unpin .group .tagall .banall .lock .unlock .locks .slock |
| global | .gban .ungban .gbanlist .gmute .ungmute .gmutelist |
| protection | .antidel .watchspam .unwatchspam .setgpfp .autogpfp .stopgpfp .rlock .srlock |
| media | .yt .ig .pt .fb .music |
| fun | .tictactoe .ttt .rps .roll .flip .fact .bomb .love |
| ai & sudo | .ai .sudo .delsudo .list sudo |
| bot manager | .addbots .listbots .invitebots .promotebots |
| raid | .reply .sreply .rr .srr .flag .sflag .hrr .shrr .replygod .sgod .replyyorichi .syorichi .nikreply .nik .raidstopall .stopall .gali |
| spam | .spray .dspray .sspam .spam .mspam .delayspam .d .purgeall .tagall .stop |
| gc tools | .fastgc .copy .normal |
| tools | .tts .qrcode .fancy .style .emoji .calc .weather .ip .short |
| notes | .notesadd .noteslist .notesdelete .banner .rembanner |
| stories | .love1 .love2 .love3 .love4 .love5 .lovestory .fun1 .fun2 .fun3 .fun4 .fun5 .fun6 .fun7 .fun8 |

## Notes

* **`.purge`** — reply ke saath: *replied message ke niche (baad) ka sab* uda deta hai
  (reply + command samet). Bina reply: `.purge 200` → 200 purane messages.
  **Bina reply aur bina count → error** (andaza nahi lagata).
* **`.purgeme <n>`** is chat me apne n messages · **`.delmine [n] [@chat]`** —
  us chat ke **saare** apne messages (koi 20 ka cap nahi).
* **`.lock <type>` / `.slock`** — `.lock all` aur `.slock` group ke sab members ko
  **mute** bhi kar dete hain; locked chat me non-admin ka message **0.3s** me delete.
  `.unlock all` sabko wapas unmute karta hai. Types: `all msg text media photo video
  document sticker gif audio voice link forward command inline poll contact location
  game dice webpage`
* **`.info` / `.id`** — reply, `@username`, ya **kuch nahi** (DM me khud detect kar leta hai).
* Har **status/progress** message ~**3 sec** me apne aap delete.
* **`.fwd`** — replied message Saved Messages me bhejta hai (`.save` se store karo, `.fwd <n>` se wapas).
* **`.music` / koi bhi audio** — caption me `Powered by @Nikkkwa` credit ke saath.
* **`.speed <seconds>`** — story animation ki speed (default `1.6s`).
* **`.nikreply <count> <text>`** (reply ke saath) — us user ko N baar wo text. Band → `.nik`
* **`.ghost on 30`** — apne outgoing messages 30s me auto-delete (commands chhod kar).
* **Owner-only**: `copy normal addadmin deladmin admins gban ungban gmute ungmute gcast
  ucast bc autobc autofw join leave purgeall fastgc addbots invitebots promotebots spray
  dspray banall addbot c p user setgame rob kill solve` — baaki sab admin bhi chala sakta hai.
* **Access**: sirf owner + sudo users. Baaki logon ko auto-delete hone wala "owner / sudo only" reply.

## Files

* `Nik_userbot.py` — poora bot (single file)
* `data/` — runtime state (admins, filters, blacklist, gban/gmute, locks, bcdb, saved msgs)
