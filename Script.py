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

    CUSTOM_FILE_CAPTION = (
        "<strong><blockquote>{filename}\n\n"
        "Mᴏʀᴇ Mᴏᴠɪᴇꜱ Jᴏɪɴ @sandalwood_kannada_moviesz\n\n"
        "Tᴇᴀᴍ : @KR_Picture\n\n"
        "Uᴘʟᴏᴀᴅᴇᴅ Bʏ 👉\n"
        "https://t.me/+X5CwwZB-jV9iODc1\n"
        "https://t.me/+X5CwwZB-jV9iODc1"
        "</blockquote></strong>"
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
