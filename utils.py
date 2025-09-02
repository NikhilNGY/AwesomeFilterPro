import logging
import os
import re
import asyncio
from datetime import datetime
from typing import Union, List

import aiohttp
import requests
from bs4 import BeautifulSoup
from pyrogram import enums
from pyrogram.errors import (
    InputUserDeactivated,
    UserNotParticipant,
    FloodWait,
    UserIsBlocked,
    PeerIdInvalid,
)
from pyrogram.types import Message, InlineKeyboardButton
from imdb import Cinemagoer

from database.users_chats_db import db  # Assuming the db module is correctly implemented
from info import *  # Assuming constants like AUTH_CHANNEL, LONG_IMDB_DESCRIPTION, MAX_LIST_ELM, SHORTNER_API, SHORTNER_SITE

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BTN_URL_REGEX = re.compile(r"(\[([^\[]+?)\]\((buttonurl|buttonalert):(?:/{0,2})(.+?)(:same)?\))")
imdb = Cinemagoer()

SMART_OPEN = '“'
SMART_CLOSE = '”'
START_CHAR = ("'", '"', SMART_OPEN)


class TempState:
    BANNED_USERS = []
    BANNED_CHATS = []
    ME = None
    CURRENT = int(os.environ.get("SKIP", 2))
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None
    SETTINGS = {}
# At the end of utils.py
temp = TempState()


async def is_subscribed(bot, query):
    """
    Check if a user is subscribed to a particular channel.
    """
    try:
        user = await bot.get_chat_member(AUTH_CHANNEL, query.from_user.id)
    except UserNotParticipant:
        # User is not a participant
        return False
    except Exception as e:
        logger.exception(f"Subscription check failed: {e}")
        return False
    else:
        return user.status != 'kicked'


async def get_poster(query, bulk=False, id=False, file=None):
    """
    Fetch movie or TV series information from IMDB using Cinemagoer.
    """

    def list_to_str_safe(val):
        if not val:
            return "N/A"
        if isinstance(val, list):
            if len(val) == 1:
                return str(val[0])
            if MAX_LIST_ELM:
                val = val[:int(MAX_LIST_ELM)]
            return ', '.join(str(elem) for elem in val)
        return str(val)

    if not id:
        query = query.strip().lower()

        # Extract year if available
        year_match = re.findall(r'[1-2]\d{3}$', query)
        title = query
        year = None

        if year_match:
            year = year_match[0]
            title = query.replace(year, "").strip()
        elif file:
            year_file_match = re.findall(r'[1-2]\d{3}', file)
            if year_file_match:
                year = year_file_match[0]

        search_results = imdb.search_movie(title, results=10)
        if not search_results:
            return None

        if year:
            filtered_results = [m for m in search_results if str(m.get('year')) == str(year)]
            if not filtered_results:
                filtered_results = search_results
        else:
            filtered_results = search_results

        movie_candidates = [m for m in filtered_results if m.get('kind') in ['movie', 'tv series']]
        if not movie_candidates:
            movie_candidates = filtered_results

        if bulk:
            return movie_candidates

        movie_id = movie_candidates[0].movieID
    else:
        movie_id = query

    movie = imdb.get_movie(movie_id)
    date = movie.get("original air date") or movie.get("year") or "N/A"

    plot = ""
    if not LONG_IMDB_DESCRIPTION:
        plot_list = movie.get('plot')
        if plot_list:
            plot = plot_list[0]
    else:
        plot = movie.get('plot outline') or ""

    if plot and len(plot) > 800:
        plot = plot[:800] + "..."

    return {
        "title": movie.get("title"),
        "votes": movie.get("votes"),
        "aka": list_to_str_safe(movie.get("akas")),
        "seasons": movie.get("number of seasons"),
        "box_office": movie.get("box office"),
        "localized_title": movie.get("localized title"),
        "kind": movie.get("kind"),
        "imdb_id": f"tt{movie.get('imdbID')}",
        "cast": list_to_str_safe(movie.get("cast")),
        "runtime": list_to_str_safe(movie.get("runtimes")),
        "countries": list_to_str_safe(movie.get("countries")),
        "certificates": list_to_str_safe(movie.get("certificates")),
        "languages": list_to_str_safe(movie.get("languages")),
        "director": list_to_str_safe(movie.get("director")),
        "writer": list_to_str_safe(movie.get("writer")),
        "producer": list_to_str_safe(movie.get("producer")),
        "composer": list_to_str_safe(movie.get("composer")),
        "cinematographer": list_to_str_safe(movie.get("cinematographer")),
        "music_team": list_to_str_safe(movie.get("music department")),
        "distributors": list_to_str_safe(movie.get("distributors")),
        "release_date": date,
        "year": movie.get("year"),
        "genres": list_to_str_safe(movie.get("genres")),
        "poster": movie.get("full-size cover url"),
        "plot": plot,
        "rating": str(movie.get("rating")),
        "url": f'https://www.imdb.com/title/tt{movie_id}'
    }


async def broadcast_messages(user_id, message):
    """
    Broadcast a message to a user handling exceptions gracefully.
    """
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        logger.info(f"Deleted user {user_id} from DB due to deactivated account.")
        return False, "Deleted"
    except UserIsBlocked:
        logger.info(f"User {user_id} blocked the bot.")
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        logger.info(f"Invalid peer ID for user {user_id}, removed from DB.")
        return False, "Error"
    except Exception as e:
        logger.error(f"Broadcast error for user {user_id}: {e}")
        return False, "Error"


async def search_gagala(text):
    """
    Perform a Google search and return the titles of the results.
    """
    user_agent = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/61.0.3163.100 Safari/537.36')
    }
    query_text = text.replace(" ", "+")
    url = f'https://www.google.com/search?q={query_text}'

    response = requests.get(url, headers=user_agent)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    titles = [h3.get_text() for h3 in soup.find_all('h3')]

    return titles


async def get_settings(group_id):
    """
    Retrieve group settings with caching.
    """
    settings = TempState.SETTINGS.get(group_id)
    if not settings:
        settings = await db.get_settings(group_id)
        TempState.SETTINGS[group_id] = settings
    return settings


async def save_group_settings(group_id, key, value):
    """
    Save a group setting and update cache.
    """
    current = await get_settings(group_id)
    current[key] = value
    TempState.SETTINGS[group_id] = current
    await db.update_settings(group_id, current)


def get_size(size):
    """
    Convert a file size in bytes into a human-readable string.
    """
    units = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']
    size = float(size)
    i = 0
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    return f"{size:.2f} {units[i]}"


def split_list(l, n):
    """
    Yield successive n-sized chunks from list l.
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_file_id(msg: Message):
    """
    Extract file/media object from a Telegram message.
    """
    if msg.media:
        media_types = (
            "photo", "animation", "audio", "document", "video",
            "video_note", "voice", "sticker"
        )
        for media_type in media_types:
            media_obj = getattr(msg, media_type, None)
            if media_obj:
                setattr(media_obj, "message_type", media_type)
                return media_obj
    return None


def extract_user(message: Message) -> Union[int, str]:
    """
    Extract user ID and name from a message or its reply.
    Supports commands, mentions, or reply cases.
    """
    user_id = None
    user_first_name = None

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.first_name

    elif len(message.command) > 1:
        if len(message.entities) > 1 and message.entities[1].type == enums.MessageEntityType.TEXT_MENTION:
            entity = message.entities[1]
            user_id = entity.user.id
            user_first_name = entity.user.first_name
        else:
            user_id = message.command[1]
            user_first_name = user_id  # fallback to ID string
        try:
            user_id = int(user_id)
        except ValueError:
            pass
    else:
        user_id = message.from_user.id
        user_first_name = message.from_user.first_name

    return user_id, user_first_name


def list_to_str(k):
    """
    Converts list to string with optional truncation from MAX_LIST_ELM.
    """
    if not k:
        return "N/A"
    if isinstance(k, list):
        if len(k) == 1:
            return str(k[0])
        items = k[:int(MAX_LIST_ELM)] if MAX_LIST_ELM else k
        return ', '.join(str(elem) for elem in items)
    return str(k)


def last_online(from_user):
    """
    Return a string describing the user's last online status.
    """
    if from_user.is_bot:
        return "🤖 Bot :("
    status = from_user.status
    if status == enums.UserStatus.RECENTLY:
        return "Recently"
    elif status == enums.UserStatus.LAST_WEEK:
        return "Within the last week"
    elif status == enums.UserStatus.LAST_MONTH:
        return "Within the last month"
    elif status == enums.UserStatus.LONG_AGO:
        return "A long time ago :("
    elif status == enums.UserStatus.ONLINE:
        return "Currently Online"
    elif status == enums.UserStatus.OFFLINE:
        last_seen = from_user.last_online_date
        if last_seen:
            return last_seen.strftime("%a, %d %b %Y, %H:%M:%S")
        return "Offline"
    return "Unknown"


def split_quotes(text: str) -> List[str]:
    """
    Split a string by quotes or whitespace into two parts: 
    - quoted part or first word, 
    - remaining text.
    """
    if not any(text.startswith(char) for char in START_CHAR):
        return text.split(None, 1)

    counter = 1  # Skip the first quote character
    while counter < len(text):
        if text[counter] == '\\':
            counter += 2  # Skip escaped char
            continue
        if text[counter] == text[0] or (text[0] == SMART_OPEN and text[counter] == SMART_CLOSE):
            break
        counter += 1
    else:
        return text.split(None, 1)

    key = remove_escapes(text[1:counter].strip())
    rest = text[counter + 1:].strip()
    if not key:
        key = text[0] * 2

    return list(filter(None, [key, rest]))


def parser(text, keyword):
    """
    Parse text and extract inline buttons and alerts in the format:
    [label](buttonurl:link) or [label](buttonalert:link) with optional :same for inline buttons.
    Returns note data text, buttons list, and alerts list.
    """
    if "buttonalert" in text:
        text = text.replace("\n", "\\n").replace("\t", "\\t")

    buttons = []
    alerts = []
    note_data = ""
    prev = 0
    i = 0

    for match in BTN_URL_REGEX.finditer(text):
        # Check if button url is escaped
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check >= 0 and text[to_check] == '\\':
            n_escapes += 1
            to_check -= 1

        if n_escapes % 2 == 0:  # Not escaped
            note_data += text[prev:match.start(1)]
            prev = match.end(1)
            label = match.group(2)
            link_type = match.group(3)
            url = match.group(4).replace(" ", "")
            same_line = bool(match.group(5))

            if link_type == "buttonalert":
                # Adding callback buttons
                btn = InlineKeyboardButton(text=label, callback_data=f"alertmessage:{i}:{keyword}")
                if same_line and buttons:
                    buttons[-1].append(btn)
                else:
                    buttons.append([btn])
                alerts.append(url)
                i += 1
            else:  # buttonurl
                btn = InlineKeyboardButton(text=label, url=url)
                if same_line and buttons:
                    buttons[-1].append(btn)
                else:
                    buttons.append([btn])
        else:
            note_data += text[prev:match.start(1) - 1]
            prev = match.start(1) - 1

    note_data += text[prev:]

    return note_data, buttons, alerts


def remove_escapes(text: str) -> str:
    """
    Remove backslash escape characters from text.
    """
    result = ""
    escaped = False
    for char in text:
        if escaped:
            result += char
            escaped = False
        elif char == '\\':
            escaped = True
        else:
            result += char
    return result


def humanbytes(size):
    """
    Convert bytes to human-readable format with IEC prefixes.
    """
    if not size:
        return ""
    power = 2 ** 10
    n = 0
    units = [' ', 'Ki', 'Mi', 'Gi', 'Ti']
    while size > power and n < len(units) - 1:
        size /= power
        n += 1
    return f"{round(size, 2)} {units[n]}B"


async def get_shortlink(link):
    """
    Shorten a URL using an API.
    """
    url = 'https://vplink.in/api'
    protocol = link.split(":")[0]
    if protocol == "http":
        link = link.replace("http", "https", 1)

    params = {'api': SHORTNER_API, 'url': link}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
                data = await response.json()
                if data.get("status") == "success":
                    return data.get('shortenedUrl')
                logger.error(f"Shortlink error: {data.get('message')}")
                return f"https://{SHORTNER_SITE}/api?api={SHORTNER_API}&link={link}"
    except Exception as e:
        logger.error(f"Shortlink exception: {e}")
        return f"{SHORTNER_SITE}/api?api={SHORTNER_API}&link={link}"
