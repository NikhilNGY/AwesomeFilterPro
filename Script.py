import re
from os import environ

id_pattern = re.compile(r'^.\d+$')
def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

class script(object):
    START_TXT = """<strong><blockquote>Fʀɪᴇɴᴅꜱ.......🖤\n  Wᴇ Hᴀᴠᴇ Aʟʀᴇᴀᴅʏ Lᴏꜱᴛ Mᴀɴʏ Cʜᴀɴɴᴇʟꜱ Dᴜᴇ Tᴏ Cᴏᴘʏʀɪɢʜᴛ... Sᴏ Jᴏɪɴ Uꜱ Bʏ Gɪᴠɪɴɢ Yᴏᴜʀ Sᴜᴘᴘᴏʀᴛ, Cᴏᴏᴘᴇʀᴀᴛɪᴏɴ Aɴᴅ Bʟᴇꜱꜱɪɴɢꜱ Tᴏ Tʜɪꜱ Nᴇᴡ Cʜᴀɴɴᴇʟ Oꜰ Oᴜʀꜱ 🙏🙏 Tᴇᴀᴍ: @KR_Picture</blockquote></strong>"""
    
    HELP_TXT = """<strong><blockquote>Aɴʏ Iꜱꜱᴜᴇꜱ Mᴏᴠɪᴇ Fɪʟᴇꜱ Cᴏɴᴛᴀᴄᴛ Oᴡɴᴇʀ\n      \n🍁 Oᴡɴᴇʀ: <a href=https://t.me/Nikhil5757h> Ｄ Ｉ Ｃ Ｔ Ａ ＴＯ Ｒ</a></blockquote></strong>"""
    
    ABOUT_TXT = HELP_TXT
    SOURCE_TXT = HELP_TXT
    MANUELFILTER_TXT = HELP_TXT
    BUTTON_TXT = HELP_TXT
    AUTOFILTER_TXT = HELP_TXT
    EXTRAMOD_TXT = HELP_TXT
    ADMIN_TXT = HELP_TXT

    CAPTION = (
        "<strong><blockquote>Mᴏʀᴇ Mᴏᴠɪᴇꜱ Jᴏɪɴ @sandalwood_kannada_moviesz\n \nTᴇᴀᴍ : @KR_Picture\n \nUᴘʟᴏᴀᴅᴇᴅ Bʏ 👉\nhttps://t.me/+X5CwwZB-jV9iODc1\nhttps://t.me/+X5CwwZB-jV9iODc1</blockquote></strong>"
    )

    STATUS_TXT = """<b><u>Cᴜʀʀᴇɴᴛ Dᴀᴛᴀʙᴀsᴇ Sᴛᴀᴛᴜs</b></u>
    
📑 ғɪʟᴇs sᴀᴠᴇᴅ: <code>{}</code>
👩🏻‍💻 ᴜsᴇʀs: <code>{}</code>
👥 ɢʀᴏᴜᴘs: <code>{}</code>
🗂️ ᴏᴄᴄᴜᴘɪᴇᴅ: <code>{}</code>
"""
    LOG_TEXT_G = """#NewGroup
👥 ɢʀᴏᴜᴘ 👥 = {}(<code>{}</code>)
😇 ᴛᴏᴛᴀʟ ᴍᴇᴍʙᴇʀs 😇 = <code>{}</code>
💌 ᴀᴅᴅᴇᴅ ʙʏ 💌 - {} 
"""
    LOG_TEXT_P = """#NewUser
ɪᴅ ♥️- <code>{}</code>
ɴᴀᴍᴇ 💥- {} 
"""

BAD_WORDS = {
    "@THE_DD_MOVIEZ",
    "@RKN_MOVIEZ1",
    "@MG_Movie",
    "@KnMoviez",
    "@AddaFiles",
    "@adda_files",
    "@MGBMFliX",
    "[DRN]",
    "Sandalwood",
    "@MoviezAddaKA",
    "@AAFliX",
    "@KA_HUB",
    "@Kannada_Cine_Hub",
    "@knmoviez",
    "@AK_Kiccha1",
    "[MG]",
    "@Kannada_Cineflix",
    "@DM_Entertainment" ,
    "@nmk_backup7" ,
    "@Kannada_CineHub" ,
    "[MG]" ,
    "@Kiccha_Creations" ,
    "@TG_Movies4u" ,
    "@TG_MOVIES4U"
} # Set of bad words to filter out
