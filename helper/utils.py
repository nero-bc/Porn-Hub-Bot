import math
import os
import sys
import threading
import time
import asyncio
import logging
import requests
import uuid
from datetime import datetime
from pytz import timezone
from pyrogram.errors.exceptions import MessageNotModified, FloodWait, UserNotParticipant
from pyrogram import enums
from youtube_dl import DownloadError
import youtube_dl
from config import Config, Txt
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def progress_for_pyrogram(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 5.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "{0}{1}".format(
            ''.join(["⬢" for i in range(math.floor(percentage / 5))]),
            ''.join(["⬡" for i in range(20 - math.floor(percentage / 5))])
        )
        tmp = progress + Txt.PROGRESS_BAR.format(
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            await message.edit(
                text=f"{ud_type}\n\n{tmp}"
            )
        except:
            pass


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "ᴅ, ") if days else "") + \
        ((str(hours) + "ʜ, ") if hours else "") + \
        ((str(minutes) + "ᴍ, ") if minutes else "") + \
        ((str(seconds) + "ꜱ, ") if seconds else "") + \
        ((str(milliseconds) + "ᴍꜱ, ") if milliseconds else "")
    return tmp[:-2]


def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds)


def humanbytes(size):
    if not size:
        return ""
    power = 2 ** 10
    raised_to_pow = 0
    dict_power_n = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"


async def run_async(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)


def edit_msg(client, message, to_edit):
    try:
        client.loop.create_task(message.edit(to_edit))
    except FloodWait as e:
        client.loop.create_task(asyncio.sleep(e.value))
    except MessageNotModified:
        pass
    except TypeError:
        pass


def download_progress_hook(d, message, client):
    if d['status'] == 'downloading':
        current = d.get("_downloaded_bytes_str") or humanbytes(
            int(d.get("downloaded_bytes", 1)))
        total = d.get("_total_bytes_str") or d.get("_total_bytes_estimate_str")
        file_name = d.get("filename")
        eta = d.get('_eta_str', "N/A")
        percent = d.get("_percent_str", "N/A")
        speed = d.get("_speed_str", "N/A")
        to_edit = f"📥 <b>Downloading!</b>\n\n<b>Name :</b> <code>{file_name}</code>\n<b>Size :</b> <code>{total}</code>\n<b>Speed :</b> <code>{speed}</code>\n<b>ETA :</b> <code>{eta}</code>\n\n<b>Percentage: </b> <code>{current}</code> from <code>{total} (__{percent}__)</code>"
        threading.Thread(target=edit_msg, args=(
            client, message, to_edit)).start()


def get_thumbnail_url(video_url):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        try:
            thumbnail_url = info_dict['entries'][0]['thumbnails'][0]['url']
            return thumbnail_url
        except Exception as e:
            return None


async def send_log(b, u):
    if Config.LOG_CHANNEL is not None:
        curr = datetime.now(timezone("Asia/Kolkata"))
        date = curr.strftime("%d %B, %Y")
        time_str = curr.strftime("%I:%M:%S %p")
        await b.send_message(
            Config.LOG_CHANNEL,
            f"**--Nᴇᴡ Uꜱᴇʀ Sᴛᴀʀᴛᴇᴅ Tʜᴇ Bᴏᴛ--**\n\n"
            f"Uꜱᴇʀ: {u.mention}\nIᴅ: `{u.id}`\nUɴ: @{u.username}\n\n"
            f"Dᴀᴛᴇ: {date}\nTɪᴍᴇ: {time_str}\n\nBy: @{Config.BOT_USERNAME}",
        )


def get_porn_thumbnail_url(video_url):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        try:
            thumbnail_url = info_dict['thumbnail']
            return thumbnail_url
        except Exception as e:
            print(e)
            return None


async def run_async(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)


async def single_download(bot, update, http_link):
    msg = await update.message.edit(f"**Link:-** {http_link}\n\nDownloading... Please Have Patience\n 𝙇𝙤𝙖𝙙𝙞𝙣𝙜...", disable_web_page_preview=True)

    output_folder = f'downloads/{update.from_user.id}'

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Set options for youtube-dl
    if str(http_link).startswith("https://www.pornhub"):
        thumbnail = get_porn_thumbnail_url(http_link)
    else:
        thumbnail = get_thumbnail_url(http_link)

    ytdl_opts = {
        'format': 'best',
        'outtmpl': f"{output_folder}\{'%(title)s-%(id)s.%(ext)s'}",
        'progress_hooks': [lambda d: download_progress_hook(d, update.message, bot)],

    }

    with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
        try:
            await run_async(ydl.download, [http_link])
        except DownloadError:
            await msg.edit("Sorry, There was a problem with that particular video")
            return

    await msg.edit("⚠️ Please Wait...\n\n**Trying to Upload....**")
    unique_id = uuid.uuid4().hex

    if thumbnail:
        thumbnail_filename = f"downloads\{update.from_user.id}\\thumbnail_{unique_id}.jpg"
        response = requests.get(thumbnail)
        if response.status_code == 200:
            with open(thumbnail_filename, 'wb') as f:
                f.write(response.content)

    for file in os.listdir(f'downloads\{update.from_user.id}'):
        if file.endswith(".mp4") or file.endswith('.mkv'):
            try:
                if thumbnail:
                    await bot.send_video(chat_id=update.from_user.id, video=f"downloads\{update.from_user.id}\{file}", thumb=thumbnail_filename, caption=f"**📁 File Name:- `{file}`\n\nHere Is your Requested Video 🔥**\n\nPowered By - @{Config.BOT_USERNAME}", progress=progress_for_pyrogram, progress_args=("\n⚠️ Please Wait...\n\n**Uploading Started...**", msg, time.time()), reply_to_message_id=update.message.id)
                    os.remove(thumbnail_filename)
                    os.remove(f'downloads\{update.from_user.id}\{file}')
                    break
                else:
                    await bot.send_video(chat_id=update.from_user.id, video=f"downloads\{update.from_user.id}\{file}", caption=f"**📁 File Name:- `{file}`\n\nHere Is your Requested Video 🔥**\n\nPowered By - @{Config.BOT_USERNAME}", progress=progress_for_pyrogram, progress_args=("\n⚠️ Please Wait...\n\n**Uploading Started...**", msg, time.time()))
                    os.remove(f'downloads\{update.from_user.id}\{file}')
            except Exception as e:
                await msg.edit(e)
                break
        else:
            continue
    
    os.remove(f'downloads\{update.from_user.id}')
    await msg.delete()