import logging
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, PeerIdInvalid
from imdb import Cinemagoer
import asyncio
from pyrogram.types import Message, InlineKeyboardButton
from datetime import datetime
import pytz
import re
from database.users_chats_db import db
from shortzy import Shortzy
from functools import lru_cache
from asyncio import Lock

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

imdb = Cinemagoer()

class TempData:
    START_TIME = 0
    BANNED_USERS = []
    BANNED_CHATS = []
    SETTINGS = {}
    FILES = {}

temp = TempData()
temp_lock = Lock()

@lru_cache(maxsize=100)
async def get_movie_from_imdb(query):
    return imdb.search_movie(query, results=10)

async def is_subscribed(bot, query, channels):
    btn = []
    for channel_id in channels:
        try:
            chat = await bot.get_chat(channel_id)
            await bot.get_chat_member(channel_id, query.from_user.id)
        except UserNotParticipant:
            btn.append([InlineKeyboardButton(f'Join {chat.title}', url=chat.invite_link)])
        except PeerIdInvalid:
            logger.warning(f"Invalid peer ID for chat {channel_id}")
        except Exception as e:
            logger.error(f"Error while checking subscription: {e}")
    return btn

async def get_poster(query, bulk=False, id=False, file=None):
    if not id:
        query = query.strip().lower()
        title = re.sub(r'[1-2]\d{3}$', '', query).strip()
        year_match = re.findall(r'[1-2]\d{3}$', query)
        year = year_match[0] if year_match else None

        movie_results = await get_movie_from_imdb(title)
        if not movie_results:
            logger.warning(f"No movie found for query: {query}")
            return None
        
        if year:
            movie_results = [m for m in movie_results if str(m.get('year')) == year]
        movie = movie_results[0]  # Pick the top result for simplicity

    else:
        movie = imdb.get_movie(query)

    plot = movie.get('plot outline', '')
    plot = plot if len(plot) < 800 else plot[:800] + "..."

    return {
        'title': movie.get('title'),
        'year': movie.get('year'),
        'poster': movie.get('full-size cover url'),
        'plot': plot,
        'url': f'https://www.imdb.com/title/tt{movie.movieID}'
    }

def list_to_str(lst):
    if not lst:
        return "N/A"
    return ', '.join(str(item) for item in lst)

async def broadcast_messages(user_id, message, retries=3):
    try:
        await message.copy(chat_id=user_id)
        return "Success"
    except FloodWait as e:
        if retries > 0:
            await asyncio.sleep(e.value)
            return await broadcast_messages(user_id, message, retries - 1)
        else:
            logger.warning(f"Failed to send message to {user_id} after multiple retries.")
            return "Error"
    except Exception as e:
        await db.delete_user(int(user_id))
        logger.error(f"Error while broadcasting to {user_id}: {e}")
        return "Error"

async def groups_broadcast_messages(chat_id, message):
    try:
        k = await message.copy(chat_id=chat_id)
        try:
            await k.pin()
        except Exception as e:
            logger.warning(f"Error pinning message in {chat_id}: {e}")
        return "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await groups_broadcast_messages(chat_id, message)
    except Exception as e:
        await db.delete_chat(chat_id)
        logger.error(f"Error while broadcasting to group {chat_id}: {e}")
        return "Error"

async def get_settings(group_id):
    settings = temp.SETTINGS.get(group_id)
    if not settings:
        settings = await db.get_settings(group_id)
        temp.SETTINGS.update({group_id: settings})
    return settings
    
async def save_group_settings(group_id, key, value):
    async with temp_lock:
        current = await get_settings(group_id)
        current.update({key: value})
        temp.SETTINGS.update({group_id: current})
        await db.update_settings(group_id, current)

def get_size(size):
    """Get size in readable format"""
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

def get_readable_time(seconds):
    periods = [('d', 86400), ('h', 3600), ('m', 60), ('s', 1)]
    result = ''
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f'{int(period_value)}{period_name}'
    return result

def get_wish():
    tz = pytz.timezone('Asia/Colombo')
    time = datetime.now(tz)
    now = time.strftime("%H")
    if now < "12":
        status = "ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ 🌞"
    elif now < "18":
        status = "ɢᴏᴏᴅ ᴀꜰᴛᴇʀɴᴏᴏɴ 🌗"
    else:
        status = "ɢᴏᴏᴅ ᴇᴠᴇɴɪɴɢ 🌘"
    return status
