import re, sys, logging
from os import environ
from Script import script

logging.basicConfig(level=logging.ERROR)

def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# Bot information
SESSION = environ.get('SESSION', 'Auto_Filters_Bot')
API_ID = environ.get('API_ID', '27002519')
if len(API_ID) == 0:
    logging.error('API_ID is missing, exiting now')
    exit()
else:
    API_ID = int(API_ID)
API_HASH = environ.get('API_HASH', '1033ee721101d78366b4ac46aadf3930')
if len(API_HASH) == 0:
    logging.error('API_HASH is missing, exiting now')
    exit()
BOT_TOKEN = environ.get('BOT_TOKEN', '7139992977:AAEvdepM-M9lLhp5uPS7fxRFE1O18KVI0ok')
if len(BOT_TOKEN) == 0:
    logging.error('BOT_TOKEN is missing, exiting now')
    exit()
PORT = int(environ.get('PORT', '8080'))

# Bot pics
PICS = (environ.get('PICS', 'https://telegra.ph/file/58fef5cb458d5b29b0186.jpg https://telegra.ph/file/f0aa4f433132769f8970c.jpg https://telegra.ph/file/f515fbc2084592eca60a5.jpg https://telegra.ph/file/20dbdcffaa89bd3d09a74.jpg https://telegra.ph/file/6045ba953af4def846238.jpg')).split()

# Bot Admins
ADMINS = environ.get('ADMINS', '6174868004')
if len(ADMINS) == 0:
    logging.error('ADMINS is missing, exiting now')
    exit()
else:
    ADMINS = [int(admins) for admins in ADMINS.split()]

# Channels
INDEX_CHANNELS = [int(index_channels) if index_channels.startswith("-") else index_channels for index_channels in environ.get('INDEX_CHANNELS', '-1002233820213').split()]
AUTH_CHANNEL = [int(auth_channels) for auth_channels in environ.get('AUTH_CHANNEL', '').split()]
LOG_CHANNEL = environ.get('LOG_CHANNEL', '-1002213457968')
if len(LOG_CHANNEL) == 0:
    logging.error('LOG_CHANNEL is missing, exiting now')
    exit()
else:
    LOG_CHANNEL = int(LOG_CHANNEL)

# MongoDB information
DATABASE_URL = environ.get('DATABASE_URL', "mongodb+srv://RP44:RZoUNws5PGcZroT6@rajps33.a0tsf.mongodb.net/?retryWrites=true&w=majority&appName=Rajps33")
if len(DATABASE_URL) == 0:
    logging.error('DATABASE_URL is missing, exiting now')
    exit()
DATABASE_NAME = environ.get('DATABASE_NAME', "Cluster0")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Files')

# Links
SUPPORT_LINK = environ.get('SUPPORT_LINK', 'https://t.me/Netfilix_movie_shaport')
UPDATES_LINK = environ.get('UPDATES_LINK', 'https://t.me/+Ie4mNf6lL5RjYjM1')

# Bot settings
AUTO_FILTER = is_enabled((environ.get('AUTO_FILTER', "True")), True)
IMDB = is_enabled((environ.get('IMDB', "True")), True)
SPELL_CHECK = is_enabled(environ.get("SPELL_CHECK", "True"), True)
SHORTLINK = is_enabled((environ.get('SHORTLINK', "False")), False)
DELETE_TIME = int(environ.get('DELETE_TIME', 3600))
AUTO_DELETE = is_enabled((environ.get('AUTO_DELETE', "False")), False)
WELCOME = is_enabled((environ.get('WELCOME', "False")), False)
PROTECT_CONTENT = is_enabled((environ.get('PROTECT_CONTENT', "False")), False)
LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
LINK_MODE = is_enabled(environ.get("LINK_MODE", "True"), True)
CACHE_TIME = int(environ.get('CACHE_TIME', 300))

# Other
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", script.IMDB_TEMPLATE)
FILE_CAPTION = environ.get("FILE_CAPTION", script.FILE_CAPTION)
SHORTLINK_URL = environ.get("SHORTLINK_URL", "shortxlinks.com")
SHORTLINK_API = environ.get("SHORTLINK_API", "fa2a0768fc8d2a51b22e46293634a52670a73c7a")
WELCOME_TEXT = environ.get("WELCOME_TEXT", script.WELCOME_TEXT)
TUTORIAL = environ.get("TUTORIAL", "")

# stream features vars
BIN_CHANNEL = environ.get("BIN_CHANNEL", "-1002237538640")
if len(BIN_CHANNEL) == 0:
    logging.error('BIN_CHANNEL is missing, exiting now')
    exit()
else:
    BIN_CHANNEL = int(BIN_CHANNEL)
URL = environ.get("URL", "https://t.me/+kP4LSVcocBVhZjc1")
if len(URL) == 0:
    logging.error('URL is missing, exiting now')
    exit()
else:
    if URL.startswith(('https://', 'http://')):
        if not URL.endswith("/"):
            URL += '/'
    else:
        logging.error('URL is not valid, exiting now')
        exit()
