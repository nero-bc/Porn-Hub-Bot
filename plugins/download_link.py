import asyncio
import os
import sys
import time
import uuid
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from youtube_dl import DownloadError
import youtube_dl
from config import Config
from helper.utils import (
    single_download,
    run_async,
    download_progress_hook,
    get_porn_thumbnail_url,
    get_thumbnail_url,
    progress_for_pyrogram
)

USER_QUEUE = []
QUEUE_LINKS = {}
index = 0


async def multiple_download(bot, update, link_msg):
    global index
    user_id = update.from_user.id
    msg = await update.message.reply_text(
        f"**{index+1}. Link:-** {QUEUE_LINKS[user_id][index]}\n\nDownloading... Please Have Patience\n 𝙇𝙤𝙖𝙙𝙞𝙣𝙜...",
        disable_web_page_preview=True,
        reply_to_message_id=link_msg.id
    )

    output_folder = f'downloads/{update.from_user.id}'

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Set options for youtube-dl
    if str(QUEUE_LINKS[user_id][index]).startswith("https://www.pornhub"):
        thumbnail = get_porn_thumbnail_url(QUEUE_LINKS[user_id][index])
    else:
        thumbnail = get_thumbnail_url(QUEUE_LINKS[user_id][index])

    ytdl_opts = {
        'format': 'best',
        'outtmpl': f"{output_folder}\{'%(title)s-%(id)s.%(ext)s'}",
        'progress_hooks': [lambda d: download_progress_hook(d, msg, bot)],

    }

    with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
        try:
            await run_async(ydl.download, [QUEUE_LINKS[user_id][index]])
        except DownloadError:
            await msg.edit("Sorry, There was a problem with that particular video")

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
        
    await msg.delete()
    
    index += 1
    if index < len(QUEUE_LINKS[user_id]):
        await multiple_download(bot, update, link_msg)
    else:
        await update.message.reply_text(f"𝗔𝗟𝗟 𝗟𝗜𝗡𝗞𝗦 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬 ✅", reply_to_message_id=link_msg.id)



@Client.on_message(filters.regex(pattern=r"(?=.*https://)(?!.*\bmega\b).*"))
async def handle_yt_dl(bot: Client, cmd: Message):
    if cmd.from_user.id in USER_QUEUE:
        return await cmd.reply_text("❗ Yᴏᴜ ᴄᴀɴ ᴅᴏᴡɴʟᴏᴀᴅ sɪɴɢʟᴇ ғɪʟᴇ ᴀᴛ ᴀ ᴛɪᴍᴇ ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴍᴜʟᴛɪᴘʟᴇ ғɪʟᴇs ᴛʀʏ ᴀᴅᴅ ᴍᴜʟᴛɪᴘʟᴇ ʟɪɴᴋs.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('✘ Close ✘', callback_data='close')]]), reply_to_message_id=cmd.id)


    else:
        USER_QUEUE.append(cmd.from_user.id)

    
    btn = [[InlineKeyboardButton('🔻 Download 🔻', callback_data='http_link')]]
    
    if int(cmd.from_user.id) == Config.ADMIN:
        btn.append([InlineKeyboardButton('🖇️ Add Multiple Links 🖇️', callback_data='multiple_http_link')])

    await cmd.reply_text("**Do you want to download this file ?**", reply_to_message_id=cmd.id, reply_markup=InlineKeyboardMarkup(btn))


@Client.on_callback_query(filters.regex('^http_link'))
async def handle_single_download(bot: Client, update: CallbackQuery):
    http_link = update.message.reply_to_message.text
    await single_download(bot, update, http_link)
    USER_QUEUE.remove(update.from_user.id)


@Client.on_callback_query(filters.regex('^multiple_http_link'))
async def handle_multiple_download(bot: Client, update: CallbackQuery):
    http_link = update.message.reply_to_message.text

    user_id = update.from_user.id
    try:
        global QUEUE_LINKS
        user_id = update.from_user.id

        if user_id not in QUEUE_LINKS:
            QUEUE_LINKS.update({user_id: [http_link]})
            await update.message.delete()
            while True:
                link = await bot.ask(chat_id=user_id, text="🔗Send Link to add it to queue 🔗\n\nUse /done when you're done adding links to queue.", filters=filters.text, reply_to_message_id=update.message.id)

                if str(link.text).startswith("https"):
                    QUEUE_LINKS[user_id].append(link.text)
                    await update.message.reply_text("Successfully Added To Queue ✅", reply_to_message_id=link.id)
                elif link.text == "/done":
                    user = QUEUE_LINKS[user_id]
                    links = ""
                    for idx, link in enumerate(user):
                        links += f"{(idx+1)}. `{link}`\n"

                    links_msg = await update.message.reply_text(f"👤 <code>{update.from_user.first_name}</code> 🍁\n\n {links}")
                    break
                else:
                    await update.message.reply_text("⚠️ Please Send Valid Link !")
                    continue

        await update.message.reply_text("Dᴏᴡɴʟᴏᴀᴅɪɴɢ Sᴛᴀʀᴛᴇᴅ ✅\n\nPʟᴇᴀsᴇ ʜᴀᴠᴇ ᴘᴀᴛɪᴇɴᴄᴇ ᴡʜɪʟᴇ ɪᴛ's ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴛ ᴍᴀʏ ᴛᴀᴋᴇ sᴏᴍᴇᴛɪᴍᴇs...")

        if user_id in QUEUE_LINKS:
            try:
                await multiple_download(bot, update, links_msg)

            except Exception as e:
                print('Error on line {}'.format(
                    sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    except Exception as e:
        print('Error on line {}'.format(
            sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


@Client.on_message(filters.private & filters.command('cc'))
async def handle_clear_queue(bot: Client, msg: Message):

    if msg.from_user.id in USER_QUEUE:
        USER_QUEUE.remove(msg.from_user.id)
        await msg.reply_text("**QUEUE CLEARED SUCCESSFULLY ✅**", reply_to_message_id=msg.id)
    else:
        await msg.reply_text("**NO QUEUE FOUND ❗**", reply_to_message_id=msg.id)
