import asyncio
import io
import re
import json
import html
import os
import httpx
import random
import string
import time
import struct
import hmac
import hashlib
import base64
import threading
from datetime import datetime, timedelta
from flask import Flask
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler

# ==================== FLASK SERVER FOR RENDER ====================
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is Running Live 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

# ==================== LOCAL CONFIGURATION ====================
CONFIG_BOT_TOKEN = "8413412337:AAHy_S2urriXztED2c3c25IrFruSAGRJUgM"
CONFIG_STEX_API_KEY = "MFFACUE0J2F"
CONFIG_STEX_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tness/@public/api"
CONFIG_ADMIN_ID = 8991828975
CONFIG_OTP_GROUP_ID = -1003964512828

# Premium copy button (PTB 21+)
try:
    from telegram import CopyTextButton
    HAS_COPY_BTN = True
except ImportError:
    HAS_COPY_BTN = False

# ==================== CONFIG SECTION ====================
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip() or CONFIG_BOT_TOKEN.strip()
USER_DATA_FILE = "users.json"
PAID_SMS_FILE = "paid_sms.json"
STATS_FILE = "user_stats.json"
REFERRAL_DATA_FILE = "referral_data.json"
BANNED_USERS_FILE = "banned_users.json"
WITHDRAW_DATA_FILE = "withdraw_requests.json"
ACTIVITY_LOGS_FILE = "activity_logs.json"
DATA_RANGE_FILE = "datarange.json"
SETTINGS_FILE = "settings.json"

BOT_USERNAME = None

ADMIN_ID = int(os.getenv("ADMIN_ID", str(CONFIG_ADMIN_ID)))
ADMINS = [ADMIN_ID]

OTP_GROUP_ID = int(os.getenv("OTP_GROUP_ID", str(CONFIG_OTP_GROUP_ID)))

# ==================== PREMIUM EMOJI MAPPING ====================
EMOJI_ID_MAP = {
    "telegram": "5271801931814165886", "instagram": "5269682734820777950",
    "facebook": "5269427536453984598", "tiktok": "5271527792641595125",
    "x": "5269500885905468781",        "whatsapp": "5271536803482981220",
    "up": "5244837092042750681",        "down": "5246762912428603768",
    "add": "5397916757333654639",       "setting": "5341715473882955310",
    "1st": "5440539497383087970",       "2st": "5447203607294265305",
    "3rd": "5453902265922376865",       "free": "5406756500108501710",
    "msg": "5253742260054409879",       "link": "5271604874419647061",
    "status": "5231200819986047254",    "home": "5416041192905265756",
    "gift_box": "5970074171449808121",  "delete": "5422557736330106570",
    "number_change": "5267295703666824255", "refer_btn": "5420396762189831222",
    "get_number_btn": "5375338737028841420", "cross": "5420130255174145507",
    "stop": "5956074558044770726",      "ban": "5420323339723881652",
    "loading": "5386367538735104399",   "profile": "5352861489541714456",
    "done": "6298670698948724690",      "otp_success": "5190781475468915802",
    "nagad": "5352985330628730418",     "bkash": "5348469219761626211",
    "rocket": "5346042941196507141",    "binance": "5348212415077064131",
    "live": "5355102594886833928",      "developer": "5267294466716244344",
    "channel": "6215074610845585917",   "copy": "5429483843541284898",
    "admin": "5350396951407895212",     "waiting": "6217721388736712699",
    "back": "5267490665117275176",      "leader_board": "5280769763398671636",
    "money": "6233367447789899509",     "discord": "5807892405306791778",
    "custom_range": "5231012545799666522", "paypal": "5107533253946901363",
    "imo": "5337155807752524558",       "hi": "5353027129250453493",
    "off": "5352974971167611327",       "diamond": "5251562950698759162",
    "broadcast": "5251671501702196837", "key": "5296369303661067030",
    "bot_logo": "4943094697238201446",  "tk": "5201873447554145566",
    "roket": "5188481279963715781",     "all_done": "5859265295113261399",
    "yes": "5875017993909440887",       "no": "5875005555684152921",
    "fire_love": "5864093929275658617",
}

FALLBACK_EMOJI_MAP = {
    "telegram": "✈️", "instagram": "📷", "facebook": "🔵",
    "tiktok": "🎵", "x": "❌", "whatsapp": "💬",
    "up": "📈", "down": "📉", "add": "➕", "setting": "⚙️",
    "1st": "🥇", "2st": "🥈", "3rd": "🥉", "free": "🆓",
    "msg": "💬", "link": "🔗", "status": "📊", "home": "🏠",
    "gift_box": "🎁", "delete": "🗑️", "number_change": "🔄",
    "get_number_btn": "📞", "cross": "❌", "stop": "🛑",
    "ban": "🚫", "loading": "⏳", "profile": "👤", "done": "✅",
    "otp_success": "⭐", "nagad": "🟠", "bkash": "💖",
    "rocket": "🚀", "binance": "🟡", "live": "🟢",
    "developer": "👨‍💻", "channel": "📢",
    "copy": "📋", "admin": "👑", "waiting": "⏳", "back": "🔙",
    "leader_board": "🏆", "custom_range": "🎯", "refer_btn": "🔗",
    "paypal": "💳", "imo": "💬", "hi": "👋", "off": "🛑",
    "diamond": "💎", "broadcast": "📢", "key": "🔑", "tk": "৳",
    "roket": "🚀", "all_done": "✅", "yes": "✔️", "no": "❌",
    "fire_love": "❤️",
}

PREMIUM_FLAGS = {
    "🇺🇸": "5913463998522592692", "🇺🇦": "5911406692007941050", "🇵🇱": "5913550391789752571",
    "🇰🇿": "5913724621433082323", "🇦🇿": "5911197578640233518", "🇪🇸": "5911106310585193018",
    "🇦🇲": "5913272455866093666", "🇷🇺": "5913274246867456342", "🇺🇿": "5911051846104912282",
    "🇩🇪": "5911096835887337583", "🇯🇵": "5913293711659241040", "🇹🇷": "5910995113881901195",
    "🇧🇩": "5911011185649521599", "🇬🇧": "5913443365499703513", "🇮🇳": "5913754823643107921",
    "🇧🇷": "5911148568768418614", "🇾🇪": "5913346492512341993", "🇻🇳": "5913428887164949581",
    "🇦🇪": "5913726554168365343", "🇺🇬": "5913488939397681980", "🇹🇲": "5913315521503170180",
    "🇹🇳": "5911332947419468671", "🇹🇭": "5913617968805187987", "🇹🇯": "5911418949844603556",
    "🇸🇪": "5911156510162949403", "🇸🇩": "5911387497799094470", "🇱🇰": "5911293163137406640",
    "🇿🇦": "5911203119148044594", "🇸🇬": "5911531460808051849", "🇷🇸": "5913592598433369871",
    "🇸🇳": "5910995302860461643", "🇶🇦": "5911260864983339619", "🇵🇹": "5911023653939581472",
    "🇵🇭": "5911268638874145162", "🇵🇪": "5911207993935925780", "🇵🇰": "5913705895375672082",
    "🇴🇲": "5913570801474343473", "🇳🇴": "591361797574537046", "🇳🇬": "5911143844304393105",
    "🇳🇿": "5913640044937089340", "🇳🇱": "5913367645226275100", "🇳🇵": "5913496520014958723",
    "🇲🇦": "5911482111633658301", "🇲🇳": "5911041383564580038", "🇲🇩": "5913456847402045950",
    "🇲🇽": "5913687302462246518", "🇲🇾": "5913654360063087453", "🇰🇪": "5911154710571651231",
    "🇱🇹": "5911172315642597775", "🇱🇻": "5913738489882480243", "🇱🇧": "5911504273664905447",
    "🇮🇩": "5913479361620611038", "🇮🇷": "5911308891307643032", "🇮🇶": "5911382442622587735",
    "🇮🇱": "5911471936856134692", "🇮🇹": "5913688444923547525", "🇭🇺": "5913767635530551104",
    "🇬🇷": "5911210399117611448", "🇬🇭": "5913391155877252952", "🇬🇪": "5913434771270144023",
    "🇫🇷": "5913605586414473124", "🇫🇮": "5911041344909873378", "🇪🇹": "5911078333168227043",
    "🇪🇬": "5913694831539916769", "🇩🇰": "5911206009661034712", "🇨🇾": "5911023550860366409",
    "🇭🇷": "5913692684056269311", "🇨🇳": "5913779335021466780", "🇨🇦": "5911365056594973179",
    "🇧🇪": "5913529642802745141", "🇦🇺": "5913632326880858455", "🇦🇹": "5911338831524664592",
    "🇦🇷": "5913573356979884082", "🇰🇷": "5913371673905598425", "🇸🇦": "4985897134424328239",
    "🇨🇴": "5913773060074246009", "🇨🇱": "5911470957603592832", "🇿🇲": "5913564754160389778",
}

def get_tg_emoji(key, default_char=""):
    emoji_id = EMOJI_ID_MAP.get(key)
    fallback = default_char or FALLBACK_EMOJI_MAP.get(key, "⭐")
    if emoji_id:
        return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'
    return fallback

def get_country_tg_flag(flag_emoji):
    emoji_id = PREMIUM_FLAGS.get(flag_emoji)
    if emoji_id:
        return f'<tg-emoji emoji-id="{emoji_id}">{flag_emoji}</tg-emoji>'
    return f'<tg-emoji emoji-id="5911106310585193018">{flag_emoji}</tg-emoji>'

# ==================== SYSTEM DYNAMIC SETTINGS ====================
_settings_cache = None

def load_settings():
    global _settings_cache
    if _settings_cache is not None:
        return _settings_cache
    default = {
        "active_panel": "stex",
        "stex_api_key": os.getenv("STEX_API_KEY", "").strip() or CONFIG_STEX_API_KEY.strip(),
        "stex_base_url": os.getenv("STEX_BASE_URL", CONFIG_STEX_BASE_URL),
        "panel_url": "https://stexsms.com",
        "allowed_services": ["Instagram","Facebook","WhatsApp","TikTok","Telegram","Discord","PayPal","Imo"],
        "otp_group_url": "https://t.me/+31eV11IT7WQzMjI9",
        "channel_url": "https://t.me/MinoXofficial0",
        "support_username": "@support",
        "maintenance_mode": False,
        "cooldown_time": 1.0,
        "min_withdraw": 50.0,
        "otp_bonus": 0.20,
        "referral_bonus": 0.0,
        "admins": [ADMIN_ID],
        "owners": [ADMIN_ID],
        "otp_group_chat_id": OTP_GROUP_ID,
        "force_join_channel": None,
        "manual_services": [],
    }
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(default, f, indent=4)
        _settings_cache = default
        return default
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
        updated = False
        for k, v in default.items():
            if k not in data:
                data[k] = v; updated = True
        if updated:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(data, f, indent=4)
        _settings_cache = data
        return data
    except Exception:
        _settings_cache = default
        return default

def save_settings(settings):
    global _settings_cache
    _settings_cache = settings
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

def clean_base_url(url):
    return str(url).strip().rstrip('/')

def get_api_credentials():
    settings = load_settings()
    env_api_key = os.getenv("STEX_API_KEY", "").strip() or CONFIG_STEX_API_KEY.strip()
    configured_api_key = str(settings.get("stex_api_key", "")).strip()
    return (env_api_key or configured_api_key,
            clean_base_url(settings.get("stex_base_url", CONFIG_STEX_BASE_URL)))

def get_api_urls(base_url):
    base = str(base_url).strip().rstrip('/')
    return {
        "getnum": f"{base}/getnum",
        "liveaccess": f"{base}/active-ranges",
        "otp": f"{base}/numsuccess/info"
    }

def get_api_headers(api_key):
    return {
        "mapikey": api_key,
        "api-key": api_key,
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }

# ==================== WELCOME & CONFIG ====================
WELCOME_MESSAGE = """✨ 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 TEST BOT🚀 ✨ 
━━━━━━━━━━━━━━━━━━━━━━
🚀 Enjoy Premium Quality Service 🚀"""

OTP_RATE = 0.20
REFERRAL_PRICE = 0
MIN_WITHDRAW = 50
MAX_WITHDRAW = 10000

SUPPORT_LINK = "https://t.me/DEM_Support_Chat"
DEVELOPER_LINK = "https://t.me/Davil_Raju"

request_queue = asyncio.Queue()
MAX_WORKERS = max(1, int(os.getenv("MAX_WORKERS", "20")))

client_async = httpx.AsyncClient(
    http2=True,
    timeout=httpx.Timeout(8.0, connect=2.0, read=5.0),
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
    trust_env=False,
)

active_numbers = {}
last_range = {}
CHECK_INTERVAL = 1.5
number_assignment_lock = asyncio.Lock()

# ==================== RANGES CACHE ====================
_ranges_cache = {"data": None, "updated_at": 0.0, "fetching": False}

def get_app_emoji_id(app_name):
    n = app_name.lower()
    SERVICE_EMOJI_MAP = [
        ("whatsapp business", "5336814486701514414"),
        ("whatsapp",          "5334759662677957452"),
        ("telegram",          "5337010556253543833"),
        ("facebook",          "5334807341109908955"),
        ("instagram",         "5334868205091459431"),
        ("amazon prime",      "6111801057061374810"),
        ("amazon",            "4995019580536524226"),
        ("imo",               "5337155807752524558"),
        ("apple",             "5334637951894722661"),
        ("google",            "5335010201005231986"),
        ("microsoft",         "5334880948259427772"),
        ("teams",             "5334590977837403844"),
        ("tiktok",            "5339213256001102461"),
        ("bkash",             "5348469219761626211"),
        ("bybit",             "5348372939479751825"),
        ("binance",           "5348212415077064131"),
        ("melbet",            "5337102391244263212"),
        ("snapchat",          "5359441366554255082"),
        ("uber",              "5298715455316303708"),
        ("paypal",            "5776103539872896061"),
        ("discord",           "5116246243646898866"),
        ("viber",             "5463060437572528782"),
        ("linkedin",          "6224222994265279792"),
        ("line",              "5399818044866327279"),
        ("wechat",            "5782757599560602950"),
        ("twitter",           "5215726959056662534"),
        ("reddit",            "4992421103847604984"),
        ("pinterest",         "5346103513120258857"),
        ("twitch",            "5233333563306301418"),
        ("zoom",              "5881799193219043268"),
        ("signal",            "5293998404404272267"),
        ("slack",             "4994972469040251302"),
        ("skype",             "4992613535562334989"),
        ("netflix",           "6255738712664050133"),
        ("spotify",           "5411392711146095115"),
        ("hoichoi",           "6104822598493801746"),
        ("daraz",             "5336879280578138635"),
        ("foodpanda",         "5336879280578138635"),
        ("pathao",            "5336879280578138635"),
        ("aliexpress",        "5336879280578138635"),
        ("shopee",            "5336879280578138635"),
        ("payoneer",          "5336879280578138635"),
        ("wise",              "5336879280578138635"),
        ("chatgpt",           "5296516998996445955"),
        ("notion",            "5336879280578138635"),
        ("github",            "5417836094098007862"),
        ("canva",             "5111661409008092227"),
        ("figma",             "5336879280578138635"),
        ("upwork",            "5336879280578138635"),
        ("fiverr",            "5336879280578138635"),
        ("yahoo",             "5336879280578138635"),
        ("dropbox",           "5336879280578138635"),
        ("coursera",          "5336879280578138635"),
        ("duolingo",          "5336879280578138635"),
        ("rocket",            "5346042941196507141"),
    ]
    for k, v in SERVICE_EMOJI_MAP:
        if k in n:
            return v
    return "5861680977994060034"

def get_platform_icon(platform_name):
    return f'<tg-emoji emoji-id="{get_app_emoji_id(platform_name)}">📞</tg-emoji>'

def get_clean_app_name(raw):
    n = raw.lower().strip()
    for k, v in [("facebook","Facebook"),("instagram","Instagram"),("whatsapp","WhatsApp"),
                  ("tiktok","TikTok"),("paypal","PayPal"),("telegram","Telegram"),
                  ("discord","Discord"),("imo","Imo")]:
        if k in n: return v
    return raw.strip().capitalize()

def make_bold_text(text):
    out = []
    for ch in str(text):
        o = ord(ch)
        if 65 <= o <= 90:    out.append(chr(o - 65 + 0x1D5D4))
        elif 97 <= o <= 122: out.append(chr(o - 97 + 0x1D5EE))
        elif 48 <= o <= 57:  out.append(chr(o - 48 + 0x1D7EC))
        else: out.append(ch)
    return "".join(out)

async def fetch_top55_ranges_by_app():
    settings = load_settings()
    api_key, base_url = get_api_credentials()
    allowed = {s.lower() for s in settings.get("allowed_services",
        ["Instagram","Facebook","WhatsApp","TikTok","Telegram","Discord","PayPal","Imo"])}
    urls = get_api_urls(base_url)
    headers = get_api_headers(api_key)
    ranges_list = None
    for attempt in range(2):
        try:
            r = await client_async.get(urls["liveaccess"], headers=headers,
                                        timeout=httpx.Timeout(5.0, connect=1.5))
            data = r.json()
            ranges_list = extract_active_ranges(data)
            if ranges_list is not None: break
        except Exception:
            if attempt == 0: await asyncio.sleep(0.2)
    if ranges_list is None: return None, "Server unreachable or invalid API key."
    if not ranges_list:     return {}, None
    top = {}
    for obj in ranges_list:
        if isinstance(obj, str):
            rng = obj.strip()
            service = "Unknown"
        elif isinstance(obj, dict):
            rng = (
                obj.get("range") or obj.get("prefix") or
                obj.get("range_text") or obj.get("value") or ""
            )
            service = (
                obj.get("service") or obj.get("app") or
                obj.get("application") or obj.get("service_name") or "Unknown"
            )
        else:
            continue

        rng = str(rng).strip().upper()
        if not rng or not re.search(r"\d", rng):
            continue
        clean = get_clean_app_name(str(service))
        if clean.lower() not in allowed and clean != "Unknown":
            continue
        if clean not in top:
            top[clean] = {"icon": get_platform_icon(clean), "ranges": []}
        if rng not in top[clean]["ranges"]:
            top[clean]["ranges"].append(rng)
    return dict(sorted(top.items(), key=lambda x: len(x[1]["ranges"]), reverse=True)), None

def extract_active_ranges(payload):
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return None

    for key in (
        "active_ranges", "activeRanges", "available_ranges",
        "availableRanges", "ranges", "range_list", "data"
    ):
        value = payload.get(key)
        if isinstance(value, list):
            return value

    for key in ("data", "result", "response", "payload"):
        value = payload.get(key)
        if isinstance(value, (dict, list)):
            nested = extract_active_ranges(value)
            if nested is not None:
                return nested

    grouped = []
    for service, values in payload.items():
        if not isinstance(values, list):
            continue
        for value in values:
            if isinstance(value, dict):
                item = dict(value)
                item.setdefault("service", service)
            else:
                item = {"service": service, "range": value}
            grouped.append(item)
    return grouped if grouped else None

def build_app_buttons_from_cache(top):
    btns, row, ci = [], [], 0
    clrs = ["primary"]
    for app_name in top:
        row.append(InlineKeyboardButton(make_bold_text(app_name),
            callback_data=f"sel_app_{app_name}",
            api_kwargs={"icon_custom_emoji_id": get_app_emoji_id(app_name), "style": clrs[ci % len(clrs)]}))
        ci += 1
        if len(row) == 2: btns.append(row); row = []
    if row: btns.append(row)
    return btns

async def _bg_refresh_ranges():
    global _ranges_cache
    while True:
        try:
            if not _ranges_cache["fetching"]:
                _ranges_cache["fetching"] = True
                try:
                    data, _ = await fetch_top55_ranges_by_app()
                    if data:
                        _ranges_cache["data"] = data
                        _ranges_cache["updated_at"] = time.monotonic()
                except Exception: pass
                finally: _ranges_cache["fetching"] = False
        except Exception: pass
        await asyncio.sleep(200)

# ==================== ADMIN CHECKS ====================
def is_admin(user_id):
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return False
    return user_id in get_admin_ids()

def get_admin_ids():
    candidates = [ADMIN_ID, CONFIG_ADMIN_ID]
    try:
        configured = load_settings().get("admins", [])
        if isinstance(configured, list):
            candidates.extend(configured)
    except Exception as exc:
        print(f"Admin settings error: {exc}")

    admin_ids = []
    for candidate in candidates:
        try:
            admin_id = int(candidate)
        except (TypeError, ValueError):
            continue
        if admin_id > 0 and admin_id not in admin_ids:
            admin_ids.append(admin_id)
    return admin_ids

def get_min_withdraw():
    try:
        return max(0.0, float(load_settings().get("min_withdraw", MIN_WITHDRAW)))
    except (TypeError, ValueError):
        return float(MIN_WITHDRAW)

# ==================== WITHDRAW DATA ====================
def load_withdraw_requests():
    if not os.path.exists(WITHDRAW_DATA_FILE):
        with open(WITHDRAW_DATA_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(WITHDRAW_DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_withdraw_requests(data):
    with open(WITHDRAW_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_payment_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

# ==================== BANNED USERS ====================
def load_banned_users():
    if not os.path.exists(BANNED_USERS_FILE):
        with open(BANNED_USERS_FILE, "w") as f:
            json.dump([], f)
        return []
    try:
        with open(BANNED_USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_banned_users(banned_list):
    with open(BANNED_USERS_FILE, "w") as f:
        json.dump(banned_list, f, indent=4)

def is_user_banned(uid):
    banned_list = load_banned_users()
    return str(uid) in banned_list

def ban_user(uid):
    banned_list = load_banned_users()
    uid_str = str(uid)
    if uid_str not in banned_list:
        banned_list.append(uid_str)
        save_banned_users(banned_list)
        return True
    return False

def unban_user(uid):
    banned_list = load_banned_users()
    uid_str = str(uid)
    if uid_str in banned_list:
        banned_list.remove(uid_str)
        save_banned_users(banned_list)
        return True
    return False

# ==================== REFERRAL DATA ====================
def load_referral_data():
    if not os.path.exists(REFERRAL_DATA_FILE):
        with open(REFERRAL_DATA_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(REFERRAL_DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_referral_data(data):
    with open(REFERRAL_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def update_referral_count(uid, count):
    referral_data = load_referral_data()
    uid_str = str(uid)
    if uid_str not in referral_data:
        referral_data[uid_str] = {"referral_count": 0}
    referral_data[uid_str]["referral_count"] = count
    save_referral_data(referral_data)

def get_referral_count(uid):
    referral_data = load_referral_data()
    uid_str = str(uid)
    return referral_data.get(uid_str, {}).get("referral_count", 0)

# ==================== DATA RANGE FILE ====================
def load_range_db():
    if not os.path.exists(DATA_RANGE_FILE):
        return {}
    try:
        with open(DATA_RANGE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_range_db(data):
    with open(DATA_RANGE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def save_number_range_info(uid, number, range_text):
    db = load_range_db()
    flag, name = get_country_info(number)
    db[normalize_number(number)] = {
        "user_id": str(uid),
        "number": f"+{normalize_number(number)}",
        "range": range_text,
        "country": f"{flag} {name}"
    }
    save_range_db(db)

# ==================== COUNTRY MAPPING ====================
def get_country_info(number):
    number = str(number).strip()
    country_map = {
        "2376": ("🇨🇲", "Cameroon"), "2250": ("🇨🇮", "Ivory Coast"), "2613": ("🇲🇬", "Madagascar"),
        "4077": ("🇷🇴", "Romania"), "237": ("🇨🇲", "Cameroon"), "225": ("🇨🇮", "Ivory Coast"),
        "261": ("🇲🇬", "Madagascar"), "20": ("🇪🇬", "Egypt"), "27": ("🇿🇦", "South Africa"),
        "234": ("🇳🇬", "Nigeria"), "254": ("🇰🇪", "Kenya"), "233": ("🇬🇭", "Ghana"),
        "212": ("🇲🇦", "Morocco"), "213": ("🇩🇿", "Algeria"), "216": ("🇹🇳", "Tunisia"),
        "218": ("🇱🇾", "Libya"), "249": ("🇸🇩", "Sudan"), "251": ("🇪🇹", "Ethiopia"),
        "252": ("🇸🇴", "Somalia"), "253": ("🇩🇯", "Djibouti"), "255": ("🇹🇿", "Tanzania"),
        "256": ("🇺🇬", "Uganda"), "257": ("🇧🇮", "Burundi"), "258": ("🇲🇿", "Mozambique"),
        "260": ("🇿🇲", "Zambia"), "263": ("🇿🇼", "Zimbabwe"), "264": ("🇳🇦", "Namibia"),
        "265": ("🇲🇼", "Malawi"), "266": ("🇱🇸", "Lesotho"), "267": ("🇧🇼", "Botswana"),
        "268": ("🇸🇿", "Swaziland"), "269": ("🇰🇲", "Comoros"), "220": ("🇬🇲", "Gambia"),
        "221": ("🇸🇳", "Senegal"), "222": ("🇲🇷", "Mauritania"), "223": ("🇲🇱", "Mali"),
        "224": ("🇬🇳", "Guinea"), "226": ("🇧🇫", "Burkina Faso"), "227": ("🇳🇪", "Niger"),
        "228": ("🇹🇬", "Togo"), "229": ("🇧🇯", "Benin"), "230": ("🇲🇺", "Mauritius"),
        "231": ("🇱🇷", "Liberia"), "232": ("🇸🇱", "Sierra Leone"), "235": ("🇹🇩", "Chad"),
        "236": ("🇨🇫", "Central African Republic"), "238": ("🇨🇻", "Cape Verde"), "239": ("🇸🇹", "Sao Tome and Principe"),
        "240": ("🇬🇶", "Equatorial Guinea"), "241": ("🇬🇦", "Gabon"), "242": ("🇨🇬", "Congo"),
        "243": ("🇨🇩", "DR Congo"), "244": ("🇦🇴", "Angola"), "245": ("🇬🇼", "Guinea-Bissau"),
        "247": ("🇸🇭", "Saint Helena"), "248": ("🇸🇨", "Seychelles"), "250": ("🇷🇼", "Rwanda"),
        "290": ("🇸🇭", "Saint Helena"), "291": ("🇪🇷", "Eritrea"), "40": ("🇷🇴", "Romania"),
        "44": ("🇬🇧", "United Kingdom"), "33": ("🇫🇷", "France"), "49": ("🇩🇪", "Germany"),
        "39": ("🇮🇹", "Italy"), "34": ("🇪🇸", "Spain"), "31": ("🇳🇱", "Netherlands"),
        "32": ("🇧🇪", "Belgium"), "41": ("🇨🇭", "Switzerland"), "43": ("🇦🇹", "Austria"),
        "46": ("🇸🇪", "Sweden"), "47": ("🇳🇴", "Norway"), "45": ("🇩🇰", "Denmark"),
        "358": ("🇫🇮", "Finland"), "351": ("🇵🇹", "Portugal"), "353": ("🇮🇪", "Ireland"),
        "36": ("🇭🇺", "Hungary"), "48": ("🇵🇱", "Poland"), "380": ("🇺🇦", "Ukraine"),
        "370": ("🇱🇹", "Lithuania"), "371": ("🇱🇻", "Latvia"), "372": ("🇪🇪", "Estonia"),
        "373": ("🇲🇩", "Moldova"), "374": ("🇦🇲", "Armenia"), "375": ("🇧🇾", "Belarus"),
        "376": ("🇦🇩", "Andorra"), "377": ("🇲🇨", "Monaco"), "381": ("🇷🇸", "Serbia"),
        "382": ("🇲🇪", "Montenegro"), "385": ("🇭🇷", "Croatia"), "386": ("🇸🇮", "Slovenia"),
        "387": ("🇧🇦", "Bosnia and Herzegovina"), "389": ("🇲🇰", "North Macedonia"), "350": ("🇬🇮", "Gibraltar"),
        "352": ("🇱🇺", "Luxembourg"), "354": ("🇮🇸", "Iceland"), "355": ("🇦🇱", "Albania"),
        "356": ("🇲🇹", "Malta"), "357": ("🇨🇾", "Cyprus"), "359": ("🇧🇬", "Bulgaria"),
        "421": ("🇸🇰", "Slovakia"), "420": ("🇨🇿", "Czech Republic"), "298": ("🇫🇴", "Faroe Islands"),
        "299": ("🇬🇱", "Greenland"), "1": ("🇺🇸", "United States"), "7": ("🇷🇺", "Russia"),
        "91": ("🇮🇳", "India"), "92": ("🇵🇰", "Pakistan"), "880": ("🇧🇩", "Bangladesh"),
        "86": ("🇨🇳", "China"), "81": ("🇯🇵", "Japan"), "82": ("🇰🇷", "South Korea"),
        "84": ("🇻🇳", "Vietnam"), "66": ("🇹🇭", "Thailand"), "62": ("🇮🇩", "Indonesia"),
        "60": ("🇲🇾", "Malaysia"), "65": ("🇸🇬", "Singapore"), "63": ("🇵🇭", "Philippines"),
        "95": ("🇲🇲", "Myanmar"), "94": ("🇱🇰", "Sri Lanka"), "977": ("🇳🇵", "Nepal"),
        "93": ("🇦🇫", "Afghanistan"), "98": ("🇮🇷", "Iran"), "90": ("🇹🇷", "Turkey"),
        "964": ("🇮🇶", "Iraq"), "963": ("🇸🇾", "Syria"), "961": ("🇱🇧", "Lebanon"),
        "962": ("🇯🇴", "Jordan"), "965": ("🇰🇼", "Kuwait"), "966": ("🇸🇦", "Saudi Arabia"),
        "967": ("🇾🇲", "Yemen"), "968": ("🇴🇲", "Oman"), "971": ("🇦🇪", "United Arab Emirates"),
        "972": ("🇮🇱", "Israel"), "973": ("🇧🇭", "Bahrain"), "974": ("🇶🇦", "Qatar"),
        "994": ("🇦🇿", "Azerbaijan"), "995": ("🇬🇪", "Georgia"), "996": ("🇰🇬", "Kyrgyzstan"),
        "992": ("🇹🇯", "Tajikistan"), "993": ("🇹🇲", "Turkmenistan"), "998": ("🇺🇿", "Uzbekistan"),
        "855": ("🇰🇭", "Cambodia"), "856": ("🇱🇦", "Laos"), "976": ("🇲🇳", "Mongolia"),
        "850": ("🇰🇵", "North Korea"), "55": ("🇧🇷", "Brazil"), "52": ("🇲🇽", "Mexico"),
        "54": ("🇦🇷", "Argentina"), "57": ("🇨🇴", "Colombia"), "51": ("🇵🇪", "Peru"),
        "58": ("🇻🇪", "Venezuela"), "56": ("🇨🇱", "Chile"), "593": ("🇪🇨", "Ecuador"),
        "591": ("🇧🇴", "Bolivia"), "595": ("🇵🇾", "Paraguay"), "598": ("🇺🇾", "Uruguay"),
        "502": ("🇬🇹", "Guatemala"), "503": ("🇸🇻", "El Salvador"), "504": ("🇭🇳", "Honduras"),
        "506": ("🇨🇷", "Costa Rica"), "507": ("🇵🇦", "Panama"), "509": ("🇭🇹", "Haiti"),
        "501": ("🇧🇿", "Belize"), "61": ("🇦🇺", "Australia"), "64": ("🇳🇿", "New Zealand"),
        "675": ("🇵🇬", "Papua New Guinea"), "679": ("🇫🇯", "Fiji"), "1246": ("🇧🇧", "Barbados"),
        "1876": ("🇯🇲", "Jamaica"), "53": ("🇨🇺", "Cuba"), "592": ("🇬🇾", "Guyana"),
    }

    clean_num = str(number).replace('+', '').replace(' ', '').replace('-', '').strip()
    sorted_prefixes = sorted(country_map.keys(), key=len, reverse=True)

    for prefix in sorted_prefixes:
        if clean_num.startswith(prefix):
            return country_map[prefix]

    return ("🌍", "Unknown")

# ==================== SERVICE DETECTION ====================
def detect_service(full_sms):
    if not full_sms:
        return "SMS SERVICE"

    sms_lower = full_sms.lower()
    service_keywords = {
        "facebook": "FACEBOOK", "fb": "FACEBOOK",
        "instagram": "INSTAGRAM", "insta": "INSTAGRAM",
        "tiktok": "TIKTOK",
        "twitter": "TWITTER", "x.com": "TWITTER",
        "snapchat": "SNAPCHAT", "snap": "SNAPCHAT",
        "whatsapp": "WHATSAPP",
        "telegram": "TELEGRAM",
        "discord": "DISCORD",
        "messenger": "MESSENGER",
        "linkedin": "LINKEDIN",
        "google": "GOOGLE", "gmail": "GOOGLE",
        "amazon": "AMAZON",
        "microsoft": "MICROSOFT", "outlook": "MICROSOFT",
        "yahoo": "YAHOO",
        "paypal": "PAYPAL",
        "binance": "BINANCE",
        "coinbase": "COINBASE",
        "spotify": "SPOTIFY",
        "netflix": "NETFLIX",
        "uber": "UBER",
        "apple": "APPLE", "icloud": "APPLE",
        "bkash": "BKASH",
        "nagad": "NAGAD",
        "stripe": "STRIPE",
        "line": "LINE",
        "wechat": "WECHAT",
        "viber": "VIBER",
        "signal": "SIGNAL",
        "pubg": "PUBG",
        "free fire": "FREE FIRE",
    }

    for keyword, service_name in sorted(service_keywords.items(), key=lambda x: len(x[0]), reverse=True):
        if keyword in sms_lower:
            return service_name

    return "SMS SERVICE"

# ==================== KEYBOARDS ====================
def make_reply_btn(text, emoji_id=None, style=None):
    api_kwargs = {}
    if emoji_id:
        api_kwargs['icon_custom_emoji_id'] = str(emoji_id)
    if style:
        api_kwargs['style'] = style
    return KeyboardButton(text=text, api_kwargs=api_kwargs if api_kwargs else None)

def main_keyboard(user_id):
    keyboard = [
        [
            make_reply_btn("GET NUMBER",     emoji_id="5228843986747147814", style="primary"),
            make_reply_btn("GET 2FA",        emoji_id="5296369303661067030", style="primary")
        ],
        [
            make_reply_btn("PROFILE",        emoji_id="5422444280473998663", style="primary"),
            make_reply_btn("LEADERBOARD",    emoji_id="5228875876879318811", style="primary")
        ],
        [
            make_reply_btn("SUPPORT",        emoji_id="5267294466716244344", style="primary")
        ],
    ]

    if is_admin(user_id):
        keyboard.append([
            make_reply_btn("ADMIN PANEL", emoji_id="5350396951407895212", style="primary")
        ])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def account_keyboard():
    keyboard = [
        [
            make_reply_btn("BALANCE",        emoji_id="6233367447789899509", style="primary"),
            make_reply_btn("REFER AND EARN", emoji_id="5420396762189831222", style="primary")
        ],
        [
            make_reply_btn("VIEW PROFILE",   emoji_id="5422444280473998663", style="primary"),
            make_reply_btn("BACK TO MAIN",  emoji_id="5267490665117275176", style="primary")
        ],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def cancel_keyboard():
    keyboard = [[make_reply_btn("CANCEL", emoji_id="5420130255174145507", style="primary")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_main_keyboard():
    keyboard = [
        [make_reply_btn("USER MANAGEMENT",      emoji_id="5193063022226086560", style="primary"),
         make_reply_btn("SYSTEM CONFIGURATION", emoji_id="5341715473882955310", style="primary")],
        [make_reply_btn("BOT SETTINGS",         emoji_id="5282843764451195532", style="primary"),
         make_reply_btn("SERVICE MANAGEMENT",   emoji_id="5375338737028841420", style="primary")],
        [make_reply_btn("WITHDRAWAL MANAGEMENT", emoji_id="6233367447789899509", style="primary"),
         make_reply_btn("SUPPORT CHAT",           emoji_id="5267294466716244344", style="primary")],
        [make_reply_btn("⏳ PENDING WITHDRAWALS", emoji_id="6217721388736712699", style="primary")],
        [make_reply_btn("BACK TO MAIN",         emoji_id="5267490665117275176", style="primary")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def user_management_keyboard():
    keyboard = [
        [make_reply_btn("SEND MESSAGE TO ALL USERS", emoji_id="5251671733630431622", style="primary"),
         make_reply_btn("ALL USER ID",               emoji_id="5352861489541714456", style="primary")],
        [make_reply_btn("BAN USER LIST",             emoji_id="5420323339723881652", style="primary"),
         make_reply_btn("ALL USER BALANCE",          emoji_id="6233367447789899509", style="primary")],
        [make_reply_btn("BACK TO ADMIN",             emoji_id="5267490665117275176", style="primary")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def system_config_keyboard():
    keyboard = [
        [make_reply_btn("TODAY ALL STATUS",  emoji_id="5231200819986047254", style="primary"),
         make_reply_btn("USER STATUS CHECK", emoji_id="5352861489541714456", style="primary")],
        [make_reply_btn("BAN USER",          emoji_id="5420323339723881652", style="primary"),
         make_reply_btn("UNBAN USER",        emoji_id="5875017993909440887", style="primary")],
        [make_reply_btn("BAN USER LIST",     emoji_id="5956074558044770726", style="primary"),
         make_reply_btn("REMOVE BALANCE",    emoji_id="5244837092042750681", style="primary")],
        [make_reply_btn("ADD BALANCE",       emoji_id="5397916757333654639", style="primary"),
         make_reply_btn("BACK TO ADMIN",     emoji_id="5267490665117275176", style="primary")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def bot_settings_keyboard():
    keyboard = [
        [make_reply_btn("ADD ADMIN",          emoji_id="5397916757333654639", style="primary"),
         make_reply_btn("REMOVE ADMIN",       emoji_id="5244837092042750681", style="primary")],
        [make_reply_btn("SET OTP GROUP LINK", emoji_id="5253742260054409879", style="primary"),
         make_reply_btn("SET FORCE CHANNEL",  emoji_id="5282843764451195532", style="primary")],
        [make_reply_btn("SET OTP CHAT ID",    emoji_id="5231200819986047254", style="primary"),
         make_reply_btn("STEX CONFIG",        emoji_id="5350396951407895212", style="primary")],
        [make_reply_btn("BACK TO ADMIN",      emoji_id="5267490665117275176", style="primary")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def stex_config_keyboard():
    keyboard = [
        [make_reply_btn("SET API KEY",          emoji_id="5397916757333654639", style="primary"),
         make_reply_btn("SET BASE URL",         emoji_id="5253742260054409879", style="primary")],
        [make_reply_btn("SET ALLOWED SERVICES", emoji_id="5341715473882955310", style="primary"),
         make_reply_btn("VIEW STEX CONFIG",     emoji_id="5231200819986047254", style="primary")],
        [make_reply_btn("BACK TO BOT SETTINGS", emoji_id="5267490665117275176", style="primary")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def service_management_keyboard():
    keyboard = [
        [make_reply_btn("ADD SERVICE",    emoji_id="5397916757333654639", style="primary"),
         make_reply_btn("REMOVE SERVICE", emoji_id="5244837092042750681", style="primary")],
        [make_reply_btn("LIST SERVICES",  emoji_id="5352861489541714456", style="primary"),
         make_reply_btn("BACK TO ADMIN",  emoji_id="5267490665117275176", style="primary")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def withdrawal_management_keyboard():
    keyboard = [
        [
            make_reply_btn("PENDING WITHDRAWALS", emoji_id="6217721388736712699", style="primary"),
            make_reply_btn("SET MINIMUM WITHDRAW", emoji_id="5397916757333654639", style="primary"),
        ],
        [
            make_reply_btn("BACK TO ADMIN", emoji_id="5267490665117275176", style="primary"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def withdraw_method_keyboard():
    return ReplyKeyboardMarkup([
        [make_reply_btn("BKASH",  emoji_id="5348469219761626211", style="primary"),
         make_reply_btn("NAGAD",  emoji_id="5352985330628730418", style="primary")],
        [make_reply_btn("ROCKET", emoji_id="5346042941196507141", style="primary"),
         make_reply_btn("BINANCE",emoji_id="5348212415077064131", style="primary")],
        [make_reply_btn("CANCEL", emoji_id="5420130255174145507", style="primary")]
    ], resize_keyboard=True)

# ==================== HELPERS ====================
def format_balance(balance):
    return f"{balance:.2f}"

def extract_otp(text):
    if not text or text == "No Content":
        return "N/A"
    spaced_otp = re.search(r'\b(\d{3}\s\d{3})\b', text)
    if spaced_otp:
        return spaced_otp.group(1).replace(" ", "")
    match = re.search(r'\b(\d{4,8})\b', text)
    return match.group(1) if match else "N/A"

def normalize_number(num):
    return re.sub(r'\D', '', str(num))

def mask_number(num):
    if len(num) > 6:
        return f"{num[:4]}****{num[-6:]}"
    return num

def get_date_reset_time():
    now = datetime.now()
    return datetime(now.year, now.month, now.day, 0, 0, 0)

def is_valid_bangladesh_number(number):
    number = re.sub(r'\D', '', str(number))
    return len(number) == 11 and number.startswith('01')

def is_range_request(param):
    return 'X' in param.upper()

def is_referral_request(param):
    return param.isdigit()

# ==================== DATABASE ====================
def load_data(filename=USER_DATA_FILE):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data, filename=USER_DATA_FILE):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def get_user(uid):
    uid = str(uid)
    data = load_data()
    if uid not in data:
        data[uid] = {"user_id": uid, "balance": 0.0, "total_numbers": 0, "referral_count": 0}
        save_data(data)
    return data[uid]

async def update_db_balance(uid, amount):
    uid = str(uid)
    data = load_data()
    if uid in data:
        data[uid]["balance"] = round(data[uid].get("balance", 0.0) + amount, 2)
        save_data(data)
        return data[uid]["balance"]
    return 0.0

def get_all_users():
    data = load_data(USER_DATA_FILE)
    return list(data.keys()) if data else []

def user_exists(uid):
    data = load_data(USER_DATA_FILE)
    return str(uid) in data

# ==================== STATS ====================
def load_stats():
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)

def add_number_taken(uid, count=1):
    uid = str(uid)
    stats = load_stats()
    if uid not in stats:
        stats[uid] = {"numbers_taken": [], "otps_received": []}
    now = datetime.now().isoformat()
    for _ in range(count):
        stats[uid]["numbers_taken"].append(now)
    log_global_activity(uid, "NUMBER_TAKEN", {"count": count})
    save_stats(stats)

def add_otp_received(uid):
    uid = str(uid)
    stats = load_stats()
    if uid not in stats:
        stats[uid] = {"numbers_taken": [], "otps_received": []}
    stats[uid]["otps_received"].append(datetime.now().isoformat())
    save_stats(stats)

def get_user_stats(uid):
    uid = str(uid)
    stats = load_stats()
    user_stats = stats.get(uid, {"numbers_taken": [], "otps_received": []})

    now = datetime.now()
    today_midnight = get_date_reset_time()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)

    numbers_taken = user_stats.get("numbers_taken", [])
    otps_received = user_stats.get("otps_received", [])

    return {
        "total_numbers": len(numbers_taken),
        "total_otps": len(otps_received),
        "today_numbers": sum(1 for t in numbers_taken if datetime.fromisoformat(t) >= today_midnight),
        "today_otps": sum(1 for t in otps_received if datetime.fromisoformat(t) >= today_midnight),
        "last24h_numbers": sum(1 for t in numbers_taken if datetime.fromisoformat(t) > last_24h),
        "last24h_otps": sum(1 for t in otps_received if datetime.fromisoformat(t) > last_24h),
        "last7d_numbers": sum(1 for t in numbers_taken if datetime.fromisoformat(t) > last_7d),
        "last7d_otps": sum(1 for t in otps_received if datetime.fromisoformat(t) > last_7d)
    }

def log_global_activity(uid, action, details):
    if not os.path.exists(ACTIVITY_LOGS_FILE):
        with open(ACTIVITY_LOGS_FILE, "w") as f:
            json.dump([], f)
    try:
        with open(ACTIVITY_LOGS_FILE, "r") as f:
            logs = json.load(f)
    except:
        logs = []
    now = datetime.now()
    logs.append({
        "uid": str(uid), "action": action, "details": details,
        "timestamp": now.isoformat(),
        "date": now.strftime("%d/%m/%Y"),
        "time": now.strftime("%H:%M:%S")
    })
    with open(ACTIVITY_LOGS_FILE, "w") as f:
        json.dump(logs, f, indent=4)

def get_global_system_stats():
    stats = load_stats()
    now = datetime.now()
    today_midnight = datetime(now.year, now.month, now.day)
    last_7d = now - timedelta(days=7)
    total_n = total_o = today_n = today_o = seven_n = seven_o = 0
    for uid in stats:
        u = stats[uid]
        n_list = u.get("numbers_taken", [])
        o_list = u.get("otps_received", [])
        total_n += len(n_list)
        total_o += len(o_list)
        for t in n_list:
            dt = datetime.fromisoformat(t)
            if dt >= today_midnight: today_n += 1
            if dt >= last_7d: seven_n += 1
        for t in o_list:
            dt = datetime.fromisoformat(t)
            if dt >= today_midnight: today_o += 1
            if dt >= last_7d: seven_o += 1
    return today_n, today_o, seven_n, seven_o, total_n, total_o

# ==================== LEADERBOARD ====================
async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return

    stats_data = load_stats()
    today_midnight = get_date_reset_time()
    user_data_all = load_data(USER_DATA_FILE)

    user_today_counts = []
    for uid_str, user_stats in stats_data.items():
        otps_received = user_stats.get("otps_received", [])
        today_count = 0
        for ts in otps_received:
            try:
                if datetime.fromisoformat(ts) >= today_midnight:
                    today_count += 1
            except:
                continue
        if today_count > 0:
            name = user_data_all.get(uid_str, {}).get("full_name") or user_data_all.get(uid_str, {}).get("username") or f"User {uid_str}"
            user_today_counts.append((uid_str, today_count, html.escape(name)))

    user_today_counts.sort(key=lambda x: x[1], reverse=True)
    top10 = user_today_counts[:10]

    if not top10:
        msg = "<b>🏆 TOP 10 OTP LEADERBOARD 🏆</b>\n━━━━━━━━━━━━━━━━━━━━\n\n❌ আজ পর্যন্ত কেউ OTP পায়নি。\n"
    else:
        msg = "<b>🏆 TOP 10 OTP RECEIVERS (TODAY) 🏆</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
        for idx, (uid_str, count, name) in enumerate(top10, 1):
            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}️⃣"
            msg += f"{medal} <b>{name}</b>\n   🔑 <code>{count}</code> OTPs\n\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n📊 <i>প্রতিদিন রাত ১২টায় রিসেট হয়</i>"

    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=main_keyboard(uid))

# ==================== 2FA GENERATOR ====================
def generate_2fa_code(secret_key):
    try:
        clean_secret = secret_key.replace(" ", "").upper().strip()
        key = base64.b32decode(clean_secret, casefold=True)
        t = int(time.time()) // 30
        msg_bytes = struct.pack(">Q", t)
        h = hmac.new(key, msg_bytes, hashlib.sha1).digest()
        o = h[-1] & 0xf
        code = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1_000_000
        return f"{code:06d}", clean_secret
    except:
        return None, None

async def get_2fa_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return
    context.user_data["mode"] = "get_2fa"
    await update.message.reply_text(
        "⚡ <b>GET 2FA CODE</b> ⚡\n\n<blockquote>🔑 ENTER YOUR 2FA SECRET KEY:</blockquote>",
        parse_mode="HTML"
    )

async def process_2fa_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    secret_key = update.message.text.strip()
    context.user_data["mode"] = None

    otp_code, clean_key = generate_2fa_code(secret_key)
    if otp_code is None:
        await update.message.reply_text(
            "❌ <b>INVALID 2FA SECRET KEY</b>\n\n⚠️ Please send a valid base32 key.",
            parse_mode="HTML",
            reply_markup=main_keyboard(uid)
        )
        return

    now = datetime.now()
    final_msg = (
        "✅ <b>2FA CODE GENERATED!</b>\n\n"
        f"<blockquote>🔑 KEY: <code>{clean_key}</code></blockquote>\n"
        f"<blockquote>🔢 CODE: <code>{otp_code}</code></blockquote>\n"
        f"<blockquote>⏳ EXPIRES IN: 30 SECONDS</blockquote>\n"
        f"📅 {now.strftime('%d %B, %Y')} | {now.strftime('%I:%M %p')}"
    )
    await update.message.reply_text(final_msg, parse_mode="HTML")

# ==================== NUMBER & SERVICE SELECTION ====================
def build_manual_service_buttons():
    s = load_settings()
    manual = s.get("manual_services", [])
    btns = []
    clrs = ["primary"]
    for i, svc in enumerate(manual):
        btns.append(InlineKeyboardButton(
            make_bold_text(svc['name']),
            callback_data=f"manual_svc_{i}",
            api_kwargs={"icon_custom_emoji_id": get_app_emoji_id(svc['name']), "style": clrs[i % len(clrs)]}
        ))
    return [btns[j:j+2] for j in range(0, len(btns), 2)]

async def show_app_selection(update, context):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return
    context.user_data.pop("top_ranges_by_app", None)

    async def _build_full_keyboard(top):
        stex_rows = build_app_buttons_from_cache(top)
        manual_rows = build_manual_service_buttons()
        all_rows = stex_rows + manual_rows
        all_rows.append([InlineKeyboardButton("⚙️ CUSTOM RANGE", callback_data="custom_range", api_kwargs={"style": "primary"})])
        return all_rows

    cache_age = time.monotonic() - _ranges_cache["updated_at"]
    if _ranges_cache["data"] and cache_age < 300:
        top = _ranges_cache["data"]
        context.user_data["top_ranges_by_app"] = top
        msg = f'{get_tg_emoji("get_number_btn")} <b>SELECT APP TO GET NUMBER</b>\n━━━━━━━━━━━━━━━━━━━━━'
        kb = await _build_full_keyboard(top)
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))
        return

    status = await update.message.reply_text(f'{get_tg_emoji("loading")} <b>Loading ranges...</b>', parse_mode="HTML")
    top, err = await fetch_top55_ranges_by_app()
    if err or not top:
        top, err = await fetch_top55_ranges_by_app()

    if err or not top:
        manual_rows = build_manual_service_buttons()
        if manual_rows:
            manual_rows.append([InlineKeyboardButton("⚙️ CUSTOM RANGE", callback_data="custom_range", api_kwargs={"style": "primary"})])
            await status.edit_text(
                f'{get_tg_emoji("get_number_btn")} <b>SELECT APP TO GET NUMBER</b>\n━━━━━━━━━━━━━━━━━━━━━\n<blockquote>⚠️ Stex unavailable — showing manual services</blockquote>',
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(manual_rows))
        else:
            await status.edit_text(f'{get_tg_emoji("cross")} <b>Could not load ranges.</b>\n<blockquote>{err or "No active ranges"}</blockquote>', parse_mode="HTML")
        return

    _ranges_cache["data"] = top
    _ranges_cache["updated_at"] = time.monotonic()
    context.user_data["top_ranges_by_app"] = top
    msg = f'{get_tg_emoji("get_number_btn")} <b>SELECT APP TO GET NUMBER</b>\n━━━━━━━━━━━━━━━━━━━━━'
    kb = await _build_full_keyboard(top)
    await status.edit_text(msg, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))

# ==================== AUTO OTP MONITOR ====================
async def monitor_loop(app):
    while True:
        try:
            settings = load_settings()
            api_key, base_url = get_api_credentials()
            urls = get_api_urls(base_url)
            headers = get_api_headers(api_key)
            r = await client_async.get(urls["otp"], headers=headers)
            if r.status_code == 200:
                try: res = r.json()
                except Exception: res = None

                otps = []
                if isinstance(res, dict):
                    if "data" in res:
                        d = res["data"]
                        otps = d if isinstance(d, list) else (d.get("otps") or d.get("active") or [])
                    else:
                        otps = res.get("otps") or []
                elif isinstance(res, list):
                    otps = res

                if otps:
                    paid_data = load_data(PAID_SMS_FILE)
                    paid_keys_set = set(paid_data.keys())
                    processed_in_session = set()

                    for otp in otps:
                        num = normalize_number(otp.get("number") or otp.get("phone") or "")
                        full_sms = otp.get("otp") or otp.get("sms") or otp.get("message") or "No SMS Content"
                        otp_id = str(otp.get("nid") or otp.get("otp_id") or otp.get("id", ""))
                        otp_code = extract_otp(full_sms)
                        if not otp_code or otp_code == "N/A": continue
                        sms_key = otp_id if otp_id else f"{num}_{full_sms}"

                        if (num in active_numbers and sms_key not in paid_keys_set and sms_key not in processed_in_session):
                            details = active_numbers[num]
                            paid_keys_set.add(sms_key)
                            processed_in_session.add(sms_key)
                            paid_data[sms_key] = {"uid": details["uid"], "otp": otp_code}

                            otp_bonus = settings.get("otp_bonus", OTP_RATE)
                            await update_db_balance(details["uid"], otp_bonus)
                            add_otp_received(details["uid"])
                            log_global_activity(details["uid"], "OTP_RECEIVED", {"number": num, "otp": otp_code, "sms": full_sms})

                            country_flag, country_name = get_country_info(num)
                            clean_num = num.replace('+', '').strip()
                            flag_tg = get_country_tg_flag(country_flag)
                            purchased_app = details.get("app") or detect_service(full_sms)
                            app_em = get_platform_icon(purchased_app)

                            if HAS_COPY_BTN:
                                try:
                                    btn_copy = InlineKeyboardButton(
                                        text=otp_code,
                                        copy_text=CopyTextButton(text=otp_code),
                                        api_kwargs={"icon_custom_emoji_id": "5296369303661067030"})
                                except Exception:
                                    btn_copy = InlineKeyboardButton(otp_code, callback_data=f"copy_text_{otp_code}", api_kwargs={"icon_custom_emoji_id": "5296369303661067030"})
                            else:
                                btn_copy = InlineKeyboardButton(otp_code, callback_data=f"copy_text_{otp_code}", api_kwargs={"icon_custom_emoji_id": "5296369303661067030"})

                            panel_url = settings.get("panel_url", "https://stexsms.com")
                            channel_url = settings.get("channel_url", "https://t.me/MinoXofficial0")
                            masked = mask_number(clean_num)
                            user_msg  = f"{flag_tg} {app_em} +{clean_num}"
                            group_msg = f"{flag_tg} {app_em} +{masked}"
                            user_kb   = InlineKeyboardMarkup([[btn_copy]])
                            group_kb  = InlineKeyboardMarkup([
                                [btn_copy],
                                [InlineKeyboardButton(" NUMBER", url=panel_url, api_kwargs={"icon_custom_emoji_id": "4943094697238201446", "style": "primary"}),
                                 InlineKeyboardButton(" CHANNEL", url=channel_url, api_kwargs={"icon_custom_emoji_id": "6215074610845585917", "style": "primary"})]])

                            try: await app.bot.send_message(details["uid"], user_msg, parse_mode="HTML", reply_markup=user_kb)
                            except Exception: pass
                            try:
                                gid = settings.get("otp_group_chat_id") or OTP_GROUP_ID
                                await app.bot.send_message(gid, group_msg, parse_mode="HTML", reply_markup=group_kb)
                            except Exception: pass
                            save_data(paid_data, PAID_SMS_FILE)

            now = datetime.now()
            for nk in [k for k, v in list(active_numbers.items()) if isinstance(v, dict) and "timestamp" in v and (now - v["timestamp"]).total_seconds() > 3600]:
                del active_numbers[nk]
        except Exception:
            pass
        await asyncio.sleep(CHECK_INTERVAL)

# ==================== WORKER & API ====================
async def fetch_number_async(range_str):
    range_str = str(range_str or "").strip().upper()
    if not range_str:
        return None

    try:
        api_key, base_url = get_api_credentials()
        urls = get_api_urls(base_url)
        headers = get_api_headers(api_key)
        payload = {"range": range_str, "is_national": False, "remove_plus": False, "key": api_key}
        r = await client_async.post(urls["getnum"], json=payload, headers=headers, timeout=httpx.Timeout(8.0, connect=2.0, read=6.0))
        if not 200 <= r.status_code < 300:
            return None

        data = r.json()
        num, number_payload = extract_number_from_payload(data)
        if num:
            otp = extract_first_value(number_payload, ("otp", "otp_code", "code", "verification_code"))
            sms = extract_first_value(number_payload, ("sms", "message", "full_sms", "text"))
            return {"number": num, "otp_now": bool(otp), "otp": otp, "sms": sms}
    except Exception:
        return None
    return None

def extract_first_value(payload, keys):
    if isinstance(payload, dict):
        for key in keys:
            value = payload.get(key)
            if value not in (None, "") and isinstance(value, (str, int, float)):
                return value
        for value in payload.values():
            found = extract_first_value(value, keys)
            if found not in (None, ""):
                return found
    elif isinstance(payload, list):
        for value in payload:
            found = extract_first_value(value, keys)
            if found not in (None, ""):
                return found
    return None

def extract_number_from_payload(payload):
    number_keys = ("full_number", "no_plus_number", "phone_number", "phone", "mobile", "msisdn", "number", "copy")
    if isinstance(payload, dict):
        for key in number_keys:
            value = payload.get(key)
            if isinstance(value, (str, int, float)):
                normalized = normalize_number(value)
                if len(normalized) >= 7:
                    return value, payload
        for value in payload.values():
            number, owner = extract_number_from_payload(value)
            if number:
                return number, owner
    elif isinstance(payload, list):
        for value in payload:
            number, owner = extract_number_from_payload(value)
            if number:
                return number, owner
    return None, {}

async def register_active_number(uid, number, range_text, app_name=None):
    clean_num = normalize_number(number)
    if len(clean_num) < 7:
        return None

    async with number_assignment_lock:
        if clean_num in active_numbers:
            return None
        active_numbers[clean_num] = {
            "uid": uid,
            "range": str(range_text).strip().upper(),
            "app": app_name or "",
            "timestamp": datetime.now(),
        }
        save_number_range_info(uid, clean_num, range_text)
    return clean_num

async def fast_allocate_number(query, context, range_text, sid):
    uid = query.from_user.id
    if is_user_banned(uid):
        await query.message.edit_text("🚫 YOU ARE BANNED 🚫")
        return

    res = None
    clean_num = None
    for _ in range(3):
        res = await fetch_number_async(range_text)
        if not res or not res.get("number"):
            break
        clean_num = await register_active_number(uid, res["number"], range_text, sid)
        if clean_num:
            break

    if not res or not clean_num:
        await query.message.edit_text(
            "❌ <b>Number পাওয়া যায়নি।</b>\n\n"
            "<blockquote>⚠️ এই range-এ এখন number নেই বা server busy।\n"
            "আরেকটি range চেষ্টা করুন।</blockquote>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 BACK", callback_data="back_services", api_kwargs={"style": "primary"})
            ]])
        )
        return

    add_number_taken(uid, 1)
    last_range[uid] = range_text
    country_flag, country_name = get_country_info(clean_num)

    if res.get("otp_now") and res.get("otp"):
        otp_safe = html.escape(str(res["otp"]))
        sms_safe  = html.escape(str(res.get("sms") or ""))
        _s = load_settings()
        otp_bonus = _s.get("otp_bonus", OTP_RATE)
        await update_db_balance(uid, otp_bonus)
        add_otp_received(uid)
        log_global_activity(uid, "OTP_RECEIVED", {"number": clean_num, "otp": res["otp"]})
        text = (
            f"✅ <b>YOUR NUMBER</b> ✅\n\n"
            f"<blockquote>🌍 COUNTRY: <code>{country_flag} {html.escape(country_name)}</code></blockquote>\n"
            f"<blockquote>📶 RANGE: <code>{range_text}</code></blockquote>\n"
            f"<blockquote>📞 NUMBER: <code>+{clean_num}</code></blockquote>\n"
            f"<blockquote>🔑 OTP: <code>{otp_safe}</code></blockquote>"
            + (f"\n<blockquote>📩 SMS: <code>{sms_safe}</code></blockquote>" if sms_safe else "")
            + f"\n\n<b>✅ OTP RECEIVED! +{otp_bonus:.2f} BDT ADDED</b>"
        )
    else:
        text = (
            f"✅ <b>YOUR NUMBER</b> ✅\n\n"
            f"<blockquote>🌍 COUNTRY: <code>{country_flag} {html.escape(country_name)}</code></blockquote>\n"
            f"<blockquote>📶 RANGE: <code>{range_text}</code></blockquote>\n"
            f"<blockquote>📞 NUMBER: <code>+{clean_num}</code></blockquote>\n\n"
            f"<b>📩 SMS STATUS: ⏳ WAITING...</b>"
        )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 SAME RANGE", callback_data="same_range", api_kwargs={"style": "primary"})],
        [InlineKeyboardButton("📢 OTP GROUP", url="https://t.me/volt_x_lite_otp", api_kwargs={"style": "primary"})]
    ])
    try:
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    except Exception as e:
        print(f"fast_allocate edit error: {e}")

async def worker():
    while True:
        task = await request_queue.get()
        try:
            if task['type'] == 'process_numbers':
                await process_numbers(task['update'], task['context'], task['range_text'], task['count'])
            elif task['type'] == 'search_otp':
                await perform_otp_search(task['update'], task['context'], task['target_num'])
            elif task['type'] == 'auto_number':
                await process_auto_number(task['update'], task['context'], task['range_text'])
        except Exception as e:
            print(f"Worker Error: {e}")
        finally:
            request_queue.task_done()

# ==================== AUTO NUMBER / WORKER HANDLERS ====================
async def process_auto_number(update, context, range_text):
    uid = update.effective_user.id
    chat_id = update.effective_chat.id

    if is_user_banned(uid):
        await context.bot.send_message(chat_id=chat_id, text="🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return

    status_msg = await context.bot.send_message(chat_id=chat_id, text="🔍 SEARCHING...")
    try:
        res = await fetch_number_async(range_text)
        if not res:
            await status_msg.edit_text("❌ NO NUMBERS FOUND. TRY A VALID RANGE.")
            return

        generated_num = await register_active_number(uid, res["number"], range_text, detect_service(range_text))
        if not generated_num:
            await status_msg.edit_text("❌ NO NUMBERS FOUND. TRY A VALID RANGE.")
            return

        last_range[uid] = range_text
        add_number_taken(uid, 1)
        country_flag, country_name = get_country_info(generated_num)

        if res.get("otp_now") and res.get("otp"):
            instant_otp = html.escape(str(res["otp"]))
            instant_sms = html.escape(str(res.get("sms") or ""))
            _s = load_settings()
            otp_bonus = _s.get("otp_bonus", OTP_RATE)
            await update_db_balance(uid, otp_bonus)
            add_otp_received(uid)
            log_global_activity(uid, "OTP_RECEIVED", {"number": generated_num, "otp": res["otp"]})
            final_text = (
                f"✅ <b>YOUR NUMBER DETAILS</b> ✅\n\n"
                f"<blockquote>🌍 COUNTRY: <code>{country_flag} {country_name}</code></blockquote>\n"
                f"<blockquote>📶 RANGE: <code>{range_text}</code></blockquote>\n\n"
                f"<blockquote>📞 NUMBER: <code>+{generated_num}</code></blockquote>\n\n"
                f"<blockquote>🔑 OTP: <code>{instant_otp}</code></blockquote>\n"
                + (f"<blockquote>📩 SMS: <code>{instant_sms}</code></blockquote>\n" if instant_sms else "")
                + f"\n<b>✅ OTP RECEIVED! +{otp_bonus:.2f} BDT ADDED</b>"
            )
        else:
            final_text = (
                f"✅ <b>YOUR NUMBER DETAILS</b> ✅\n\n"
                f"<blockquote>🌍 COUNTRY: <code>{country_flag} {country_name}</code></blockquote>\n"
                f"<blockquote>📶 RANGE: <code>{range_text}</code></blockquote>\n\n"
                f"<blockquote>📞 NUMBER: <code>+{generated_num}</code></blockquote>\n\n"
                f"<b>📩 SMS STATUS: ⏳ WAITING...</b>"
            )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 SAME RANGE", callback_data="same_range", api_kwargs={"style": "primary"})],
            [InlineKeyboardButton("📢 OTP GROUP", url="https://t.me/volt_x_lite_otp", api_kwargs={"style": "primary"})]
        ])
        await status_msg.edit_text(final_text, parse_mode="HTML", reply_markup=keyboard)
    except Exception as e:
        print(f"Auto Number Error: {e}")
        await status_msg.edit_text(f"❌ Error: {str(e)}")

async def process_numbers(update_or_query, context, range_text, count):
    if isinstance(update_or_query, Update) and update_or_query.callback_query:
        uid = update_or_query.callback_query.from_user.id
        chat_id = update_or_query.callback_query.message.chat_id
    else:
        uid = update_or_query.effective_user.id
        chat_id = update_or_query.effective_chat.id

    if is_user_banned(uid):
        await context.bot.send_message(chat_id=chat_id, text="🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return

    status_msg = await context.bot.send_message(chat_id=chat_id, text="🔍 SEARCHING . . .")

    try:
        last_range[uid] = range_text
        tasks = [fetch_number_async(range_text) for _ in range(count)]
        results = await asyncio.gather(*tasks)
        valid_results = [r for r in results if r and r.get("number")]

        if not valid_results:
            await status_msg.edit_text("❌ NO NUMBERS FOUND. TRY A VALID RANGE.")
            return

        num_entries = []
        for r in valid_results:
            clean_num = await register_active_number(uid, r["number"], range_text, r.get("app") or "")
            if clean_num:
                add_number_taken(uid, 1)
                num_entries.append({
                    "num": clean_num,
                    "otp_now": r.get("otp_now", False),
                    "otp": r.get("otp"),
                    "sms": r.get("sms"),
                })

        if not num_entries:
            await status_msg.edit_text("❌ NO NUMBERS FOUND. TRY A VALID RANGE.")
            return

        country_flag, country_name = get_country_info(num_entries[0]["num"])
        _s = load_settings()
        otp_bonus = _s.get("otp_bonus", OTP_RATE)
        num_lines = []
        for entry in num_entries:
            if entry["otp_now"] and entry["otp"]:
                otp_safe = html.escape(str(entry["otp"]))
                sms_safe = html.escape(str(entry.get("sms") or ""))
                await update_db_balance(uid, otp_bonus)
                add_otp_received(uid)
                log_global_activity(uid, "OTP_RECEIVED", {"number": entry["num"], "otp": entry["otp"]})
                line = (
                    f"<blockquote>📞 NUMBER: <code>+{entry['num']}</code>\n"
                    f"🔑 OTP: <code>{otp_safe}</code>"
                    + (f"\n📩 SMS: <code>{sms_safe}</code>" if sms_safe else "")
                    + f"\n💰 +{otp_bonus:.2f} BDT ADDED</blockquote>"
                )
            else:
                line = f"<blockquote>📞 NUMBER: <code>+{entry['num']}</code></blockquote>"
            num_lines.append(line)

        num_list_text = "\n".join(num_lines)
        any_instant = any(e["otp_now"] and e["otp"] for e in num_entries)
        sms_status = "✅ OTP RECEIVED INSTANTLY!" if any_instant else "📩 SMS STATUS: ⏳ WAITING..."

        final_text = (
            f"✅ <b>YOUR NUMBER DETAILS</b> ✅\n\n"
            f"<blockquote>🌍 COUNTRY: <code>{country_flag} {country_name}</code></blockquote>\n"
            f"<blockquote>📶 RANGE: <code>{range_text}</code></blockquote>\n\n"
            f"{num_list_text}\n\n"
            f"<b>{sms_status}</b>"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 SAME RANGE", callback_data="same_range", api_kwargs={"style": "primary"})],
            [InlineKeyboardButton("📢 OTP GROUP", url="https://t.me/volt_x_lite_otp", api_kwargs={"style": "primary"})]
        ])
        await status_msg.edit_text(final_text, parse_mode="HTML", reply_markup=keyboard)
    except Exception as e:
        print(f"Process Number Error: {e}")
        await status_msg.edit_text(f"❌ System Error: {str(e)}")

async def perform_otp_search(update, context, target_num):
    uid = str(update.effective_user.id)
    if is_user_banned(int(uid)):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(int(uid)))
        return

    status_msg = await update.message.reply_text("🔍 SEARCHING IN SERVER...")
    try:
        api_key, base_url = get_api_credentials()
        urls = get_api_urls(base_url)
        headers = get_api_headers(api_key)
        r = await client_async.get(urls["otp"], headers=headers)
        res = r.json()
        raw_otps = []
        if isinstance(res, dict):
            if "data" in res:
                d = res["data"]
                raw_otps = d if isinstance(d, list) else (d.get("otps") or d.get("active") or [])
            else: raw_otps = res.get("otps") or []
        elif isinstance(res, list): raw_otps = res

        found_otps = [o for o in raw_otps if normalize_number(o.get("number") or o.get("phone", "")) == target_num]

        if not found_otps:
            error_msg = (
                "━━━━━━━━━━━━━━━━━━\n❌ NO OTP FOUND\n━━━━━━━━━━━━━━━━━━\n\n"
                f"📞 NUMBER:\n`+{target_num}`\n\n⏳ PLEASE TRY AGAIN LATER\n━━━━━━━━━━━━━━━━━━"
            )
            await status_msg.edit_text(error_msg, parse_mode="Markdown")
            await update.message.reply_text("🔙 RETURNING TO MAIN MENU...", reply_markup=main_keyboard(int(uid)))
        else:
            await status_msg.delete()
            paid_data = load_data(PAID_SMS_FILE)

            for o in found_otps:
                full_sms = o.get('message') or o.get('otp') or o.get('sms') or "No Content Found"
                otp_code = extract_otp(full_sms)
                otp_id = str(o.get("otp_id") or o.get("id", ""))
                sms_key = otp_id if otp_id else f"{target_num}_{full_sms}"

                if sms_key in paid_data:
                    payment_status = "❌ ALREADY PAID"
                else:
                    _s = load_settings()
                    otp_bonus = _s.get("otp_bonus", OTP_RATE)
                    await update_db_balance(uid, otp_bonus)
                    add_otp_received(uid)
                    log_global_activity(int(uid), "OTP_RECEIVED", {"number": target_num, "otp": otp_code})
                    paid_data[sms_key] = {"uid": uid, "otp": otp_code}
                    payment_status = f"💵 +{otp_bonus:.2f} BDT BALANCE ADDED"

                save_data(paid_data, PAID_SMS_FILE)
                country_flag, country_name = get_country_info(target_num)
                service_name = detect_service(full_sms)

                msg = (
                    f"✅ <b>OTP FOUND!</b>\n\n"
                    f"<blockquote>🌍 COUNTRY: <code>{country_flag} {country_name}</code></blockquote>\n"
                    f"<blockquote>📱 SERVICE: <code>{service_name}</code></blockquote>\n"
                    f"<blockquote>📞 NUMBER: <code>+{target_num}</code></blockquote>\n"
                    f"<blockquote>🔑 OTP: <code>{html.escape(otp_code)}</code></blockquote>\n\n"
                    f"<blockquote>📩 FULL SMS:\n<code>{html.escape(str(full_sms))}</code></blockquote>\n\n"
                    f"<b>{payment_status}</b>"
                )
                await update.message.reply_text(msg, parse_mode="HTML", reply_markup=main_keyboard(int(uid)))
    except Exception as e:
        try: await status_msg.edit_text(f"❌ Error: {str(e)}")
        except: await update.message.reply_text(f"❌ Error: {str(e)}")
        await update.message.reply_text("🔙 Returning to Main Menu...", reply_markup=main_keyboard(int(uid)))

# ==================== REFERRAL COMMAND ====================
async def refer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return

    bot_info = await context.bot.get_me()
    referral_link = f"https://t.me/{bot_info.username}?start={uid}"
    successful_refers = get_referral_count(uid)
    total_reward = float(successful_refers) * REFERRAL_PRICE

    refer_msg = (
        f"🎁 <b>REFER AND EARN SYSTEM</b> 🎁\n\n"
        f"<blockquote>🚀 INVITE FRIENDS &amp; EARN {int(REFERRAL_PRICE)} BDT EACH! 💸</blockquote>\n\n"
        f"<b>🔗 YOUR REFERRAL LINK:</b>\n"
        f"<blockquote><code>{referral_link}</code></blockquote>\n\n"
        f"<b>📊 YOUR STATS:</b>\n"
        f"<blockquote>👥 TOTAL REFERS: {successful_refers}\n"
        f"💰 TOTAL EARNED: {format_balance(total_reward)} BDT</blockquote>\n\n"
        f"✨ <b>SHARE LINK &amp; EARN MONEY!</b> ✨"
    )
    await update.message.reply_text(
        refer_msg,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("👥 YOUR REFERRAL", callback_data=f"my_ref_{uid}", api_kwargs={"style": "primary"})
        ]])
    )

# ==================== WITHDRAW SYSTEM ====================
async def withdraw_method_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    uid = update.effective_user.id

    if text == "CANCEL":
        context.user_data["withdraw_mode"] = None
        await update.message.reply_text("❌ WITHDRAW CANCELLED", reply_markup=main_keyboard(uid))
        return

    method_map = {"BKASH": "BKASH", "NAGAD": "NAGAD", "ROCKET": "ROCKET", "BINANCE": "BINANCE"}
    if text in method_map:
        balance = get_user(uid)['balance']
        context.user_data["withdraw_method"] = method_map[text]
        context.user_data["withdraw_mode"] = "amount"
        msg = (
            f"<blockquote>💸 SEND YOUR AMOUNT!\n"
            f"💵 TOTAL BALANCE: {format_balance(balance)} BDT</blockquote>\n\n"
            f"<blockquote>📉 MINIMUM WITHDRAW {get_min_withdraw():.2f} BDT</blockquote>"
        )
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=cancel_keyboard())
    else:
        await update.message.reply_text("⚠️ PLEASE SELECT A VALID PAYMENT METHOD!", reply_markup=withdraw_method_keyboard())

async def withdraw_amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    uid = update.effective_user.id

    if text == "CANCEL":
        context.user_data["withdraw_mode"] = None
        await update.message.reply_text("❌ WITHDRAW CANCELLED", reply_markup=main_keyboard(uid))
        return

    try:
        amount = float(text)
    except:
        await update.message.reply_text("⚠️ PLEASE SEND A VALID AMOUNT!", reply_markup=cancel_keyboard())
        return

    balance = get_user(uid)['balance']
    min_withdraw = get_min_withdraw()
    if amount < min_withdraw or amount > MAX_WITHDRAW:
        await update.message.reply_text(f"📉 MIN: {min_withdraw:.2f} BDT | MAX: {MAX_WITHDRAW} BDT", reply_markup=cancel_keyboard())
        return
    if amount > balance:
        await update.message.reply_text("🚫 INSUFFICIENT BALANCE!", reply_markup=cancel_keyboard())
        return

    context.user_data["withdraw_amount"] = amount
    context.user_data["withdraw_mode"] = "number"
    await update.message.reply_text("📞 PLEASE SEND YOUR PAYMENT NUMBER!\n\n<blockquote>🔢 EXAMPLE: 017XXXXXXXX</blockquote>", parse_mode="HTML", reply_markup=cancel_keyboard())

async def withdraw_number_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    uid = update.effective_user.id

    if text == "CANCEL":
        context.user_data["withdraw_mode"] = None
        await update.message.reply_text("❌ WITHDRAW CANCELLED", reply_markup=main_keyboard(uid))
        return

    if not is_valid_bangladesh_number(text):
        await update.message.reply_text("⚠️ PLEASE SEND VALID NUMBER! 017XXXXXXXX", reply_markup=cancel_keyboard())
        return

    method = context.user_data.get("withdraw_method")
    amount = context.user_data.get("withdraw_amount")
    payment_number = text
    payment_id = generate_payment_id()

    context.user_data["temp_withdraw"] = {
        "method": method, "amount": amount,
        "number": payment_number, "payment_id": payment_id
    }

    msg = (
        "✨ <b>YOUR PAYMENT DETAILS!</b> ✨\n\n"
        f"<blockquote>📝 METHOD: {method}\n"
        f"📞 NUMBER: {payment_number}\n\n"
        f"✅ CORRECT → CONFIRM\n❌ WRONG → CANCEL</blockquote>"
    )
    await update.message.reply_text(
        msg, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ CANCEL", callback_data="withdraw_cancel", api_kwargs={"style": "primary"}),
            InlineKeyboardButton("✅ CONFIRM", callback_data="withdraw_confirm", api_kwargs={"style": "primary"})
        ]])
    )

async def process_withdraw_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()

    temp_data = context.user_data.get("temp_withdraw")
    if not temp_data:
        await query.message.reply_text("⚠️ SESSION EXPIRED.", reply_markup=main_keyboard(uid))
        return

    method = temp_data["method"]
    amount = temp_data["amount"]
    payment_number = temp_data["number"]
    payment_id = temp_data["payment_id"]

    await update_db_balance(uid, -amount)
    wr = load_withdraw_requests()
    wr[str(payment_id)] = {
        "user_id": uid, "method": method, "amount": amount,
        "number": payment_number, "payment_id": payment_id,
        "status": "pending", "timestamp": datetime.now().isoformat()
    }
    save_withdraw_requests(wr)

    await query.message.edit_text(
        f"✅ <b>WITHDRAWAL REQUEST SUBMITTED</b> ✅\n\n"
        f"<blockquote>📝 METHOD: <code>{method}</code>\n"
        f"📞 NUMBER: <code>{payment_number}</code>\n"
        f"💰 AMOUNT: <code>{format_balance(amount)} BDT</code>\n"
        f"🆔 ID: <code>{payment_id}</code></blockquote>",
        parse_mode="HTML"
    )
    await context.bot.send_message(uid, "🎉 <b>WITHDRAW REQUEST SUBMITTED!</b>", parse_mode="HTML", reply_markup=main_keyboard(uid))

    admin_msg = (
        f"✅ <b>NEW WITHDRAWAL REQUEST</b>\n\n"
        f"<blockquote>🆔 USER: <code>{uid}</code>\n"
        f"📝 METHOD: <code>{method}</code>\n"
        f"📞 NUMBER: <code>{payment_number}</code>\n"
        f"💰 AMOUNT: <code>{format_balance(amount)} BDT</code>\n"
        f"🆔 ID: <code>{payment_id}</code></blockquote>"
    )
    admin_kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("❌ REJECT", callback_data=f"admin_reject_{payment_id}", api_kwargs={"style": "primary"}),
        InlineKeyboardButton("✅ APPROVE", callback_data=f"admin_approve_{payment_id}", api_kwargs={"style": "primary"})
    ]])
    for admin_id in get_admin_ids():
        try:
            await context.bot.send_message(admin_id, admin_msg, parse_mode="HTML", reply_markup=admin_kb)
        except Exception as e:
            print(f"Admin notify fail {admin_id}: {e}")

    context.user_data["temp_withdraw"] = None
    context.user_data["withdraw_mode"] = None

async def process_withdraw_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()
    context.user_data["temp_withdraw"] = None
    context.user_data["withdraw_mode"] = None
    await query.message.edit_text("❌ WITHDRAW CANCELLED")
    await context.bot.send_message(uid, "🔹 PLEASE USE THE BUTTONS BELOW:", reply_markup=main_keyboard(uid))

# ==================== ADMIN APPROVALS ====================
async def admin_approve_withdraw(update, context, payment_id):
    query = update.callback_query
    await query.answer()
    wr = load_withdraw_requests()
    if payment_id not in wr:
        await query.message.reply_text("⚠️ REQUEST NOT FOUND!")
        return
    rd = wr[payment_id]
    if rd.get("status") != "pending":
        await query.message.reply_text("⚠️ THIS REQUEST HAS ALREADY BEEN PROCESSED.")
        return
    uid = rd["user_id"]
    method = rd["method"]
    amount = rd["amount"]
    payment_number = rd["number"]
    wr[payment_id]["status"] = "approved"
    save_withdraw_requests(wr)

    try:
        await context.bot.send_message(
            uid,
            f"🎉 <b>WITHDRAWAL APPROVED!</b>\n\n"
            f"<blockquote>📝 METHOD: <code>{method}</code>\n"
            f"📞 NUMBER: <code>{payment_number}</code>\n"
            f"💰 AMOUNT: <code>{format_balance(amount)} BDT</code></blockquote>",
            parse_mode="HTML"
        )
    except:
        pass
    await query.message.edit_text(f"✅ APPROVED | User: {uid} | Amount: {format_balance(amount)} BDT")

async def admin_reject_withdraw(update, context, payment_id):
    query = update.callback_query
    await query.answer()
    wr = load_withdraw_requests()
    if payment_id not in wr:
        await query.message.reply_text("⚠️ REQUEST NOT FOUND!")
        return
    rd = wr[payment_id]
    if rd.get("status") != "pending":
        await query.message.reply_text("⚠️ THIS REQUEST HAS ALREADY BEEN PROCESSED.")
        return
    uid = rd["user_id"]
    amount = rd["amount"]
    wr[payment_id]["status"] = "rejected"
    save_withdraw_requests(wr)
    await update_db_balance(uid, amount)

    try:
        await context.bot.send_message(uid, "❌ <b>WITHDRAWAL REQUEST REJECTED</b>\n\nContact admin for more info.", parse_mode="HTML")
    except:
        pass
    await query.message.edit_text(f"❌ REJECTED | User: {uid} | Amount: {format_balance(amount)} BDT")

async def show_pending_withdrawals(update, context):
    pending = [
        (payment_id, request)
        for payment_id, request in load_withdraw_requests().items()
        if request.get("status") == "pending"
    ]
    if not pending:
        await update.message.reply_text("✅ <b>NO PENDING WITHDRAWALS</b>", parse_mode="HTML", reply_markup=withdrawal_management_keyboard())
        return

    rows = []
    lines = ["⏳ <b>PENDING WITHDRAWALS</b>\n"]
    for payment_id, request in pending:
        uid = request.get("user_id", "N/A")
        amount = float(request.get("amount", 0))
        method = html.escape(str(request.get("method", "N/A")))
        number = html.escape(str(request.get("number", "N/A")))
        lines.append(
            f"🆔 <code>{payment_id}</code>\n"
            f"👤 User: <code>{uid}</code> | 💰 {format_balance(amount)} BDT\n"
            f"📝 {method} | 📞 <code>{number}</code>\n"
        )
        rows.append([
            InlineKeyboardButton("✅ APPROVE", callback_data=f"admin_approve_{payment_id}", api_kwargs={"style": "primary"}),
            InlineKeyboardButton("❌ REJECT", callback_data=f"admin_reject_{payment_id}", api_kwargs={"style": "primary"}),
        ])
    rows.append([
        InlineKeyboardButton("🔙 BACK TO WITHDRAWAL MENU", callback_data="withdraw_admin_back", api_kwargs={"style": "primary"})
    ])
    await update.message.reply_text("\n".join(lines), parse_mode="HTML", reply_markup=InlineKeyboardMarkup(rows))

# ==================== ADMIN BALANCE ====================
async def admin_add_balance_start(update, context):
    context.user_data["add_balance_mode"] = True
    context.user_data["remove_balance_mode"] = False
    await update.message.reply_text("💰 SEND USER ID TO ADD BALANCE:")

async def admin_remove_balance_start(update, context):
    context.user_data["remove_balance_mode"] = True
    context.user_data["add_balance_mode"] = False
    await update.message.reply_text("💸 SEND USER ID TO REMOVE BALANCE:")

async def process_add_balance_user(update, context):
    uid_to_add = update.message.text.strip()
    if not uid_to_add.isdigit():
        await update.message.reply_text("❌ INVALID USER ID!")
        return
    uid_to_add_int = int(uid_to_add)
    if not user_exists(uid_to_add_int):
        await update.message.reply_text("❌ USER NOT FOUND!")
        context.user_data["add_balance_mode"] = False
        return
    context.user_data["pending_add_user"] = uid_to_add_int
    await update.message.reply_text("💵 SEND AMOUNT TO ADD:")

async def process_remove_balance_user(update, context):
    uid_to_remove = update.message.text.strip()
    if not uid_to_remove.isdigit():
        await update.message.reply_text("❌ INVALID USER ID!")
        return
    uid_to_remove_int = int(uid_to_remove)
    if not user_exists(uid_to_remove_int):
        await update.message.reply_text("❌ USER NOT FOUND!")
        context.user_data["remove_balance_mode"] = False
        return
    context.user_data["pending_remove_user"] = uid_to_remove_int
    await update.message.reply_text("💸 SEND AMOUNT TO REMOVE:")

async def process_add_balance_amount(update, context):
    try:
        amount = float(update.message.text.strip())
        if amount <= 0: raise ValueError
    except:
        await update.message.reply_text("❌ INVALID AMOUNT!")
        return
    uid = context.user_data.get("pending_add_user")
    if not uid:
        context.user_data["add_balance_mode"] = False
        await update.message.reply_text("⚠️ SESSION EXPIRED.")
        return
    new_balance = await update_db_balance(uid, amount)
    await update.message.reply_text(
        f"✅ <b>ADD BALANCE SUCCESSFUL</b>\n🆔 USER: <code>{uid}</code>\n"
        f"💰 ADDED: <code>{format_balance(amount)} BDT</code>\n"
        f"📈 NEW BALANCE: <code>{format_balance(new_balance)} BDT</code>",
        parse_mode="HTML"
    )
    try:
        await context.bot.send_message(uid, f"🎉 ADMIN ADDED <code>{format_balance(amount)} BDT</code> TO YOUR ACCOUNT!\n💵 NEW BALANCE: <code>{format_balance(new_balance)} BDT</code>", parse_mode="HTML")
    except:
        pass
    context.user_data["add_balance_mode"] = False
    context.user_data["pending_add_user"] = None

async def process_remove_balance_amount(update, context):
    try:
        amount = float(update.message.text.strip())
        if amount <= 0: raise ValueError
    except:
        await update.message.reply_text("❌ INVALID AMOUNT!")
        return
    uid = context.user_data.get("pending_remove_user")
    if not uid:
        context.user_data["remove_balance_mode"] = False
        await update.message.reply_text("⚠️ SESSION EXPIRED.")
        return
    old_balance = get_user(uid).get("balance", 0)
    if amount > old_balance:
        await update.message.reply_text(f"❌ INSUFFICIENT BALANCE! Current: {format_balance(old_balance)} BDT")
        context.user_data["remove_balance_mode"] = False
        context.user_data["pending_remove_user"] = None
        return
    new_balance = await update_db_balance(uid, -amount)
    await update.message.reply_text(
        f"✅ <b>REMOVE BALANCE SUCCESSFUL</b>\n🆔 USER: <code>{uid}</code>\n"
        f"💸 REMOVED: <code>{format_balance(amount)} BDT</code>\n"
        f"📉 NEW BALANCE: <code>{format_balance(new_balance)} BDT</code>",
        parse_mode="HTML"
    )
    try:
        await context.bot.send_message(uid, f"⚠️ ADMIN REMOVED <code>{format_balance(amount)} BDT</code> FROM YOUR ACCOUNT!\n💵 NEW BALANCE: <code>{format_balance(new_balance)} BDT</code>", parse_mode="HTML")
    except:
        pass
    context.user_data["remove_balance_mode"] = False
    context.user_data["pending_remove_user"] = None

# ==================== BAN / UNBAN ====================
async def admin_ban_user_start(update, context):
    context.user_data["admin_ban_mode"] = True
    context.user_data["admin_unban_mode"] = False
    await update.message.reply_text("🚫 SEND TELEGRAM ID TO BAN USER:")

async def admin_unban_user_start(update, context):
    context.user_data["admin_unban_mode"] = True
    context.user_data["admin_ban_mode"] = False
    await update.message.reply_text("🔓 SEND TELEGRAM ID TO UNBAN USER:")

async def process_ban_user(update, context):
    uid_to_ban = update.message.text.strip()
    if not uid_to_ban.isdigit():
        await update.message.reply_text("❌ INVALID USER ID!")
        return
    uid_to_ban_int = int(uid_to_ban)
    if not user_exists(uid_to_ban_int):
        await update.message.reply_text("❌ USER NOT FOUND!")
        context.user_data["admin_ban_mode"] = False
        return
    if is_user_banned(uid_to_ban_int):
        await update.message.reply_text("⚠️ USER IS ALREADY BANNED!")
        context.user_data["admin_ban_mode"] = False
        return
    ban_user(uid_to_ban_int)
    try:
        await context.bot.send_message(uid_to_ban_int, "🚫 <b>YOU HAVE BEEN BANNED</b>\n📞 Contact support.", parse_mode="HTML")
    except:
        pass
    await update.message.reply_text(f"✅ USER <code>{uid_to_ban}</code> BANNED!", parse_mode="HTML", reply_markup=system_config_keyboard())
    context.user_data["admin_ban_mode"] = False

async def process_unban_user(update, context):
    uid_to_unban = update.message.text.strip()
    if not uid_to_unban.isdigit():
        await update.message.reply_text("❌ INVALID USER ID!")
        return
    uid_to_unban_int = int(uid_to_unban)
    if not is_user_banned(uid_to_unban_int):
        await update.message.reply_text("⚠️ THIS USER IS NOT BANNED!")
        context.user_data["admin_unban_mode"] = False
        return
    unban_user(uid_to_unban_int)
    try:
        await context.bot.send_message(uid_to_unban_int, "✅ <b>YOU HAVE BEEN UNBANNED!</b> Use /start", parse_mode="HTML")
    except:
        pass
    await update.message.reply_text(f"✅ USER <code>{uid_to_unban}</code> UNBANNED!", parse_mode="HTML", reply_markup=system_config_keyboard())
    context.user_data["admin_unban_mode"] = False

async def show_banned_users_list(update, context):
    banned_list = load_banned_users()
    if not banned_list:
        await update.message.reply_text("📜 NO BANNED USERS.", reply_markup=system_config_keyboard())
        return
    text = "📜 <b>BANNED USER LIST</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
    for i, uid in enumerate(banned_list, 1):
        text += f"{i}. <code>{uid}</code>\n"
    text += f"\n📊 Total: {len(banned_list)}"
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=system_config_keyboard())

# ==================== MESSAGE HANDLER ====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    uid = update.effective_user.id
    text = update.message.text.strip()

    if is_admin(uid) and context.user_data.get("support_reply_uid"):
        target_uid = int(context.user_data["support_reply_uid"])
        if text == "CANCEL":
            context.user_data.pop("support_reply_uid", None)
            await update.message.reply_text("❌ Support reply cancelled.", reply_markup=admin_main_keyboard())
            return

        context.user_data.pop("support_reply_uid", None)
        try:
            await context.bot.send_message(
                chat_id=target_uid,
                text=f"💬 <b>ADMIN REPLY</b>\n\n{html.escape(text)}",
                parse_mode="HTML",
                reply_markup=main_keyboard(target_uid),
            )
            await update.message.reply_text(f"✅ Reply sent to user <code>{target_uid}</code>.", parse_mode="HTML", reply_markup=admin_main_keyboard())
        except Exception:
            await update.message.reply_text("❌ Could not send the reply. The user may have blocked the bot.", reply_markup=admin_main_keyboard())
        return

    if is_admin(uid) and update.message.reply_to_message:
        replied_text = update.message.reply_to_message.text or ""
        match = re.search(r"SUPPORT_USER_ID:(\d+)", replied_text)
        if match:
            target_uid = int(match.group(1))
            try:
                await context.bot.send_message(
                    chat_id=target_uid,
                    text=f"💬 <b>ADMIN REPLY</b>\n\n{html.escape(text)}",
                    parse_mode="HTML",
                    reply_markup=main_keyboard(target_uid),
                )
                await update.message.reply_text(f"✅ Reply sent to user <code>{target_uid}</code>.", parse_mode="HTML")
            except Exception:
                await update.message.reply_text("❌ Could not send the reply. The user may have blocked the bot.")
            return

    if context.user_data.get("support_mode") and not is_admin(uid):
        context.user_data["support_mode"] = False
        user = update.effective_user
        user_name = html.escape(user.full_name or "Unknown")
        username = html.escape(f"@{user.username}" if user.username else "No username")
        support_message = (
            "📩 <b>NEW SUPPORT MESSAGE</b>\n\n"
            f"👤 <b>User:</b> {user_name}\n"
            f"🔗 <b>Username:</b> {username}\n"
            f"🆔 <b>User ID:</b> <code>{uid}</code>\n"
            f"🔐 <code>SUPPORT_USER_ID:{uid}</code>\n\n"
            f"💬 <b>Message:</b>\n{html.escape(text)}"
        )
        sent_count = 0
        admin_ids = get_admin_ids()
        for admin_id in admin_ids:
            if admin_id == uid: continue
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=support_message,
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("↩️ REPLY USER", callback_data=f"support_reply_{uid}", api_kwargs={"style": "primary"})
                    ]]),
                )
                sent_count += 1
            except Exception as exc:
                print(f"Support delivery failed to admin {admin_id}: {exc}")

        if sent_count:
            await update.message.reply_text(
                f"✅ আপনার message {sent_count} জন admin-এর কাছে পাঠানো হয়েছে।\nAdmin reply করলে আপনি এই bot-এ উত্তর পাবেন।",
                reply_markup=main_keyboard(uid),
            )
        else:
            await update.message.reply_text(
                "❌ এখন কোনো admin-এর কাছে message পৌঁছানো যায়নি।\nAdmin-কে আগে এই bot খুলে /start দিতে হবে।",
                reply_markup=main_keyboard(uid),
            )
        return

    if context.user_data.get("withdraw_mode") == "select_method":
        await withdraw_method_selected(update, context)
        return
    if context.user_data.get("withdraw_mode") == "amount":
        await withdraw_amount_received(update, context)
        return
    if context.user_data.get("withdraw_mode") == "number":
        await withdraw_number_received(update, context)
        return

    if context.user_data.get("add_balance_mode") and is_admin(uid):
        if context.user_data.get("pending_add_user"):
            await process_add_balance_amount(update, context)
        else:
            await process_add_balance_user(update, context)
        return
    if context.user_data.get("remove_balance_mode") and is_admin(uid):
        if context.user_data.get("pending_remove_user"):
            await process_remove_balance_amount(update, context)
        else:
            await process_remove_balance_user(update, context)
        return

    if context.user_data.get("admin_ban_mode") and is_admin(uid):
        await process_ban_user(update, context)
        return
    if context.user_data.get("admin_unban_mode") and is_admin(uid):
        await process_unban_user(update, context)
        return

    if context.user_data.get("mode") == "custom_range":
        context.user_data["mode"] = None
        range_text = text.strip().upper()
        if not re.search(r'\d', range_text):
            await update.message.reply_text("❌ <b>INVALID RANGE!</b>\n\n<blockquote>সঠিক উদাহরণ: <code>234XXX</code></blockquote>", parse_mode="HTML", reply_markup=main_keyboard(uid))
            return
        await request_queue.put({'type': 'process_numbers', 'update': update, 'context': context, 'range_text': range_text, 'count': 1})
        return

    if not is_admin(uid) and is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return

    if text == "CANCEL":
        context.user_data.clear()
        await update.message.reply_text("❌ CANCELLED", reply_markup=main_keyboard(uid))
        return

    if text == "PROFILE":
        context.user_data["mode"] = None
        context.user_data["account_menu"] = True
        await update.message.reply_text("👤 <b>PROFILE MENU</b>\n\nSELECT AN OPTION:", parse_mode="HTML", reply_markup=account_keyboard())
        return

    if text == "BACK TO MAIN" and context.user_data.get("account_menu"):
        context.user_data["account_menu"] = None
        context.user_data["mode"] = None
        await update.message.reply_text("🔙 Back to main menu.", reply_markup=main_keyboard(uid))
        return

    if text == "VIEW PROFILE" and context.user_data.get("account_menu"):
        user_data = get_user(uid)
        stats = get_user_stats(uid)
        user = update.effective_user
        profile_text = (
            f"👤 <b>YOUR PROFILE</b>\n\n"
            f"<blockquote>🏷️ NAME: <b>{html.escape(user.full_name)}</b></blockquote>\n"
            f"<blockquote>🆔 USERNAME: @{html.escape(user.username or 'No username')}</blockquote>\n"
            f"<blockquote>🗝️ TELEGRAM ID: <code>{uid}</code></blockquote>\n\n"
            f"<blockquote>💵 BALANCE: <b>{format_balance(user_data.get('balance', 0))} BDT</b></blockquote>\n\n"
            f"✨ <b>TODAY</b>\n<blockquote>📱 NUMBERS: {stats['today_numbers']}\n🔑 OTPS: {stats['today_otps']}</blockquote>\n\n"
            f"🔥 <b>LAST 7 DAYS</b>\n<blockquote>📱 NUMBERS: {stats['last7d_numbers']}\n🔑 OTPS: {stats['last7d_otps']}</blockquote>\n\n"
            f"🌐 <b>ALL TIME</b>\n<blockquote>📱 NUMBERS: {stats['total_numbers']}\n🔑 OTPS: {stats['total_otps']}</blockquote>"
        )
        await update.message.reply_text(profile_text, parse_mode="HTML", reply_markup=account_keyboard())
        return

    if text == "BALANCE" and context.user_data.get("account_menu"):
        balance = get_user(uid)['balance']
        await update.message.reply_text(
            f"💰 <b>YOUR CURRENT BALANCE</b>\n\n<blockquote>💵 TOTAL: <b>{format_balance(balance)} BDT</b></blockquote>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("💸 WITHDRAW", callback_data="withdraw_start", api_kwargs={"style": "primary"})
            ]])
        )
        return

    if text == "REFER AND EARN" and context.user_data.get("account_menu"):
        await refer_command(update, context)
        return

    if text == "SEARCH OTP":
        context.user_data["mode"] = "search_otp"
        await update.message.reply_text("🔍 **ENTER THE NUMBER TO SEARCH OTP:**", parse_mode="Markdown")
        return

    if context.user_data.get("mode") == "search_otp":
        context.user_data["mode"] = None
        await request_queue.put({'type': 'search_otp', 'update': update, 'context': context, 'target_num': normalize_number(text)})
        return

    if text == "GET 2FA":
        await get_2fa_code(update, context)
        return

    if text == "GET NUMBER":
        await show_app_selection(update, context)
        return

    if context.user_data.get("mode") == "get_2fa":
        await process_2fa_key(update, context)
        return

    if text == "LEADERBOARD":
        await leaderboard_command(update, context)
        return

    if text == "SUPPORT":
        if is_admin(uid):
            await update.message.reply_text("💬 <b>SUPPORT CHAT</b>\n\nUser-এর message-এর উপর সরাসরি Reply করলে উত্তরটি সেই user-এর কাছে যাবে।", parse_mode="HTML", reply_markup=main_keyboard(uid))
            return
        context.user_data["support_mode"] = True
        await update.message.reply_text("💬 <b>SUPPORT CHAT</b>\n\nআপনার সমস্যা বা message লিখে পাঠান। আমি সেটি admin-এর কাছে পাঠিয়ে দেব।", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if text == "ADMIN PANEL" and is_admin(uid):
        context.user_data["admin_mode"] = "main"
        await update.message.reply_text("⌬━━━━━━━━━━━━━━━━━━━━⌬\n   WELCOME ADMIN PANEL\n⌬━━━━━━━━━━━━━━━━━━━━⌬", reply_markup=admin_main_keyboard())
        return

    if text == "BACK TO MAIN" and context.user_data.get("admin_mode"):
        context.user_data["admin_mode"] = None
        await update.message.reply_text("🔙 Back to main menu.", reply_markup=main_keyboard(uid))
        return

    if text == "BACK TO ADMIN":
        for k in ["user_management_mode", "system_config_mode", "bot_settings_mode", "stex_config_mode", "service_mgmt_mode", "withdrawal_admin_mode"]:
            context.user_data[k] = None
        context.user_data["admin_mode"] = "main"
        await update.message.reply_text("🔙 Back to admin panel.", reply_markup=admin_main_keyboard())
        return

    if text == "SUPPORT CHAT" and context.user_data.get("admin_mode") == "main" and is_admin(uid):
        await update.message.reply_text("💬 <b>SUPPORT CHAT</b>\n\nUser-এর message-এর উপর সরাসরি Reply করুন।", parse_mode="HTML", reply_markup=admin_main_keyboard())
        return

    if text == "WITHDRAWAL MANAGEMENT" and context.user_data.get("admin_mode") == "main" and is_admin(uid):
        context.user_data["withdrawal_admin_mode"] = "main"
        await update.message.reply_text(f"💸 <b>WITHDRAWAL MANAGEMENT</b>\n\n📉 Current minimum: <code>{get_min_withdraw():.2f} BDT</code>", parse_mode="HTML", reply_markup=withdrawal_management_keyboard())
        return

    if text == "⏳ PENDING WITHDRAWALS" and is_admin(uid):
        await show_pending_withdrawals(update, context)
        return

    if text == "PENDING WITHDRAWALS" and context.user_data.get("withdrawal_admin_mode") == "main" and is_admin(uid):
        await show_pending_withdrawals(update, context)
        return

    if text == "SET MINIMUM WITHDRAW" and context.user_data.get("withdrawal_admin_mode") == "main" and is_admin(uid):
        context.user_data["withdrawal_admin_mode"] = "set_minimum"
        await update.message.reply_text(f"📉 <b>SET MINIMUM WITHDRAW</b>\n\nCurrent: <code>{get_min_withdraw():.2f} BDT</code>\n\nনতুন minimum amount লিখুন:", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("withdrawal_admin_mode") == "set_minimum" and is_admin(uid):
        try:
            new_minimum = float(text)
            if new_minimum <= 0 or new_minimum > MAX_WITHDRAW: raise ValueError
            settings = load_settings()
            settings["min_withdraw"] = new_minimum
            save_settings(settings)
            context.user_data["withdrawal_admin_mode"] = "main"
            await update.message.reply_text(f"✅ <b>MINIMUM WITHDRAW UPDATED</b>\nNew minimum: <code>{new_minimum:.2f} BDT</code>", parse_mode="HTML", reply_markup=withdrawal_management_keyboard())
        except ValueError:
            await update.message.reply_text("❌ সঠিক amount দিন (০ থেকে ১০,০০০ এর মধ্যে):", reply_markup=cancel_keyboard())
        return

    if text == "USER MANAGEMENT" and context.user_data.get("admin_mode") == "main" and is_admin(uid):
        context.user_data["user_management_mode"] = "main"
        await update.message.reply_text("👥 User Management:", reply_markup=user_management_keyboard())
        return

    if text == "SYSTEM CONFIGURATION" and context.user_data.get("admin_mode") == "main" and is_admin(uid):
        context.user_data["system_config_mode"] = "main"
        await update.message.reply_text("⚙️ System Configuration:", reply_markup=system_config_keyboard())
        return

    if text == "TODAY ALL STATUS" and context.user_data.get("system_config_mode") == "main" and is_admin(uid):
        t_n, t_o, s_n, s_o, tot_n, tot_o = get_global_system_stats()
        msg = (
            f"📊 <b>SYSTEM STATUS</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"✨ <b>TODAY</b>\n📱 NUMBERS: {t_n}\n🔑 OTPS: {t_o}\n\n"
            f"🔥 <b>LAST 7 DAYS</b>\n📱 NUMBERS: {s_n}\n🔑 OTPS: {s_o}\n\n"
            f"🌐 <b>ALL TIME</b>\n📱 NUMBERS: {tot_n}\n🔑 OTPS: {tot_o}"
        )
        await update.message.reply_text(msg, parse_mode="HTML")
        return

    if text == "USER STATUS CHECK" and is_admin(uid):
        context.user_data["mode"] = "input_user_id"
        await update.message.reply_text("🔍 ENTER TELEGRAM ID:", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("mode") == "input_user_id" and is_admin(uid):
        target_uid = text.strip()
        if not target_uid.isdigit():
            await update.message.reply_text("❌ INVALID ID!")
            return
        context.user_data["mode"] = None
        stats = get_user_stats(target_uid)
        msg = (
            f"👤 <b>USER STATUS</b> — <code>{target_uid}</code>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"✨ TODAY: 📱 {stats['today_numbers']} | 🔑 {stats['today_otps']}\n"
            f"🔥 7 DAYS: 📱 {stats['last7d_numbers']} | 🔑 {stats['last7d_otps']}\n"
            f"🌐 ALL TIME: 📱 {stats['total_numbers']} | 🔑 {stats['total_otps']}"
        )
        await update.message.reply_text(
            msg, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📂 CHECK ALL DATA", callback_data=f"full_logs_{target_uid}", api_kwargs={"style": "primary"})
            ]])
        )
        return

    if text == "ALL USER ID" and context.user_data.get("user_management_mode") == "main" and is_admin(uid):
        users = get_all_users()
        if users:
            content = "\n".join(f"{i}. {u}" for i, u in enumerate(users, 1))
            f = io.BytesIO(content.encode()); f.name = f"ALL_USERS_{len(users)}.txt"
            await update.message.reply_document(document=f, caption=f"👥 Total Users: {len(users)}", reply_markup=user_management_keyboard())
        else:
            await update.message.reply_text("No users found.", reply_markup=user_management_keyboard())
        return

    if text == "ALL USER BALANCE" and context.user_data.get("user_management_mode") == "main" and is_admin(uid):
        user_db = load_data(USER_DATA_FILE)
        if user_db:
            total_bal = sum(v.get("balance", 0) for v in user_db.values())
            lines = [f"{i}. {uid_}: {v.get('balance', 0):.2f} BDT" for i, (uid_, v) in enumerate(user_db.items(), 1)]
            content = f"💰 TOTAL BALANCE: {total_bal:.2f} BDT\n\n" + "\n".join(lines)
            f = io.BytesIO(content.encode()); f.name = f"BALANCES_{total_bal:.0f}.txt"
            await update.message.reply_document(document=f, caption=f"💵 Total Balance: {total_bal:.2f} BDT", reply_markup=user_management_keyboard())
        else:
            await update.message.reply_text("No data.", reply_markup=user_management_keyboard())
        return

    if text == "BAN USER LIST" and is_admin(uid):
        await show_banned_users_list(update, context)
        return

    if text == "BAN USER" and context.user_data.get("system_config_mode") == "main" and is_admin(uid):
        await admin_ban_user_start(update, context)
        return

    if text == "UNBAN USER" and context.user_data.get("system_config_mode") == "main" and is_admin(uid):
        await admin_unban_user_start(update, context)
        return

    if text == "ADD BALANCE" and context.user_data.get("system_config_mode") == "main" and is_admin(uid):
        await admin_add_balance_start(update, context)
        return

    if text == "REMOVE BALANCE" and context.user_data.get("system_config_mode") == "main" and is_admin(uid):
        await admin_remove_balance_start(update, context)
        return

    if text == "SEND MESSAGE TO ALL USERS" and is_admin(uid):
        context.user_data["broadcast_mode"] = True
        await update.message.reply_text(
            "📢 <b>ADMIN BROADCAST SYSTEM (PRO)</b>\n\n"
            "💬 আপনি এখন যা পাঠাবেন – সকল ইউজারের কাছে চলে যাবে।", 
            parse_mode="HTML", 
            reply_markup=cancel_keyboard()
        )
        return

    if context.user_data.get("broadcast_mode") and is_admin(uid):
        context.user_data["broadcast_mode"] = False
        user_db = load_data(USER_DATA_FILE)
        all_uids = list(user_db.keys())
        
        if not all_uids:
            await update.message.reply_text("❌ পাঠানোর জন্য কোনো ইউজার পাওয়া যায়নি!")
            return

        success_ids, fail_ids = [], []
        status_msg = await update.message.reply_text(f"🚀 <b>ব্রডকাস্ট শুরু হয়েছে...</b>\n🎯 টার্গেট: {len(all_uids)} জন ইউজার।", parse_mode="HTML")

        def format_broadcast_caption(caption_text):
            if not caption_text: return "<blockquote>📢 <b>ADMIN NOTICE :</b></blockquote>"
            formatted = re.sub(r'(\d{3,}[xX]{3,})', r'<code>\1</code>', str(caption_text))
            return f"<blockquote>📢 <b>ADMIN NOTICE :</b></blockquote>\n\n{formatted}"

        for user_id_str in all_uids:
            try:
                target_id = int(user_id_str)
                if update.message.text:
                    await context.bot.send_message(chat_id=target_id, text=format_broadcast_caption(update.message.text), parse_mode="HTML")
                elif update.message.photo:
                    caption = format_broadcast_caption(update.message.caption) if update.message.caption else None
                    await context.bot.send_photo(chat_id=target_id, photo=update.message.photo[-1].file_id, caption=caption, parse_mode="HTML" if caption else None)
                elif update.message.video:
                    caption = format_broadcast_caption(update.message.caption) if update.message.caption else None
                    await context.bot.send_video(chat_id=target_id, video=update.message.video.file_id, caption=caption, parse_mode="HTML" if caption else None)
                elif update.message.document:
                    caption = format_broadcast_caption(update.message.caption) if update.message.caption else None
                    await context.bot.send_document(chat_id=target_id, document=update.message.document.file_id, caption=caption, parse_mode="HTML" if caption else None)
                else:
                    await context.bot.copy_message(chat_id=target_id, from_chat_id=update.message.chat_id, message_id=update.message.message_id)
                success_ids.append(user_id_str)
            except Exception as e:
                fail_ids.append(user_id_str)
            await asyncio.sleep(0.05)

        report_text = (
            f"✅ <b>ADMIN NOTICE COMPLETE !</b>\n\n"
            f"📊 <b>BROADCAST REPORT:</b>\n\n"
            f"<blockquote>✅ SUCCESSFULLY SENT: {len(success_ids)} USERS !</blockquote>\n"
            f"<blockquote>❌ FAILED TO SEND: {len(fail_ids)} USERS !</blockquote>"
        )
        await status_msg.delete()
        await context.bot.send_message(chat_id=uid, text=report_text, parse_mode="HTML", reply_markup=main_keyboard(uid))
        return

    # ==================== BOT SETTINGS ====================
    if text == "BOT SETTINGS" and context.user_data.get("admin_mode") == "main" and is_admin(uid):
        context.user_data["bot_settings_mode"] = "main"
        await update.message.reply_text("⚙️ <b>BOT SETTINGS</b>", parse_mode="HTML", reply_markup=bot_settings_keyboard())
        return

    if text == "BACK TO BOT SETTINGS" and is_admin(uid):
        context.user_data["bot_settings_mode"] = "main"
        await update.message.reply_text("⚙️ <b>BOT SETTINGS</b>", parse_mode="HTML", reply_markup=bot_settings_keyboard())
        return

    if text == "STEX CONFIG" and context.user_data.get("bot_settings_mode") == "main" and is_admin(uid):
        context.user_data["stex_config_mode"] = "main"
        await update.message.reply_text("📡 <b>STEX PANEL CONFIG</b>", parse_mode="HTML", reply_markup=stex_config_keyboard())
        return

    if text == "SERVICE MANAGEMENT" and context.user_data.get("admin_mode") == "main" and is_admin(uid):
        context.user_data["service_mgmt_mode"] = "main"
        await update.message.reply_text("🔧 <b>SERVICE MANAGEMENT</b>", parse_mode="HTML", reply_markup=service_management_keyboard())
        return

    if text == "ADD ADMIN" and context.user_data.get("bot_settings_mode") == "main" and is_admin(uid):
        context.user_data["bot_settings_mode"] = "add_admin"
        s = load_settings()
        admin_list = "\n".join(f"• <code>{a}</code>" for a in s.get("admins", []))
        await update.message.reply_text(f"➕ <b>ADD ADMIN</b>\n\n<blockquote>Current admins:\n{admin_list}</blockquote>\n\nSend Telegram User ID:", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("bot_settings_mode") == "add_admin" and is_admin(uid):
        if not text.lstrip("-").isdigit():
            await update.message.reply_text("❌ Invalid ID! Send a numeric Telegram ID.")
            return
        new_admin_id = int(text)
        s = load_settings()
        admins = s.get("admins", [])
        if new_admin_id in admins:
            await update.message.reply_text("⚠️ User already admin!", reply_markup=bot_settings_keyboard())
        else:
            admins.append(new_admin_id)
            s["admins"] = admins
            save_settings(s)
            await update.message.reply_text(f"✅ <b>ADMIN ADDED!</b>\n<blockquote>🆔 ID: <code>{new_admin_id}</code></blockquote>", parse_mode="HTML", reply_markup=bot_settings_keyboard())
        context.user_data["bot_settings_mode"] = "main"
        return

    if text == "REMOVE ADMIN" and context.user_data.get("bot_settings_mode") == "main" and is_admin(uid):
        context.user_data["bot_settings_mode"] = "remove_admin"
        s = load_settings()
        admin_list = "\n".join(f"• <code>{a}</code>" for a in s.get("admins", []))
        await update.message.reply_text(f"➖ <b>REMOVE ADMIN</b>\n\n<blockquote>Current admins:\n{admin_list}</blockquote>\n\nSend Telegram User ID:", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("bot_settings_mode") == "remove_admin" and is_admin(uid):
        if not text.lstrip("-").isdigit():
            await update.message.reply_text("❌ Invalid ID!")
            return
        rem_id = int(text)
        s = load_settings()
        admins = s.get("admins", [])
        if rem_id == ADMIN_ID or (rem_id in s.get("owners", []) and rem_id == uid):
            await update.message.reply_text("❌ Cannot remove primary owner!", reply_markup=bot_settings_keyboard())
        elif rem_id not in admins:
            await update.message.reply_text("⚠️ User not found in admin list!", reply_markup=bot_settings_keyboard())
        else:
            admins.remove(rem_id)
            s["admins"] = admins
            save_settings(s)
            await update.message.reply_text(f"✅ <b>ADMIN REMOVED!</b>\n<blockquote>🆔 ID: <code>{rem_id}</code></blockquote>", parse_mode="HTML", reply_markup=bot_settings_keyboard())
        context.user_data["bot_settings_mode"] = "main"
        return

    if text == "SET OTP GROUP LINK" and context.user_data.get("bot_settings_mode") == "main" and is_admin(uid):
        context.user_data["bot_settings_mode"] = "set_otp_link"
        s = load_settings()
        await update.message.reply_text(f"🔗 <b>SET OTP GROUP LINK</b>\n\n<blockquote>Current: <code>{s.get('otp_group_url')}</code></blockquote>\n\nSend link:", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("bot_settings_mode") == "set_otp_link" and is_admin(uid):
        s = load_settings()
        s["otp_group_url"] = text.strip()
        save_settings(s)
        await update.message.reply_text(f"✅ <b>OTP GROUP LINK UPDATED!</b>", parse_mode="HTML", reply_markup=bot_settings_keyboard())
        context.user_data["bot_settings_mode"] = "main"
        return

    if text == "SET FORCE CHANNEL" and context.user_data.get("bot_settings_mode") == "main" and is_admin(uid):
        context.user_data["bot_settings_mode"] = "set_force_channel"
        await update.message.reply_text("📢 Send channel username (e.g. @channel) or <b>DISABLE</b>:", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("bot_settings_mode") == "set_force_channel" and is_admin(uid):
        s = load_settings()
        val = text.strip()
        if val.upper() == "DISABLE":
            s["force_join_channel"] = None
        else:
            if not val.startswith("@") and not val.lstrip("-").isdigit():
                val = "@" + val
            s["force_join_channel"] = val
        save_settings(s)
        await update.message.reply_text("✅ Updated Force Channel Settings!", reply_markup=bot_settings_keyboard())
        context.user_data["bot_settings_mode"] = "main"
        return

    if text == "SET OTP CHAT ID" and context.user_data.get("bot_settings_mode") == "main" and is_admin(uid):
        context.user_data["bot_settings_mode"] = "set_otp_chat_id"
        await update.message.reply_text("📋 Send numeric Group Chat ID (e.g. -100xxxxxxxx) or <b>DISABLE</b>:", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("bot_settings_mode") == "set_otp_chat_id" and is_admin(uid):
        s = load_settings()
        val = text.strip()
        if val.upper() == "DISABLE":
            s["otp_group_chat_id"] = None
        elif val.lstrip("-").isdigit():
            s["otp_group_chat_id"] = int(val)
        else:
            await update.message.reply_text("❌ Invalid ID!")
            return
        save_settings(s)
        await update.message.reply_text("✅ OTP Group Chat ID updated!", reply_markup=bot_settings_keyboard())
        context.user_data["bot_settings_mode"] = "main"
        return

    # ==================== STEX CONFIG ====================
    if text == "SET API KEY" and context.user_data.get("stex_config_mode") == "main" and is_admin(uid):
        context.user_data["stex_config_mode"] = "set_api_key"
        await update.message.reply_text("🔑 Send new STEX API Key:", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("stex_config_mode") == "set_api_key" and is_admin(uid):
        s = load_settings()
        s["stex_api_key"] = text.strip()
        save_settings(s)
        await update.message.reply_text("✅ STEX API Key Updated!", reply_markup=stex_config_keyboard())
        context.user_data["stex_config_mode"] = "main"
        return

    if text == "SET BASE URL" and context.user_data.get("stex_config_mode") == "main" and is_admin(uid):
        context.user_data["stex_config_mode"] = "set_base_url"
        await update.message.reply_text("🌐 Send new Base URL:", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("stex_config_mode") == "set_base_url" and is_admin(uid):
        s = load_settings()
        s["stex_base_url"] = text.strip().rstrip("/")
        save_settings(s)
        await update.message.reply_text("✅ STEX Base URL Updated!", reply_markup=stex_config_keyboard())
        context.user_data["stex_config_mode"] = "main"
        return

    if text == "SET ALLOWED SERVICES" and context.user_data.get("stex_config_mode") == "main" and is_admin(uid):
        context.user_data["stex_config_mode"] = "set_services"
        await update.message.reply_text("📋 Send comma separated service names (e.g. WhatsApp,Telegram):", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("stex_config_mode") == "set_services" and is_admin(uid):
        services = [x.strip() for x in text.split(",") if x.strip()]
        s = load_settings()
        s["allowed_services"] = services
        save_settings(s)
        _ranges_cache["data"] = {}
        _ranges_cache["updated_at"] = 0
        await update.message.reply_text("✅ Allowed Services Updated!", reply_markup=stex_config_keyboard())
        context.user_data["stex_config_mode"] = "main"
        return

    if text == "VIEW STEX CONFIG" and context.user_data.get("stex_config_mode") == "main" and is_admin(uid):
        s = load_settings()
        msg = (
            f"📡 <b>STEX PANEL CONFIG</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>🔑 API KEY: <code>{html.escape(s.get('stex_api_key',''))}</code></blockquote>\n"
            f"<blockquote>🌐 BASE URL: <code>{html.escape(s.get('stex_base_url',''))}</code></blockquote>\n"
            f"<blockquote>📋 ALLOWED: {', '.join(s.get('allowed_services',[]))}</blockquote>\n"
            f"<blockquote>📋 OTP CHAT ID: <code>{s.get('otp_group_chat_id')}</code></blockquote>"
        )
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=stex_config_keyboard())
        return

    # ==================== MANUAL SERVICE MANAGEMENT ====================
    if text == "LIST SERVICES" and context.user_data.get("service_mgmt_mode") == "main" and is_admin(uid):
        s = load_settings()
        manual = s.get("manual_services", [])
        if not manual:
            await update.message.reply_text("📋 No manual services.", reply_markup=service_management_keyboard())
        else:
            lines = []
            for i, svc in enumerate(manual):
                clines = "\n".join(f"   {c.get('flag','🌍')} {c.get('name','?')} — <code>{', '.join(c.get('ranges',[]))}</code>" for c in svc.get("countries", []))
                lines.append(f"{i+1}. <b>{html.escape(svc['name'])}</b>\n{clines}")
            await update.message.reply_text("\n\n".join(lines), parse_mode="HTML", reply_markup=service_management_keyboard())
        return

    if text == "ADD SERVICE" and context.user_data.get("service_mgmt_mode") == "main" and is_admin(uid):
        context.user_data["service_mgmt_mode"] = "add_name"
        await update.message.reply_text("➕ Send Service Name (e.g. FACEBOOK):", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("service_mgmt_mode") == "add_name" and is_admin(uid):
        context.user_data["new_svc_name"] = text.strip().upper()
        context.user_data["new_svc_countries"] = []
        context.user_data["service_mgmt_mode"] = "add_country"
        await update.message.reply_text(f"➕ Send Country Name for <b>{html.escape(text.strip().upper())}</b>:", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if text == "DONE" and context.user_data.get("service_mgmt_mode") == "add_country" and is_admin(uid):
        svc_name = context.user_data.get("new_svc_name")
        countries_done = context.user_data.get("new_svc_countries", [])
        if svc_name and countries_done:
            s = load_settings()
            manual = s.get("manual_services", [])
            manual.append({"name": svc_name, "countries": countries_done})
            s["manual_services"] = manual
            save_settings(s)
            await update.message.reply_text("✅ SERVICE SAVED!", reply_markup=service_management_keyboard())
        context.user_data["service_mgmt_mode"] = "main"
        return

    if context.user_data.get("service_mgmt_mode") == "add_country" and is_admin(uid):
        context.user_data["new_svc_cur_country"] = text.strip().title()
        context.user_data["service_mgmt_mode"] = "add_range"
        await update.message.reply_text(f"➕ Send Range(s) for <b>{html.escape(text.strip().title())}</b> (e.g. 880XXX):", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("service_mgmt_mode") == "add_range" and is_admin(uid):
        raw_ranges = [r.strip().upper() for r in text.split(",") if r.strip()]
        country_name = context.user_data.get("new_svc_cur_country", "Unknown")
        flag, detected = "🌍", country_name
        if raw_ranges:
            prefix = re.sub(r'[xX]+$', '', raw_ranges[0]).strip()
            pfx_d  = re.sub(r'\D', '', prefix)
            flag, detected = get_country_info(pfx_d)
        countries_done = context.user_data.get("new_svc_countries", [])
        countries_done.append({"name": country_name, "flag": flag, "ranges": raw_ranges})
        context.user_data["new_svc_countries"] = countries_done
        context.user_data["service_mgmt_mode"] = "add_country"
        await update.message.reply_text(f"✅ Added {country_name}! Send another Country Name or send <b>DONE</b>:", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if text == "REMOVE SERVICE" and context.user_data.get("service_mgmt_mode") == "main" and is_admin(uid):
        s = load_settings()
        manual = s.get("manual_services", [])
        if not manual:
            await update.message.reply_text("📋 No services to remove.", reply_markup=service_management_keyboard())
            return
        lines = "\n".join(f"{i+1}. <b>{html.escape(svc['name'])}</b>" for i, svc in enumerate(manual))
        context.user_data["service_mgmt_mode"] = "remove"
        await update.message.reply_text(f"➖ <b>REMOVE SERVICE</b>\n\n{lines}\n\nSend index number to remove:", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("service_mgmt_mode") == "remove" and is_admin(uid):
        if text.isdigit():
            idx = int(text) - 1
            s = load_settings()
            manual = s.get("manual_services", [])
            if 0 <= idx < len(manual):
                removed = manual.pop(idx)
                s["manual_services"] = manual
                save_settings(s)
                await update.message.reply_text(f"✅ Removed {removed['name']}!", reply_markup=service_management_keyboard())
                context.user_data["service_mgmt_mode"] = "main"
                return
        await update.message.reply_text("❌ Invalid index!")
        return

    if not is_admin(uid):
        if not await check_force_join(update, context):
            return

    await update.message.reply_text("🔹 PLEASE USE THE BUTTONS BELOW:", reply_markup=main_keyboard(uid))

# ==================== SLASH COMMANDS ====================
async def get1number_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid): return
    await show_app_selection(update, context)

async def searchotp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid): return
    context.user_data["mode"] = "search_otp"
    await update.message.reply_text("🔍 **ENTER THE NUMBER TO SEARCH OTP:**", parse_mode="Markdown")

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid): return
    balance = get_user(uid)['balance']
    await update.message.reply_text(f"💰 BALANCE: `{format_balance(balance)} BDT`", parse_mode="Markdown", reply_markup=main_keyboard(uid))

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid): return
    user_data = get_user(uid)
    stats = get_user_stats(uid)
    user = update.effective_user
    profile_text = (
        f"👤 **YOUR PROFILE**\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🏷️ NAME: `{user.full_name}`\n"
        f"🆔 USERNAME: @{user.username or 'No username'}\n"
        f"🗝️ ID: `{uid}`\n\n"
        f"💵 BALANCE: {format_balance(user_data.get('balance', 0))} BDT\n\n"
        f"✨ TODAY: 📱 {stats['today_numbers']} | 🔑 {stats['today_otps']}\n"
        f"🔥 7 DAYS: 📱 {stats['last7d_numbers']} | 🔑 {stats['last7d_otps']}\n"
        f"🌐 ALL TIME: 📱 {stats['total_numbers']} | 🔑 {stats['total_otps']}"
    )
    await update.message.reply_text(profile_text, parse_mode="Markdown")

async def refer_command_slash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid): return
    await refer_command(update, context)

async def leaderboard_command_slash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid): return
    await leaderboard_command(update, context)

# ==================== FORCE JOIN & START ====================
async def check_force_join(update, context):
    s = load_settings()
    channel = s.get("force_join_channel")
    if not channel:
        return True
    uid = update.effective_user.id
    if is_admin(uid):
        return True
    try:
        member = await context.bot.get_chat_member(channel, uid)
        if member.status in ("member", "administrator", "creator", "restricted"):
            return True
    except Exception:
        pass
    channel_clean = str(channel).lstrip("@")
    try:
        chat = await context.bot.get_chat(channel)
        invite_url = chat.invite_link or f"https://t.me/{channel_clean}"
    except Exception:
        invite_url = f"https://t.me/{channel_clean}"
    btn = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ JOIN CHANNEL", url=invite_url, api_kwargs={"style": "primary"})
    ]])
    await update.message.reply_text(
        f"⚠️ <b>FORCE JOIN REQUIRED!</b>\n\n<blockquote>বট ব্যবহার করতে আগে আমাদের চ্যানেলে জয়েন করুন।\nজয়েন করার পর আবার চেষ্টা করুন।</blockquote>",
        parse_mode="HTML",
        reply_markup=btn
    )
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    uid_str = str(uid)
    existing_data = load_data(USER_DATA_FILE)
    is_new_user = uid_str not in existing_data
    if is_new_user:
        get_user(uid)

    args = context.args
    if args:
        param = args[0]
        if is_range_request(param):
            await request_queue.put({'type': 'auto_number', 'update': update, 'context': context, 'range_text': param})
            return
        elif is_referral_request(param) and is_new_user:
            try:
                referrer_id = int(param)
                if referrer_id != uid and str(referrer_id) in existing_data:
                    current_count = get_referral_count(referrer_id)
                    new_count = current_count + 1
                    update_referral_count(referrer_id, new_count)
                    await update_db_balance(referrer_id, REFERRAL_PRICE)
                    log_global_activity(referrer_id, "REFERRAL_JOINED", {"referred_user": uid})
                    try:
                        await context.bot.send_message(
                            referrer_id,
                            f"🎉 <b>NEW REFERRAL!</b>\n\n<blockquote>🗝️ ID: <code>{uid}</code>\n💰 REWARD: {format_balance(REFERRAL_PRICE)} BDT\n👥 TOTAL REFERS: {new_count}</blockquote>",
                            parse_mode="HTML"
                        )
                    except:
                        pass
            except Exception as e:
                print(f"Referral error: {e}")

    if not await check_force_join(update, context):
        return

    context.user_data.clear()
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode="Markdown")
    await update.message.reply_text("🔹 PLEASE USE THE BUTTONS BELOW:", reply_markup=main_keyboard(uid))

# ==================== CALLBACK QUERY ROUTER ====================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    data = query.data
    await query.answer()

    if not is_admin(uid) and is_user_banned(uid):
        await query.edit_message_text("🚫 YOU ARE BANNED 🚫")
        return

    if data.startswith("support_reply_"):
        if not is_admin(uid):
            await query.answer("Only admins can reply.", show_alert=True)
            return
        target_uid = int(data.replace("support_reply_", ""))
        context.user_data["support_reply_uid"] = target_uid
        await query.message.reply_text(f"✍️ <b>REPLYING TO USER</b> <code>{target_uid}</code>\n\nএখন আপনার reply লিখে পাঠান:", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if data.startswith("sel_app_"):
        app_name = data[8:]
        top = context.user_data.get("top_ranges_by_app") or (_ranges_cache.get("data") or {})
        if not top or app_name not in top:
            await query.answer("App not found. Please try again.", show_alert=True); return
        ranges = top[app_name].get("ranges", [])
        if not ranges:
            await query.answer("No ranges available for this app.", show_alert=True); return
        context.user_data["sel_app"] = app_name
        context.user_data["sel_ranges"] = ranges
        btns, seen = [], {}
        clrs = ["primary"]
        ci = 0
        for i, r in enumerate(ranges[:24]):
            prefix = re.sub(r'[xX]+$', '', str(r)).strip()
            pfx_d = re.sub(r'\D', '', prefix)
            flag, cname = get_country_info(pfx_d)
            label = f"{flag} {cname}"
            if label not in seen:
                seen[label] = i
                btns.append(InlineKeyboardButton(label, callback_data=f"sel_rng_{i}", api_kwargs={"style": clrs[ci % len(clrs)]}))
                ci += 1
        rows = [btns[j:j+2] for j in range(0, len(btns), 2)]
        rows.append([InlineKeyboardButton("◀️ BACK", callback_data="back_apps", api_kwargs={"style": "primary"})])
        await query.message.edit_text(
            f'{get_tg_emoji("get_number_btn")} <b>SELECT COUNTRY</b>\n━━━━━━━━━━━━━━━━━━━━━\n'
            f'<blockquote>📱 App: <b>{html.escape(app_name)}</b></blockquote>\n'
            f'<blockquote>🌍 Select your Country:</blockquote>',
            parse_mode="HTML", reply_markup=InlineKeyboardMarkup(rows))
        return

    if data.startswith("sel_rng_"):
        idx = int(data[8:])
        ranges = context.user_data.get("sel_ranges", [])
        app_name = context.user_data.get("sel_app", "")
        if idx >= len(ranges):
            await query.answer("Range not found.", show_alert=True); return
        asyncio.create_task(fast_allocate_number(query, context, ranges[idx], app_name))
        return

    if data == "custom_range":
        context.user_data["mode"] = "custom_range"
        await query.message.edit_text(
            "⚙️ <b>CUSTOM RANGE</b>\n\n<blockquote>📡 Type your custom range.\nExample: <code>234XXX</code> or <code>225XXX</code></blockquote>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ BACK", callback_data="back_apps", api_kwargs={"style": "primary"})
            ]]))
        return

    if data.startswith("manual_svc_"):
        idx = int(data[len("manual_svc_"):])
        s = load_settings()
        manual = s.get("manual_services", [])
        if idx >= len(manual):
            await query.answer("Service not found.", show_alert=True); return
        svc = manual[idx]
        countries = svc.get("countries", [])
        if not countries:
            await query.answer("No countries available.", show_alert=True); return
        btns = [InlineKeyboardButton(f"{c.get('flag','🌍')} {c.get('name','Unknown')}", callback_data=f"manual_cnt_{idx}_{ci}", api_kwargs={"style": "primary"}) for ci, c in enumerate(countries)]
        rows = [btns[j:j+2] for j in range(0, len(btns), 2)]
        rows.append([InlineKeyboardButton("◀️ BACK", callback_data="back_apps", api_kwargs={"style": "primary"})])
        await query.message.edit_text(f'🔧 <b>{html.escape(svc["name"])}</b>\n━━━━━━━━━━━━━━━━━━━━━\n<blockquote>Select Country:</blockquote>', parse_mode="HTML", reply_markup=InlineKeyboardMarkup(rows))
        return

    if data.startswith("manual_cnt_"):
        parts = data.split("_")
        svc_idx, cnt_idx = int(parts[2]), int(parts[3])
        s = load_settings()
        manual = s.get("manual_services", [])
        if svc_idx < len(manual) and cnt_idx < len(manual[svc_idx].get("countries", [])):
            country = manual[svc_idx]["countries"][cnt_idx]
            ranges = country.get("ranges", [])
            if ranges:
                range_text = random.choice(ranges).strip().upper()
                asyncio.create_task(fast_allocate_number(query, context, range_text, manual[svc_idx]["name"]))
                return
        await query.answer("Country/Range not found.", show_alert=True)
        return

    if data in ("back_apps", "back_services"):
        top = context.user_data.get("top_ranges_by_app") or (_ranges_cache.get("data") or {})
        manual_rows = build_manual_service_buttons()
        stex_rows = build_app_buttons_from_cache(top) if top else []
        all_rows = stex_rows + manual_rows
        all_rows.append([InlineKeyboardButton("⚙️ CUSTOM RANGE", callback_data="custom_range", api_kwargs={"style": "primary"})])
        msg = f'{get_tg_emoji("get_number_btn")} <b>SELECT APP TO GET NUMBER</b>\n━━━━━━━━━━━━━━━━━━━━━'
        await query.message.edit_text(msg, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(all_rows))
        return

    if data == "same_range":
        r_text = last_range.get(uid)
        if r_text:
            try:
                await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("📢 OTP GROUP", url="https://t.me/volt_x_lite_otp", api_kwargs={"style": "primary"})
                ]]))
            except: pass
            await process_numbers(update, context, r_text, 1)
        return

    if data == "withdraw_start":
        balance = get_user(uid)['balance']
        min_withdraw = get_min_withdraw()
        if balance < min_withdraw:
            await query.message.reply_text(f"<blockquote>💵 BALANCE: {format_balance(balance)} BDT\n📉 MIN WITHDRAW: {min_withdraw:.2f} BDT</blockquote>", parse_mode="HTML")
            return
        context.user_data["withdraw_mode"] = "select_method"
        await query.message.reply_text("💳 SELECT YOUR PAYMENT METHOD!", reply_markup=withdraw_method_keyboard())
        return

    if data == "withdraw_confirm":
        await process_withdraw_confirm(update, context)
        return

    if data == "withdraw_cancel":
        await process_withdraw_cancel(update, context)
        return

    if data == "withdraw_admin_back":
        await query.message.edit_text(
            f"💸 <b>WITHDRAWAL MANAGEMENT</b>\n\n📉 Current minimum: <code>{get_min_withdraw():.2f} BDT</code>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 BACK TO ADMIN", callback_data="withdraw_admin_close", api_kwargs={"style": "primary"})
            ]]),
        )
        return

    if data == "withdraw_admin_close":
        await query.message.edit_text("🔙 Open the Admin Panel menu to continue.")
        return

    if data.startswith("admin_approve_"):
        if not is_admin(uid):
            await query.answer("Admin access required.", show_alert=True)
            return
        await admin_approve_withdraw(update, context, data.replace("admin_approve_", ""))
        return

    if data.startswith("admin_reject_"):
        if not is_admin(uid):
            await query.answer("Admin access required.", show_alert=True)
            return
        await admin_reject_withdraw(update, context, data.replace("admin_reject_", ""))
        return

    if data.startswith("copy_text_"):
        await query.answer(f"✅ Copied: {data.replace('copy_text_', '')}", show_alert=True)
        return

    if data.startswith("my_ref_"):
        target_uid = data.replace("my_ref_", "")
        all_logs = load_data(ACTIVITY_LOGS_FILE)
        my_referrals = [log for log in all_logs if str(log.get('uid')) == str(target_uid) and log.get('action') == "REFERRAL_JOINED"]
        content = f"👥 REFERRAL REPORT — {target_uid}\n━━━━━━━━━━━━\nTOTAL: {len(my_referrals)}\n\n"
        for i, log in enumerate(my_referrals, 1):
            try:
                dt_obj = datetime.fromisoformat(log['timestamp'])
                ref_id = log.get('details', {}).get('referred_user', 'N/A')
                content += f"{i}. ID: {ref_id} | {dt_obj.strftime('%d/%m/%Y %I:%M %p')}\n"
            except: continue
        f = io.BytesIO(content.encode()); f.name = f"REF_{target_uid}.txt"
        await context.bot.send_document(chat_id=uid, document=f, caption="✅ **REFERRAL DATA**", parse_mode="Markdown")
        return

    if data.startswith("full_logs_"):
        target_uid = data.replace("full_logs_", "")
        stats = get_user_stats(target_uid)
        all_logs = load_data(ACTIVITY_LOGS_FILE)
        user_db = load_data(USER_DATA_FILE)
        user_info = user_db.get(str(target_uid), {})
        user_otps = [log for log in all_logs if str(log.get('uid')) == str(target_uid) and log.get('action') == "OTP_RECEIVED"]
        content = (
            f"📊 USER DATA REPORT — {target_uid}\n"
            f"💰 BALANCE: {user_info.get('balance', 0):.2f} BDT\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"TODAY NUMBERS: {stats['today_numbers']}\nTODAY OTPS: {stats['today_otps']}\n"
            f"7D NUMBERS: {stats['last7d_numbers']}\n7D OTPS: {stats['last7d_otps']}\n"
            f"TOTAL NUMBERS: {stats['total_numbers']}\nTOTAL OTPS: {stats['total_otps']}\n"
            f"━━━━━━━━━━━━━━━━━━\n\nOTP LOGS:\n"
        )
        for i, log in enumerate(user_otps, 1):
            try:
                dt_obj = datetime.fromisoformat(log['timestamp'])
                d = log.get('details', {})
                content += f"{i}. {dt_obj.strftime('%d/%m/%Y %I:%M %p')}\n   📞 {d.get('number', 'N/A')}\n   🔑 {d.get('otp', 'N/A')}\n\n"
            except: continue
        f = io.BytesIO(content.encode()); f.name = f"USER_{target_uid}.txt"
        await context.bot.send_document(chat_id=uid, document=f, caption=f"✅ <b>DATA FOR USER: <code>{target_uid}</code></b>", parse_mode="HTML")
        return

# ==================== MAIN EXECUTION ====================
async def post_init(application):
    for _ in range(MAX_WORKERS):
        asyncio.create_task(worker())
    asyncio.create_task(monitor_loop(application))
    asyncio.create_task(_bg_refresh_ranges())

async def post_shutdown(application):
    await client_async.aclose()

def main():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("get1number", get1number_command))
    app.add_handler(CommandHandler("searchotp", searchotp_command))
    app.add_handler(CommandHandler("balance", balance_command))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("refer", refer_command_slash))
    app.add_handler(CommandHandler("leaderboard", leaderboard_command_slash))

    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("🚀 BOT RUNNING...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    # Render-এর জন্য ব্যাকগ্রাউন্ডে Flask ওয়েব সার্ভার চালু করা হচ্ছে
    threading.Thread(target=run_flask, daemon=True).start()
    
    asyncio.set_event_loop(asyncio.new_event_loop())
    main()
