# Coded by @mmagneto

import os
import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import yt_dlp
import requests
download_queue = asyncio.Queue()
import os
import time
import asyncio
import ffmpeg
import json
from subprocess import check_output
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from config import LOG_CHANNEL, userbot
import math
sira = []
dsira = []
 

preferred_language = "tr" 
                
def get_codec(filepath, channel="v:0"):
    output = check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            channel,
            "-show_entries",
            "stream=codec_name,codec_tag_string",
            "-of",
            "default=nokey=1:noprint_wrappers=1",
            filepath,
        ]
    )
    return output.decode("utf-8").split()

async def encode(filepath):
    path, extension = os.path.splitext(filepath)
    file_name = os.path.basename(path)
    encode_dir = file_name
    output_filepath = encode_dir + 'A.mp4'
    assert (output_filepath != filepath)
    if os.path.isfile(output_filepath):
        print('"{}" Atlanıyor: dosya zaten var'.format(output_filepath))
    print(filepath)

    # Get the audio and subs channel codec
    audio_codec = get_codec(filepath, channel='a:0')

    if not audio_codec:
        audio_opts = '-c:v copy'
    elif audio_codec[0] in 'aac':
        audio_opts = '-c:v copy'
    else:
        audio_opts = '-c:a aac -c:v copy'

    command = ['ffmpeg', '-y', '-i', filepath]
    command.extend(audio_opts.split())
    proc = await asyncio.create_subprocess_exec(
        *command, output_filepath,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await proc.communicate()
    try:
        os.remove(filepath)
    except Exception as e:
        print(e)
    return output_filepath

async def progress_bar(current, total, text, message, start):

    now = time.time()
    diff = now-start
    if round(diff % 10) == 0 or current == total:
        percentage = current*100/total
        speed = current/diff
        elapsed_time = round(diff)*1000
        eta = round((total-current)/speed)*1000
        ett = eta + elapsed_time

        elapsed_time = TimeFormatter(elapsed_time)
        ett = TimeFormatter(ett)

        progress = "[{0}{1}] \n**İlerleme**: {2}%\n".format(
            ''.join(["●" for i in range(math.floor(percentage / 10))]),
            ''.join(["○" for i in range(10 - math.floor(percentage / 10))]),
            round(percentage, 2))

        tmp = progress + "**Indirilen**: {0}/{1}\n**Hız**: `{2}`/s".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            # elapsed_time if elapsed_time != '' else "0 s",
            ett if ett != '' else "0 s"
        )

        try :
            print('{}'.format(tmp))
        except:
            pass

def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

def format_filename(filename):
    # Dosya adı ve uzantısını ayır
    name, ext = os.path.splitext(filename)
    
    # Dosya adını böl ve dönüştür
    formatted_name = '.'.join(word.capitalize() for word in name.split('.'))
    
    # Uzantıyı geri ekle
    return formatted_name + ext
 
def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]

def get_width_height(filepath):
    metadata = extractMetadata(createParser(filepath))
    if metadata.has("width") and metadata.has("height"):
      return metadata.get("width"), metadata.get("height")
    else:
      return 1280, 720
    
async def get_thumbnail(video_file, output_directory, ttl):
    # https://stackoverflow.com/a/13891070/4723940
    out_put_file_name = str(time.time()) + ".jpg"
    file_genertor_command = [
        "ffmpeg",
        "-ss",
        str(ttl),
        "-i",
        video_file,
        "-vframes",
        "1",
        out_put_file_name
    ]
    # width = "90"
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None

def get_duration(filepath):
    metadata = extractMetadata(createParser(filepath))
    if metadata.has("duration"):
      return metadata.get('duration').seconds
    else:
      return 0   

async def tg_upload(message,video,a,thumb):
    caption = f"{video}"
    start_time = time.time()
    duration = get_duration(video)
    if thumb:
        thumb = thumb
    else:
        thumb_path = f"thumbs/{message.chat.id}/{message.chat.id}.jpg"
        if os.path.exists(thumb_path):
            thumb = thumb_path
        else:
            thumb = await get_thumbnail(video, "decrypted", duration / 4)
    file_size = os.stat(video).st_size
    if file_size > 2093796556 and file_size < 4294967296:
        await userbot.send_video(
            chat_id=LOG_CHANNEL,
            video=video,
            caption=caption,
            thumb=thumb, 
            progress=progress_bar,
            progress_args=(
                'Dosyan Yükleniyor!',
                a,
                start_time),
            duration=duration)
        
    elif file_size < 2093796556:
        copy = await message.reply_video(
            video=video,
            caption=caption,
            thumb=thumb,
            progress = progress_bar, 
            progress_args = (
                'Dosyan Yükleniyor!',
                a,
                start_time
                ),
            duration=duration)
        try:
            await copy.copy(LOG_CHANNEL)
        except Exception as e:
            await message.reply_text(e)
        
    os.remove(video)





def download_video(video_url, preferred_language):
    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        'merge_output_format': 'mp4',
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        
        info = ydl.extract_info(video_url, download=False)
        
        audio_streams = [
            f for f in info.get('formats', [])
            if f.get('acodec') != 'none'  
        ]
        
        audio_languages = {stream.get('language') for stream in audio_streams if stream.get('language')}

        if audio_languages: 
            if preferred_language in audio_languages:
                print(f"{preferred_language} var")
                ydl_opts['format'] = f"bestvideo[height<=720]+bestaudio[language={preferred_language}]/best[height<=720]"
            else:
                print(f"{preferred_language} yok")
                ydl_opts['format'] = f"bestvideo[height<=720]+bestaudio[language={audio_languages.pop()}]/best[height<=720]"
        else: 
            print("Dil bilgisi bulunamadı. Varsayılan ses indirilecek.")
            ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]'

        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            filename = ydl.prepare_filename(info)
    
    return filename



def download_m3u8_with_ytdlp(m3u8_url, output_dir,name,a):
    """Download an M3U8 video using yt-dlp."""
    nname = f"downloads/{name}"
    ydl_opts = {
        'outtmpl': nname,
        'format': 'best',
        'quiet': True,
        'merge_output_format': 'mp4',
        'http_headers': {},
        'external_downloader': 'aria2c',
        'external_downloader_args': ['-x16', '-s16', '-k1M']
    }

    if ".cloud" in m3u8_url:
        ydl_opts['http_headers']['Referer'] = "https://vidmoly.to/"
    if ".mubicdn.net" in m3u8_url:
        ydl_opts['http_headers']['Referer'] = "https://mubi.com"
    if "storage.diziyou.co" in m3u8_url:
        ydl_opts['http_headers']['Referer'] = "https://storage.diziyou.co/episodes/"
    if ".online" in m3u8_url:
        ydl_opts['http_headers']['Referer'] = "https://vidmoly.to/"
    if ".space" in m3u8_url:
        ydl_opts['http_headers']['Referer'] = "https://vidmoly.to/"
    if ".lat" in m3u8_url:
        ydl_opts['http_headers']['Referer'] = "https://vidmoly.to/"
    if "https://upstreamcdn.co" in m3u8_url:
        ydl_opts['http_headers']['Referer'] = "https://upstreamcdn.co"
    if "rapidrame" in m3u8_url:
        ydl_opts['http_headers']['Referer'] = "https://www.hdfilmcehennemi.fun/"
    if "closeload" in m3u8_url:
        ydl_opts['http_headers']['Referer'] = "https://closeload.com/"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(m3u8_url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

async def on_task_complete(bot, message: Message):
    if len(sira) > 0:
        await download_playlist(bot, sira[0])

async def on_task_completed(bot, message: Message):
    if len(dsira) > 0:
        await pllll(bot, dsira[0])
        
@Client.on_message(filters.text & filters.private)
async def pl(bot, message):
    try:
        text = message.text
        url_pattern = r"https?://[^\s]+"
        urls = re.findall(url_pattern, text)
        if not urls:
            return
        sirasi = len(sira)
        await message.reply_text(f"İşlem Sıraya Eklendi...\n\nSıranız: {sirasi}")
        sira.append(message)
        if len(sira) == 1:
            await download_playlist(bot, message)
    except Exception as e:
        await message.reply_text(e)
        del sira[0]
        await on_task_complete(bot, message)

@Client.on_message(filters.document)
async def dss(bot, message):
    try:
        sirasi = len(dsira)
        await message.reply_text(f"İşlem Sıraya Eklendi...\n\nSıranız: {sirasi}")
        dsira.append(message)
        if len(dsira) == 1:
            await pllll(bot, message)
    except Exception as e:
        await message.reply_text(e)
        del dsira[0]
        await on_task_completed(bot, message)

async def pllll(bot, message):
    a = await message.reply_text("Başladım")
    try:
        file = message.document or message.video or message.audio
        file_name = file.file_name
        download_path = await message.download(file_name=file_name)
        try:
            with open(download_path, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)
            for i in data:
                dub_url = i["dublaj_url"]
                dub_name = i["dub_name"]
                if dub_url != "DUBLAJ YOK":
                    try:
                        video = download_m3u8_with_ytdlp(dub_url, "ne",dub_name,"ne")
                        thumb = None
                        await tg_upload(message,video,a,thumb)
                    except Exception as e:
                        print(e)
                alt_url = i["alt_url"]
                alt_name = i["alt_name"]
                if alt_url != "URL YOK":
                    try:
                        video = download_m3u8_with_ytdlp(alt_url, "ne",alt_name,"ne")
                        thumb = None
                        await tg_upload(message,video,a,thumb)
                    except Exception as e:
                        print(e)
            try:
                await message.reply_text("Bitti")
                os.remove(download_path)
                del dsira[0]
                await on_task_completed(bot, message)
            except Exception as e:
                print(e)        
        except Exception as e:
            print(e)
    except Exception as e:
        await message.reply_text(e)
        

async def download_playlist(bot, message: Message):
    tt = message.text.split(" ")
   
    if len(tt) < 1:
        await message.reply("Lütfen bir YouTube playlist URL'si gönderin. Örnek: /download_playlist <URL>")
        return
    
    playlist_url = tt[0]
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)

    
    a = await message.reply_text("İşlem Başlıyor")
    if 1 == 1:
        if "playlist" in playlist_url:
            ydl_opts = {'quiet': True, 'extract_flat': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(playlist_url, download=False)

            if 'entries' not in playlist_info:
                await message.reply("Playlist bilgileri alınamadı. Lütfen URL'yi kontrol edin.")
                return

            video_urls = [entry['url'] for entry in playlist_info['entries']]
            for video_url in video_urls:
                await a.edit(f"Video indiriliyor: {video_url}")
                video = download_video(video_url,preferred_language)
                id = video_url.split("watch?v=")[1]
                t_url = f"https://i.ytimg.com/vi/{id}/maxresdefault.jpg"
                try:
                    c = f"wget {t_url} -O {id}.jpg"
                    os.system(c)
                    thumb = f"{id}.jpg"
                except Exception as e:
                    print(e)
                    thumb = None
                await tg_upload(message,video,a,thumb)
                os.remove(thumb)
        elif "youtu" in playlist_url and "playlist" not in playlist_url:
            video_urls = []
            video_urls.append(playlist_url)
            for video_url in video_urls:
                await a.edit(f"Video indiriliyor: {video_url}")
                video = download_video(video_url, preferred_language)
                id = video_url.split("watch?v=")[1]
                t_url = f"https://i.ytimg.com/vi/{id}/maxresdefault.jpg"
                try:
                    c = f"wget {t_url} -O {id}.jpg"
                    os.system(c)
                    thumb = f"{id}.jpg"
                except Exception as e:
                    print(e)
                    thumb = None
                await tg_upload(message,video,a,thumb)
                os.remove(thumb)
        else:
            if 1 == 1:
                name = tt[1]
                filename = download_m3u8_with_ytdlp(playlist_url, output_dir,name,a)
                video = filename
                thumb = None
                await tg_upload(message,video,a,thumb)
            
        
        await a.edit("Başarıyla indirildi!")
        del sira[0]
        await on_task_complete(bot, message)

Client.on_message(filters.command("restart"))
async def restart(bot, message):
    cmd = message.text.split(' ', 1)
    dynoRestart = False
    dynoKill = False
    if len(cmd) == 2:
        dynoRestart = (cmd[1].lower()).startswith('d')
        dynoKill = (cmd[1].lower()).startswith('k')
    try:
        await message.reply_text("Normal Restart oluyor.")
        os.execl(executable, executable, "bot.py")
    except Exception as f:
        await message.reply_text(f"başaramadım {f}")
