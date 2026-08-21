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
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is running online 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

# ==================== LOCAL CONFIGURATION ====================
CONFIG_BOT_TOKEN = "8413412337:AAHy_S2urriXztED2c3c25IrFruSAGRJUgM"
CONFIG_ZENEX_API_KEY = "ZNX_M1I5X6MKBRTDZTJ7MY7R6BRG"
CONFIG_ZENEX_BASE_URL = "https://api.zenexnetwork.com"
CONFIG_ADMIN_ID = 8991828975
CONFIG_OTP_GROUP_ID = -1003964512828

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

ADMIN_ID = int(os.getenv("ADMIN_ID", str(CONFIG_ADMIN_ID or "8991828975")))
ADMINS = [ADMIN_ID]
OTP_GROUP_ID = int(os.getenv("OTP_GROUP_ID", str(CONFIG_OTP_GROUP_ID or "-1003964512828")))

# ==================== SYSTEM DYNAMIC SETTINGS ====================
_settings_cache = None

def load_settings():
    global _settings_cache
    if _settings_cache is not None:
        return _settings_cache
    default = {
        "active_panel": "zenex",
        "zenex_api_key": os.getenv("ZENEX_API_KEY", "").strip() or CONFIG_ZENEX_API_KEY.strip(),
        "zenex_base_url": os.getenv("ZENEX_BASE_URL", CONFIG_ZENEX_BASE_URL),
        "panel_url": f"https://t.me/Zenex_Number_bot?start={ADMIN_ID}",
        "allowed_services": ["Instagram","Facebook","WhatsApp","TikTok","Telegram","Discord","PayPal","Imo"],
        "otp_group_url": "https://t.me/+31eV11IT7WQzMjI9",
        "channel_url": "https://t.me/MinoXofficial0",
        "support_username": "@support",
        "maintenance_mode": False,
        "cooldown_time": 1.0,
        "min_withdraw": 25.0,
        "otp_bonus": 0.20,
        "referral_bonus": 0.0,
        "admins": [ADMIN_ID],
        "owners": [ADMIN_ID],
        "otp_group_chat_id": None,
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
    url = str(url).strip().rstrip('/')
    url = re.sub(r'(/v1|/api|/api/v1)$', '', url)
    return url.rstrip('/')

def get_api_credentials():
    settings = load_settings()
    env_api_key = os.getenv("ZENEX_API_KEY", "").strip() or CONFIG_ZENEX_API_KEY.strip()
    configured_api_key = str(settings.get("zenex_api_key", "")).strip()
    return (env_api_key or configured_api_key,
            clean_base_url(settings.get("zenex_base_url","https://api.zenexnetwork.com")))

def get_api_urls(base_url):
    base = str(base_url).strip().rstrip('/')
    return {"getnum": f"{base}/v1/getnum",
            "liveaccess": f"{base}/v1/active-ranges",
            "otp": f"{base}/v1/numsuccess/info"}

def get_api_headers(api_key):
    return {"mapikey": api_key}

WELCOME_MESSAGE = """✨ 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 SPIDER BOT🚀 ✨ 
━━━━━━━━━━━━━━━━━━━━━━
🚀 Enjoy Premium Quality Service 🚀"""

OTP_RATE = 0.20
REFERRAL_PRICE = 0
MIN_WITHDRAW = 25
MAX_WITHDRAW = 10000

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
_ranges_cache = {"data": None, "updated_at": 0.0, "fetching": False}

# ==================== KEYBOARD WITH COLORS & ICONS ====================

def make_reply_btn(text, emoji_id=None, style=None):
    api_kwargs = {}
    if emoji_id:
        api_kwargs['icon_custom_emoji_id'] = str(emoji_id)
    if style:
        api_kwargs['style'] = style
    return KeyboardButton(text=text, api_kwargs=api_kwargs if api_kwargs else None)

def main_keyboard(user_id):
    # আপনার দেওয়া ছবি অনুযায়ী হুবহু সবুজ (success) ও নীল (primary) কালার ম্যাপিং
    keyboard = [
        [
            make_reply_btn("GET NUMBER", emoji_id="5228843986747147814", style="success"),
            make_reply_btn("TRAFFIC", emoji_id="5244837092042750681", style="primary")
        ],
        [
            make_reply_btn("BALANCE", emoji_id="6233367447789899509", style="success"),
            make_reply_btn("REFER & EARN", emoji_id="5420396762189831222", style="primary")
        ],
        [
            make_reply_btn("LEADERBOARD", emoji_id="5228875876879318811", style="primary"),
            make_reply_btn("SUPPORT", emoji_id="5267294466716244344", style="success")
        ],
        [
            make_reply_btn("GET 2FA", emoji_id="5296369303661067030", style="primary"),
            make_reply_btn("PROFILE", emoji_id="5422444280473998663", style="success")
        ]
    ]
    if is_admin(user_id):
        keyboard.append([make_reply_btn("ADMIN PANEL", emoji_id="5350396951407895212", style="primary")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def cancel_keyboard():
    return ReplyKeyboardMarkup([[make_reply_btn("CANCEL", style="primary")]], resize_keyboard=True)

def admin_main_keyboard():
    return ReplyKeyboardMarkup([
        [make_reply_btn("USER MANAGEMENT", style="primary"), make_reply_btn("SYSTEM CONFIGURATION", style="primary")],
        [make_reply_btn("BOT SETTINGS", style="primary"), make_reply_btn("SERVICE MANAGEMENT", style="primary")],
        [make_reply_btn("WITHDRAWAL MANAGEMENT", style="primary"), make_reply_btn("SUPPORT CHAT", style="primary")],
        [make_reply_btn("⏳ PENDING WITHDRAWALS", style="primary")],
        [make_reply_btn("BACK TO MAIN", style="success")]
    ], resize_keyboard=True)

def withdraw_method_keyboard():
    return ReplyKeyboardMarkup([
        [make_reply_btn("BKASH", style="primary"), make_reply_btn("NAGAD", style="primary")],
        [make_reply_btn("ROCKET", style="primary"), make_reply_btn("BINANCE", style="primary")],
        [make_reply_btn("CANCEL", style="primary")]
    ], resize_keyboard=True)

# ==================== COUNTRY & HELPER FUNCTIONS ====================

def get_country_info(number):
    number = str(number).strip()
    country_map = {
        "2376": ("🇨🇲", "Cameroon"), "2250": ("🇨🇮", "Ivory Coast"), "2613": ("🇲🇬", "Madagascar"),
        "4077": ("🇷🇴", "Romania"), "237": ("🇨🇲", "Cameroon"), "225": ("🇨🇮", "Ivory Coast"),
        "261": ("🇲🇬", "Madagascar"), "20": ("🇪🇬", "Egypt"), "27": ("🇿🇦", "South Africa"),
        "234": ("🇳🇬", "Nigeria"), "254": ("🇰🇪", "Kenya"), "233": ("🇬🇭", "Ghana"),
        "212": ("🇲🇦", "Morocco"), "213": ("🇩🇿", "Algeria"), "216": ("🇹🇳", "Tunisia"),
        "218": ("🇱🇾", "Libya"), "249": ("🇸🇩", "Sudan"), "251": ("🇪🇹", "Ethiopia"),
        "255": ("🇹🇿", "Tanzania"), "256": ("🇺🇬", "Uganda"), "880": ("🇧🇩", "Bangladesh"),
        "91": ("🇮🇳", "India"), "92": ("🇵🇰", "Pakistan"), "1": ("🇺🇸", "United States"),
        "44": ("🇬🇧", "United Kingdom"), "60": ("🇲🇾", "Malaysia"), "62": ("🇮🇩", "Indonesia"),
        "63": ("🇵🇭", "Philippines"), "966": ("🇸🇦", "Saudi Arabia"), "971": ("🇦🇪", "UAE"),
    }
    clean_num = str(number).replace('+', '').replace(' ', '').replace('-', '').strip()
    sorted_prefixes = sorted(country_map.keys(), key=len, reverse=True)
    for prefix in sorted_prefixes:
        if clean_num.startswith(prefix):
            return country_map[prefix]
    return ("🌍", "Unknown")

def detect_service(full_sms):
    if not full_sms: return "SMS SERVICE"
    sms_lower = full_sms.lower()
    for kw, sname in [("facebook","FACEBOOK"),("fb","FACEBOOK"),("instagram","INSTAGRAM"),("insta","INSTAGRAM"),
                      ("tiktok","TIKTOK"),("whatsapp","WHATSAPP"),("telegram","TELEGRAM"),("discord","DISCORD"),
                      ("imo","IMO"),("binance","BINANCE"),("bkash","BKASH"),("nagad","NAGAD")]:
        if kw in sms_lower: return sname
    return "SMS SERVICE"

def format_balance(balance): return f"{balance:.2f}"

def extract_otp(text):
    if not text or text == "No Content": return "N/A"
    spaced_otp = re.search(r'\b(\d{3}\s\d{3})\b', text)
    if spaced_otp: return spaced_otp.group(1).replace(" ", "")
    match = re.search(r'\b(\d{4,8})\b', text)
    return match.group(1) if match else "N/A"

def normalize_number(num): return re.sub(r'\D', '', str(num))
def mask_number(num): return f"{num[:4]}****{num[-6:]}" if len(num) > 6 else num
def get_date_reset_time(): return datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 0, 0)
def is_valid_bangladesh_number(number): return len(re.sub(r'\D', '', str(number))) == 11 and str(number).startswith('01')

def is_admin(user_id):
    try: return int(user_id) in get_admin_ids()
    except: return False

def get_admin_ids():
    candidates = [ADMIN_ID, CONFIG_ADMIN_ID]
    try:
        configured = load_settings().get("admins", [])
        if isinstance(configured, list): candidates.extend(configured)
    except: pass
    admin_ids = []
    for c in candidates:
        try:
            val = int(c)
            if val > 0 and val not in admin_ids: admin_ids.append(val)
        except: continue
    return admin_ids

def get_min_withdraw():
    try: return max(0.0, float(load_settings().get("min_withdraw", MIN_WITHDRAW)))
    except: return float(MIN_WITHDRAW)

# ==================== DATABASE & STATS ====================

def load_data(filename=USER_DATA_FILE):
    if not os.path.exists(filename):
        with open(filename, "w") as f: json.dump({}, f)
        return {}
    try:
        with open(filename, "r") as f: return json.load(f)
    except: return {}

def save_data(data, filename=USER_DATA_FILE):
    with open(filename, "w") as f: json.dump(data, f, indent=4)

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

def load_stats():
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, "w") as f: json.dump({}, f)
        return {}
    try:
        with open(STATS_FILE, "r") as f: return json.load(f)
    except: return {}

def save_stats(stats):
    with open(STATS_FILE, "w") as f: json.dump(stats, f, indent=4)

def add_number_taken(uid, count=1):
    uid = str(uid)
    stats = load_stats()
    if uid not in stats: stats[uid] = {"numbers_taken": [], "otps_received": []}
    now = datetime.now().isoformat()
    for _ in range(count): stats[uid]["numbers_taken"].append(now)
    save_stats(stats)

def add_otp_received(uid):
    uid = str(uid)
    stats = load_stats()
    if uid not in stats: stats[uid] = {"numbers_taken": [], "otps_received": []}
    stats[uid]["otps_received"].append(datetime.now().isoformat())
    save_stats(stats)

def get_user_stats(uid):
    uid = str(uid)
    stats = load_stats()
    user_stats = stats.get(uid, {"numbers_taken": [], "otps_received": []})
    now = datetime.now()
    today_midnight = get_date_reset_time()
    last_7d = now - timedelta(days=7)
    numbers_taken = user_stats.get("numbers_taken", [])
    otps_received = user_stats.get("otps_received", [])
    return {
        "total_numbers": len(numbers_taken),
        "total_otps": len(otps_received),
        "today_numbers": sum(1 for t in numbers_taken if datetime.fromisoformat(t) >= today_midnight),
        "today_otps": sum(1 for t in otps_received if datetime.fromisoformat(t) >= today_midnight),
        "last7d_numbers": sum(1 for t in numbers_taken if datetime.fromisoformat(t) > last_7d),
        "last7d_otps": sum(1 for t in otps_received if datetime.fromisoformat(t) > last_7d)
    }

def is_user_banned(uid):
    if not os.path.exists(BANNED_USERS_FILE): return False
    try:
        with open(BANNED_USERS_FILE, "r") as f: return str(uid) in json.load(f)
    except: return False

def get_referral_count(uid):
    if not os.path.exists(REFERRAL_DATA_FILE): return 0
    try:
        with open(REFERRAL_DATA_FILE, "r") as f: return json.load(f).get(str(uid), {}).get("referral_count", 0)
    except: return 0

# ==================== LIVE TRAFFIC COMMAND ====================

async def traffic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return

    msg = (
        "📈 <b>LIVE NETWORK TRAFFIC (BY COUNTRY)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "• <b>Facebook:</b>\n"
        "  🌍 Top Country: 🇹🇿 <b>Tanzania</b> 🔥 <code>[HIGH TRAFFIC]</code>\n\n"
        "• <b>Instagram:</b>\n"
        "  🌍 Top Country: 🇲🇬 <b>Madagascar</b> 🔥 <code>[HIGH TRAFFIC]</code>\n\n"
        "• <b>WhatsApp:</b>\n"
        "  🌍 Top Country: 🇲🇬 <b>Madagascar</b> 🔥 <code>[HIGH TRAFFIC]</code>\n\n"
        "• <b>TikTok:</b>\n"
        "  🌍 Top Country: 🇨🇮 <b>Ivory Coast</b> 🔥 <code>[HIGH TRAFFIC]</code>\n\n"
        "• <b>Telegram:</b>\n"
        "  🌍 Top Country: 🇨🇲 <b>Cameroon</b> 🔥 <code>[HIGH TRAFFIC]</code>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ <i>Fastest OTP arrival rate right now!</i>"
    )
    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=main_keyboard(uid))

# ==================== NUMBER & API SYSTEM ====================

async def fetch_top55_ranges_by_app():
    settings = load_settings()
    api_key, base_url = get_api_credentials()
    urls = get_api_urls(base_url)
    headers = get_api_headers(api_key)
    try:
        r = await client_async.get(urls["liveaccess"], headers=headers, timeout=httpx.Timeout(5.0, connect=1.5))
        data = r.json()
        ranges_list = data if isinstance(data, list) else data.get("ranges", [])
        if not ranges_list: return {}, None
        top = {}
        for obj in ranges_list:
            if isinstance(obj, dict):
                rng = str(obj.get("range") or obj.get("prefix") or "").strip().upper()
                service = str(obj.get("service") or obj.get("app") or "Unknown").capitalize()
                if rng:
                    if service not in top: top[service] = {"ranges": []}
                    if rng not in top[service]["ranges"]: top[service]["ranges"].append(rng)
        return top, None
    except Exception as e:
        return None, str(e)

async def fetch_number_async(range_str):
    try:
        api_key, base_url = get_api_credentials()
        urls = get_api_urls(base_url)
        headers = {**get_api_headers(api_key), "Accept": "application/json"}
        r = await client_async.post(
            urls["getnum"],
            json={"range": range_str.upper(), "is_national": False, "remove_plus": False},
            headers=headers,
            timeout=httpx.Timeout(8.0, connect=2.0, read=6.0),
        )
        if 200 <= r.status_code < 300:
            d = r.json()
            num = d.get("number") or d.get("phone") or d.get("mobile")
            if num:
                return {"number": num, "otp_now": bool(d.get("otp")), "otp": d.get("otp"), "sms": d.get("sms")}
    except: pass
    return None

async def register_active_number(uid, number, range_text, app_name=None):
    clean_num = normalize_number(number)
    if len(clean_num) < 7: return None
    async with number_assignment_lock:
        if clean_num in active_numbers: return None
        active_numbers[clean_num] = {
            "uid": uid, "range": str(range_text).strip().upper(),
            "app": app_name or "", "timestamp": datetime.now()
        }
    return clean_num

async def show_app_selection(update, context):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return

    top, _ = await fetch_top55_ranges_by_app()
    apps = list(top.keys()) if top else ["WhatsApp", "Telegram", "Facebook", "Instagram", "TikTok"]
    btns = [InlineKeyboardButton(app, callback_data=f"sel_app_{app}", style="primary") for app in apps]
    rows = [btns[i:i+2] for i in range(0, len(btns), 2)]
    rows.append([InlineKeyboardButton("⚙️ CUSTOM RANGE", callback_data="custom_range", style="primary")])
    await update.message.reply_text("📞 <b>SELECT APP TO GET NUMBER</b>\n━━━━━━━━━━━━━━━━━━━━━", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(rows))

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
                res = r.json()
                otps = res if isinstance(res, list) else (res.get("data") if isinstance(res.get("data"), list) else res.get("otps", []))
                paid_data = load_data(PAID_SMS_FILE)
                for otp in otps:
                    num = normalize_number(otp.get("number", ""))
                    full_sms = otp.get("otp") or otp.get("sms") or otp.get("message") or ""
                    otp_code = extract_otp(full_sms)
                    sms_key = str(otp.get("nid") or f"{num}_{full_sms}")
                    if num in active_numbers and sms_key not in paid_data and otp_code != "N/A":
                        details = active_numbers[num]
                        paid_data[sms_key] = {"uid": details["uid"], "otp": otp_code}
                        save_data(paid_data, PAID_SMS_FILE)
                        await update_db_balance(details["uid"], settings.get("otp_bonus", OTP_RATE))
                        add_otp_received(details["uid"])
                        country_flag, _ = get_country_info(num)
                        btn_copy = InlineKeyboardButton(f"🔑 {otp_code}", callback_data=f"copy_text_{otp_code}")
                        await app.bot.send_message(
                            details["uid"],
                            f"{country_flag} +{num}\n🔑 <b>OTP:</b> <code>{otp_code}</code>\n📩 {full_sms}",
                            parse_mode="HTML",
                            reply_markup=InlineKeyboardMarkup([[btn_copy]])
                        )
        except: pass
        await asyncio.sleep(CHECK_INTERVAL)

# ==================== MESSAGE HANDLER ====================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    uid = update.effective_user.id
    raw_text = update.message.text.strip()
    text = raw_text.upper()

    # Cancel handler
    if "CANCEL" in text:
        context.user_data.clear()
        await update.message.reply_text("❌ CANCELLED", reply_markup=main_keyboard(uid))
        return

    # Button: GET NUMBER
    if "GET NUMBER" in text:
        await show_app_selection(update, context)
        return

    # Button: TRAFFIC
    if "TRAFFIC" in text:
        await traffic_command(update, context)
        return

    # Button: BALANCE
    if "BALANCE" in text:
        balance = get_user(uid)['balance']
        await update.message.reply_text(
            f"💰 <b>YOUR CURRENT BALANCE</b>\n\n<blockquote>💵 TOTAL: <b>{format_balance(balance)} BDT</b></blockquote>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💸 WITHDRAW", callback_data="withdraw_start", style="primary")]])
        )
        return

    # Button: REFER & EARN
    if "REFER" in text:
        bot_info = await context.bot.get_me()
        link = f"https://t.me/{bot_info.username}?start={uid}"
        ref_count = get_referral_count(uid)
        await update.message.reply_text(
            f"🎁 <b>REFER AND EARN SYSTEM</b> 🎁\n\n"
            f"<b>🔗 YOUR REFERRAL LINK:</b>\n<blockquote><code>{link}</code></blockquote>\n\n"
            f"👥 TOTAL REFERS: <b>{ref_count}</b>\n💰 TOTAL EARNED: <b>{format_balance(ref_count * REFERRAL_PRICE)} BDT</b>",
            parse_mode="HTML"
        )
        return

    # Button: LEADERBOARD
    if "LEADERBOARD" in text:
        stats_data = load_stats()
        today_midnight = get_date_reset_time()
        counts = []
        for u_str, u_s in stats_data.items():
            c = sum(1 for ts in u_s.get("otps_received", []) if datetime.fromisoformat(ts) >= today_midnight)
            if c > 0: counts.append((u_str, c))
        counts.sort(key=lambda x: x[1], reverse=True)
        top10 = counts[:10]
        if not top10:
            msg = "<b>🏆 TOP 10 OTP LEADERBOARD (TODAY) 🏆</b>\n━━━━━━━━━━━━━━━━━━━━\n\n❌ আজ পর্যন্ত কেউ OTP পায়নি।"
        else:
            msg = "<b>🏆 TOP 10 OTP LEADERBOARD (TODAY) 🏆</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
            for i, (u, cnt) in enumerate(top10, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}️⃣"
                msg += f"{medal} User <code>{u}</code> — 🔑 <b>{cnt} OTPs</b>\n"
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=main_keyboard(uid))
        return

    # Button: SUPPORT
    if "SUPPORT" in text:
        if is_admin(uid):
            await update.message.reply_text("💬 <b>SUPPORT CHAT</b>\n\nUser মেসেজে Reply করলে উত্তর যাবে।", parse_mode="HTML", reply_markup=main_keyboard(uid))
            return
        context.user_data["support_mode"] = True
        await update.message.reply_text("💬 <b>SUPPORT CHAT</b>\n\nআপনার সমস্যা লিখে পাঠান, অ্যাডমিন উত্তর দেবে:", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    # Button: PROFILE
    if "PROFILE" in text:
        user_data = get_user(uid)
        stats = get_user_stats(uid)
        user = update.effective_user
        profile_text = (
            f"👤 <b>YOUR PROFILE</b>\n\n"
            f"🏷️ NAME: <b>{html.escape(user.full_name)}</b>\n"
            f"🆔 USER ID: <code>{uid}</code>\n"
            f"💵 BALANCE: <b>{format_balance(user_data.get('balance', 0))} BDT</b>\n\n"
            f"✨ <b>TODAY:</b> 📱 Numbers: {stats['today_numbers']} | 🔑 OTPs: {stats['today_otps']}\n"
            f"🌐 <b>ALL TIME:</b> 📱 Numbers: {stats['total_numbers']} | 🔑 OTPs: {stats['total_otps']}"
        )
        await update.message.reply_text(profile_text, parse_mode="HTML", reply_markup=main_keyboard(uid))
        return

    # Button: GET 2FA
    if "2FA" in text:
        context.user_data["mode"] = "get_2fa"
        await update.message.reply_text("🔑 <b>ENTER YOUR 2FA SECRET KEY:</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    # 2FA Processor
    if context.user_data.get("mode") == "get_2fa":
        context.user_data["mode"] = None
        try:
            clean_secret = raw_text.replace(" ", "").upper().strip()
            key = base64.b32decode(clean_secret, casefold=True)
            t = int(time.time()) // 30
            msg_bytes = struct.pack(">Q", t)
            h = hmac.new(key, msg_bytes, hashlib.sha1).digest()
            o = h[-1] & 0xf
            code = f"{(struct.unpack('>I', h[o:o+4])[0] & 0x7fffffff) % 1_000_000:06d}"
            await update.message.reply_text(f"✅ <b>2FA CODE:</b> <code>{code}</code>\n⏳ Expires in 30s", parse_mode="HTML", reply_markup=main_keyboard(uid))
        except:
            await update.message.reply_text("❌ Invalid 2FA Secret Key!", reply_markup=main_keyboard(uid))
        return

    # Support Message to Admins
    if context.user_data.get("support_mode"):
        context.user_data["support_mode"] = False
        for admin_id in get_admin_ids():
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"📩 <b>SUPPORT MESSAGE</b> from <code>{uid}</code>:\n\n{html.escape(raw_text)}",
                    parse_mode="HTML"
                )
            except: pass
        await update.message.reply_text("✅ আপনার মেসেজ অ্যাডমিনের কাছে পাঠানো হয়েছে!", reply_markup=main_keyboard(uid))
        return

    # Admin Panel
    if "ADMIN PANEL" in text and is_admin(uid):
        await update.message.reply_text("⚙️ <b>ADMIN PANEL</b>", parse_mode="HTML", reply_markup=admin_main_keyboard())
        return

    if "BACK TO MAIN" in text:
        await update.message.reply_text("🔙 Main Menu", reply_markup=main_keyboard(uid))
        return

    await update.message.reply_text("🔹 অনুগ্রহ করে নিচের মেনু বাটন ব্যবহার করুন:", reply_markup=main_keyboard(uid))

# ==================== CALLBACK QUERY ====================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    data = query.data
    await query.answer()

    if data.startswith("sel_app_"):
        app_name = data[8:]
        range_text = "234XXX"
        res = await fetch_number_async(range_text)
        if res:
            clean_num = await register_active_number(uid, res["number"], range_text, app_name)
            flag, country_name = get_country_info(clean_num)
            add_number_taken(uid, 1)
            await query.message.edit_text(
                f"✅ <b>YOUR NUMBER DETAILS</b>\n\n"
                f"<blockquote>🌍 COUNTRY: {flag} {country_name}\n"
                f"📱 APP: {app_name}\n"
                f"📞 NUMBER: <code>+{clean_num}</code></blockquote>\n\n"
                f"📩 SMS STATUS: ⏳ WAITING...",
                parse_mode="HTML"
            )
        else:
            await query.message.edit_text("❌ সার্ভারে এই মুহূর্তে নাম্বার নেই। পরে চেষ্টা করুন।")
        return

    if data == "withdraw_start":
        balance = get_user(uid)['balance']
        if balance < get_min_withdraw():
            await query.message.reply_text(f"📉 Minimum withdraw is {get_min_withdraw():.2f} BDT")
            return
        await query.message.reply_text("💳 Select Payment Method:", reply_markup=withdraw_method_keyboard())
        return

    if data.startswith("copy_text_"):
        await query.answer(f"✅ OTP Copied: {data.replace('copy_text_', '')}", show_alert=True)
        return

# ==================== START & MAIN INIT ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    get_user(uid)
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode="HTML")
    await update.message.reply_text("🔹 মেনু থেকে আপনার সার্ভিস নির্বাচন করুন:", reply_markup=main_keyboard(uid))

async def post_init(application):
    asyncio.create_task(monitor_loop(application))

def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not configured.")

    # Start Flask Web Server for Render
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("traffic", traffic_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("🚀 BOT RUNNING WITH FULL COLOR THEME & TRAFFIC SYSTEM...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.set_event_loop(asyncio.new_event_loop())
    main()
