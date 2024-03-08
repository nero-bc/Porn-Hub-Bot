import re
import os
import time

id_pattern = re.compile(r'^.\d+$')


class Config(object):
    # pyro client config
    API_ID = os.environ.get("API_ID", "")  # ⚠️ Required
    API_HASH = os.environ.get("API_HASH", "")  # ⚠️ Required
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")  # ⚠️ Required
    BOT_USERNAME = os.environ.get("BOT_USERNAME", "")  # ⚠️ Required

    # database config
    DB_URL = os.environ.get("DB_URL", "")  # ⚠️ Required

    # other configs
    DOWNLOAD_LOCATION = "./DOWNLOADS"
    TG_MAX_SIZE = 2040108421
    BOT_UPTIME = time.time()
    START_PIC = os.environ.get("START_PIC", "")
    ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '').split()]  # ⚠️ Required
    
    FORCE_SUB = os.environ.get('FORCE_SUB', '') # ⚠️ Required without [@]
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", ""))  # ⚠️ Required

    # Mega User Account ⚠️ Only Set When you have Pro or Enterprise Mega Account
    MEGA_EMAIL = os.environ.get("MEGA_EMAIL")
    MEGA_PASSWORD = os.environ.get("MEGA_PASSWORD")

    # wes response configuration
    WEBHOOK = bool(os.environ.get("WEBHOOK", True))
    PORT = int(os.environ.get("PORT", "8080"))


class Txt(object):
    # part of text configuration
    START_TXT = """<b>Hello {} 👋,
━━━━━━━━━━━━━━━━━━━━━
This Bot Can Search PornHub
Videos & Download Them For You

Can Also Download Files through
Link of Mega & YouTube
━━━━━━━━━━━━━━━━━━━━━
⚠️The Bot Contains 18+ Content
So Kindly Access it with Your own
Risk. Children Please Stay Away."
We don't intend to spread Pørno-
-graphy here. It's just a bot for a"
purpose as many of them wanted."
━━━━━━━━━━━━━━━━━━━━━
Click The Buttons Below To Search
"""

    ABOUT_TXT = """<b>╭───────────⍟
├🤖 ᴍy ɴᴀᴍᴇ : {}
├👨‍💻 Pʀᴏɢʀᴀᴍᴇʀ : <a href=https://t.me/Snowball_Official>𝓢𝓝𝓞𝓦𝓑𝓐𝓛𝓛</a>
├👑 Instagram : <a href=https://www.instagram.com/ritesh6_>C-Insta</a> 
├☃️ ꜰᴏᴜɴᴅᴇʀ ᴏꜰ : <a href=https://t.me/+HzGpLAZXTxoyYTNl>𝖱𝖮𝖮𝖥𝖨𝖵𝖤𝖱𝖲𝖤</a>
├📕 Lɪʙʀᴀʀy : <a href=https://github.com/pyrogram>Pyʀᴏɢʀᴀᴍ</a>
├✏️ Lᴀɴɢᴜᴀɢᴇ: <a href=https://www.python.org>Pyᴛʜᴏɴ 3</a>
├💾 Dᴀᴛᴀ Bᴀꜱᴇ: <a href=https://cloud.mongodb.com>Mᴏɴɢᴏ DB</a>
├🌀 ᴍʏ ꜱᴇʀᴠᴇʀ : <a href=https://dashboard.heroku.com>Heroku</a>
╰───────────────⍟ """

    HELP_TXT = """
Tʜɪs Bᴏᴛ Wɪʟʟ Hᴇʟᴘ Yᴏᴜ Tᴏ Dᴏᴡɴʟᴏᴀᴅ Fᴏʟʟᴏᴡɪɴɢ Fɪʟᴇ ᴛʜʀᴏᴜɢʜ ʟɪɴᴋs:

⊚ YouTube
⊚ Mega
⊚ PornHub

❗ 𝗔𝗻𝘆 𝗢𝘁𝗵𝗲𝗿 𝗛𝗲𝗹𝗽 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 :- <a href=https://t.me/Snowball_official>𝑺𝑼𝑷𝑷𝑶𝑹𝑻</a>
"""

    PROGRESS_BAR = """<b>\n
╭━━━━❰ᴘʀᴏɢʀᴇss ʙᴀʀ❱━➣
┣⪼ 🗃️ Sɪᴢᴇ: {1} | {2}
┣⪼ ⏳️ Dᴏɴᴇ : {0}%
┣⪼ 🚀 Sᴩᴇᴇᴅ: {3}/s
┣⪼ ⏰️ Eᴛᴀ: {4}
╰━━━━━━━━━━━━━━━➣ </b>"""
