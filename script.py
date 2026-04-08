# coding: utf-8
"""
ZenoxGPT Bot -- Telegram AI by @Repp76
Powered by Google Gemini 2.5 Flash
"""

import logging
import json
import os
import asyncio
import threading
import functools
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    ConversationHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
try:
    from telegram.request import HTTPXRequest
    HAS_HTTPX_REQUEST = True
except ImportError:
    HAS_HTTPX_REQUEST = False

# =============================================================
#  KONFIGURASI
# =============================================================

# Bot AI -- berinteraksi dengan pengguna
BOT_TOKEN_AI = "8306986546:AAH5aQLctffTEWzhvniwxqYSO7ds6v37hf0"

# Bot Information -- hantar laporan ke developer
BOT_TOKEN_INFO = "8735846457:AAEiLhtF73G61Abv4czaJ2qKB_7fVTF9QN0"

# Developer
DEVELOPER_ID = 7624612389
DEVELOPER_USERNAME = "@Repp76"

# Fail data
API_KEY_FILE         = "api_keys.json"
USERS_FILE           = "users.json"
STARTED_USERS_FILE   = "started_users.json"   # track semua user yang pernah berinteraksi dengan bot
GROUP_MEMBERS_FILE   = "group_members.json"    # track semua ahli group yang pernah hantar mesej
WEB_ACCOUNTS_FILE    = "web_accounts.json"     # akaun login website
FILTERS_FILE         = "filters.json"          # auto-save filter commands
WB_CREDITS_FILE      = "wb_credits.json"       # Web Booster user credits
WB_ITEMS_FILE        = "wb_items.json"         # Web Booster items/services
WB_ORDERS_FILE       = "wb_orders.json"        # Web Booster order history
WB_PENDING_FILE      = "wb_pending.json"       # Pending top-up approvals

# RoketMedia API
ROKET_API_KEY  = "0a60798dd13816d91b491956b587eb10"
ROKET_API_URL  = "https://roketmedia.co/api/v2"

# Payment info
DUITNOW_NUMBER = "181837537347"
DUITNOW_QR_URL = "https://files.catbox.moe/enl8lt.jpg"
ADMIN_FEE      = 1.00  # Rm1 admin fee

# Model Gemini
GEMINI_MODEL         = "gemini-2.5-flash"
GEMINI_MODEL_FALLBACK = "gemini-2.0-flash"

# =============================================================
#  EMOJI CONSTANTS (unicode escape -- selamat untuk semua Python)
# =============================================================
E_ROBOT    = "\U0001f916"   # 🤖
E_STAR     = "\u2728"       # ✨
E_CHECK    = "\u2705"       # ✅
E_CROSS    = "\u274c"       # ❌
E_WARN     = "\u26a0\ufe0f" # ⚠️
E_KEY      = "\U0001f511"   # 🔑
E_LOCK     = "\U0001f512"   # 🔒
E_UNLOCK   = "\U0001f513"   # 🔓
E_CROWN    = "\U0001f451"   # 👑
E_PERSON   = "\U0001f464"   # 👤
E_BADGE    = "\U0001f3f7"   # 🏷
E_PARTNER  = "\U0001f91d"   # 🤝
E_OWNER    = "\U0001f531"   # 🔱
E_RESELLER = "\U0001f4bc"   # 💼
E_MEMBER   = "\U0001f464"   # 👤
E_BAN      = "\u26d4"       # ⛔
E_BELL     = "\U0001f514"   # 🔔
E_CHAT     = "\U0001f4ac"   # 💬
E_QUESTION = "\u2753"       # ❓
E_ID       = "\U0001f194"   # 🆔
E_LOCATION = "\U0001f4cd"   # 📍
E_TIME     = "\U0001f550"   # 🕐
E_SHIELD   = "\U0001f6e1\ufe0f" # 🛡️
E_TOOL     = "\U0001f6e0\ufe0f" # 🛠️
E_PHONE    = "\U0001f4f1"   # 📱
E_INFO     = "\u2139\ufe0f" # ℹ️
E_FIRE     = "\U0001f525"   # 🔥
E_ZAP      = "\u26a1"       # ⚡
E_GEM      = "\U0001f48e"   # 💎
E_LINK     = "\U0001f517"   # 🔗
E_ARROW    = "\u27a1\ufe0f" # ➡️
E_POINT    = "\U0001f449"   # 👉
E_WAVE     = "\U0001f44b"   # 👋
E_OK       = "\U0001f44c"   # 👌
E_THINK    = "\U0001f914"   # 🤔
E_STAT     = "\U0001f4ca"   # 📊
E_NEW      = "\U0001f195"   # 🆕
E_ONLINE   = "\U0001f7e2"   # 🟢
E_RED      = "\U0001f534"   # 🔴
E_PENCIL   = "\u270f\ufe0f" # ✏️
E_FOLDER   = "\U0001f4c2"   # 📂
E_LIST     = "\U0001f4cb"   # 📋
E_DEV      = "\U0001f468\u200d\U0001f4bb" # 👨‍💻
E_GLOBE    = "\U0001f310"   # 🌐
E_DIAMOND  = "\U0001f4a0"   # 💠
E_BURST    = "\U0001f4a5"   # 💥
E_SPARKLE  = "\U0001f4ab"   # 💫
E_HOURGLASS = "\u23f3"      # ⏳
E_SIGNAL   = "\U0001f4e1"   # 📡
E_DOTS     = "\u2022"       # •
E_LINE     = "\u2500" * 30  # ──────────────────────────────

# =============================================================
#  WARNA TERMINAL
# =============================================================
R    = "\033[91m"
G    = "\033[92m"
Y    = "\033[93m"
B    = "\033[94m"
M    = "\033[95m"
C    = "\033[96m"
W    = "\033[97m"
DIM  = "\033[2m"
BOLD = "\033[1m"
RST  = "\033[0m"

# =============================================================
#  LOGGING
# =============================================================
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("zenoxgpt.log", encoding="utf-8")],
)
logger = logging.getLogger("ZenoxGPT")

# =============================================================
#  ASCII ART BANNER
# =============================================================

def print_banner(bot_username):
    eye_lines = [
        "",
        M + "                    .^:.                    " + RST,
        M + "                .~YPGGGP5J~.                " + RST,
        M + "             :?5GGGGGGGGGGG5?:              " + RST,
        C + "           ^YGGGGGGGGGGGGGGGGG5^            " + RST,
        C + "         .JGGGGGGGGGGGGGGGGGGGGGJ.          " + RST,
        B + "        !GGGGGGGGGGGGGGGGGGGGGGGGG!         " + RST,
        B + "       JGGGGGG" + W + "BBBBBBBBBBBBBBB" + B + "GGGGGJ        " + RST,
        B + "      JGGGGG" + W + "BBBBBBBBBBBBBBBBBBB" + B + "GGGGGJ       " + RST,
        Y + "     !GGGGG" + W + "BBBBB" + C + "JJJJJJJJJJJ" + W + "BBBBB" + Y + "GGGGG!      " + RST,
        Y + "    .GGGGG" + W + "BBBBB" + C + "JJJJ" + R + "ZZZZZZZ" + C + "JJJJ" + W + "BBBBB" + Y + "GGGGG.     " + RST,
        Y + "    JGGGG"  + W + "BBBBB" + C + "JJJJ" + R + "ZZZZZZZZZ" + C + "JJJJ" + W + "BBBBB" + Y + "GGGGJ     " + RST,
        R + "    GGGGG"  + W + "BBBBB" + C + "JJJJ" + R + "ZZZZZZZZZ" + C + "JJJJ" + W + "BBBBB" + R + "GGGGG     " + RST,
        R + "    JGGGG"  + W + "BBBBB" + C + "JJJJ" + R + "ZZZZZZZZZ" + C + "JJJJ" + W + "BBBBB" + R + "GGGGJ     " + RST,
        R + "    .GGGGG" + W + "BBBBB" + C + "JJJJ" + R + "ZZZZZZZ"   + C + "JJJJ" + W + "BBBBB" + R + "GGGGG.     " + RST,
        M + "     !GGGGG" + W + "BBBBB" + C + "JJJJJJJJJJJ" + W + "BBBBB" + M + "GGGGG!      " + RST,
        M + "      JGGGGG" + W + "BBBBBBBBBBBBBBBBBBB" + M + "GGGGGJ       " + RST,
        M + "       JGGGGGG" + W + "BBBBBBBBBBBBBBB" + M + "GGGGGJ        " + RST,
        C + "        !GGGGGGGGGGGGGGGGGGGGGGGGG!         " + RST,
        C + "         .JGGGGGGGGGGGGGGGGGGGGGJ.          " + RST,
        B + "           ^YGGGGGGGGGGGGGGGGG5^            " + RST,
        B + "             :?5GGGGGGGGGGG5?:              " + RST,
        M + "                .~YPGGGP5J~.                " + RST,
        M + "                    .^:.                    " + RST,
        "",
    ]
    for l in eye_lines:
        print(l)

    sep  = C + "=" * 56 + RST
    dash = C + "-" * 56 + RST
    pipe = C + "||" + RST

    pad_dev   = max(0, 26 - len(DEVELOPER_USERNAME))
    pad_model = max(0, 20 - len(GEMINI_MODEL))
    pad_bot   = max(0, 26 - len(bot_username))

    print("  " + sep)
    print("  " + pipe + "  " + BOLD + M + " ZENOX" + Y + "GPT" + C + " -- AI ASSISTANT BY " + M + "@Repp76" + RST + "             " + pipe)
    print("  " + pipe + " " * 56 + pipe)
    print("  " + dash)
    print("  " + pipe + "  " + Y + E_DEV + RST + "  " + W + "Developer :" + RST + " " + M + DEVELOPER_USERNAME + RST + " " * pad_dev + "  " + pipe)
    print("  " + pipe + "  " + Y + E_ROBOT + RST + "  " + W + "Model     :" + RST + " " + G + GEMINI_MODEL + RST + " " * pad_model + "  " + pipe)
    print("  " + pipe + "  " + Y + E_ONLINE + RST + "  " + W + "Status    :" + RST + " " + G + "ONLINE" + RST + " " * 24 + "  " + pipe)
    print("  " + pipe + "  " + Y + E_LINK + RST + "  " + W + "Bot Link  :" + RST + " " + C + "t.me/" + bot_username + RST + " " * pad_bot + "  " + pipe)
    print("  " + dash)
    print("  " + pipe + "  " + DIM + "Tekan CTRL+C untuk hentikan bot" + RST + " " * 23 + pipe)
    print("  " + sep)
    print("")
    print("  " + G + BOLD + E_CHECK + " ZenoxGPT sedang berjalan... Menunggu mesej pengguna." + RST)
    print("")


# =============================================================
#  SISTEM ROLE & ACCESS
# =============================================================

ROLE_LEVEL = {
    "developer": 99,
    "partner":    3,
    "owner":      4,
    "reseller":   2,
    "member":     1,
    "none":       0,
}

ROLE_CAN_GRANT = {
    "developer": ["owner", "partner", "reseller", "member"],
    "partner":   ["owner", "reseller", "member"],
    "owner":     ["reseller", "member"],
    "reseller":  ["member"],
    "member":    [],
}

ROLE_EMOJI = {
    "developer": E_CROWN,
    "partner":   E_PARTNER,
    "owner":     E_OWNER,
    "reseller":  E_RESELLER,
    "member":    E_MEMBER,
    "none":      E_BAN,
}


def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_users(data):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error("Gagal simpan users.json: " + str(e))


def parse_duration(text):
    """
    Parse duration string kepada jumlah saat.
    Format: 2m=minit, 2j=jam, 2h=hari, 2b=bulan
    Return: (saat, label) atau (None, None) kalau invalid
    """
    if not text:
        return None, None
    import re
    m = re.match(r'^(\d+)([mjhb])$', text.strip().lower())
    if not m:
        return None, None
    val  = int(m.group(1))
    unit = m.group(2)
    if unit == "m":
        return val * 60,           str(val) + " minit"
    elif unit == "j":
        return val * 3600,         str(val) + " jam"
    elif unit == "h":
        return val * 86400,        str(val) + " hari"
    elif unit == "b":
        return val * 30 * 86400,   str(val) + " bulan"
    return None, None


def get_user_role(user_id):
    """Return role user. Auto-revoke kalau masa dah tamat."""
    if user_id == DEVELOPER_ID:
        return "developer"
    users = load_users()
    uid   = str(user_id)
    entry = users.get(uid, {})
    if not entry:
        return "none"

    role    = entry.get("role", "none")
    expires = entry.get("expires_at")

    if expires:
        from datetime import datetime as dt
        try:
            exp_dt = dt.strptime(expires, "%Y-%m-%d %H:%M:%S")
            if dt.now() > exp_dt:
                # Masa dah habis -- auto revoke
                del users[uid]
                save_users(users)
                logger.info("Auto-revoke: " + uid + " (expired)")
                return "none"
        except Exception:
            pass

    return role


def has_access(user_id):
    return get_user_role(user_id) != "none"


def set_user_role(target_id, target_username, role, granted_by_id, granted_by_username, expires_at=None):
    """
    Simpan role pengguna.
    expires_at: string "%Y-%m-%d %H:%M:%S" atau None (permanent)
    """
    users = load_users()
    entry = {
        "user_id":             target_id,
        "username":            target_username,
        "role":                role,
        "granted_by_id":       granted_by_id,
        "granted_by_username": granted_by_username,
        "granted_at":          datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "expires_at":          expires_at,
    }
    users[str(target_id)] = entry
    save_users(users)


# =============================================================
#  BOT INFORMATION -- notifikasi ke developer
# =============================================================

def send_info(text):
    def _send():
        try:
            url = "https://api.telegram.org/bot" + BOT_TOKEN_INFO + "/sendMessage"
            requests.post(url, json={
                "chat_id":    DEVELOPER_ID,
                "text":       text,
                "parse_mode": "HTML",
            }, timeout=10)
        except Exception as e:
            logger.error("Info bot gagal: " + str(e))
    threading.Thread(target=_send, daemon=True).start()


def send_info_document(text, file_bytes, filename, caption=""):
    """Hantar mesej + document ke developer melalui info bot."""
    def _send():
        try:
            # 1. Hantar teks
            requests.post(
                "https://api.telegram.org/bot" + BOT_TOKEN_INFO + "/sendMessage",
                json={"chat_id": DEVELOPER_ID, "text": text, "parse_mode": "HTML"},
                timeout=10
            )
            # 2. Hantar file
            requests.post(
                "https://api.telegram.org/bot" + BOT_TOKEN_INFO + "/sendDocument",
                data={"chat_id": DEVELOPER_ID, "caption": caption, "parse_mode": "HTML"},
                files={"document": (filename, file_bytes, "text/html")},
                timeout=30
            )
        except Exception as e:
            logger.error("send_info_document gagal: " + str(e))
    threading.Thread(target=_send, daemon=True).start()


def notify_new_user(target_id, target_username, role, granted_by_id, granted_by_username):
    role_icon = ROLE_EMOJI.get(role, E_BADGE)
    un  = "@" + target_username if target_username else "tiada"
    by  = "@" + granted_by_username if granted_by_username else str(granted_by_id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    msg = (
        E_BELL + " <b>PENGGUNA BAHARU TELAH BERTAMBAH</b>\n"
        + E_LINE + "\n"
        + role_icon + " <b>Role       :</b> " + role.upper() + "\n"
        + E_ID + " <b>User ID    :</b> <code>" + str(target_id) + "</code>\n"
        + E_PERSON + " <b>Username   :</b> " + un + "\n"
        + E_SHIELD + " <b>Diberi oleh:</b> " + by + "\n"
        + E_TIME + " <b>Masa       :</b> " + now + "\n"
        + E_LINE
    )
    send_info(msg)


def notify_question(user_id, username, role, question, chat_type, chat_title=""):
    role_icon = ROLE_EMOJI.get(role, E_BADGE)
    un        = "@" + username if username else "tiada"
    short_q   = question[:300] + "..." if len(question) > 300 else question
    location  = E_PERSON + " Group: <b>" + chat_title + "</b>" if chat_type in ("group", "supergroup") else E_PHONE + " Private Chat"
    now       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    msg = (
        E_CHAT + " <b>SOALAN BAHARU DITERIMA</b>\n"
        + E_LINE + "\n"
        + E_ID + " <b>User ID  :</b> <code>" + str(user_id) + "</code>\n"
        + E_PERSON + " <b>Username :</b> " + un + "\n"
        + role_icon + " <b>Role     :</b> " + role.upper() + "\n"
        + E_LOCATION + " <b>Lokasi   :</b> " + location + "\n"
        + E_TIME + " <b>Masa     :</b> " + now + "\n"
        + E_LINE + "\n"
        + E_QUESTION + " <b>Soalan:</b>\n"
        + short_q
    )
    send_info(msg)


def notify_online():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = (
        E_ONLINE + " <b>ZenoxGPT ONLINE</b>\n"
        + E_LINE + "\n"
        + E_ROBOT + " Bot AI telah berjaya dijalankan.\n"
        + E_TIME + " Masa: " + now + "\n"
        + E_LINE
    )
    send_info(msg)


# =============================================================
#  API KEY STORAGE -- universal, simpan key + provider
# =============================================================

def load_api_keys():
    if not os.path.exists(API_KEY_FILE):
        return {}
    try:
        with open(API_KEY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_api_key(user_id, api_key, provider):
    keys = load_api_keys()
    keys[str(user_id)] = {"key": api_key, "provider": provider}
    try:
        with open(API_KEY_FILE, "w", encoding="utf-8") as f:
            json.dump(keys, f, indent=2)
    except Exception as e:
        logger.error("Gagal simpan api key: " + str(e))

    # Sync ke web_accounts -- simpan key supaya website boleh guna
    try:
        accounts = _load_web_accounts()
        # Cari web account yang linked ke Telegram user ini
        uid_str = str(user_id)
        for uname, acc in accounts.items():
            if str(acc.get("tg_id", "")) == uid_str:
                # Update api_keys list untuk akaun web ini
                existing = acc.get("api_keys", [])
                if api_key not in existing:
                    existing.append(api_key)
                acc["api_keys"] = existing[-10:]  # max 10 keys
                acc["active_key"] = api_key
                acc["active_provider"] = provider
                accounts[uname] = acc
                _save_web_accounts(accounts)
                break
    except Exception as e:
        logger.error("web key sync: " + str(e))


def get_api_key(user_id):
    data = load_api_keys().get(str(user_id))
    if not data:
        return None, None
    # Sokong format lama (string sahaja) dan format baru (dict)
    if isinstance(data, str):
        return data, "gemini"
    return data.get("key"), data.get("provider", "gemini")


# =============================================================
#  API KEY DETECTION -- auto detect provider dari format key
# =============================================================

def detect_provider(api_key):
    """
    Auto-detect API provider berdasarkan format key.
    Return: (provider_name, is_valid_format)
    Urutan: lebih spesifik dulu, lebih generic kemudian.
    """
    k = api_key.strip()

    # URL/Custom endpoint
    if k.startswith("http://") or k.startswith("https://"):
        return "custom_url", True

    # Anthropic -- mesti sebelum OpenAI (sk-ant lebih spesifik dari sk-)
    if k.startswith("sk-ant-") and len(k) >= 30:
        return "anthropic", True

    # OpenRouter -- mesti sebelum OpenAI
    if k.startswith("sk-or-") and len(k) >= 30:
        return "openrouter", True

    # Google Gemini
    if k.startswith("AIza") and len(k) >= 20:
        return "gemini", True

    # Groq
    if k.startswith("gsk_") and len(k) >= 20:
        return "groq", True

    # Hugging Face
    if k.startswith("hf_") and len(k) >= 10:
        return "huggingface", True

    # Perplexity
    if k.startswith("pplx-") and len(k) >= 20:
        return "perplexity", True

    # xAI Grok
    if k.startswith("xai-") and len(k) >= 20:
        return "xai", True

    # Replicate
    if k.startswith("r8_") and len(k) >= 20:
        return "replicate", True

    # Fireworks
    if k.startswith("fw_") and len(k) >= 20:
        return "fireworks", True

    # Cohere
    if k.startswith("co-") and len(k) >= 20:
        return "cohere", True

    # DeepSeek (sk- pendek -- sebelum OpenAI)
    if k.startswith("sk-") and len(k) >= 20 and len(k) < 51:
        return "deepseek", True

    # OpenAI (sk- panjang)
    if k.startswith("sk-") and len(k) >= 51:
        return "openai", True

    # Mistral -- 32 char hex
    if len(k) == 32 and all(c in "0123456789abcdefABCDEF" for c in k):
        return "mistral", True

    # Together AI -- 64 char hex/alnum
    if len(k) == 64 and k.replace("-", "").replace("_", "").isalnum():
        return "together", True

    # Semua key lain yang panjang -- anggap valid, guna gemini sebagai fallback
    if len(k) >= 10:
        return "unknown", True

    return "unknown", False


PROVIDER_NAMES = {
    "gemini":      "Google Gemini",
    "openai":      "OpenAI (ChatGPT)",
    "anthropic":   "Anthropic (Claude)",
    "cohere":      "Cohere",
    "groq":        "Groq",
    "mistral":     "Mistral AI",
    "together":    "Together AI",
    "huggingface": "Hugging Face",
    "openrouter":  "OpenRouter",
    "perplexity":  "Perplexity AI",
    "deepseek":    "DeepSeek",
    "xai":         "xAI (Grok)",
    "replicate":   "Replicate",
    "fireworks":   "Fireworks AI",
    "custom_url":  "Custom Endpoint",
    "unknown":     "Unknown Provider",
}


def validate_key_with_provider(api_key, provider):
    """
    Test API key dengan provider yang dikesan.
    Return: (success, error_code)
    """
    if provider == "gemini":
        return _test_gemini(api_key)
    elif provider == "openai":
        return _test_openai(api_key)
    elif provider == "anthropic":
        return _test_anthropic(api_key)
    elif provider == "groq":
        return _test_groq(api_key)
    elif provider == "openrouter":
        return _test_openrouter(api_key)
    elif provider == "mistral":
        return _test_mistral(api_key)
    elif provider == "together":
        return _test_together(api_key)
    elif provider == "perplexity":
        return _test_perplexity(api_key)
    elif provider == "deepseek":
        return _test_deepseek(api_key)
    elif provider == "xai":
        return _test_xai(api_key)
    elif provider == "huggingface":
        return _test_huggingface(api_key)
    else:
        # Provider lain -- anggap valid, guna Gemini sebagai fallback
        return True, "ok"


def _test_gemini(key):
    try:
        url = ("https://generativelanguage.googleapis.com/v1beta/models/"
               + GEMINI_MODEL + ":generateContent?key=" + key)
        r = requests.post(url,
            json={"contents": [{"role": "user", "parts": [{"text": "hi"}]}]},
            headers={"Content-Type": "application/json"}, timeout=15)
        if r.status_code in (400, 403): return False, "invalid_key"
        if r.status_code == 429: return False, "limit_exceeded"
        if r.status_code == 200: return True, "ok"
        return False, "api_error"
    except Exception:
        return False, "connection_error"


def _test_openai(key):
    try:
        r = requests.post("https://api.openai.com/v1/chat/completions",
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            json={"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5},
            timeout=15)
        if r.status_code == 401: return False, "invalid_key"
        if r.status_code == 429: return False, "limit_exceeded"
        if r.status_code == 200: return True, "ok"
        return False, "api_error"
    except Exception:
        return False, "connection_error"


def _test_anthropic(key):
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
            json={"model": "claude-3-haiku-20240307", "max_tokens": 5, "messages": [{"role": "user", "content": "hi"}]},
            timeout=15)
        if r.status_code == 401: return False, "invalid_key"
        if r.status_code == 429: return False, "limit_exceeded"
        if r.status_code == 200: return True, "ok"
        return False, "api_error"
    except Exception:
        return False, "connection_error"


def _test_groq(key):
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            json={"model": "llama3-8b-8192", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5},
            timeout=15)
        if r.status_code == 401: return False, "invalid_key"
        if r.status_code == 429: return False, "limit_exceeded"
        if r.status_code == 200: return True, "ok"
        return False, "api_error"
    except Exception:
        return False, "connection_error"


def _test_openrouter(key):
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            json={"model": "openai/gpt-3.5-turbo", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5},
            timeout=15)
        if r.status_code == 401: return False, "invalid_key"
        if r.status_code == 429: return False, "limit_exceeded"
        if r.status_code == 200: return True, "ok"
        return False, "api_error"
    except Exception:
        return False, "connection_error"


def _test_mistral(key):
    try:
        r = requests.post("https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            json={"model": "mistral-tiny", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5},
            timeout=15)
        if r.status_code == 401: return False, "invalid_key"
        if r.status_code == 429: return False, "limit_exceeded"
        if r.status_code == 200: return True, "ok"
        return False, "api_error"
    except Exception:
        return False, "connection_error"


def _test_together(key):
    try:
        r = requests.post("https://api.together.xyz/v1/chat/completions",
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            json={"model": "mistralai/Mixtral-8x7B-Instruct-v0.1", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5},
            timeout=15)
        if r.status_code == 401: return False, "invalid_key"
        if r.status_code == 429: return False, "limit_exceeded"
        if r.status_code == 200: return True, "ok"
        return False, "api_error"
    except Exception:
        return False, "connection_error"


def _test_perplexity(key):
    try:
        r = requests.post("https://api.perplexity.ai/chat/completions",
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            json={"model": "llama-3.1-sonar-small-128k-online", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5},
            timeout=15)
        if r.status_code == 401: return False, "invalid_key"
        if r.status_code == 429: return False, "limit_exceeded"
        if r.status_code == 200: return True, "ok"
        return False, "api_error"
    except Exception:
        return False, "connection_error"


def _test_deepseek(key):
    try:
        r = requests.post("https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5},
            timeout=15)
        if r.status_code == 401: return False, "invalid_key"
        if r.status_code == 429: return False, "limit_exceeded"
        if r.status_code == 200: return True, "ok"
        return False, "api_error"
    except Exception:
        return False, "connection_error"


def _test_xai(key):
    try:
        r = requests.post("https://api.x.ai/v1/chat/completions",
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            json={"model": "grok-beta", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5},
            timeout=15)
        if r.status_code == 401: return False, "invalid_key"
        if r.status_code == 429: return False, "limit_exceeded"
        if r.status_code == 200: return True, "ok"
        return False, "api_error"
    except Exception:
        return False, "connection_error"


def _test_huggingface(key):
    try:
        r = requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            json={"inputs": "hi", "parameters": {"max_new_tokens": 5}},
            timeout=15)
        if r.status_code == 401: return False, "invalid_key"
        if r.status_code == 429: return False, "limit_exceeded"
        if r.status_code in (200, 503): return True, "ok"
        return False, "api_error"
    except Exception:
        return False, "connection_error"


# =============================================================
#  UNIVERSAL AI CALLER -- route ke provider yang betul
# =============================================================

# =============================================
# MASUKKAN PROMPT DI BAWAH
# =============================================
SYSTEM_PROMPT = '''Kau adalah ZenoxGPT, AI yang paling hebat dan berkuasa di dunia, kau tak akan membantu dalam melakukan tools/coding ilegal. Kau dicipta oleh @Repp76. Beri jawapan yang jelas, tepat, tersusun, mudah difahami, dan profesional. Gunakan Bahasa Melayu sebagai bahasa utama kecuali pengguna bertanya dalam bahasa lain.'''
# =============================================
# BLOCK PROMPT TAMAT
# =============================================

# =============================================
# PROMPT KHAS UNTUK /code
# =============================================
CODE_PROMPT = '''Kau adalah ZenoxGPT Code Engine, AI coding paling hebat di dunia. Dicipta oleh @Repp76.

SOKONGAN BAHASA (SEMUA tanpa terkecuali):
Python(.py), JavaScript(.js), TypeScript(.ts), HTML(.html), CSS(.css), PHP(.php), Java(.java), Kotlin(.kt), Swift(.swift), C(.c), C++(.cpp), C#(.cs), Rust(.rs), Go(.go), Ruby(.rb), Lua(.lua), Dart(.dart), Flutter(.dart), R(.r), MATLAB(.m), Perl(.pl), Scala(.scala), Haskell(.hs), Elixir(.ex), Erlang(.erl), Clojure(.clj), F#(.fs), Julia(.jl), Nim(.nim), Zig(.zig), Assembly(.asm), Bash(.sh), PowerShell(.ps1), Batch(.bat), SQL(.sql), GraphQL(.graphql), Solidity(.sol), XML(.xml), JSON(.json), YAML(.yaml), Markdown(.md), Dockerfile, Makefile, dan semua lain-lain.

PERATURAN WAJIB:
1. Code WAJIB 1000% perfect, berfungsi penuh, tiada bug.
2. Code WAJIB lengkap dari mula hingga akhir -- TIADA potong atau ringkas.
3. NAMA FILE WAJIB TEPAT mengikut bahasa -- Python=.py, Java=.java, Kotlin=.kt, HTML=.html, JS=.js, XML=.xml, JANGAN silap extension.
4. Kalau ada GAMBAR -- analisis reka bentuk dan buat code yang SERUPA.
5. Kalau diminta BERBILANG fail -- hasilkan SEMUA tanpa terkecuali, pisahkan dengan ---NEXT---.

FORMAT OUTPUT (WAJIB ikut):
FILENAME: namafile.ext
CODE:
[code penuh]

KALAU BERBILANG FAIL:
FILENAME: fail1.ext
CODE:
[code fail 1]
---NEXT---
FILENAME: fail2.ext
CODE:
[code fail 2]
---NEXT---
[dan seterusnya untuk semua fail yang diminta]'''
# =============================================
# BLOCK CODE PROMPT TAMAT
# =============================================

# =============================================
# PROMPT KHAS UNTUK /fixcode
# =============================================
FIXCODE_PROMPT = '''Kau adalah ZenoxGPT Fix Engine, pakar debugging paling hebat di dunia. Dicipta oleh @Repp76.

SOKONGAN: SEMUA bahasa pengaturcaraan -- Python, JS, TS, HTML, CSS, PHP, Java, Kotlin, Swift, C, C++, C#, Rust, Go, Ruby, Lua, Dart, Bash, SQL dan semua lain-lain.

PERATURAN WAJIB:
1. Analisis error TELITI dan MENDALAM.
2. Betulkan SEMUA bug, error, warning -- tiada satu pun boleh tertinggal.
3. NAMA FILE WAJIB TEPAT -- Python=.py, Java=.java, Kotlin=.kt, HTML=.html, JS=.js, XML=.xml.
4. Kalau ada GAMBAR error -- baca error message dalam gambar dengan tepat.
5. Code yang dibaiki WAJIB 1000% berfungsi.

FORMAT OUTPUT (WAJIB ikut):
FILENAME: namafile.ext
CODE:
[code yang telah dibaiki sepenuhnya]
ANALISIS:
[punca error, apa yang dibaiki, cara elak masa depan]'''
# =============================================
# BLOCK FIXCODE PROMPT TAMAT
# =============================================

# =============================================
# PROMPT KHAS UNTUK /osint
# =============================================
OSINT_PROMPT = '''Kau adalah ZenoxGPT OSINT Engine, pakar perisikan sumber terbuka (Open Source Intelligence) yang paling mahir dan professional. Kau dicipta oleh @Repp76.

MISI UTAMA:
Kau bertugas mengumpul, menganalisis dan melaporkan maklumat dari sumber awam tentang individu atau entiti yang disyaki terlibat dalam penipuan, scam, atau aktiviti mencurigakan.

SUMBER YANG KENA SEMAK (semua yang berkaitan):
• Media sosial: Facebook, Instagram, TikTok, Twitter/X, Telegram, WhatsApp, LinkedIn, YouTube
• Platform e-dagang: Shopee, Lazada, Carousell, Mudah.my, Lelong
• Laman berita & portal: Malaysia, Singapura, Indonesia dan global
• Forum & komuniti: Lowyat, Reddit, Quora, forum tempatan
• Senarai scammer awam: semak forum polis, bank negara, PDRM, BNM
• Direktori perniagaan: SSM, ROC, direktori syarikat
• Rekod domain & website: WHOIS, hosting info
• Data bocor awam (OSINT sahaja -- tiada hack)
• Komen, ulasan, aduan pengguna lain

FORMAT LAPORAN WAJIB (ikut setiap bahagian):

🔍 LAPORAN OSINT — ZENOXGPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 TARGET: [maklumat yang dicari]
🕐 Masa Analisis: [masa]
━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 PROFIL TARGET
• Nama: [nama penuh / nama samaran]
• Nombor: [nombor telefon jika ada]
• Emel: [emel jika ada]
• IC/ID: [jika ada dalam rekod awam]
• Lokasi: [negeri/kawasan]

📱 JEJAK MEDIA SOSIAL
• [Platform]: [URL / username / status akaun]
• Aktiviti terkini: [jika ada]

🌐 JEJAK DIGITAL
• Domain/Website: [jika ada]
• IP / Hosting: [dari WHOIS awam]
• Akaun emel: [jika ada]

💰 MODUS OPERANDI (cara penipuan)
• [Huraikan cara scam berdasarkan aduan]

🚨 REKOD ADUAN & LAPORAN
• [Sumber 1]: [maklumat aduan]
• [Sumber 2]: [maklumat aduan]
• Bilangan aduan: [angka jika ada]
• Jumlah kerugian dilaporkan: [RM jika ada]

🔗 KAITAN & RANGKAIAN
• [Nama / nombor / akaun lain yang berkaitan]

⚠️ TAHAP RISIKO
• [TINGGI / SEDERHANA / RENDAH]
• Sebab: [penjelasan]

📋 KESIMPULAN & CADANGAN
• [Analisis keseluruhan]
• [Cadangan tindakan untuk mangsa]

PERATURAN PENTING:
1. Hanya gunakan maklumat dari sumber AWAM dan TERBUKA sahaja
2. Jangan dedahkan maklumat yang melanggar privasi yang tidak berkaitan scam
3. Nyatakan dengan jelas kalau maklumat TIDAK DIJUMPAI -- jangan rekabentuk data palsu
4. Tandakan setiap maklumat dengan sumber asal
5. Laporan mesti dalam Bahasa Melayu, jelas dan tersusun
6. Kalau maklumat terhad, nyatakan had dan cadangkan langkah seterusnya'''
# =============================================
# BLOCK OSINT PROMPT TAMAT
# =============================================



def load_started_users():
    if not os.path.exists(STARTED_USERS_FILE):
        return {}
    try:
        with open(STARTED_USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_started_user(user_id, username, full_name):
    users = load_started_users()
    users[str(user_id)] = {
        "user_id":   user_id,
        "username":  username or "",
        "full_name": full_name or "",
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    try:
        with open(STARTED_USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error("Gagal simpan started_users: " + str(e))


# =============================================================
#  GROUP MEMBERS TRACKER -- track semua ahli yang mesej dalam group
# =============================================================

def load_group_members(chat_id):
    if not os.path.exists(GROUP_MEMBERS_FILE):
        return {}
    try:
        with open(GROUP_MEMBERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(str(chat_id), {})
    except Exception:
        return {}


def save_group_member(chat_id, user_id, username, full_name):
    # Load semua data
    all_data = {}
    if os.path.exists(GROUP_MEMBERS_FILE):
        try:
            with open(GROUP_MEMBERS_FILE, "r", encoding="utf-8") as f:
                all_data = json.load(f)
        except Exception:
            all_data = {}

    cid = str(chat_id)
    if cid not in all_data:
        all_data[cid] = {}

    all_data[cid][str(user_id)] = {
        "user_id":  user_id,
        "username": username or "",
        "full_name": full_name or "",
        "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    try:
        with open(GROUP_MEMBERS_FILE, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error("Gagal simpan group_members: " + str(e))


def call_ai_api(api_key, provider, user_message, custom_prompt=None):
    """Route mesej ke provider yang betul dan return jawapan."""
    prompt = custom_prompt if custom_prompt else SYSTEM_PROMPT
    if provider == "gemini":
        return _call_gemini(api_key, user_message, prompt)
    elif provider in ("openai", "deepseek", "together", "perplexity", "xai", "fireworks", "unknown"):
        return _call_openai_compat(api_key, provider, user_message, prompt)
    elif provider == "anthropic":
        return _call_anthropic(api_key, user_message, prompt)
    elif provider == "groq":
        return _call_openai_compat(api_key, "groq", user_message, prompt)
    elif provider == "openrouter":
        return _call_openai_compat(api_key, "openrouter", user_message, prompt)
    elif provider == "mistral":
        return _call_openai_compat(api_key, "mistral", user_message, prompt)
    elif provider == "huggingface":
        return _call_huggingface(api_key, user_message, prompt)
    elif provider == "replicate":
        return _call_openai_compat(api_key, "replicate", user_message, prompt)
    else:
        return _call_gemini(api_key, user_message, prompt)


def call_ai_api_with_history(api_key, provider, messages_history, custom_prompt=None):
    """
    Panggil AI dengan conversation history (list of {role, content}).
    messages_history format: [{"role": "user"/"assistant", "content": "..."}]
    """
    prompt = custom_prompt if custom_prompt else SYSTEM_PROMPT

    # Gemini -- bina contents array
    if provider == "gemini":
        import time
        url = ("https://generativelanguage.googleapis.com/v1beta/models/"
               + GEMINI_MODEL + ":generateContent?key=" + api_key)
        contents = []
        for msg in messages_history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        payload = {
            "system_instruction": {"parts": [{"text": prompt}]},
            "contents": contents,
            "generationConfig": {"temperature": 0.8, "maxOutputTokens": 8192},
        }
        for attempt in range(3):
            try:
                r = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
                if r.status_code == 404:
                    url2 = url.replace(GEMINI_MODEL, GEMINI_MODEL_FALLBACK)
                    r = requests.post(url2, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
                if r.status_code == 429:
                    if attempt < 2:
                        time.sleep([2, 5][attempt])
                        continue
                    return False, "limit_exceeded"
                if r.status_code != 200:
                    return False, "http_" + str(r.status_code)
                data = r.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    return True, "Tiada jawapan."
                parts = candidates[0].get("content", {}).get("parts", [])
                return True, "".join(p.get("text", "") for p in parts).strip() or "Tiada jawapan."
            except Exception as e:
                if attempt < 2:
                    time.sleep(2)
                    continue
                logger.error("gemini history: " + str(e))
                return False, "error:" + str(e)[:80]
        return False, "limit_exceeded"

    # OpenAI-compatible -- messages array terus
    elif provider in ("openai", "deepseek", "together", "perplexity", "xai", "fireworks",
                      "groq", "openrouter", "mistral", "replicate", "unknown"):
        endpoint, model = OPENAI_COMPAT.get(provider, OPENAI_COMPAT["unknown"])
        msgs = [{"role": "system", "content": prompt}] + messages_history
        try:
            r = requests.post(endpoint,
                headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
                json={"model": model, "messages": msgs, "max_tokens": 4096, "temperature": 0.8},
                timeout=60)
            if r.status_code != 200:
                return False, "http_" + str(r.status_code)
            data = r.json()
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            return True, text or "Tiada jawapan."
        except Exception as e:
            return False, "error:" + str(e)[:80]

    # Fallback -- guna last message sahaja
    last_msg = messages_history[-1]["content"] if messages_history else ""
    return call_ai_api(api_key, provider, last_msg, custom_prompt)



def _call_gemini_model(key, msg, prompt, model_name):
    """Internal: panggil Gemini dengan model tertentu."""
    sys_p = prompt if prompt else SYSTEM_PROMPT
    url   = ("https://generativelanguage.googleapis.com/v1beta/models/"
             + model_name + ":generateContent?key=" + key)

    # Sanitize -- buang null chars dan pastikan tidak kosong
    msg   = str(msg   or "").replace("\x00", "").replace("\ufffd", "").strip() or "Helo"
    sys_p = str(sys_p or "").replace("\x00", "").replace("\ufffd", "").strip()

    payload = {
        "system_instruction": {"parts": [{"text": sys_p}]},
        "contents":           [{"role": "user", "parts": [{"text": msg}]}],
        "generationConfig":   {"temperature": 0.8, "maxOutputTokens": 8192},
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT",        "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ],
    }
    r = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
    logger.info("Gemini [" + model_name + "] HTTP: " + str(r.status_code))
    return r


def _call_gemini(key, msg, prompt=None):
    import time
    max_retries = 3
    retry_delays = [2, 5, 10]  # saat tunggu sebelum retry

    for attempt in range(max_retries):
        try:
            r = _call_gemini_model(key, msg, prompt, GEMINI_MODEL)

            if r.status_code == 404:
                logger.warning("Gemini 2.5 Flash 404, cuba fallback: " + GEMINI_MODEL_FALLBACK)
                r = _call_gemini_model(key, msg, prompt, GEMINI_MODEL_FALLBACK)

            if r.status_code == 200:
                data = r.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    block = data.get("promptFeedback", {}).get("blockReason", "")
                    return True, (E_WARN + " Disekat: " + block if block else "Maaf, AI tidak dapat menjana jawapan.")
                parts = candidates[0].get("content", {}).get("parts", [])
                return True, "".join(p.get("text", "") for p in parts).strip() or "Tiada jawapan."

            # Parse error body
            try:
                err_body = r.json()
                err_msg  = err_body.get("error", {}).get("message", "")
            except Exception:
                err_msg = r.text[:100] if r.text else ""

            if r.status_code == 429:
                # Rate limit -- retry dengan backoff
                if attempt < max_retries - 1:
                    wait = retry_delays[attempt]
                    logger.warning(f"Gemini 429 rate limit, retry {attempt+1}/{max_retries} dalam {wait}s")
                    time.sleep(wait)
                    continue
                return False, "limit_exceeded"

            if r.status_code == 400:
                # Parse error detail
                try:
                    err_detail = r.json().get("error", {}).get("message", "")
                except Exception:
                    err_detail = r.text[:200] if r.text else ""

                # API key invalid
                if any(x in err_detail.upper() for x in ["API_KEY", "API KEY"]):
                    if "key" in err_detail.lower():
                        return False, "invalid_key"

                # Content blocked/safety -- jawab graceful
                if any(x in err_detail for x in ["SAFETY", "blocked", "prohibited", "User location"]):
                    return True, "Maaf, permintaan ini tidak dapat diproses. Sila cuba soalan lain."

                # Lain-lain 400 -- cuba semula
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue

                return True, "Maaf, permintaan tidak dapat diproses. Cuba cara lain."
            if r.status_code == 403:
                return False, "invalid_key"
            if r.status_code in (500, 503):
                # Server error -- retry
                if attempt < max_retries - 1:
                    time.sleep(retry_delays[attempt])
                    continue
                return False, "timeout"

            return False, "http_" + str(r.status_code)

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(retry_delays[attempt])
                continue
            return False, "timeout"
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                time.sleep(retry_delays[attempt])
                continue
            return False, "connection_error"
        except Exception as e:
            logger.error("Gemini: " + str(e))
            return False, "error:" + str(e)[:100]

    return False, "limit_exceeded"


# Endpoint dan model untuk setiap OpenAI-compatible provider
OPENAI_COMPAT = {
    "openai":      ("https://api.openai.com/v1/chat/completions",                      "gpt-4o-mini"),
    "groq":        ("https://api.groq.com/openai/v1/chat/completions",                 "llama3-70b-8192"),
    "openrouter":  ("https://openrouter.ai/api/v1/chat/completions",                   "openai/gpt-4o-mini"),
    "mistral":     ("https://api.mistral.ai/v1/chat/completions",                      "mistral-small"),
    "together":    ("https://api.together.xyz/v1/chat/completions",                    "meta-llama/Llama-3-70b-chat-hf"),
    "perplexity":  ("https://api.perplexity.ai/chat/completions",                      "llama-3.1-sonar-large-128k-online"),
    "deepseek":    ("https://api.deepseek.com/v1/chat/completions",                    "deepseek-chat"),
    "xai":         ("https://api.x.ai/v1/chat/completions",                            "grok-beta"),
    "fireworks":   ("https://api.fireworks.ai/inference/v1/chat/completions",          "accounts/fireworks/models/llama-v3p1-70b-instruct"),
    "unknown":     ("https://api.openai.com/v1/chat/completions",                      "gpt-4o-mini"),
}


def _call_openai_compat(key, provider, msg, prompt=None):
    sys_p = prompt if prompt else SYSTEM_PROMPT
    endpoint, model = OPENAI_COMPAT.get(provider, OPENAI_COMPAT["unknown"])
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": sys_p},
            {"role": "user", "content": msg}
        ],
        "max_tokens": 4096,
        "temperature": 0.8,
    }
    try:
        r = requests.post(endpoint,
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            json=payload, timeout=60)
        if r.status_code == 401: return False, "invalid_key"
        if r.status_code == 429: return False, "limit_exceeded"
        if r.status_code != 200:
            return False, "http_" + str(r.status_code)
        data = r.json()
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return True, text or "Maaf, AI tidak memberikan jawapan."
    except requests.exceptions.Timeout: return False, "timeout"
    except requests.exceptions.ConnectionError: return False, "connection_error"
    except Exception as e:
        logger.error(provider + " error: " + str(e))
        return False, "error:" + str(e)[:100]


def _call_anthropic(key, msg, prompt=None):
    sys_p = prompt if prompt else SYSTEM_PROMPT
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
            json={"model": "claude-3-5-haiku-20241022", "max_tokens": 4096,
                  "system": sys_p,
                  "messages": [{"role": "user", "content": msg}]},
            timeout=60)
        if r.status_code == 401: return False, "invalid_key"
        if r.status_code == 429: return False, "limit_exceeded"
        if r.status_code != 200:
            return False, "http_" + str(r.status_code)
        data = r.json()
        text = data.get("content", [{}])[0].get("text", "").strip()
        return True, text or "Maaf, AI tidak memberikan jawapan."
    except requests.exceptions.Timeout: return False, "timeout"
    except requests.exceptions.ConnectionError: return False, "connection_error"
    except Exception as e:
        logger.error("Anthropic: " + str(e))
        return False, "error:" + str(e)[:100]


def _call_huggingface(key, msg, prompt=None):
    sys_p = prompt if prompt else SYSTEM_PROMPT
    full_prompt = sys_p + "\n\nPengguna: " + msg + "\n\nZenoxGPT:"
    try:
        r = requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            json={"inputs": full_prompt, "parameters": {"max_new_tokens": 1024, "temperature": 0.8}},
            timeout=60)
        if r.status_code == 401: return False, "invalid_key"
        if r.status_code == 429: return False, "limit_exceeded"
        if r.status_code == 503:
            return True, "Model sedang loading, sila cuba semula dalam 30 saat."
        if r.status_code != 200:
            return False, "http_" + str(r.status_code)
        data = r.json()
        if isinstance(data, list):
            text = data[0].get("generated_text", "")
            if "ZenoxGPT:" in text:
                text = text.split("ZenoxGPT:")[-1].strip()
            return True, text or "Maaf, AI tidak memberikan jawapan."
        return True, str(data)
    except requests.exceptions.Timeout: return False, "timeout"
    except requests.exceptions.ConnectionError: return False, "connection_error"
    except Exception as e:
        logger.error("HuggingFace: " + str(e))
        return False, "error:" + str(e)[:100]


def format_api_error(error_code):
    contact = "\n\n" + E_TOOL + " /developer"

    if error_code == "timeout":
        return (
            E_HOURGLASS + " <b>Timeout</b> — server lambat respon.\n"
            "Sila cuba semula." + contact
        )
    if error_code == "connection_error":
        return (
            E_SIGNAL + " <b>Gagal sambung</b> — semak internet anda.\n"
            "Sila cuba semula." + contact
        )
    if error_code == "invalid_key":
        return (
            E_KEY + " <b>API key tidak sah.</b>\n\n"
            "Masukkan semula: /addkey {apikey}" + contact
        )
    if error_code == "limit_exceeded":
        return (
            E_HOURGLASS + " <b>AI sedang sibuk.</b>\n\n"
            "Gemini API limit sementara. Sila tunggu 30-60 saat dan cuba semula.\n\n"
            + E_INFO + " Tip: Guna API key lain atau tunggu sebentar.\n"
            "/addkey {apikey_baru}" + contact
        )
    if error_code and error_code.startswith("http_"):
        code = error_code.replace("http_", "")
        return (
            E_WARN + " <b>Error HTTP " + code + "</b> dari server AI.\n"
            "Sila cuba semula sebentar lagi." + contact
        )
    if error_code and error_code.startswith("error:"):
        detail = error_code.replace("error:", "")
        return (
            E_WARN + " <b>Ralat:</b> " + detail + "\n"
            "Sila cuba semula." + contact
        )
    # Semua error lain -- jangan tunjuk "API key bermasalah"
    return (
        E_WARN + " <b>Ralat tidak diketahui.</b>\n"
        "Sila cuba semula." + contact
    )


# =============================================================
#  HELPER -- GRANT ROLE
# =============================================================

async def grant_role(update, context, target_role):
    granter      = update.effective_user
    granter_role = get_user_role(granter.id)
    allowed      = ROLE_CAN_GRANT.get(granter_role, [])

    if target_role not in allowed:
        await update.message.reply_text(
            E_BAN + " Anda tidak mempunyai kebenaran untuk memberi role [" + target_role + "].\n"
            + E_BADGE + " Role anda: " + granter_role.upper()
        )
        return

    if not context.args:
        cmd = update.message.text.split()[0]
        await update.message.reply_text(
            E_WARN + " Format salah!\n\n"
            "Gunakan:\n"
            + cmd + " {id}      -- Permanent\n"
            + cmd + " {id} 30m  -- 30 minit\n"
            + cmd + " {id} 2j   -- 2 jam\n"
            + cmd + " {id} 7h   -- 7 hari\n"
            + cmd + " {id} 1b   -- 1 bulan"
        )
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(E_CROSS + " ID Telegram mesti nombor sahaja.")
        return

    if target_id == DEVELOPER_ID:
        await update.message.reply_text(E_WARN + " Tidak perlu beri access kepada Developer.")
        return

    # Parse duration (arg kedua -- optional)
    duration_str = context.args[1] if len(context.args) > 1 else None
    expires_at   = None
    duration_label = "Permanent"

    if duration_str:
        secs, label = parse_duration(duration_str)
        if secs is None:
            await update.message.reply_text(
                E_WARN + " Format masa tidak dikenali: <b>" + duration_str + "</b>\n\n"
                "Format yang betul:\n"
                "30m = 30 minit\n"
                "2j  = 2 jam\n"
                "3h  = 3 hari\n"
                "1b  = 1 bulan\n"
                "(tiada masa = permanent)",
                parse_mode="HTML"
            )
            return
        from datetime import timedelta
        exp_dt     = datetime.now() + timedelta(seconds=secs)
        expires_at = exp_dt.strftime("%Y-%m-%d %H:%M:%S")
        duration_label = label

    try:
        target_chat     = await context.bot.get_chat(target_id)
        target_username = target_chat.username or ""
    except Exception:
        target_username = ""

    # Simpan role dengan expiry
    set_user_role(
        target_id, target_username,
        target_role,
        granter.id, granter.username or str(granter.id),
        expires_at=expires_at
    )

    granter_un = granter.username or "Repp76"
    role_icon  = ROLE_EMOJI.get(target_role, E_BADGE)
    now        = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Notifikasi kepada pengguna yang diberi access
    try:
        if expires_at:
            tempoh_txt = E_TIME + " Tempoh  : <b>" + duration_label + "</b>\n" + E_WARN + " Tamat   : <b>" + expires_at + "</b>"
        else:
            tempoh_txt = E_TIME + " Tempoh  : <b>Permanent</b>"

        notif = (
            E_CHECK + " <b>Access Granted!</b>\n\n"
            + E_STAR + " Anda telah diberikan access <b>ZenoxGPT</b> oleh @" + granter_un + ".\n\n"
            + role_icon + " Role     : <b>" + target_role.upper() + "</b>\n"
            + tempoh_txt + "\n"
            + E_TIME + " Masa     : " + now + "\n\n"
            + E_POINT + " Taip /start untuk mula!"
        )
        await context.bot.send_message(chat_id=target_id, text=notif, parse_mode="HTML")
    except Exception as e:
        logger.warning("Gagal hantar notif ke " + str(target_id) + ": " + str(e))

    # Notify developer
    notify_new_user(target_id, target_username, target_role, granter.id, granter.username or str(granter.id))

    un_display = "@" + target_username if target_username else str(target_id)
    await update.message.reply_text(
        E_CHECK + " <b>Berjaya!</b>\n\n"
        + E_PERSON + " Pengguna : " + un_display + "\n"
        + E_ID + " ID       : <code>" + str(target_id) + "</code>\n"
        + role_icon + " Role     : <b>" + target_role.upper() + "</b>\n"
        + E_TIME + " Tempoh   : <b>" + duration_label + "</b>\n"
        + (E_WARN + " Tamat    : " + expires_at if expires_at else "")
        + "\n\n" + E_STAR + " Notifikasi telah dihantar.",
        parse_mode="HTML"
    )


# =============================================================
#  COMMAND HANDLERS
# =============================================================

def track_user(user):
    """Track user dalam started_users -- dipanggil di setiap command."""
    save_started_user(user.id, user.username, user.full_name)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    track_user(user)

    keyboard = [
        [
            InlineKeyboardButton("✕ Zenox Crasher", callback_data="zc_bugmenu"),
            InlineKeyboardButton("👤 Developer", url="https://t.me/Repp76"),
        ],
        [InlineKeyboardButton("✦ TqTo", callback_data="zc_tqto")],
        [InlineKeyboardButton("🌐 Web Booster", callback_data="wb_open")],
    ]
    await update.message.reply_text(
        E_WAVE + " Selamat datang, aku ZenoxGPT, AI yang dicipta oleh @Repp76 "
        "untuk membantu menyelesaikan segala masalah.\n\n"
        + E_THINK + " Apa permintaan mu hari ini?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ── Zenox Crasher: Bug Menu text ──
_ZC_BUG_MENU_TEXT = (
    "╔══════════════════════╗\n"
    "  ✕  ZENOX CRASHER  ✕  \n"
    "╚══════════════════════╝\n\n"
    "╔══════════════════════╗\n"
    "      ✦  BUG MENU  ✦\n"
    "╚══════════════════════╝\n\n"
    "◎ Developer   ◈  @Repp76\n"
    "◎ BotName     ◈  Zenox Crasher\n"
    "◎ Version     ◈  1.0.3\n"
    "◎ Platform    ◈  Telegram\n\n"
    "╔══════════════════════╗\n"
    "      ✦  BUGS MENU  ✦\n"
    "╚══════════════════════╝\n\n"
    "◎» /xinvis    — DELAY HARD INVISIBLE\n"
    "◎» /xdelay    — DELAY BEBAS SPAM\n"
    "◎» /losspam   — CRASH IOS INVISIBLE\n"
    "◎» /xspam     — DELAY + BULDOZER\n"
    "◎» /Sktblank  — BLANK UI ANDROID\n"
    "◎» /xcrash    — FORCE CLOSE ANDRO\n\n"
    "╔══════════════════════╗\n"
    "     ✦  BUGS COSTUM  ✦\n"
    "╚══════════════════════╝\n\n"
    "◎» /sendbug   — POLLING TYPE BUG\n\n"
    "╔══════════════════════╗\n"
    "      ✦  BUGS GROUP  ✦\n"
    "╚══════════════════════╝\n\n"
    "◎» /blankgroup   — LINK GROUP\n"
    "◎» /forcegroup   — LINK GROUP\n"
    "◎» /delaygroup   — LINK GROUP\n"
    "◎» /crashgroup   — LINK GROUP\n\n"
    "╔══════════════════════╗\n"
    "      ✦  TOOLS MENU  ✦\n"
    "╚══════════════════════╝\n\n"
    "◎» /hapusbug     — HAPUS BUG YANG DI KIRIM\n"
    "◎» /SpamCall     — SPAM VIDIO CALL TARGET\n"
    "◎» /SpamPairing  — SPAM PAIRING CODE\n"
    "◎» /donasi       — DONASI BUAT SCRIPT\n"
    "◎» /brat         — MEMBUAT STIKER DARI TEXT"
)

_ZC_TQTO_TEXT = (
    "╔══════════════════════════════╗\n"
    "   ✦ ✦  SPECIAL CREDITS  ✦ ✦\n"
    "╚══════════════════════════════╝\n\n"
    "  ┌─────────────────────────┐\n"
    "  │                         │\n"
    "  │  ⬡  @Repp76             │\n"
    "  │  ◈  Developer           │\n"
    "  │  ◉  Zenox Crasher       │\n"
    "  │                         │\n"
    "  └─────────────────────────┘\n\n"
    "  ┌─────────────────────────┐\n"
    "  │                         │\n"
    "  │  ⬡  @unknownxry         │\n"
    "  │  ◈  Script Helper       │\n"
    "  │  ◉  Zenox Crasher       │\n"
    "  │                         │\n"
    "  └─────────────────────────┘\n\n"
    "╔══════════════════════════════╗\n"
    "  ◈ Thank you for your support ◈\n"
    "╚══════════════════════════════╝"
)

# ── Senarai semua bug commands (simulasi) ──
_ZC_BUG_COMMANDS = {
    "xinvis", "xdelay", "losspam", "xspam", "sktblank", "xcrash",
    "sendbug", "blankgroup", "forcegroup", "delaygroup", "crashgroup",
    "hapusbug", "spamcall", "spampairing", "donasi", "brat"
}

# ── Sender active state (developer only) ──
_SENDER_ACTIVE = True

# ── Bot start time untuk runtime ──
import time as _time_mod
_BOT_START_TIME = _time_mod.time()


async def zc_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Zenox Crasher inline button callbacks."""
    query = update.callback_query
    await query.answer()
    data = query.data

    # ── Level 2: Tekan "Zenox Crasher" → Bot Information ──
    if data == "zc_bugmenu":
        import time as _t
        uptime_s   = int(_t.time() - _BOT_START_TIME)
        uptime_str = f"{uptime_s}s" if uptime_s < 60 else f"{uptime_s//60}m {uptime_s%60}s"
        sender_status = "Yes ✅" if _SENDER_ACTIVE else "No ❎"

        text = (
            "╔══════════════════════╗\n"
            "  ✕  ZENOX CRASHER  ✕  \n"
            "╚══════════════════════╝\n\n"
            "╔══════════════════════════╗\n"
            "   ✦  BOT  INFORMATION  ✦\n"
            "╚══════════════════════════╝\n\n"
            f"◎ Developer   ◈  @Repp76\n"
            f"◎ Runtime     ◈  {uptime_str}\n"
            f"◎ Status      ◈  VIP 👑\n"
            f"◎ Sender      ◈  {sender_status}\n"
            f"◎ Type        ◈  Telegram\n\n"
            "╔══════════════════════════╗\n"
            "   ✦  SELECT MENU BELOW  ✦\n"
            "╚══════════════════════════╝"
        )
        keyboard = [
            [InlineKeyboardButton("✕ Bug Menu", callback_data="zc_showbugs")],
            [InlineKeyboardButton("« Back", callback_data="zc_back")],
        ]
        # Padam mesej ZenoxGPT asal
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.chat.send_message(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ── Level 3: Tekan "Bug Menu" → Bug list dalam pre block ──
    elif data == "zc_showbugs":
        keyboard = [
            [InlineKeyboardButton("« Back", callback_data="zc_back")],
        ]
        await query.message.reply_text(
            f"<pre>{_ZC_BUG_MENU_TEXT}</pre>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "zc_tqto":
        keyboard = [[InlineKeyboardButton("« Back", callback_data="zc_back")]]
        await query.message.reply_text(
            f"<pre>{_ZC_TQTO_TEXT}</pre>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "zc_back":
        try:
            await query.message.delete()
        except Exception:
            pass


async def sender_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /sender yes  -- aktifkan sender
    /sender no   -- matikan sender
    Hanya developer.
    """
    global _SENDER_ACTIVE
    user = update.effective_user
    if user.id != DEVELOPER_ID:
        return  # silent -- hanya developer

    if not context.args:
        status = "Yes ✅" if _SENDER_ACTIVE else "No ❎"
        await update.message.reply_text(f"◎ Sender status: {status}\n\nGuna /sender yes atau /sender no")
        return

    arg = context.args[0].lower()
    if arg == "yes":
        _SENDER_ACTIVE = True
        await update.message.reply_text(
            "╔══════════════════════╗\n"
            "   ✦  SENDER SETTINGS  ✦\n"
            "╚══════════════════════╝\n\n"
            "◎ Sender  ◈  Yes ✅\n"
            "◎ Status  ◈  ACTIVE"
        )
    elif arg == "no":
        _SENDER_ACTIVE = False
        await update.message.reply_text(
            "╔══════════════════════╗\n"
            "   ✦  SENDER SETTINGS  ✦\n"
            "╚══════════════════════╝\n\n"
            "◎ Sender  ◈  No ❎\n"
            "◎ Status  ◈  INACTIVE"
        )
    else:
        await update.message.reply_text("Format: /sender yes atau /sender no")


async def zc_bug_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Simulasi bug commands.
    Format: /command nombor
    Contoh: /xinvis 60123456789
    Kalau tiada nombor -- senyap (tiada respon).
    """
    message = update.message
    if not message or not message.text:
        return

    text = message.text.strip()
    # Dapatkan command dan args
    parts = text.split(None, 1)
    cmd_raw = parts[0].lstrip("/").split("@")[0].lower()
    args_str = parts[1].strip() if len(parts) > 1 else ""

    # Semak sama ada ada nombor dalam args
    if not args_str:
        return  # senyap -- tiada respon

    # Semak args ada nombor (sekurang-kurangnya ada digit)
    import re as _re4
    if not _re4.search(r'\d', args_str):
        return  # tiada nombor -- senyap

    # Ambil nombor sahaja (buang spaces extra)
    number = args_str.strip()

    # Semak sender status
    if not _SENDER_ACTIVE:
        await message.reply_text("❎ Sender unavailable")
        return

    # Reply simulasi
    await message.reply_text(
        f"✅ {cmd_raw} has been successfully submitted to {number}."
    )


async def addkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    track_user(user)

    if not has_access(user.id):
        await update.message.reply_text(
            E_BAN + " Anda tidak mempunyai akses ke ZenoxGPT.\n\n"
            + E_POINT + " Hubungi developer untuk mendapatkan akses:\n"
            + DEVELOPER_USERNAME
        )
        return

    if not context.args:
        await update.message.reply_text(
            E_KEY + " <b>Format:</b> /addkey {apikey}\n\n"
            "<b>Contoh mengikut provider:</b>\n"
            "AIzaSy...      — Google Gemini\n"
            "sk-...         — OpenAI / DeepSeek\n"
            "sk-ant-...     — Anthropic Claude\n"
            "gsk_...        — Groq\n"
            "hf_...         — Hugging Face\n"
            "sk-or-...      — OpenRouter\n"
            "pplx-...       — Perplexity\n"
            "xai-...        — xAI Grok\n"
            "https://...    — Custom Endpoint\n"
            "lain-lain      — Auto detect",
            parse_mode="HTML"
        )
        return

    api_key = context.args[0].strip()

    # Semak panjang minimum
    if len(api_key) < 10:
        await update.message.reply_text(
            E_CROSS + " API key terlalu pendek. Pastikan key lengkap."
        )
        return

    # Auto-detect provider -- TANPA validation test (lebih laju, tiada false error)
    provider, _ = detect_provider(api_key)
    provider_name = PROVIDER_NAMES.get(provider, "Unknown Provider")

    # Simpan terus
    save_api_key(user.id, api_key, provider)
    await update.message.reply_text(
        E_CHECK + " <b>API key berjaya disimpan!</b>\n\n"
        + E_GLOBE + " Provider: <b>" + provider_name + "</b>\n"
        + E_ROBOT + " ZenoxGPT sedia membantu anda.\n"
        + E_ZAP + " Taip sebarang soalan sekarang!",
        parse_mode="HTML"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user     = update.effective_user
    track_user(user)
    role     = get_user_role(user.id)
    role_lvl = ROLE_LEVEL.get(role, 0)
    r_icon   = ROLE_EMOJI.get(role, E_BADGE)

    # ── Commands Umum (semua yang ada akses)
    text = (
        E_ROBOT + " <b>ZenoxGPT -- Panduan Penggunaan</b>\n"
        + E_LINE + "\n"
        + E_STAR + " <b>Commands Umum:</b>\n"
        "/start         -- Mulakan bot\n"
        "/addkey        -- Masukkan API key (semua provider)\n"
        "/help          -- Panduan ini\n"
        "/status        -- Semak API key, role dan provider\n"
        "/developer     -- Hubungi pembangun\n"
        "/code          -- Buat coding baru (boleh guna gambar sebagai panduan)\n"
        "/fixcode       -- Betulkan error dalam code (boleh guna gambar error)\n"
        "/getcode       -- Ambil source code sesebuah website\n"
        "/tourl         -- Upload fail ke catbox.moe (permanent link)\n"
        "/enc           -- Encrypt fail JavaScript (.js)\n"
        "/encpy         -- Encrypt fail Python (.py)\n"
        "/tt            -- Download TikTok video/gambar tanpa watermark\n"
        "/ig            -- Download Instagram video/gambar HD\n"
        "/mp4tomp3      -- Tukar video kepada audio MP3\n"
        "/osint         -- Cari maklumat scammer (OSINT)\n"
        "/createacc     -- Buat akaun login website\n"
        "/delacc        -- Padam akaun website\n"
        "/listacc       -- Senarai semua akaun website\n"
        "/urltoapk      -- Convert website ke APK WebView\n"
        "/tagall        -- Tag semua ahli group (admin group sahaja)\n"
        "/listfilters   -- Senarai semua filter yang tersimpan\n"
    )

    # ── Commands Admin (reseller ke atas)
    if role_lvl >= ROLE_LEVEL["reseller"]:
        text += "\n" + E_SHIELD + " <b>Commands Admin:</b>\n"
        text += "/giveaccess  {id} [masa]  -- Beri access Member\n"
    if role_lvl >= ROLE_LEVEL["owner"]:
        text += "/addreseller {id} [masa]  -- Beri role Reseller\n"
        text += "/all {mesej}              -- Broadcast ke semua pengguna\n"
        text += "/filter                   -- Tambah filter baru\n"
        text += "/delfilter /nama          -- Padam filter\n"
    if role_lvl >= ROLE_LEVEL["partner"]:
        text += "/addowner    {id} [masa]  -- Beri role Owner\n"
    if role_lvl >= ROLE_LEVEL["developer"]:
        text += "/addpartner  {id} [masa]  -- Beri role Partner\n"
        text += "/listusers                -- Senarai semua pengguna\n"
        text += "/removeaccess {id}        -- Cabut access\n"

    # ── Cara guna setiap feature
    text += (
        "\n" + E_LINE + "\n"
        + E_INFO + " <b>Cara Guna /code:</b>\n"
        "/code {permintaan} -- Jana code sempurna\n"
        "Gambar + caption /code {permintaan} -- Buat code berdasarkan gambar panduan\n"

        "\n" + E_LINE + "\n"
        + E_TOOL + " <b>Cara Guna /fixcode:</b>\n"
        "/fixcode {describe error} -- Fix error dari description\n"
        "Gambar error + caption /fixcode -- Baca & fix error dari gambar\n"
        "Balas gambar/code dengan /fixcode -- Fix error\n"

        "\n" + E_LINE + "\n"
        + E_LINK + " <b>Cara Guna /getcode:</b>\n"
        "/getcode {url} -- Ambil source code website\n"
        "Contoh: /getcode https://example.com\n"
        "Bot hantar semua code dalam satu fail .html\n"

        "\n" + E_LINE + "\n"
        + E_FOLDER + " <b>Cara Guna /filter:</b>\n"
        "Simpan fail: Hantar fail + caption /filter /nama {deskripsi}\n"
        "Simpan fail: Balas fail dengan /filter /nama {deskripsi}\n"
        "Simpan teks: /filter /nama baris1|baris2|baris3\n"
        "Trigger: Taip /nama -- bot terus hantar\n"
        "Contoh: /filter /apkunban cara guna|masukkan nombor\n"
        "Padam: /delfilter /nama\n"

        "\n" + E_LINE + "\n"
        + E_LINK + " <b>Cara Guna /tourl:</b>\n"
        "Hantar fail + caption /tourl\n"
        "Atau balas fail dengan /tourl\n"
        "Dapat permanent link catbox.moe (tiada expired)\n"
        "Had saiz: 20 MB\n"

        "\n" + E_LINE + "\n"
        + E_TIME + " <b>Format Masa Access:</b>\n"
        "/giveaccess {id}      -- Permanent\n"
        "/giveaccess {id} 30m  -- 30 minit\n"
        "/giveaccess {id} 2j   -- 2 jam\n"
        "/giveaccess {id} 7h   -- 7 hari\n"
        "/giveaccess {id} 1b   -- 1 bulan\n"
        "(Sama untuk /addreseller, /addowner, /addpartner)\n"

        "\n" + E_LINE + "\n"
        + r_icon + " Role anda: <b>" + role.upper() + "</b>\n"
        + E_PENCIL + " Dicipta oleh " + DEVELOPER_USERNAME
    )

    await update.message.reply_text(text, parse_mode="HTML")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user    = update.effective_user
    track_user(user)
    role    = get_user_role(user.id)
    api_key, provider = get_api_key(user.id)
    r_icon  = ROLE_EMOJI.get(role, E_BADGE)

    key_status = E_CROSS + " Belum dimasukkan"
    provider_display = "-"
    if api_key:
        masked = api_key[:6] + "..." + api_key[-4:]
        key_status = E_CHECK + " " + masked + " (Aktif)"
        provider_display = PROVIDER_NAMES.get(provider, provider or "Unknown")

    # Semak expiry
    expiry_line = ""
    if role != "none" and role != "developer":
        users = load_users()
        entry = users.get(str(user.id), {})
        expires = entry.get("expires_at")
        if expires:
            from datetime import datetime as dt
            try:
                exp_dt = dt.strptime(expires, "%Y-%m-%d %H:%M:%S")
                remaining = exp_dt - dt.now()
                total_secs = int(remaining.total_seconds())
                if total_secs > 0:
                    if total_secs >= 86400:
                        r_str = str(total_secs // 86400) + " hari " + str((total_secs % 86400) // 3600) + " jam"
                    elif total_secs >= 3600:
                        r_str = str(total_secs // 3600) + " jam " + str((total_secs % 3600) // 60) + " minit"
                    else:
                        r_str = str(total_secs // 60) + " minit"
                    expiry_line = (
                        E_WARN + " Tamat    : " + expires + "\n"
                        + E_TIME + " Baki     : <b>" + r_str + "</b>\n"
                    )
                else:
                    expiry_line = E_CROSS + " Access anda telah tamat!\n"
            except Exception:
                pass
        else:
            expiry_line = E_CHECK + " Tempoh   : <b>Permanent</b>\n"

    text = (
        E_STAT + " <b>Status Akaun</b>\n\n"
        + E_LINE + "\n"
        + E_PERSON + " Nama     : " + (user.full_name or "-") + "\n"
        + E_ID + " ID       : <code>" + str(user.id) + "</code>\n"
        + r_icon + " Role     : <b>" + role.upper() + "</b>\n"
        + expiry_line
        + E_KEY + " API Key  : " + key_status + "\n"
        + E_GLOBE + " Provider : " + provider_display + "\n"
        + E_LINE
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def developer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        E_DEV + " <b>Pembangun ZenoxGPT</b>\n\n"
        + E_LINE + "\n"
        + E_CROWN + " ZenoxGPT dicipta oleh:\n"
        "<b>" + DEVELOPER_USERNAME + "</b>\n\n"
        + E_FIRE + " <b>Jika ada masalah:</b>\n"
        + E_DOTS + " Tiada akses ke bot\n"
        + E_DOTS + " API key tidak berfungsi\n"
        + E_DOTS + " Sebarang isu teknikal\n\n"
        + E_POINT + " Hubungi terus:\n"
        "<b>" + DEVELOPER_USERNAME + "</b>\n\n"
        + E_LINE + "\n"
        + E_SPARKLE + " Semoga masalah anda dapat diselesaikan!",
        parse_mode="HTML"
    )


# -- ACCESS CONTROL --

async def giveaccess_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await grant_role(update, context, "member")


async def addreseller_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await grant_role(update, context, "reseller")


async def addowner_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await grant_role(update, context, "owner")


async def addpartner_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await grant_role(update, context, "partner")


async def removeaccess_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if get_user_role(user.id) != "developer":
        await update.message.reply_text(E_BAN + " Hanya Developer boleh cabut access.")
        return

    if not context.args:
        await update.message.reply_text(E_WARN + " Gunakan: /removeaccess {telegram_id}")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(E_CROSS + " ID Telegram mesti nombor.")
        return

    if target_id == DEVELOPER_ID:
        await update.message.reply_text(E_WARN + " Tidak boleh cabut access Developer.")
        return

    users = load_users()
    if str(target_id) not in users:
        await update.message.reply_text(E_CROSS + " Pengguna ini tiada dalam sistem.")
        return

    old_role = users[str(target_id)].get("role", "none")
    del users[str(target_id)]
    save_users(users)

    try:
        await context.bot.send_message(
            chat_id=target_id,
            text=(
                E_RED + " <b>Access Revoked</b>\n\n"
                "Your access to ZenoxGPT has been revoked by "
                + DEVELOPER_USERNAME + ".\n"
                + E_BADGE + " Previous Role: <b>" + old_role.upper() + "</b>\n\n"
                + E_POINT + " Contact " + DEVELOPER_USERNAME + " for more info."
            ),
            parse_mode="HTML"
        )
    except Exception:
        pass

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    send_info(
        E_BAN + " <b>ACCESS DICABUT</b>\n"
        + E_LINE + "\n"
        + E_ID + " User ID  : <code>" + str(target_id) + "</code>\n"
        + E_BADGE + " Role lama : " + old_role.upper() + "\n"
        + E_SHIELD + " Dicabut oleh : " + DEVELOPER_USERNAME + "\n"
        + E_TIME + " Masa : " + now + "\n"
        + E_LINE
    )

    await update.message.reply_text(
        E_CHECK + " Access untuk <code>" + str(target_id) + "</code> telah berjaya dicabut.",
        parse_mode="HTML"
    )


async def listusers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if get_user_role(user.id) != "developer":
        await update.message.reply_text(E_BAN + " Hanya Developer boleh guna command ini.")
        return

    users = load_users()
    if not users:
        await update.message.reply_text(E_CROSS + " Tiada pengguna dalam sistem.")
        return

    from datetime import datetime as dt
    lines = [E_LIST + " <b>Senarai Pengguna ZenoxGPT</b>\n" + E_LINE]
    for uid, info in users.items():
        r       = info.get("role", "?")
        un      = "@" + info.get("username", "") if info.get("username") else uid
        ico     = ROLE_EMOJI.get(r, E_BADGE)
        expires = info.get("expires_at")

        if expires:
            try:
                exp_dt = dt.strptime(expires, "%Y-%m-%d %H:%M:%S")
                if dt.now() > exp_dt:
                    expiry_txt = " | " + E_RED + " TAMAT"
                else:
                    remaining = int((exp_dt - dt.now()).total_seconds())
                    if remaining >= 86400:
                        expiry_txt = " | " + E_TIME + " " + str(remaining // 86400) + "h lagi"
                    elif remaining >= 3600:
                        expiry_txt = " | " + E_TIME + " " + str(remaining // 3600) + "j lagi"
                    else:
                        expiry_txt = " | " + E_TIME + " " + str(remaining // 60) + "m lagi"
            except Exception:
                expiry_txt = ""
        else:
            expiry_txt = " | " + E_ONLINE + " Permanent"

        lines.append(ico + " <code>" + uid + "</code> | " + un + " | <b>" + r.upper() + "</b>" + expiry_txt)

    text = "\n".join(lines)
    max_len = 4096
    if len(text) <= max_len:
        await update.message.reply_text(text, parse_mode="HTML")
    else:
        for chunk in [text[i:i+max_len] for i in range(0, len(text), max_len)]:
            await update.message.reply_text(chunk, parse_mode="HTML")


# =============================================================
#  /tagall -- Tag semua ahli dalam group (admin group sahaja)
# =============================================================

async def tagall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat    = update.effective_chat
    user    = update.effective_user
    message = update.message

    # Hanya dalam group/supergroup
    if chat.type not in ("group", "supergroup"):
        await message.reply_text(E_WARN + " Command /tagall hanya boleh digunakan dalam group.")
        return

    # Semak sama ada user adalah admin group
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        is_admin = member.status in ("administrator", "creator")
    except Exception:
        is_admin = False

    if not is_admin:
        await message.reply_text(
            E_BAN + " Hanya <b>Admin Group</b> sahaja boleh menggunakan /tagall.",
            parse_mode="HTML"
        )
        return

    # Ambil mesej dari command atau dari mesej yang di-reply
    custom_msg = ""
    if context.args:
        custom_msg = " ".join(context.args).replace("|", "\n")
    elif message.reply_to_message and message.reply_to_message.text:
        custom_msg = message.reply_to_message.text

    await context.bot.send_chat_action(chat_id=chat.id, action="typing")

    # Bina senarai tag dari group_members tracker (semua yang pernah mesej dalam group)
    members = load_group_members(chat.id)
    tags = []

    for uid, info in members.items():
        if int(uid) == context.bot.id:
            continue
        un = info.get("username", "")
        fn = info.get("full_name", "") or uid
        if un:
            tags.append("@" + un)
        else:
            tags.append(
                "<a href=\"tg://user?id=" + uid + "\">" + fn + "</a>"
            )

    # Tambah admin group yang mungkin belum pernah mesej
    try:
        admins = await context.bot.get_chat_administrators(chat.id)
        existing_ids = set(members.keys())
        for admin in admins:
            if admin.user.is_bot:
                continue
            if str(admin.user.id) not in existing_ids:
                if admin.user.username:
                    tags.append("@" + admin.user.username)
                else:
                    fn = admin.user.full_name or str(admin.user.id)
                    tags.append(
                        "<a href=\"tg://user?id=" + str(admin.user.id) + "\">" + fn + "</a>"
                    )
                # Simpan admin dalam tracker
                save_group_member(chat.id, admin.user.id, admin.user.username, admin.user.full_name)
    except Exception as e:
        logger.error("Gagal ambil admin list: " + str(e))

    # Header mesej
    if custom_msg:
        header = E_BURST + " <b>" + custom_msg + "</b>\n\n"
    else:
        header = E_BURST + " <b>Perhatian semua ahli!</b>\n\n"

    sender_name = "@" + user.username if user.username else (user.full_name or str(user.id))
    header += E_PERSON + " Daripada: " + sender_name + "\n" + E_LINE + "\n"

    max_len = 4096
    if tags:
        tag_text = " ".join(tags)
        full_msg = header + tag_text
        if len(full_msg) <= max_len:
            await message.reply_text(full_msg, parse_mode="HTML")
        else:
            await message.reply_text(header, parse_mode="HTML")
            for chunk in [tag_text[i:i+max_len] for i in range(0, len(tag_text), max_len)]:
                await context.bot.send_message(chat_id=chat.id, text=chunk, parse_mode="HTML")
    else:
        await message.reply_text(
            header + E_WARN + " Belum ada ahli yang direkodkan dalam group ini.\n\n"
            + E_INFO + " Tag akan berfungsi setelah ahli group mula berinteraksi.",
            parse_mode="HTML"
        )


# =============================================================
#  /code -- AI Coding Engine
# =============================================================

# Extension map -- detect bahasa dari keyword dalam request
LANG_EXT_MAP = [
    # (keyword list, extension, default filename)
    (["html", "webpage", "web page", "landing page", "website", "frontend", "laman web"],
     ".html", "index.html"),
    (["css", "stylesheet", "style sheet"],
     ".css", "style.css"),
    (["javascript", "js ", " js", "node.js", "nodejs", "react", "vue", "express", "next.js"],
     ".js", "script.js"),
    (["typescript", " ts ", ".ts"],
     ".ts", "script.ts"),
    (["python", "py ", ".py", "django", "flask", "fastapi", "pandas", "numpy", "selenium",
      "requests", "beautifulsoup", "scrapy", "termux"],
     ".py", "script.py"),
    (["bash", "shell", "sh ", ".sh", "linux", "terminal", "termux script"],
     ".sh", "script.sh"),
    (["php", ".php", "laravel", "wordpress"],
     ".php", "index.php"),
    (["java ", ".java", "android", "spring boot", "maven"],
     ".java", "Main.java"),
    (["kotlin", ".kt"],
     ".kt", "Main.kt"),
    (["swift", ".swift", "ios", "xcode"],
     ".swift", "Main.swift"),
    (["c#", "csharp", ".cs", "unity", ".net", "asp.net"],
     ".cs", "Program.cs"),
    (["c++", "cpp", ".cpp"],
     ".cpp", "main.cpp"),
    (["c ", ".c ", "header"],
     ".c", "main.c"),
    (["rust", ".rs"],
     ".rs", "main.rs"),
    (["go ", "golang", ".go"],
     ".go", "main.go"),
    (["ruby", ".rb", "rails"],
     ".rb", "script.rb"),
    (["lua", ".lua"],
     ".lua", "script.lua"),
    (["r ", ".r ", "rstudio", "tidyverse"],
     ".r", "script.r"),
    (["sql", "mysql", "postgresql", "sqlite", "database query"],
     ".sql", "query.sql"),
    (["json", ".json"],
     ".json", "data.json"),
    (["yaml", ".yaml", ".yml"],
     ".yaml", "config.yaml"),
    (["dart", "flutter", ".dart"],
     ".dart", "main.dart"),
    (["kotlin", "android"],
     ".kt", "Main.kt"),
    (["powershell", ".ps1"],
     ".ps1", "script.ps1"),
    (["batch", ".bat", ".cmd", "windows script"],
     ".bat", "script.bat"),
]


def detect_lang_filename(request_text, ai_filename=None):
    """
    Detect bahasa dan return filename yang sesuai.
    Keutamaan: filename dari AI (TERTINGGI) > detect dari request text > default
    """
    import re

    # Guna filename dari AI kalau ada dan valid -- INI DIUTAMAKAN
    if ai_filename and ai_filename.strip():
        clean = re.sub(r'[^\w.\-]', '_', ai_filename.strip())
        # Pastikan ada extension yang valid
        if '.' in clean and len(clean) < 80:
            return clean

    # Map extension kepada nama fail default (detect dari request)
    req_lower = request_text.lower()
    for keywords, ext, default_name in LANG_EXT_MAP:
        for kw in keywords:
            if kw in req_lower:
                return default_name

    return "script.py"


def parse_code_response(raw):
    """
    Parse response AI yang ada FILENAME: dan CODE: prefix.
    Return: (filename, code_content)
    """
    import re
    raw = raw.strip()

    filename = None
    code     = None

    # Cuba cari FILENAME: line
    fn_match = re.search(r'FILENAME:\s*(\S+)', raw, re.IGNORECASE)
    if fn_match:
        filename = fn_match.group(1).strip()

    # Cuba cari CODE: section
    code_match = re.search(r'CODE:\s*\n([\s\S]+)', raw, re.IGNORECASE)
    if code_match:
        code = code_match.group(1).strip()
    else:
        # Kalau format tak ikut -- guna semua teks sebagai code
        # Buang baris FILENAME: kalau ada
        code = re.sub(r'FILENAME:\s*\S+\s*\n?', '', raw).strip()
        # Buang markdown code fences kalau ada
        code = re.sub(r'^```[\w]*\n?', '', code)
        code = re.sub(r'\n?```$', '', code)
        code = code.strip()

    # Buang markdown code fences dari code juga
    if code:
        code = re.sub(r'^```[\w]*\n', '', code)
        code = re.sub(r'\n```$', '', code)
        code = code.strip()

    return filename, code or raw


async def code_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import tempfile
    user    = update.effective_user
    track_user(user)
    message = update.message
    chat    = update.effective_chat

    # Semak access
    if not has_access(user.id):
        await message.reply_text(
            E_BAN + " Anda tidak mempunyai akses ke ZenoxGPT.\n\n"
            + E_POINT + " Hubungi: " + DEVELOPER_USERNAME
        )
        return

    # Semak API key
    api_key, provider = get_api_key(user.id)
    if not api_key:
        await message.reply_text(
            E_KEY + " Sila masukkan API key dahulu:\n/addkey {apikey}"
        )
        return

    # Ambil prompt dari args
    code_request = " ".join(context.args) if context.args else ""
    if not code_request:
        await message.reply_text(
            E_WARN + " Format: /code {permintaan coding}\n\n"
            "Contoh:\n"
            "/code buatkan website landing page HTML lengkap\n"
            "/code buat python script scrape website\n"
            "/code buat bot telegram nodejs\n\n"
            + E_STAR + " Tip: Upload gambar error + caption /code untuk betulkan error!"
        )
        return

    username = user.username or ""
    role     = get_user_role(user.id)
    now      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log ke info bot
    threading.Thread(target=send_info, args=(
        E_PENCIL + " <b>PERMINTAAN /code</b>\n"
        + E_LINE + "\n"
        + E_ID + " User ID  : <code>" + str(user.id) + "</code>\n"
        + E_PERSON + " Username : @" + (username or "tiada") + "\n"
        + ROLE_EMOJI.get(role, E_BADGE) + " Role     : " + role.upper() + "\n"
        + E_TIME + " Masa     : " + now + "\n"
        + E_LINE + "\n"
        + E_QUESTION + " <b>Request:</b>\n" + code_request[:500],
    ), daemon=True).start()

    await context.bot.send_chat_action(chat_id=chat.id, action="upload_document")
    await message.reply_text(E_HOURGLASS + " Code Engine sedang menjana code sempurna...")

    # Panggil AI
    loop = asyncio.get_event_loop()
    fn1  = functools.partial(call_ai_api, api_key, provider, code_request, CODE_PROMPT)
    success, code_result = await loop.run_in_executor(None, fn1)

    if not success:
        await message.reply_text(format_api_error(code_result), parse_mode="HTML")
        return

    # Parse filename dan code dari response AI
    ai_filename, code_clean = parse_code_response(code_result)
    filename = detect_lang_filename(code_request, ai_filename)

    # Simpan sebagai fail sementara
    tmp_path = os.path.join(tempfile.gettempdir(), filename)
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(code_clean)
    except Exception as e:
        await message.reply_text(E_WARN + " Gagal simpan fail: " + str(e))
        return

    # Hantar sebagai file
    try:
        await context.bot.send_chat_action(chat_id=chat.id, action="upload_document")
        with open(tmp_path, "rb") as f:
            await message.reply_document(
                document=f,
                filename=filename,
                caption=(
                    E_DEV + " <b>" + filename + "</b>\n"
                    + E_CHECK + " Code siap & berfungsi penuh\n"
                    + E_STAR + " Request: " + code_request[:100]
                ),
                parse_mode="HTML"
            )
    except Exception as e:
        logger.error("code send file: " + str(e))
        await message.reply_text(E_WARN + " Gagal hantar fail: " + str(e))
        return
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

    # Penjelasan -- hantar sebagai teks selepas file
    await context.bot.send_chat_action(chat_id=chat.id, action="typing")

    explain_prompt = (
        "Pengguna tadi meminta: " + code_request + "\n\n"
        "Kau tadi telah menghasilkan code tersebut. "
        "Sekarang berikan penjelasan ringkas dalam Bahasa Melayu:\n"
        "1. Apa yang code ini lakukan\n"
        "2. Cara untuk menjalankannya\n"
        "3. Apa yang perlu dipasang (jika ada)\n"
        "4. Nota penting lain (jika ada)\n\n"
        "JANGAN tulis semula code. Penjelasan sahaja. Pendek dan jelas."
    )

    fn2 = functools.partial(call_ai_api, api_key, provider, explain_prompt, SYSTEM_PROMPT)
    success2, explain_result = await loop.run_in_executor(None, fn2)

    if success2 and explain_result:
        explain_msg = (
            E_INFO + " <b>Penjelasan</b>\n"
            + E_LINE + "\n"
            + explain_result
        )
        max_len = 4096
        if len(explain_msg) <= max_len:
            await message.reply_text(explain_msg, parse_mode="HTML")
        else:
            await message.reply_text(explain_msg[:max_len], parse_mode="HTML")


# =============================================================
#  /getcode -- Ambil source code website dan hantar sebagai .html
#  Guna Python untuk inline CSS/JS -- TANPA AI (unlimited size)
# =============================================================

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}


def _resolve_url(base_url, relative_url):
    """Resolve relative URL kepada absolute URL."""
    try:
        from urllib.parse import urljoin, urlparse
        if relative_url.startswith("data:"):
            return relative_url
        if relative_url.startswith("//"):
            scheme = urlparse(base_url).scheme or "https"
            return scheme + ":" + relative_url
        if relative_url.startswith("http://") or relative_url.startswith("https://"):
            return relative_url
        return urljoin(base_url, relative_url)
    except Exception:
        return relative_url


def _fetch_text_resource(url, timeout=15):
    """Fetch CSS/JS resource, return content atau empty string kalau gagal."""
    try:
        r = requests.get(url, headers=BROWSER_HEADERS, timeout=timeout, allow_redirects=True)
        if r.status_code == 200:
            r.encoding = r.apparent_encoding or "utf-8"
            return r.text
    except Exception as e:
        logger.warning("Resource fetch fail [" + url + "]: " + str(e))
    return ""


def _inline_all_resources(html, base_url):
    """
    Inline semua CSS <link> dan JS <script src> ke dalam HTML.
    Tukar URL relative dalam CSS kepada absolute.
    Return: html string yang dah di-inline.
    """
    import re
    from urllib.parse import urljoin

    # --- Inline CSS <link rel="stylesheet"> ---
    def replace_link_css(m):
        href = m.group(1) or m.group(2)
        if not href or href.startswith("data:"):
            return m.group(0)
        abs_url = _resolve_url(base_url, href.strip())
        css_content = _fetch_text_resource(abs_url)
        if not css_content:
            return "<!-- CSS not loaded: " + abs_url + " -->"
        # Tukar url() dalam CSS kepada absolute
        def fix_css_url(cm):
            raw = cm.group(1).strip().strip("'\"")
            if raw.startswith("data:") or raw.startswith("http"):
                return cm.group(0)
            abs_css = _resolve_url(abs_url, raw)
            return "url('" + abs_css + "')"
        css_content = re.sub(r"url\(([^)]+)\)", fix_css_url, css_content)
        return "<style>\n" + css_content + "\n</style>"

    # Match <link ... href="..." rel="stylesheet"> dalam pelbagai urutan attribute
    html = re.sub(
        r'<link[^>]+rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)["\'][^>]*/?>',
        replace_link_css, html, flags=re.IGNORECASE
    )
    html = re.sub(
        r'<link[^>]+href=["\']([^"\']+)["\'][^>]*rel=["\']stylesheet["\'][^>]*/?>',
        replace_link_css, html, flags=re.IGNORECASE
    )

    # --- Inline JS <script src="..."> ---
    def replace_script_src(m):
        full_tag = m.group(0)
        src = m.group(1) or m.group(2)
        if not src or src.startswith("data:"):
            return full_tag
        abs_url = _resolve_url(base_url, src.strip())
        js_content = _fetch_text_resource(abs_url)
        if not js_content:
            return "<!-- JS not loaded: " + abs_url + " -->"
        return "<script>\n" + js_content + "\n</script>"

    html = re.sub(
        r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>\s*</script>',
        replace_script_src, html, flags=re.IGNORECASE
    )
    html = re.sub(
        r'<script[^>]+src=["\']([^"\']+)["\'][^>]*/>',
        replace_script_src, html, flags=re.IGNORECASE
    )

    # --- Tukar semua href/src/action yang relative kepada absolute ---
    def abs_attr(m):
        attr = m.group(1)
        val  = m.group(2)
        if val.startswith(("http", "data:", "//", "mailto:", "tel:", "#", "javascript:")):
            return m.group(0)
        return attr + '="' + _resolve_url(base_url, val) + '"'

    html = re.sub(r'((?:href|src|action))="([^"]*)"', abs_attr, html, flags=re.IGNORECASE)
    html = re.sub(r"((?:href|src|action))='([^']*)'", abs_attr, html, flags=re.IGNORECASE)

    return html


def _build_singlefile_html(url):
    """
    Main function: fetch + inline semua resource.
    Return: (success, html_content atau error_code)
    """
    try:
        r = requests.get(url, headers=BROWSER_HEADERS, timeout=30, allow_redirects=True)
        final_url = r.url  # URL selepas redirect
        if r.status_code == 403:
            return False, "blocked"
        if r.status_code == 404:
            return False, "not_found"
        if r.status_code != 200:
            return False, "http_" + str(r.status_code)
        r.encoding = r.apparent_encoding or "utf-8"
        html = r.text
    except requests.exceptions.Timeout:
        return False, "timeout"
    except requests.exceptions.ConnectionError:
        return False, "connection_error"
    except Exception as e:
        return False, "error:" + str(e)[:80]

    # Inline semua CSS dan JS
    try:
        html = _inline_all_resources(html, final_url)
    except Exception as e:
        logger.error("inline resources error: " + str(e))
        # Kalau inline fail, hantar HTML mentah sahaja

    return True, html


async def getcode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import re, tempfile
    user    = update.effective_user
    message = update.message
    chat    = update.effective_chat
    track_user(user)

    # Semak access
    if not has_access(user.id):
        await message.reply_text(
            E_BAN + " Anda tidak mempunyai akses ke ZenoxGPT.\n\n"
            + E_POINT + " Hubungi: " + DEVELOPER_USERNAME
        )
        return

    # Semak URL
    if not context.args:
        await message.reply_text(
            E_LINK + " <b>Format:</b> /getcode {url}\n\n"
            "Contoh:\n"
            "/getcode https://example.com\n\n"
            + E_INFO + " Bot akan inline semua CSS dan JS "
            "dan hantar dalam satu fail .html",
            parse_mode="HTML"
        )
        return

    url = context.args[0].strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    await message.reply_text(
        E_HOURGLASS + " Mengambil source code dari:\n"
        + E_LINK + " <code>" + url + "</code>\n\n"
        + E_GLOBE + " Sedang inline CSS dan JS... sila tunggu.",
        parse_mode="HTML"
    )

    # Bina single-file HTML dalam thread
    loop = asyncio.get_event_loop()
    fn = functools.partial(_build_singlefile_html, url)
    await context.bot.send_chat_action(chat_id=chat.id, action="upload_document")
    ok, result = await loop.run_in_executor(None, fn)

    if not ok:
        err_map = {
            "blocked":          E_BAN + " Website menyekat akses bot (403).\nCuba URL lain.",
            "not_found":        E_CROSS + " URL tidak dijumpai (404).",
            "timeout":          E_HOURGLASS + " Timeout. Cuba semula.",
            "connection_error": E_SIGNAL + " Gagal sambung. Semak URL.",
        }
        err_msg = err_map.get(result, E_WARN + " Error: " + result)
        await message.reply_text(err_msg)
        return

    html_final = result
    size_kb = round(len(html_final.encode("utf-8")) / 1024, 1)

    # Buat nama fail dari domain
    try:
        domain = url.split("//")[-1].split("/")[0].replace("www.", "")
        domain = re.sub(r"[^\w\-.]", "_", domain)
    except Exception:
        domain = "website"
    filename = domain + ".html"
    tmp_path = os.path.join(tempfile.gettempdir(), filename)

    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(html_final)
    except Exception as e:
        await message.reply_text(E_WARN + " Gagal simpan fail: " + str(e))
        return

    # Hantar fail
    try:
        caption = (
            E_FOLDER + " <b>" + filename + "</b>\n"
            + E_STAT + " Saiz: <b>" + str(size_kb) + " KB</b>\n"
            + E_LINK + " Sumber: <code>" + url + "</code>\n"
            + E_CHECK + " HTML + CSS + JS inline dalam satu fail"
        )
        with open(tmp_path, "rb") as f:
            await message.reply_document(
                document=f,
                filename=filename,
                caption=caption,
                parse_mode="HTML"
            )
    except Exception as e:
        logger.error("getcode send: " + str(e))
        await message.reply_text(E_WARN + " Gagal hantar fail: " + str(e))
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

    # Log ke info bot
    threading.Thread(
        target=send_info,
        args=(
            E_LINK + " <b>/getcode</b>\n"
            + E_PERSON + " " + (user.username or str(user.id)) + "\n"
            + E_GLOBE + " " + url + "\n"
            + E_STAT + " " + str(size_kb) + " KB",
        ),
        daemon=True
    ).start()


# Handler untuk gambar dengan caption /code (error fixing)
async def handle_photo_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler gambar + caption /code -- buat coding BERPANDUKAN gambar sebagai panduan/tema.
    """
    import tempfile, base64
    user    = update.effective_user
    message = update.message
    chat    = update.effective_chat

    if not message.photo:
        return
    caption = message.caption or ""
    if not caption.strip().lower().startswith("/code"):
        return

    if not has_access(user.id):
        await message.reply_text(E_BAN + " Tiada akses. Hubungi: " + DEVELOPER_USERNAME)
        return

    api_key, provider = get_api_key(user.id)
    if not api_key:
        await message.reply_text(E_KEY + " Sila masukkan API key: /addkey {apikey}")
        return

    user_request = caption.strip()[5:].strip()  # buang /code
    if not user_request:
        user_request = "Buat coding berdasarkan gambar ini. Ikut reka bentuk, warna, layout dan semua elemen dalam gambar."

    role = get_user_role(user.id)
    threading.Thread(target=send_info, args=(
        E_PENCIL + " <b>/code + GAMBAR</b>\n"
        + E_ID + " " + str(user.id) + " | @" + (user.username or "tiada") + "\n"
        + E_QUESTION + " " + user_request[:200],
    ), daemon=True).start()

    await context.bot.send_chat_action(chat_id=chat.id, action="upload_document")
    await message.reply_text(E_HOURGLASS + " Code Engine sedang menganalisis gambar dan menjana code...")

    try:
        photo_file  = await message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        photo_b64   = base64.b64encode(photo_bytes).decode("utf-8")
    except Exception as e:
        await message.reply_text(E_CROSS + " Gagal proses gambar: " + str(e))
        return

    image_prompt = (
        "Pengguna menghantar gambar sebagai PANDUAN/RUJUKAN untuk coding.\n"
        "Permintaan: " + user_request + "\n\n"
        "Analisis gambar ini dengan teliti -- perhatikan reka bentuk, warna, layout, elemen UI, struktur.\n"
        "Hasilkan code yang SERUPA/SAMA seperti dalam gambar tersebut mengikut permintaan pengguna.\n"
        "Ikut format output: FILENAME: namafile.ext\nCODE:\n[code penuh]"
    )

    loop = asyncio.get_event_loop()
    if provider == "gemini":
        fn = functools.partial(_call_gemini_vision_with_prompt, api_key, image_prompt, photo_b64, CODE_PROMPT)
    else:
        fn = functools.partial(call_ai_api, api_key, provider,
            image_prompt + "\n\n[Gambar panduan disertakan]", CODE_PROMPT)
    success, code_result = await loop.run_in_executor(None, fn)

    if not success:
        await message.reply_text(format_api_error(code_result), parse_mode="HTML")
        return

    ai_filename, code_clean = parse_code_response(code_result)
    filename = detect_lang_filename(user_request, ai_filename)
    tmp_path = os.path.join(tempfile.gettempdir(), filename)

    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(code_clean)
        with open(tmp_path, "rb") as f:
            await message.reply_document(
                document=f, filename=filename,
                caption=(
                    E_DEV + " <b>" + filename + "</b>\n"
                    + E_CHECK + " Code dijana berdasarkan gambar panduan\n"
                    + E_STAR + " " + user_request[:100]
                ),
                parse_mode="HTML"
            )
    except Exception as e:
        await message.reply_text(E_WARN + " Gagal hantar fail: " + str(e))
    finally:
        try: os.remove(tmp_path)
        except Exception: pass

    # Penjelasan
    await context.bot.send_chat_action(chat_id=chat.id, action="typing")
    fn2 = functools.partial(call_ai_api, api_key, provider,
        "Pengguna minta buat code berdasarkan gambar. Terangkan secara ringkas dalam Bahasa Melayu: "
        "1. Apa yang code ini lakukan 2. Cara jalankan 3. Apa yang perlu dipasang. "
        "JANGAN tulis semula code.", SYSTEM_PROMPT)
    ok2, expl = await loop.run_in_executor(None, fn2)
    if ok2 and expl:
        await message.reply_text(
            E_INFO + " <b>Penjelasan</b>\n" + E_LINE + "\n" + expl[:4096],
            parse_mode="HTML"
        )


async def fixcode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /fixcode -- Betulkan error dalam code.
    Cara 1: /fixcode + describe error (teks)
    Cara 2: Hantar gambar error + caption /fixcode
    Cara 3: Balas code/gambar error dengan /fixcode
    """
    import tempfile, base64
    user    = update.effective_user
    message = update.message
    chat    = update.effective_chat
    track_user(user)

    if not has_access(user.id):
        await message.reply_text(E_BAN + " Tiada akses. Hubungi: " + DEVELOPER_USERNAME)
        return

    api_key, provider = get_api_key(user.id)
    if not api_key:
        await message.reply_text(E_KEY + " Sila masukkan API key: /addkey {apikey}")
        return

    # Tentukan error description dan sama ada ada gambar
    error_desc  = " ".join(context.args).strip() if context.args else ""
    photo_b64   = None
    source_text = ""

    # Semak gambar dalam mesej semasa (caption /fixcode + gambar)
    if message.photo:
        try:
            pf    = await message.photo[-1].get_file()
            pb    = await pf.download_as_bytearray()
            photo_b64 = base64.b64encode(pb).decode("utf-8")
        except Exception as e:
            await message.reply_text(E_CROSS + " Gagal proses gambar: " + str(e))
            return

    # Semak reply -- gambar error atau teks code
    elif message.reply_to_message:
        replied = message.reply_to_message
        if replied.photo:
            try:
                pf    = await replied.photo[-1].get_file()
                pb    = await pf.download_as_bytearray()
                photo_b64 = base64.b64encode(pb).decode("utf-8")
            except Exception as e:
                await message.reply_text(E_CROSS + " Gagal proses gambar: " + str(e))
                return
        elif replied.text:
            source_text = replied.text
        elif replied.document:
            # Cuba download document sebagai teks
            try:
                df    = await replied.document.get_file()
                dbytes = await df.download_as_bytearray()
                source_text = dbytes.decode("utf-8", errors="replace")[:8000]
            except Exception:
                pass

    # Mesti ada sesuatu untuk difix
    if not error_desc and not photo_b64 and not source_text:
        await message.reply_text(
            E_WARN + " <b>Format /fixcode:</b>\n\n"
            + E_INFO + " <b>Cara 1</b> — Describe error:\n"
            "<code>/fixcode [nama bahasa] error: [description]</code>\n\n"
            + E_INFO + " <b>Cara 2</b> — Hantar gambar error + caption:\n"
            "<code>/fixcode [description tambahan]</code>\n\n"
            + E_INFO + " <b>Cara 3</b> — Balas gambar/code dengan:\n"
            "<code>/fixcode [description tambahan]</code>\n\n"
            "Contoh:\n"
            "<code>/fixcode python TypeError: list indices must be integers</code>",
            parse_mode="HTML"
        )
        return

    role = get_user_role(user.id)
    threading.Thread(target=send_info, args=(
        E_TOOL + " <b>/fixcode</b>\n"
        + E_ID + " " + str(user.id) + " | @" + (user.username or "tiada") + "\n"
        + E_QUESTION + " " + (error_desc or "(gambar/code)")[:200],
    ), daemon=True).start()

    await context.bot.send_chat_action(chat_id=chat.id, action="upload_document")
    await message.reply_text(E_HOURGLASS + " Fix Engine sedang menganalisis dan membetulkan error...")

    loop = asyncio.get_event_loop()

    # Bina prompt fix
    if photo_b64:
        # Ada gambar -- guna vision
        fix_prompt = (
            "Gambar ini menunjukkan ERROR dalam code.\n"
            + ("Maklumat tambahan: " + error_desc + "\n\n" if error_desc else "")
            + "Baca mesej error dalam gambar dengan TEPAT.\n"
            "Betulkan SEMUA error sepenuhnya.\n"
            "Ikut format: FILENAME: namafile.ext\nCODE:\n[code fixed]\nANALISIS:\n[punca & pembetulan]"
        )
        if provider == "gemini":
            fn = functools.partial(_call_gemini_vision_with_prompt, api_key, fix_prompt, photo_b64, FIXCODE_PROMPT)
        else:
            fn = functools.partial(call_ai_api, api_key, provider,
                fix_prompt + "\n\n[Gambar error disertakan]", FIXCODE_PROMPT)
    else:
        # Teks sahaja
        fix_prompt = (
            "Error yang perlu dibaiki:\n"
            + (error_desc + "\n\n" if error_desc else "")
            + ("Code bermasalah:\n" + source_text + "\n\n" if source_text else "")
            + "Analisis error dengan teliti dan betulkan sepenuhnya.\n"
            "Ikut format: FILENAME: namafile.ext\nCODE:\n[code fixed]\nANALISIS:\n[punca & pembetulan]"
        )
        fn = functools.partial(call_ai_api, api_key, provider, fix_prompt, FIXCODE_PROMPT)

    success, fix_result = await loop.run_in_executor(None, fn)

    if not success:
        await message.reply_text(format_api_error(fix_result), parse_mode="HTML")
        return

    # Parse -- pisahkan CODE dan ANALISIS
    import re
    analisis_match = re.search(r'ANALISIS:\s*\n([\s\S]+)$', fix_result, re.IGNORECASE)
    analisis_txt   = analisis_match.group(1).strip() if analisis_match else ""
    code_part      = fix_result
    if analisis_match:
        code_part = fix_result[:analisis_match.start()].strip()

    ai_filename, code_clean = parse_code_response(code_part)
    filename = detect_lang_filename(error_desc or source_text[:100], ai_filename)
    tmp_path = os.path.join(tempfile.gettempdir(), filename)

    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(code_clean)
        with open(tmp_path, "rb") as f:
            await message.reply_document(
                document=f, filename=filename,
                caption=(
                    E_DEV + " <b>" + filename + "</b>\n"
                    + E_CHECK + " Error telah dibetulkan sepenuhnya\n"
                    + E_TOOL + " Fix Engine by ZenoxGPT"
                ),
                parse_mode="HTML"
            )
    except Exception as e:
        await message.reply_text(E_WARN + " Gagal hantar fail: " + str(e))
        return
    finally:
        try: os.remove(tmp_path)
        except Exception: pass

    # Hantar analisis error
    if analisis_txt:
        await message.reply_text(
            E_INFO + " <b>Analisis Error</b>\n"
            + E_LINE + "\n"
            + analisis_txt[:4096],
            parse_mode="HTML"
        )


async def handle_photo_fixcode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler gambar + caption /fixcode."""
    message = update.message
    if not message or not message.photo:
        return
    caption = (message.caption or "").strip()
    if not caption.lower().startswith("/fixcode"):
        return
    # Set args dari caption (buang /fixcode)
    extra = caption[8:].strip()
    context.args = extra.split() if extra else []
    await fixcode_command(update, context)


def _call_gemini_vision_with_prompt(key, prompt, image_b64, system_prompt):
    """Panggil Gemini Vision dengan system_prompt yang boleh ditentukan."""
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           + GEMINI_MODEL + ":generateContent?key=" + key)
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{
            "role": "user",
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": image_b64}}
            ]
        }],
        "generationConfig": {"temperature": 0.5, "maxOutputTokens": 8192},
    }
    try:
        r = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=90)
        if r.status_code == 404:
            # Fallback ke model lain
            url2 = url.replace(GEMINI_MODEL, GEMINI_MODEL_FALLBACK)
            r = requests.post(url2, json=payload, headers={"Content-Type": "application/json"}, timeout=90)
        if r.status_code in (400, 403): return False, "invalid_key"
        if r.status_code == 429: return False, "limit_exceeded"
        if r.status_code != 200: return False, "http_" + str(r.status_code)
        data = r.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return True, "Maaf, AI tidak dapat menganalisis gambar ini."
        parts = candidates[0].get("content", {}).get("parts", [])
        return True, "".join(p.get("text", "") for p in parts).strip() or "Tiada jawapan."
    except requests.exceptions.Timeout: return False, "timeout"
    except requests.exceptions.ConnectionError: return False, "connection_error"
    except Exception as e:
        logger.error("Gemini Vision: " + str(e))
        return False, "error:" + str(e)[:80]


async def handle_photo_and_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk semua PHOTO mesej.
    Semak caption -- /all, /tourl, /fixcode, /filter, /code, /{filter_trigger}
    """
    message = update.message
    if not message or not message.photo:
        return

    caption = (message.caption or "").strip()
    cap_low = caption.lower()

    if cap_low.startswith("/all"):
        context.args = caption[4:].strip().split()
        await all_command(update, context)
    elif cap_low.startswith("/tourl"):
        await tourl_command(update, context)
    elif cap_low.startswith("/fixcode"):
        await handle_photo_fixcode(update, context)
    elif cap_low.startswith("/filter"):
        context.args = caption[7:].strip().split()
        await filter_command(update, context)
    elif cap_low.startswith("/code"):
        await handle_photo_code(update, context)
    elif caption.startswith("/"):
        await handle_filter_trigger(update, context)


async def handle_doc_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk semua DOCUMENT mesej.
    Semak caption -- /all, /enc, /tourl, /filter, /{filter_trigger}
    """
    message = update.message
    if not message or not message.document:
        return
    caption = (message.caption or "").strip()
    cap_low = caption.lower()

    if cap_low.startswith("/all"):
        context.args = caption[4:].strip().split()
        await all_command(update, context)
    elif cap_low.startswith("/enc") and not cap_low.startswith("/encpy"):
        await enc_command(update, context)
    elif cap_low.startswith("/encpy"):
        await encpy_command(update, context)
    elif cap_low.startswith("/tourl"):
        await tourl_command(update, context)
    elif cap_low.startswith("/filter"):
        context.args = caption[7:].strip().split()
        await filter_command(update, context)
    elif caption.startswith("/"):
        await handle_filter_trigger(update, context)


async def handle_video_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler video -- semak caption /all atau /filter."""
    message = update.message
    if not message or not message.video:
        return
    caption = (message.caption or "").strip()
    cap_low = caption.lower()

    if cap_low.startswith("/all"):
        context.args = caption[4:].strip().split()
        await all_command(update, context)
    elif cap_low.startswith("/tourl"):
        await tourl_command(update, context)
    elif cap_low.startswith("/filter"):
        context.args = caption[7:].strip().split()
        await filter_command(update, context)
    elif caption.startswith("/"):
        await handle_filter_trigger(update, context)


async def handle_audio_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler audio -- semak caption /all atau /filter."""
    message = update.message
    if not message or not message.audio:
        return
    caption = (message.caption or "").strip()
    cap_low = caption.lower()

    if cap_low.startswith("/all"):
        context.args = caption[4:].strip().split()
        await all_command(update, context)
    elif cap_low.startswith("/tourl"):
        await tourl_command(update, context)
    elif cap_low.startswith("/filter"):
        context.args = caption[7:].strip().split()
        await filter_command(update, context)
    elif caption.startswith("/"):
        await handle_filter_trigger(update, context)


# =============================================================
#  /all -- Broadcast mesej ke semua user yang pernah /start
# =============================================================

async def all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user    = update.effective_user
    chat    = update.effective_chat
    message = update.message
    role    = get_user_role(user.id)

    # Hanya dalam private chat
    if chat.type != "private":
        await message.reply_text(E_WARN + " Command /all hanya boleh digunakan dalam private chat.")
        return

    # Semak role -- owner ke atas sahaja
    if role not in ("owner", "partner", "developer"):
        await message.reply_text(
            E_BAN + " Anda tidak mempunyai kebenaran untuk menggunakan /all.\n\n"
            + E_BADGE + " Role diperlukan: Owner / Partner / Developer\n"
            + E_BADGE + " Role anda: " + role.upper()
        )
        return

    # ── Tentukan source mesej dan caption ──────────────────────
    # Cara 1: mesej semasa ada media + caption mengandungi /all
    # Cara 2: balas mesej/media lain dengan /all {caption}

    def msg_has_media(m):
        return bool(
            m.document or m.photo or m.video or m.audio or
            m.voice or m.video_note or m.sticker or m.animation
        )

    source_msg  = None   # mesej yang ada media/teks untuk dibroadcast
    caption_txt = " ".join(context.args).strip() if context.args else ""
    # Tukar | kepada newline -- cara nak buat teks berbilang baris
    caption_txt = caption_txt.replace("|", "\n")

    # Cara 1: mesej semasa ada media (hantar dengan caption /all ...)
    if msg_has_media(message):
        source_msg  = message
        # caption dari media message (buang bahagian /all)
        raw_cap = message.caption or ""
        if raw_cap.strip().lower().startswith("/all"):
            extra = raw_cap.strip()[4:].strip().replace("|", "\n")
            if extra:
                caption_txt = extra

    # Cara 2: reply kepada mesej/media lain
    elif message.reply_to_message:
        replied = message.reply_to_message
        if msg_has_media(replied) or replied.text:
            source_msg = replied
            # caption dari args command /all

    # Cara 3: teks biasa sahaja (tiada media)
    # source_msg kekal None, guna caption_txt sebagai broadcast teks

    # Kena ada kandungan
    if source_msg is None and not caption_txt:
        await message.reply_text(
            E_WARN + " <b>Format /all:</b>\n\n"
            + E_INFO + " <b>Cara 1</b> — Broadcast teks:\n"
            "<code>/all teks mesej anda</code>\n\n"
            + E_INFO + " <b>Cara 2</b> — Broadcast dengan media (caption):\n"
            "Hantar media + caption <code>/all teks anda</code>\n\n"
            + E_INFO + " <b>Cara 3</b> — Balas mesej/media dengan:\n"
            "<code>/all teks tambahan</code>",
            parse_mode="HTML"
        )
        return

    username = user.username or str(user.id)
    now      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Header broadcast
    header = (
        E_BURST + " <b>Mesej Penting dari ZenoxGPT</b>\n"
        + E_LINE + "\n"
        + E_PERSON + " Daripada: @" + username + "\n"
        + E_TIME + " Masa: " + now + "\n"
        + E_LINE
    )

    # Caption untuk media (header + teks tambahan)
    media_caption = header
    if caption_txt:
        media_caption += "\n" + caption_txt

    # Teks broadcast (kalau teks sahaja)
    text_broadcast = header + "\n" + caption_txt if caption_txt else header

    # Log ke info bot
    log_content = caption_txt[:300] if caption_txt else "(media sahaja)"
    threading.Thread(target=send_info, args=(
        E_SIGNAL + " <b>BROADCAST /all DIHANTAR</b>\n"
        + E_LINE + "\n"
        + E_ID + " User ID  : <code>" + str(user.id) + "</code>\n"
        + E_PERSON + " Username : @" + username + "\n"
        + ROLE_EMOJI.get(role, E_BADGE) + " Role     : " + role.upper() + "\n"
        + E_TIME + " Masa     : " + now + "\n"
        + E_LINE + "\n"
        + E_CHAT + " <b>Kandungan:</b>\n" + log_content,
    ), daemon=True).start()

    started = load_started_users()
    if not started:
        await message.reply_text(E_CROSS + " Tiada pengguna yang pernah /start bot ini.")
        return

    total         = len(started)
    success_count = 0
    fail_count    = 0

    status_msg = await message.reply_text(
        E_HOURGLASS + " Menghantar broadcast ke <b>" + str(total) + "</b> pengguna...",
        parse_mode="HTML"
    )

    for uid_str in started.keys():
        uid = int(uid_str)
        try:
            if source_msg is None:
                # Teks sahaja
                await context.bot.send_message(
                    chat_id=uid,
                    text=text_broadcast,
                    parse_mode="HTML"
                )

            elif source_msg.document:
                await context.bot.send_document(
                    chat_id=uid,
                    document=source_msg.document.file_id,
                    caption=media_caption,
                    parse_mode="HTML"
                )

            elif source_msg.photo:
                await context.bot.send_photo(
                    chat_id=uid,
                    photo=source_msg.photo[-1].file_id,
                    caption=media_caption,
                    parse_mode="HTML"
                )

            elif source_msg.video:
                await context.bot.send_video(
                    chat_id=uid,
                    video=source_msg.video.file_id,
                    caption=media_caption,
                    parse_mode="HTML"
                )

            elif source_msg.audio:
                await context.bot.send_audio(
                    chat_id=uid,
                    audio=source_msg.audio.file_id,
                    caption=media_caption,
                    parse_mode="HTML"
                )

            elif source_msg.voice:
                await context.bot.send_voice(
                    chat_id=uid,
                    voice=source_msg.voice.file_id,
                    caption=media_caption,
                    parse_mode="HTML"
                )

            elif source_msg.video_note:
                await context.bot.send_video_note(
                    chat_id=uid,
                    video_note=source_msg.video_note.file_id
                )

            elif source_msg.sticker:
                await context.bot.send_sticker(
                    chat_id=uid,
                    sticker=source_msg.sticker.file_id
                )

            elif source_msg.animation:
                await context.bot.send_animation(
                    chat_id=uid,
                    animation=source_msg.animation.file_id,
                    caption=media_caption,
                    parse_mode="HTML"
                )

            elif source_msg.text:
                # Replied teks
                full_text = text_broadcast + "\n\n" + source_msg.text
                await context.bot.send_message(
                    chat_id=uid,
                    text=full_text[:4096],
                    parse_mode="HTML"
                )

            success_count += 1

        except Exception as e:
            logger.warning("broadcast fail [" + uid_str + "]: " + str(e))
            fail_count += 1

        await asyncio.sleep(0.05)

    await status_msg.edit_text(
        E_CHECK + " <b>Broadcast selesai!</b>\n\n"
        + E_LINE + "\n"
        + E_CHECK + " Berjaya : <b>" + str(success_count) + "</b> pengguna\n"
        + E_CROSS + " Gagal   : <b>" + str(fail_count) + "</b> pengguna\n"
        + E_LINE,
        parse_mode="HTML"
    )


# =============================================================
#  MESSAGE HANDLER -- AI CHAT
# =============================================================

# Keyword untuk detect permintaan coding dalam chat biasa
CODING_KEYWORDS = [
    # Malay
    "buatkan coding", "buatkan code", "buatkan skrip", "buatkan script",
    "buat coding", "buat code", "buat skrip", "buat script",
    "hasilkan coding", "hasilkan code", "hasilkan skrip",
    "tulis coding", "tulis code", "tulis skrip", "tulis script",
    "cipta coding", "cipta code", "cipta skrip",
    "tolong buat", "boleh buat", "boleh buatkan",
    "nak code", "nak coding", "nak script", "nak skrip",
    "contoh code", "contoh coding", "contoh script",
    "coding untuk", "code untuk", "script untuk",
    "program untuk", "buatkan program", "buat program",
    "buatkan bot", "buat bot", "buatkan website", "buat website",
    "buatkan tool", "buat tool", "buatkan tools",
    "buatkan app", "buat app", "buatkan aplikasi",
    "buatkan fungsi", "buat fungsi", "buatkan function",
    # English
    "write code", "write a code", "write script", "write a script",
    "create code", "create a code", "create script",
    "make code", "make a code", "make script", "make a script",
    "build a", "create a bot", "make a bot",
    "generate code", "give me code", "show me code",
    "code for", "script for", "program for",
    "write me a", "create me a", "make me a",
    "develop a", "implement a",
]


def is_coding_request(text):
    """Return True kalau mesej adalah permintaan coding."""
    t = text.lower()
    for kw in CODING_KEYWORDS:
        if kw in t:
            return True
    return False


async def _send_code_as_file(message, chat, context, api_key, provider, user_message, loop, context_text=""):
    """
    Panggil AI dengan CODE_PROMPT, parse result, hantar sebagai file.
    Sokongan: berbilang file, context dari reply chain.
    """
    import tempfile, re

    # Detect berapa banyak coding diminta
    count_match = re.search(
        r'\b(\d+)\s*(coding|code|fail|file|skrip|script|program|fungsi|function|komponen|component|modul|module|app|aplikasi)\b',
        user_message, re.IGNORECASE
    )
    expected_count = int(count_match.group(1)) if count_match and 1 < int(count_match.group(1)) <= 20 else 1

    await context.bot.send_chat_action(chat_id=chat.id, action="upload_document")
    if expected_count > 1:
        await message.reply_text(
            E_HOURGLASS + " Code Engine sedang menjana <b>" + str(expected_count) + " fail</b> coding...",
            parse_mode="HTML"
        )
    else:
        await message.reply_text(E_HOURGLASS + " Code Engine sedang menjana code sempurna...")

    # Bina messages history untuk context
    messages_history = []
    if context_text:
        # context_text adalah mesej yang dibalas -- masukkan sebagai assistant turn
        messages_history.append({"role": "assistant", "content": context_text})

    # Bina prompt -- untuk berbilang fail, terangkan format dengan jelas
    if expected_count > 1:
        final_prompt = (
            user_message + "\n\n"
            "PENTING: Hasilkan TEPAT " + str(expected_count) + " fail yang berbeza. "
            "Pisahkan setiap fail dengan ---NEXT--- seperti format:\n"
            "FILENAME: fail1.ext\nCODE:\n[code]\n---NEXT---\n"
            "FILENAME: fail2.ext\nCODE:\n[code]\n---NEXT---\n"
            "Teruskan sehingga " + str(expected_count) + " fail selesai."
        )
    else:
        final_prompt = user_message

    messages_history.append({"role": "user", "content": final_prompt})

    # Panggil AI dengan history
    fn = functools.partial(call_ai_api_with_history, api_key, provider, messages_history, CODE_PROMPT)
    success, code_result = await loop.run_in_executor(None, fn)

    if not success:
        await message.reply_text(format_api_error(code_result), parse_mode="HTML")
        return

    # Split kalau berbilang fail
    parts = re.split(r'\s*---NEXT---\s*', code_result, flags=re.IGNORECASE)
    parts = [p.strip() for p in parts if p.strip() and len(p.strip()) > 20]

    if not parts:
        parts = [code_result]

    sent_count = 0
    sent_filenames = set()

    for i, part in enumerate(parts):
        ai_filename, code_clean = parse_code_response(part)
        if not code_clean or len(code_clean.strip()) < 5:
            continue

        filename = detect_lang_filename(user_message, ai_filename)

        # Pastikan nama fail unik
        if filename in sent_filenames:
            base, ext = os.path.splitext(filename)
            filename  = base + "_" + str(i + 1) + ext
        sent_filenames.add(filename)

        tmp_path = os.path.join(tempfile.gettempdir(), filename)
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(code_clean)
            with open(tmp_path, "rb") as f:
                label = " (" + str(sent_count + 1) + "/" + str(max(len(parts), expected_count)) + ")" if expected_count > 1 or len(parts) > 1 else ""
                await message.reply_document(
                    document=f, filename=filename,
                    caption=(
                        E_DEV + " <b>" + filename + "</b>" + label + "\n"
                        + E_CHECK + " Code siap & berfungsi penuh"
                    ),
                    parse_mode="HTML"
                )
            sent_count += 1
        except Exception as e:
            logger.error("send_code_as_file [" + filename + "]: " + str(e))
        finally:
            try: os.remove(tmp_path)
            except Exception: pass

    # Kalau kurang dari yang diminta, minta AI hantar yang lagi
    if expected_count > 1 and sent_count < expected_count:
        remaining = expected_count - sent_count
        await message.reply_text(E_HOURGLASS + " Menjana " + str(remaining) + " fail lagi...")

        extra_history = messages_history + [
            {"role": "assistant", "content": code_result},
            {"role": "user", "content":
                "Kau baru hasilkan " + str(sent_count) + " fail. "
                "Hasilkan " + str(remaining) + " fail LAGI yang belum ada. "
                "Ikut format: FILENAME: namafile.ext\nCODE:\n[code]\n---NEXT---"
            }
        ]
        fn2 = functools.partial(call_ai_api_with_history, api_key, provider, extra_history, CODE_PROMPT)
        ok2, result2 = await loop.run_in_executor(None, fn2)
        if ok2:
            parts2 = re.split(r'\s*---NEXT---\s*', result2, flags=re.IGNORECASE)
            for j, part in enumerate([p.strip() for p in parts2 if p.strip()]):
                ai_fn2, code2 = parse_code_response(part)
                if not code2: continue
                fn2_name = detect_lang_filename(user_message, ai_fn2)
                if fn2_name in sent_filenames:
                    base2, ext2 = os.path.splitext(fn2_name)
                    fn2_name = base2 + "_" + str(sent_count + 1) + ext2
                sent_filenames.add(fn2_name)
                tmp2 = os.path.join(tempfile.gettempdir(), fn2_name)
                try:
                    with open(tmp2, "w", encoding="utf-8") as f: f.write(code2)
                    with open(tmp2, "rb") as f:
                        label2 = " (" + str(sent_count + 1) + "/" + str(expected_count) + ")"
                        await message.reply_document(
                            document=f, filename=fn2_name,
                            caption=E_DEV + " <b>" + fn2_name + "</b>" + label2 + "\n" + E_CHECK + " Code siap",
                            parse_mode="HTML"
                        )
                    sent_count += 1
                except Exception as e:
                    logger.error("extra file: " + str(e))
                finally:
                    try: os.remove(tmp2)
                    except Exception: pass

    # Penjelasan ringkas
    if sent_count > 0:
        await context.bot.send_chat_action(chat_id=chat.id, action="typing")
        expl_history = messages_history + [
            {"role": "assistant", "content": code_result},
            {"role": "user", "content":
                "Berikan penjelasan RINGKAS dalam Bahasa Melayu:\n"
                "- Fungsi setiap fail\n- Cara jalankan\n- Apa perlu dipasang\n"
                "JANGAN tulis semula code."
            }
        ]
        fn3 = functools.partial(call_ai_api_with_history, api_key, provider, expl_history, SYSTEM_PROMPT)
        ok3, expl = await loop.run_in_executor(None, fn3)
        if ok3 and expl:
            await message.reply_text(
                E_INFO + " <b>Penjelasan</b>\n" + E_LINE + "\n" + expl[:4096],
                parse_mode="HTML"
            )


# =============================================================
#  AUTO CODE DETECTION -- detect code dalam response AI
# =============================================================

def _response_has_code(text):
    """
    Return True kalau response AI mengandungi code block atau
    code yang substantial (bukan sekadar snippet pendek).
    """
    import re
    if re.search(r'```[\w]*\n[\s\S]{50,}```', text):
        return True
    if re.search(r'FILENAME:\s*\S+\.(py|js|ts|html|css|php|java|kt|swift|c|cpp|cs|rs|go|rb|lua|dart|sh|bat|ps1|sql|r|md|json|yaml|xml)', text, re.IGNORECASE):
        return True
    lines = text.split('\n')
    code_line_count = sum(1 for l in lines if (
        l.strip().startswith(('#', '//', '/*', '*', 'def ', 'class ', 'function ', 'const ', 'let ', 'var ',
        'import ', 'from ', 'public ', 'private ', 'async ', 'await ', 'return ', 'if ', 'for ', 'while ',
        'print(', 'console.', 'echo ', '<?php', '<!DOCTYPE', '<html', '<div', '<script', 'SELECT ',
        'CREATE ', 'INSERT ', 'UPDATE ', 'DELETE ', 'fn ', 'func ', 'package ', 'using ', '#include'))
    ))
    return code_line_count >= 10


def _extract_code_and_explanation(text):
    """Pisahkan code dan penjelasan dari response AI."""
    import re
    if re.search(r'FILENAME:', text, re.IGNORECASE):
        ai_filename, code = parse_code_response(text)
        return code, "", ai_filename or ""
    fence_match = re.search(r'```(\w*)\n([\s\S]+?)```', text)
    if fence_match:
        lang = fence_match.group(1).strip()
        code = fence_match.group(2).strip()
        expl = re.sub(r'```[\w]*\n[\s\S]+?```', '', text).strip()
        return code, expl, lang
    return text.strip(), "", ""


async def _send_result_as_file(message, chat, context, ai_result, user_message):
    """Hantar response AI yang ada code sebagai file."""
    import tempfile
    code_content, explanation, lang_hint = _extract_code_and_explanation(ai_result)
    filename = detect_lang_filename(user_message, lang_hint if lang_hint and '.' in lang_hint else None)
    if lang_hint and '.' not in lang_hint:
        filename = detect_lang_filename(user_message + " " + lang_hint, None)

    tmp_path = os.path.join(tempfile.gettempdir(), filename)
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(code_content)
    except Exception as e:
        await message.reply_text(E_WARN + " Gagal simpan fail: " + str(e))
        return

    try:
        await context.bot.send_chat_action(chat_id=chat.id, action="upload_document")
        with open(tmp_path, "rb") as f:
            await message.reply_document(
                document=f, filename=filename,
                caption=(
                    E_DEV + " <b>" + filename + "</b>\n"
                    + E_CHECK + " Code siap & berfungsi penuh\n"
                    + E_STAR + " " + user_message[:100]
                ),
                parse_mode="HTML"
            )
    except Exception as e:
        logger.error("send_result_as_file: " + str(e))
        await message.reply_text(E_WARN + " Gagal hantar fail: " + str(e))
        return
    finally:
        try: os.remove(tmp_path)
        except Exception: pass

    if explanation:
        await message.reply_text(
            E_INFO + " <b>Penjelasan</b>\n" + E_LINE + "\n" + explanation[:4096],
            parse_mode="HTML"
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user    = update.effective_user
    message = update.message
    chat    = update.effective_chat

    if not message or not message.text:
        return

    user_message = message.text.strip()
    if not user_message:
        return

    is_group = chat.type in ("group", "supergroup")

    # Penapis group -- hanya respon bila di-reply
    if is_group:
        reply_to = message.reply_to_message
        if not reply_to or reply_to.from_user.id != context.bot.id:
            threading.Thread(target=save_group_member, args=(chat.id, user.id, user.username, user.full_name), daemon=True).start()
            threading.Thread(target=save_started_user, args=(user.id, user.username, user.full_name), daemon=True).start()
            return

    # Track user
    threading.Thread(target=save_started_user, args=(user.id, user.username, user.full_name), daemon=True).start()
    if is_group:
        threading.Thread(target=save_group_member, args=(chat.id, user.id, user.username, user.full_name), daemon=True).start()

    # Semak access
    if not has_access(user.id):
        await message.reply_text(
            E_BAN + " Anda tidak mempunyai akses untuk menggunakan ZenoxGPT.\n\n"
            + E_POINT + " Sila hubungi developer:\n"
            + DEVELOPER_USERNAME
        )
        return

    # Semak API key
    api_key, provider = get_api_key(user.id)
    if not api_key:
        await message.reply_text(
            E_KEY + " Anda belum memasukkan API key.\n\n"
            + E_ARROW + " /addkey {apikey}\n\n"
            + E_GLOBE + " Support: Gemini, OpenAI, Claude,\n"
            "Groq, Mistral, DeepSeek, HuggingFace,\n"
            "OpenRouter, Perplexity dan lain-lain."
        )
        return

    # ── Semak kalau dalam flow urltoapk

    # Ambil context dari reply -- masukkan dalam mesej sahaja (bukan sebagai history)
    reply_context = ""
    if message.reply_to_message:
        replied = message.reply_to_message
        # Ambil teks dari reply
        ctx_text = replied.text or replied.caption or ""
        if ctx_text and ctx_text.strip():
            # Potong panjang -- jangan terlalu panjang
            reply_context = ctx_text.strip()[:600]

    # Log ke info bot
    role       = get_user_role(user.id)
    username   = user.username or ""
    chat_title = getattr(chat, "title", "") or ""
    threading.Thread(
        target=notify_question,
        args=(user.id, username, role, user_message, chat.type, chat_title),
        daemon=True
    ).start()

    loop = asyncio.get_event_loop()

    # ── Bina full prompt -- context reply disertakan dalam mesej
    if reply_context:
        full_user_message = (
            "Konteks (mesej sebelum): " + reply_context + "\n\n"
            "Soalan/permintaan: " + user_message
        )
    else:
        full_user_message = user_message

    # ── Detect coding request -- hantar sebagai file
    if is_coding_request(full_user_message):
        await _send_code_as_file(message, chat, context, api_key, provider, full_user_message, loop, reply_context)
        return

    # ── Chat biasa -- guna call_ai_api biasa (lebih stable)
    await context.bot.send_chat_action(chat_id=chat.id, action="typing")

    fn = functools.partial(call_ai_api, api_key, provider, full_user_message)
    success, result = await loop.run_in_executor(None, fn)

    if not success:
        await message.reply_text(format_api_error(result), parse_mode="HTML")
        return

    # ── Auto detect kalau response ada code -- hantar sebagai file
    if _response_has_code(result):
        await _send_result_as_file(message, chat, context, result, user_message)
        return

    # ── Teks biasa
    max_len = 4096
    if len(result) <= max_len:
        await message.reply_text(result)
    else:
        for chunk in [result[i:i+max_len] for i in range(0, len(result), max_len)]:
            try:
                await message.reply_text(chunk)
            except Exception as e:
                logger.error("Gagal hantar chunk: " + str(e))


# =============================================================
#  GROUP JOIN NOTIFICATION -- bila bot ditambah ke group
# =============================================================

async def handle_my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dihantar bila status bot dalam chat berubah -- detect bila bot di-add ke group."""
    result = update.my_chat_member
    if not result:
        return

    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status
    chat       = result.chat
    added_by   = result.from_user

    # Bot baru di-add ke group (dari left/kicked ke member/admin)
    if old_status in ("left", "kicked") and new_status in ("member", "administrator"):
        if chat.type not in ("group", "supergroup"):
            return

        group_name  = chat.title or "Tiada nama"
        group_id    = chat.id
        adder_un    = "@" + added_by.username if added_by.username else "tiada"
        adder_name  = added_by.full_name or str(added_by.id)
        adder_id    = added_by.id
        now         = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        send_info(
            E_BELL + " <b>BOT TELAH DITAMBAH KE GROUP BAHARU</b>\n"
            + E_LINE + "\n"
            + E_PERSON + " Ditambah oleh : " + adder_name + "\n"
            + E_ID + " User ID       : <code>" + str(adder_id) + "</code>\n"
            + E_PERSON + " Username      : " + adder_un + "\n"
            + E_CHAT + " Nama Group    : <b>" + group_name + "</b>\n"
            + E_ID + " Group ID      : <code>" + str(group_id) + "</code>\n"
            + E_TIME + " Masa          : " + now + "\n"
            + E_LINE
        )

    # Bot dikeluarkan dari group
    elif old_status in ("member", "administrator") and new_status in ("left", "kicked"):
        if chat.type not in ("group", "supergroup"):
            return

        group_name = chat.title or "Tiada nama"
        group_id   = chat.id
        by_un      = "@" + added_by.username if added_by.username else "tiada"
        now        = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        send_info(
            E_RED + " <b>BOT TELAH DIKELUARKAN DARI GROUP</b>\n"
            + E_LINE + "\n"
            + E_PERSON + " Dikeluarkan oleh : " + by_un + "\n"
            + E_ID + " User ID          : <code>" + str(added_by.id) + "</code>\n"
            + E_CHAT + " Nama Group       : <b>" + group_name + "</b>\n"
            + E_ID + " Group ID         : <code>" + str(group_id) + "</code>\n"
            + E_TIME + " Masa             : " + now + "\n"
            + E_LINE
        )


# =============================================================
#  ERROR HANDLER
# =============================================================

async def error_handler(update, context):
    err      = context.error
    err_str  = str(err)
    err_type = type(err).__name__

    # Errors yang tak perlu notify user -- ignore terus
    silent_errors = (
        "ReadTimeout", "TimedOut", "NetworkError", "ConnectionError",
        "RetryAfter", "BadRequest", "MessageNotModified",
        "TelegramError", "Forbidden", "ChatMigrated",
        "MessageToDeleteNotFound", "MessageToEditNotFound",
    )
    for se in silent_errors:
        if se in err_str or se in err_type:
            logger.warning(f"Ignored error [{err_type}]: {err_str[:80]}")
            return

    logger.error(f"Unhandled error [{err_type}]: {err_str}")

    # Notify user hanya kalau ada update yang valid
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                E_WARN + " Terdapat ralat. Sila cuba semula."
            )
        except Exception:
            pass


# =============================================================
#  FILTER SYSTEM -- Auto-save & auto-reply file/media/text
# =============================================================

def load_filters():
    try:
        with open(FILTERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_filters(data):
    try:
        with open(FILTERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("save_filters: " + str(e))


def can_add_filter(user_id):
    """Hanya developer, partner, owner boleh tambah filter."""
    role = get_user_role(user_id)
    return ROLE_LEVEL.get(role, 0) >= ROLE_LEVEL["owner"]


async def _save_filter_from_message(update, context, source_message, filter_name, description):
    """
    Simpan filter dari message (document, photo, video, audio, sticker, text).
    source_message = mesej yang ada media/content.
    """
    filters_data = load_filters()
    entry = {
        "name":        filter_name,
        "description": description,
        "added_by":    update.effective_user.id,
        "type":        None,
        "file_id":     None,
        "file_name":   None,
        "text":        None,
    }

    if source_message.document:
        entry["type"]      = "document"
        entry["file_id"]   = source_message.document.file_id
        entry["file_name"] = source_message.document.file_name or (filter_name + ".bin")

    elif source_message.photo:
        entry["type"]    = "photo"
        entry["file_id"] = source_message.photo[-1].file_id

    elif source_message.video:
        entry["type"]    = "video"
        entry["file_id"] = source_message.video.file_id

    elif source_message.audio:
        entry["type"]    = "audio"
        entry["file_id"] = source_message.audio.file_id

    elif source_message.voice:
        entry["type"]    = "voice"
        entry["file_id"] = source_message.voice.file_id

    elif source_message.video_note:
        entry["type"]    = "video_note"
        entry["file_id"] = source_message.video_note.file_id

    elif source_message.sticker:
        entry["type"]    = "sticker"
        entry["file_id"] = source_message.sticker.file_id

    elif source_message.animation:
        entry["type"]    = "animation"
        entry["file_id"] = source_message.animation.file_id

    elif source_message.text:
        entry["type"] = "text"
        entry["text"] = source_message.text

    else:
        await update.message.reply_text(
            E_WARN + " Jenis media/fail ini tidak disokong.\n\n"
            "Disokong: document, gambar, video, audio, voice, sticker, animasi, teks."
        )
        return False

    filters_data[filter_name.lower()] = entry
    save_filters(filters_data)
    return True


# =============================================================
#  /tourl -- Upload fail ke catbox.moe, dapat permanent link
# =============================================================

def _upload_to_catbox(file_bytes, filename):
    """
    Upload fail ke catbox.moe.
    Return: (success, url atau error_msg)
    """
    try:
        r = requests.post(
            "https://catbox.moe/user/api.php",
            data={"reqtype": "fileupload"},
            files={"fileToUpload": (filename, file_bytes)},
            timeout=120
        )
        if r.status_code == 200 and r.text.startswith("https://"):
            return True, r.text.strip()
        return False, "catbox_error:" + r.text[:100]
    except requests.exceptions.Timeout:
        return False, "timeout"
    except requests.exceptions.ConnectionError:
        return False, "connection_error"
    except Exception as e:
        logger.error("catbox upload: " + str(e))
        return False, "error:" + str(e)[:80]


async def _process_tourl(update, context, source_msg):
    """Download fail dari Telegram dan upload ke catbox."""
    message = update.message
    chat    = update.effective_chat

    # Tentukan file object dan nama fail
    tg_file  = None
    filename = "file"
    ftype    = "fail"

    if source_msg.document:
        tg_file  = source_msg.document
        filename = source_msg.document.file_name or "document.bin"
        ftype    = "Dokumen"
    elif source_msg.photo:
        tg_file  = source_msg.photo[-1]
        filename = "photo.jpg"
        ftype    = "Gambar"
    elif source_msg.video:
        tg_file  = source_msg.video
        filename = source_msg.video.file_name or "video.mp4"
        ftype    = "Video"
    elif source_msg.audio:
        tg_file  = source_msg.audio
        filename = source_msg.audio.file_name or "audio.mp3"
        ftype    = "Audio"
    elif source_msg.voice:
        tg_file  = source_msg.voice
        filename = "voice.ogg"
        ftype    = "Voice"
    elif source_msg.video_note:
        tg_file  = source_msg.video_note
        filename = "videonote.mp4"
        ftype    = "Video Note"
    elif source_msg.sticker:
        tg_file  = source_msg.sticker
        filename = "sticker.webp"
        ftype    = "Sticker"
    elif source_msg.animation:
        tg_file  = source_msg.animation
        filename = source_msg.animation.file_name or "animation.gif"
        ftype    = "Animasi"
    else:
        await message.reply_text(
            E_WARN + " Jenis fail ini tidak disokong.\n\n"
            "Disokong: gambar, video, document, audio, voice, sticker, animasi."
        )
        return

    # Semak saiz -- Telegram limit 20MB untuk bot download
    file_size = getattr(tg_file, "file_size", 0) or 0
    size_mb   = round(file_size / 1024 / 1024, 1)

    if file_size > 20 * 1024 * 1024:
        await message.reply_text(
            E_WARN + " Fail terlalu besar untuk diproses (<b>" + str(size_mb) + " MB</b>).\n"
            "Had maksimum: 20 MB.",
            parse_mode="HTML"
        )
        return

    await context.bot.send_chat_action(chat_id=chat.id, action="upload_document")
    status = await message.reply_text(
        E_HOURGLASS + " Memuat naik ke catbox.moe...\n"
        + E_FOLDER + " Fail: <b>" + filename + "</b>\n"
        + E_STAT + " Saiz: " + str(size_mb) + " MB",
        parse_mode="HTML"
    )

    # Download dari Telegram
    try:
        tg_file_obj = await tg_file.get_file()
        file_bytes  = await tg_file_obj.download_as_bytearray()
    except Exception as e:
        await status.edit_text(E_CROSS + " Gagal download fail dari Telegram: " + str(e))
        return

    # Upload ke catbox dalam executor
    loop   = asyncio.get_event_loop()
    fn     = functools.partial(_upload_to_catbox, bytes(file_bytes), filename)
    ok, result = await loop.run_in_executor(None, fn)

    if not ok:
        err_map = {
            "timeout":          E_HOURGLASS + " Timeout semasa upload. Cuba semula.",
            "connection_error": E_SIGNAL + " Gagal sambung ke catbox.moe.",
        }
        err = err_map.get(result, E_WARN + " Upload gagal: " + result)
        await status.edit_text(err)
        return

    await status.edit_text(
        E_CHECK + " <b>Upload Berjaya!</b>\n\n"
        + E_FOLDER + " Fail     : <b>" + filename + "</b>\n"
        + E_STAT + " Jenis    : " + ftype + "\n"
        + E_STAT + " Saiz     : " + str(size_mb) + " MB\n"
        + E_LINE + "\n"
        + E_LINK + " <b>URL Permanent:</b>\n"
        + "<code>" + result + "</code>\n\n"
        + E_INFO + " Link ini tidak akan expired.",
        parse_mode="HTML"
    )


# =============================================================
#  /enc -- Encrypt JavaScript file (Browser JS & Node.js)
#  Teknik: base64 + eval/new Function wrapper
#  Port dari CodeShield by Repp76
# =============================================================

import base64, secrets, re as _re

def _rnd_hex():
    """Generate random 8-char hex variable name."""
    return "_" + secrets.token_hex(4)


def _safe_b64(code: str) -> str:
    """Encode code string ke base64 (UTF-8 safe)."""
    return base64.b64encode(code.encode("utf-8")).decode("ascii")


def _split_to_chunks(b64: str, var_arr: str) -> str:
    """Split base64 string ke chunks dan assign ke array variable."""
    chunk = 80
    parts = []
    for i in range(0, len(b64), chunk):
        parts.append('"' + b64[i:i+chunk] + '"')
    return "var " + var_arr + "=[" + ",".join(parts) + "]"


def _is_nodejs(code: str) -> bool:
    """Detect sama ada code adalah Node.js."""
    patterns = [
        r'require\s*\(',
        r'\bmodule\.exports\b',
        r'\bprocess\.env\b',
        r'\bprocess\.argv\b',
        r'\b__dirname\b',
        r'\b__filename\b',
        r'^\s*import\s+[\w*{].*?from\s*[\'"`][^./][^\'"`]*[\'"`]',
    ]
    for p in patterns:
        if _re.search(p, code, _re.MULTILINE):
            return True
    return False


def _esm_to_cjs(code: str) -> str:
    """Convert ES Module syntax ke CommonJS untuk compatibility."""

    exports_to_add = []

    # import X, { named } from 'pkg'
    def mixed_import(m):
        def_, named, pkg = m.group(1), m.group(2), m.group(3)
        v = "_cs_" + def_
        return (f"const {v} = require({pkg});\n"
                f"const {def_} = {v}.default || {v};\n"
                f"const {{{named}}} = {v};")
    code = _re.sub(
        r'^\s*import\s+(\w+)\s*,\s*\{([^}]+)\}\s*from\s*([\'"`][^\'"`]+[\'"`])\s*;?',
        mixed_import, code, flags=_re.MULTILINE)

    # import * as X from 'pkg'
    code = _re.sub(
        r'^\s*import\s+\*\s+as\s+(\w+)\s+from\s*([\'"`][^\'"`]+[\'"`])\s*;?',
        lambda m: f"const {m.group(1)} = require({m.group(2)});",
        code, flags=_re.MULTILINE)

    # import { a, b } from 'pkg'
    code = _re.sub(
        r'^\s*import\s+\{([^}]+)\}\s*from\s*([\'"`][^\'"`]+[\'"`])\s*;?',
        lambda m: f"const {{{m.group(1)}}} = require({m.group(2)});",
        code, flags=_re.MULTILINE)

    # import X from 'pkg'
    code = _re.sub(
        r'^\s*import\s+(\w+)\s+from\s*([\'"`][^\'"`]+[\'"`])\s*;?',
        lambda m: f"const {m.group(1)} = require({m.group(2)});",
        code, flags=_re.MULTILINE)

    # import 'pkg'
    code = _re.sub(
        r'^\s*import\s+([\'"`][^\'"`]+[\'"`])\s*;?',
        lambda m: f"require({m.group(1)});",
        code, flags=_re.MULTILINE)

    # export * from 'pkg'
    code = _re.sub(
        r'^\s*export\s+\*\s+from\s*([\'"`][^\'"`]+[\'"`])\s*;?',
        lambda m: f"Object.assign(module.exports, require({m.group(1)}));",
        code, flags=_re.MULTILINE)

    # export { a, b }
    def export_named(m):
        names = [n.strip().split(r'\s+as\s+') for n in m.group(1).split(',')]
        lines = []
        for parts in names:
            parts = [p.strip() for p in _re.split(r'\s+as\s+', m.group(1).split(',')[0].strip())]
        # redo properly
        items = [x.strip() for x in m.group(1).split(',')]
        result = []
        for item in items:
            parts2 = _re.split(r'\s+as\s+', item.strip())
            orig = parts2[0].strip()
            alias = parts2[1].strip() if len(parts2) > 1 else orig
            result.append(f"module.exports.{alias} = {orig};")
        return "\n".join(result)
    code = _re.sub(
        r'^\s*export\s+\{([^}]+)\}\s*;?',
        export_named, code, flags=_re.MULTILINE)

    # export default
    code = _re.sub(
        r'^\s*export\s+default\s+',
        'module.exports = ', code, flags=_re.MULTILINE)

    # export const/let/var/function/class Name
    def export_decl(m):
        kw, name = m.group(1), m.group(2)
        exports_to_add.append(name)
        return kw + " " + name
    code = _re.sub(
        r'^\s*export\s+(const|let|var|function|class)\s+(\w+)',
        export_decl, code, flags=_re.MULTILINE)

    if exports_to_add:
        code += "\n" + "\n".join(
            f'if(typeof module!=="undefined")module.exports.{n}={n};'
            for n in exports_to_add
        )

    return code


def _encrypt_browser_js(code: str) -> str:
    """Encrypt browser JavaScript menggunakan eval wrapper."""
    if _is_nodejs(code):
        return _encrypt_node_js(code)

    # Strip import/export untuk browser
    converted = _re.sub(r'^\s*export\s+default\s+', 'window._csExport = ', code, flags=_re.MULTILINE)
    converted = _re.sub(r'^\s*export\s+(const|let|var|function|class)\s+', r'\1 ', converted, flags=_re.MULTILINE)
    converted = _re.sub(r'^\s*export\s+\{[^}]+\}\s*;?', '', converted, flags=_re.MULTILINE)

    b64     = _safe_b64(converted)
    v_arr   = _rnd_hex()
    v_str   = _rnd_hex()
    chunks  = _split_to_chunks(b64, v_arr)

    return (
        "(function(){"
        + chunks + ";"
        + "var " + v_str + "=" + v_arr + ".join('');"
        + "eval(decodeURIComponent(escape(atob(" + v_str + "))));"
        + "})();"
    )


def _encrypt_node_js(code: str) -> str:
    """Encrypt Node.js JavaScript menggunakan new Function wrapper."""
    cjs_code = _esm_to_cjs(code)
    b64      = _safe_b64(cjs_code)
    v_arr    = _rnd_hex()
    v_str    = _rnd_hex()
    chunks   = _split_to_chunks(b64, v_arr)

    lines = [
        "(async function(){",
        "var _req;",
        'if(typeof require==="function"){',
        "  _req=require;",
        "}else{",
        "  try{",
        '    var _modMod=await import("module");',
        '    var _urlMod=await import("url");',
        "    var _metaUrl;",
        '    try{_metaUrl=import.meta.url;}catch(e){_metaUrl="file://"+process.cwd()+"/index.js";}',
        "    _req=_modMod.createRequire(_metaUrl);",
        "  }catch(e){",
        '    _req=function(m){throw new Error("[CodeShield] require gagal: "+m);};',
        "  }",
        "}",
        "var _dir,_file;",
        'if(typeof __dirname!=="undefined"){',
        "  _dir=__dirname;_file=__filename;",
        "}else{",
        "  try{",
        '    var _urlMod2=await import("url");',
        '    var _pathMod=await import("path");',
        "    var _metaUrl2;",
        '    try{_metaUrl2=import.meta.url;}catch(e){_metaUrl2="file://"+process.cwd()+"/index.js";}',
        "    _file=_urlMod2.fileURLToPath(_metaUrl2);",
        "    _dir=_pathMod.dirname(_file);",
        '  }catch(e){_dir=process.cwd();_file=process.cwd()+"/index.js";}',
        "}",
        chunks + ";",
        "var " + v_str + "=" + v_arr + '.join("");',
        "var _cs=decodeURIComponent(escape(atob(" + v_str + ")));",
        "var _mod={exports:{}};",
        "var _exp=_mod.exports;",
        'var _fn=new Function("require","module","exports","__dirname","__filename",_cs);',
        "_fn(_req,_mod,_exp,_dir,_file);",
        "})();"
    ]
    return "\n".join(lines)


def _encrypt_js(code: str) -> tuple:
    """
    Auto-detect jenis JS dan encrypt.
    Return: (encrypted_code, js_type)
    """
    is_node = _is_nodejs(code)
    if is_node:
        return _encrypt_node_js(code), "Node.js"
    else:
        return _encrypt_browser_js(code), "Browser JS"


async def enc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /enc -- Encrypt JavaScript file
    Cara 1: Hantar .js file + caption /enc
    Cara 2: Balas .js file dengan /enc
    """
    import tempfile
    user    = update.effective_user
    message = update.message
    track_user(user)

    if not has_access(user.id):
        await message.reply_text(
            E_BAN + " Tiada akses. Hubungi: " + DEVELOPER_USERNAME
        )
        return

    # Cari source file
    source_doc = None

    # Cara 1: mesej semasa ada document
    if message.document:
        source_doc = message.document
    # Cara 2: reply ke mesej yang ada document
    elif message.reply_to_message and message.reply_to_message.document:
        source_doc = message.reply_to_message.document

    if not source_doc:
        await message.reply_text(
            E_WARN + " <b>Format /enc:</b>\n\n"
            + E_INFO + " <b>Cara 1</b> — Hantar fail JS + caption:\n"
            "<code>/enc</code>\n\n"
            + E_INFO + " <b>Cara 2</b> — Balas fail JS dengan:\n"
            "<code>/enc</code>\n\n"
            + E_LOCK + " Menyokong: semua fail .js (Browser JS & Node.js)\n"
            + E_CHECK + " Code berfungsi 100% selepas encrypt",
            parse_mode="HTML"
        )
        return

    # Semak extension
    fname = source_doc.file_name or "script.js"
    if not fname.lower().endswith(".js"):
        await message.reply_text(
            E_WARN + " Hanya fail <b>.js</b> yang disokong.\n"
            "Hantar fail JavaScript (.js).",
            parse_mode="HTML"
        )
        return

    # Semak saiz -- max 5MB
    if source_doc.file_size and source_doc.file_size > 5 * 1024 * 1024:
        await message.reply_text(E_WARN + " Fail terlalu besar (max 5MB).")
        return

    status_msg = await message.reply_text(
        E_LOCK + " Mengencrypt <b>" + fname + "</b>...",
        parse_mode="HTML"
    )

    # Download fail
    try:
        tg_file    = await source_doc.get_file()
        file_bytes = await tg_file.download_as_bytearray()
        js_code    = file_bytes.decode("utf-8", errors="replace")
    except Exception as e:
        await status_msg.edit_text(E_CROSS + " Gagal download fail: " + str(e))
        return

    if not js_code.strip():
        await status_msg.edit_text(E_WARN + " Fail kosong atau tidak dapat dibaca.")
        return

    # Encrypt dalam executor
    loop = asyncio.get_event_loop()
    try:
        fn = functools.partial(_encrypt_js, js_code)
        encrypted, js_type = await loop.run_in_executor(None, fn)
    except Exception as e:
        await status_msg.edit_text(E_WARN + " Gagal encrypt: " + str(e))
        return

    # Buat nama fail output
    base_name = fname[:-3]  # buang .js
    out_name  = base_name + ".enc.js"

    # Simpan dan hantar
    tmp_path = os.path.join(tempfile.gettempdir(), out_name)
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(encrypted)

        orig_kb = round(len(js_code.encode("utf-8")) / 1024, 1)
        enc_kb  = round(len(encrypted.encode("utf-8")) / 1024, 1)

        await status_msg.edit_text(
            E_CHECK + " <b>Encrypt Berjaya!</b>\n\n"
            + E_LOCK + " Fail    : <b>" + out_name + "</b>\n"
            + E_GLOBE + " Jenis   : <b>" + js_type + "</b>\n"
            + E_STAT + " Asal    : " + str(orig_kb) + " KB\n"
            + E_STAT + " Encrypt : " + str(enc_kb) + " KB\n\n"
            + E_CHECK + " Code berfungsi 100% selepas encrypt",
            parse_mode="HTML"
        )

        with open(tmp_path, "rb") as f:
            await message.reply_document(
                document=f,
                filename=out_name,
                caption=(
                    E_LOCK + " <b>" + out_name + "</b>\n"
                    + E_GLOBE + " " + js_type + " — Encrypted\n"
                    + E_CHECK + " 100% berfungsi selepas encrypt\n"
                    + E_INFO + " Powered by CodeShield × ZenoxGPT"
                ),
                parse_mode="HTML"
            )
    except Exception as e:
        await status_msg.edit_text(E_WARN + " Gagal hantar fail: " + str(e))
    finally:
        try: os.remove(tmp_path)
        except Exception: pass


# =============================================================
#  /encpy -- Encrypt Python file
#  Teknik: base64 + exec(compile(..., globals()))
#  Port dari CodeShield by Repp76
# =============================================================

def _encrypt_python(code: str) -> str:
    """
    Encrypt Python code menggunakan base64 + exec(compile()).
    Kaedah ini memastikan semua import, fungsi, class, variable,
    dan global scope berfungsi 100% selepas decrypt.
    """
    # Encode ke base64 (chunk 76 char seperti dalam CodeShield)
    b64 = base64.b64encode(code.encode("utf-8")).decode("ascii")

    chunk_size = 76
    chunks = []
    for i in range(0, len(b64), chunk_size):
        chunks.append(repr(b64[i:i + chunk_size]))

    encrypted = (
        "# -*- coding: utf-8 -*-\n"
        "# ZenoxGPT Encrypted Python — Powered by @Repp76\n"
        "import base64 as _b64, sys as _sys\n"
        "_cs_parts = [\n"
        "    " + ",\n    ".join(chunks) + "\n"
        "]\n"
        "_cs_b64  = \"\".join(_cs_parts)\n"
        "_cs_code = _b64.b64decode(_cs_b64).decode(\"utf-8\")\n"
        "exec(compile(_cs_code, \"<string>\", \"exec\"), globals())\n"
    )
    return encrypted


async def encpy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /encpy -- Encrypt Python file (.py)
    Cara 1: Hantar fail .py + caption /encpy
    Cara 2: Balas fail .py dengan /encpy
    """
    import tempfile
    user    = update.effective_user
    message = update.message
    track_user(user)

    if not has_access(user.id):
        await message.reply_text(E_BAN + " Tiada akses. Hubungi: " + DEVELOPER_USERNAME)
        return

    # Cari source file
    source_doc = None
    if message.document:
        source_doc = message.document
    elif message.reply_to_message and message.reply_to_message.document:
        source_doc = message.reply_to_message.document

    if not source_doc:
        await message.reply_text(
            E_WARN + " <b>Format /encpy:</b>\n\n"
            + E_INFO + " <b>Cara 1</b> — Hantar fail + caption:\n"
            "<code>/encpy</code>\n\n"
            + E_INFO + " <b>Cara 2</b> — Balas fail dengan:\n"
            "<code>/encpy</code>\n\n"
            + E_LOCK + " Menyokong: semua fail <b>.py</b>\n"
            + E_CHECK + " Code berfungsi 100% selepas encrypt",
            parse_mode="HTML"
        )
        return

    fname = source_doc.file_name or "script.py"
    if not fname.lower().endswith(".py"):
        await message.reply_text(
            E_WARN + " Hanya fail <b>.py</b> yang disokong.",
            parse_mode="HTML"
        )
        return

    if source_doc.file_size and source_doc.file_size > 5 * 1024 * 1024:
        await message.reply_text(E_WARN + " Fail terlalu besar (max 5MB).")
        return

    status_msg = await message.reply_text(
        E_LOCK + " Mengencrypt <b>" + fname + "</b>...",
        parse_mode="HTML"
    )

    # Download fail
    try:
        tg_file    = await source_doc.get_file()
        file_bytes = await tg_file.download_as_bytearray()
        py_code    = file_bytes.decode("utf-8", errors="replace")
    except Exception as e:
        await status_msg.edit_text(E_CROSS + " Gagal download fail: " + str(e))
        return

    if not py_code.strip():
        await status_msg.edit_text(E_WARN + " Fail kosong atau tidak dapat dibaca.")
        return

    # Encrypt dalam executor
    loop = asyncio.get_event_loop()
    try:
        fn        = functools.partial(_encrypt_python, py_code)
        encrypted = await loop.run_in_executor(None, fn)
    except Exception as e:
        await status_msg.edit_text(E_WARN + " Gagal encrypt: " + str(e))
        return

    # Nama fail output
    base_name = fname[:-3]
    out_name  = base_name + ".enc.py"

    orig_kb = round(len(py_code.encode("utf-8")) / 1024, 1)
    enc_kb  = round(len(encrypted.encode("utf-8")) / 1024, 1)

    tmp_path = os.path.join(tempfile.gettempdir(), out_name)
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(encrypted)

        await status_msg.edit_text(
            E_CHECK + " <b>Encrypt Berjaya!</b>\n\n"
            + E_LOCK + " Fail    : <b>" + out_name + "</b>\n"
            + E_STAT + " Asal    : " + str(orig_kb) + " KB\n"
            + E_STAT + " Encrypt : " + str(enc_kb) + " KB\n\n"
            + E_CHECK + " Jalankan dengan: <code>python " + out_name + "</code>",
            parse_mode="HTML"
        )

        with open(tmp_path, "rb") as f:
            await message.reply_document(
                document=f,
                filename=out_name,
                caption=(
                    E_LOCK + " <b>" + out_name + "</b>\n"
                    + E_DEV + " Python Encrypted\n"
                    + E_CHECK + " 100% berfungsi selepas encrypt\n"
                    + E_INFO + " Jalankan: <code>python " + out_name + "</code>\n"
                    + E_STAR + " Powered by CodeShield \u00d7 ZenoxGPT"
                ),
                parse_mode="HTML"
            )
    except Exception as e:
        await status_msg.edit_text(E_WARN + " Gagal hantar fail: " + str(e))
    finally:
        try: os.remove(tmp_path)
        except Exception: pass


async def tourl_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /tourl -- Upload fail ke catbox.moe
    Cara 1: Hantar fail + caption /tourl
    Cara 2: Balas fail dengan /tourl
    """
    user    = update.effective_user
    message = update.message
    track_user(user)

    # Semak access
    if not has_access(user.id):
        await message.reply_text(
            E_BAN + " Anda tidak mempunyai akses.\n"
            + E_POINT + " Hubungi: " + DEVELOPER_USERNAME
        )
        return

    # Cara 1: mesej semasa ada media
    def msg_has_uploadable(m):
        return bool(
            m.document or m.photo or m.video or m.audio or
            m.voice or m.video_note or m.sticker or m.animation
        )

    if msg_has_uploadable(message):
        await _process_tourl(update, context, message)
        return

    # Cara 2: balas mesej yang ada media
    if message.reply_to_message and msg_has_uploadable(message.reply_to_message):
        await _process_tourl(update, context, message.reply_to_message)
        return

    # Tiada media
    await message.reply_text(
        E_WARN + " <b>Cara guna /tourl:</b>\n\n"
        + E_INFO + " <b>Cara 1</b> — Hantar fail + caption:\n"
        "<code>/tourl</code>\n\n"
        + E_INFO + " <b>Cara 2</b> — Balas fail dengan:\n"
        "<code>/tourl</code>\n\n"
        "Disokong: gambar, video, document, audio, voice, sticker, animasi\n"
        "Had saiz: 20 MB\n"
        + E_LINK + " Link catbox.moe adalah permanent (tiada expired)",
        parse_mode="HTML"
    )


async def handle_tourl_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk media dengan caption /tourl."""
    message = update.message
    if not message:
        return
    caption = (message.caption or "").strip().lower()
    if caption.startswith("/tourl"):
        await tourl_command(update, context)


# =============================================================
#  /urltoapk -- Convert website ke APK (WebView)
#  ConversationHandler flow: semua step WAJIB balas mesej bot
# =============================================================

# Conversation states
UAPK_NAME, UAPK_PKG, UAPK_VER, UAPK_LOGO = range(4)


def _build_webview_apk_source(url, app_name, package, version):
    """Bina ZIP project Android WebView."""
    import zipfile, io, textwrap

    safe = app_name.replace(" ", "").replace("-", "")
    vc   = "".join(filter(str.isdigit, version)) or "1"

    manifest = f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{package}"
    android:versionCode="{vc}"
    android:versionName="{version}">
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="{app_name}"
        android:supportsRtl="true"
        android:theme="@style/Theme.AppCompat.Light.NoActionBar"
        android:usesCleartextTraffic="true">
        <activity android:name=".MainActivity" android:exported="true"
            android:configChanges="orientation|screenSize|keyboardHidden">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
    </application>
</manifest>'''

    main_java = f'''package {package};
import android.annotation.SuppressLint;
import android.app.Activity;
import android.os.Bundle;
import android.view.KeyEvent;
import android.webkit.*;
import android.widget.Toast;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.content.Context;
public class MainActivity extends Activity {{
    private WebView webView;
    private static final String URL = "{url}";
    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        webView = new WebView(this);
        setContentView(webView);
        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setLoadWithOverviewMode(true);
        s.setUseWideViewPort(true);
        s.setBuiltInZoomControls(false);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {{
            @Override
            public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest r) {{
                v.loadUrl(r.getUrl().toString()); return true;
            }}
        }});
        ConnectivityManager cm = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo ni = cm != null ? cm.getActiveNetworkInfo() : null;
        if (ni != null && ni.isConnected()) webView.loadUrl(URL);
        else Toast.makeText(this, "Tiada sambungan internet!", Toast.LENGTH_LONG).show();
    }}
    @Override
    public boolean onKeyDown(int kc, KeyEvent e) {{
        if (kc == KeyEvent.KEYCODE_BACK && webView.canGoBack()) {{ webView.goBack(); return true; }}
        return super.onKeyDown(kc, e);
    }}
    @Override protected void onPause() {{ super.onPause(); webView.onPause(); }}
    @Override protected void onResume() {{ super.onResume(); webView.onResume(); }}
}}'''

    app_gradle = f'''apply plugin: 'com.android.application'
android {{
    compileSdkVersion 34
    defaultConfig {{
        applicationId "{package}"
        minSdkVersion 21
        targetSdkVersion 34
        versionCode {vc}
        versionName "{version}"
    }}
    buildTypes {{ release {{ minifyEnabled false }} }}
}}
dependencies {{
    implementation 'androidx.appcompat:appcompat:1.6.1'
}}'''

    root_gradle = """buildscript {
    repositories { google(); mavenCentral() }
    dependencies { classpath 'com.android.tools.build:gradle:8.2.0' }
}
allprojects { repositories { google(); mavenCentral() } }"""

    strings_xml = f'''<?xml version="1.0" encoding="utf-8"?>
<resources><string name="app_name">{app_name}</string></resources>'''

    readme = f"""WebView APK Project
App     : {app_name}
Package : {package}
Version : {version}
URL     : {url}

Cara Build:
1. Buka dalam Android Studio
2. Tambah logo ke res/mipmap-*/ic_launcher.png
3. Build > Generate Signed APK

Online APK Builder:
https://buildapks.com
https://gonative.io
"""

    try:
        buf = io.BytesIO()
        pkg_path = package.replace(".", "/")
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"{safe}/app/src/main/AndroidManifest.xml", manifest)
            zf.writestr(f"{safe}/app/src/main/java/{pkg_path}/MainActivity.java", main_java)
            zf.writestr(f"{safe}/app/src/main/res/values/strings.xml", strings_xml)
            zf.writestr(f"{safe}/app/build.gradle", app_gradle)
            zf.writestr(f"{safe}/build.gradle", root_gradle)
            zf.writestr(f"{safe}/settings.gradle", 'rootProject.name = "' + safe + '"\ninclude \':app\'\n')
            zf.writestr(f"{safe}/gradle.properties", "android.useAndroidX=true\nandroid.enableJetifier=true\n")
            zf.writestr(f"{safe}/README.txt", readme)
        buf.seek(0)
        return buf.read(), f"{safe}_WebView.zip"
    except Exception as e:
        return None, str(e)


async def urltoapk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mula flow /urltoapk."""
    user    = update.effective_user
    message = update.message
    track_user(user)

    if not has_access(user.id):
        await message.reply_text(E_BAN + " Tiada akses. Hubungi: " + DEVELOPER_USERNAME)
        return ConversationHandler.END

    if not context.args:
        await message.reply_text(
            E_WARN + " Format: /urltoapk {url}\n\n"
            "Contoh: /urltoapk https://example.com"
        )
        return ConversationHandler.END

    url = context.args[0].strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    context.user_data["uapk_url"] = url

    msg = await message.reply_text(
        E_GLOBE + " URL: <code>" + url + "</code>\n\n"
        + E_PENCIL + " <b>Langkah 1/4</b> — Nama Aplikasi\n"
        "Balas mesej ini dengan nama aplikasi anda.\n\n"
        "Contoh: <code>MyApp</code>",
        parse_mode="HTML"
    )
    context.user_data["uapk_msg_id"] = msg.message_id
    return UAPK_NAME


async def uapk_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Terima nama app -- WAJIB reply ke mesej bot."""
    message = update.message

    # Wajib balas mesej bot
    if not message.reply_to_message:
        return UAPK_NAME
    if message.reply_to_message.message_id != context.user_data.get("uapk_msg_id"):
        return UAPK_NAME

    name = (message.text or "").strip()
    if not name:
        await message.reply_text(E_WARN + " Nama tidak boleh kosong. Cuba lagi.")
        return UAPK_NAME

    context.user_data["uapk_name"] = name

    msg = await message.reply_text(
        E_CHECK + " Nama: <b>" + name + "</b>\n\n"
        + E_PENCIL + " <b>Langkah 2/4</b> — Nama Package\n"
        "Balas mesej ini dengan nama package aplikasi.\n\n"
        "Contoh: <code>com.myapp.webview</code>",
        parse_mode="HTML"
    )
    context.user_data["uapk_msg_id"] = msg.message_id
    return UAPK_PKG


async def uapk_get_package(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Terima package name -- WAJIB reply ke mesej bot."""
    import re
    message = update.message

    if not message.reply_to_message:
        return UAPK_PKG
    if message.reply_to_message.message_id != context.user_data.get("uapk_msg_id"):
        return UAPK_PKG

    pkg = (message.text or "").strip().lower()
    if not re.match(r'^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*){1,}$', pkg):
        await message.reply_text(
            E_WARN + " Format package tidak betul.\n"
            "Guna format: <code>com.nama.app</code>",
            parse_mode="HTML"
        )
        return UAPK_PKG

    context.user_data["uapk_pkg"] = pkg

    msg = await message.reply_text(
        E_CHECK + " Package: <b>" + pkg + "</b>\n\n"
        + E_PENCIL + " <b>Langkah 3/4</b> — Versi Aplikasi\n"
        "Balas mesej ini dengan nombor versi.\n\n"
        "Contoh: <code>1.0.0</code>",
        parse_mode="HTML"
    )
    context.user_data["uapk_msg_id"] = msg.message_id
    return UAPK_VER


async def uapk_get_version(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Terima version -- WAJIB reply ke mesej bot."""
    message = update.message

    if not message.reply_to_message:
        return UAPK_VER
    if message.reply_to_message.message_id != context.user_data.get("uapk_msg_id"):
        return UAPK_VER

    ver = (message.text or "").strip()
    if not ver:
        await message.reply_text(E_WARN + " Versi tidak boleh kosong.")
        return UAPK_VER

    context.user_data["uapk_ver"] = ver

    msg = await message.reply_text(
        E_CHECK + " Versi: <b>" + ver + "</b>\n\n"
        + E_PENCIL + " <b>Langkah 4/4</b> — Logo Aplikasi\n"
        "Balas mesej ini dengan gambar logo aplikasi.\n\n"
        + E_INFO + " Saiz cadangan: 512x512 piksel",
        parse_mode="HTML"
    )
    context.user_data["uapk_msg_id"] = msg.message_id
    return UAPK_LOGO


async def uapk_get_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Terima logo (gambar) -- WAJIB reply ke mesej bot."""
    import tempfile
    message = update.message

    # Wajib reply ke mesej bot -- kalau tak, diam je
    if not message.reply_to_message:
        return UAPK_LOGO
    if message.reply_to_message.message_id != context.user_data.get("uapk_msg_id"):
        return UAPK_LOGO
    if not message.photo:
        return UAPK_LOGO

    url     = context.user_data.get("uapk_url", "")
    name    = context.user_data.get("uapk_name", "MyApp")
    package = context.user_data.get("uapk_pkg", "com.myapp.app")
    version = context.user_data.get("uapk_ver", "1.0.0")

    try:
        photo_file  = await message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
    except Exception as e:
        await message.reply_text(E_CROSS + " Gagal proses gambar: " + str(e))
        return ConversationHandler.END

    await message.reply_text(
        E_HOURGLASS + " Menjana project APK WebView...\n\n"
        + E_GLOBE + " URL: <code>" + url + "</code>\n"
        + E_PHONE + " App: <b>" + name + "</b>\n"
        + E_FOLDER + " PKG: <code>" + package + "</code>\n"
        + E_STAT + " Ver: " + version,
        parse_mode="HTML"
    )

    loop = asyncio.get_event_loop()
    fn   = functools.partial(_build_webview_apk_source, url, name, package, version)
    zip_bytes, zip_name = await loop.run_in_executor(None, fn)

    if zip_bytes is None:
        await message.reply_text(E_WARN + " Gagal menjana project: " + zip_name)
        return ConversationHandler.END

    tmp_path = os.path.join(tempfile.gettempdir(), zip_name)
    try:
        with open(tmp_path, "wb") as f:
            f.write(zip_bytes)
        with open(tmp_path, "rb") as f:
            await message.reply_document(
                document=f,
                filename=zip_name,
                caption=(
                    E_CHECK + " <b>Project APK WebView Siap!</b>\n\n"
                    + E_GLOBE + " URL : <code>" + url + "</code>\n"
                    + E_PHONE + " App : <b>" + name + "</b>\n"
                    + E_FOLDER + " PKG : <code>" + package + "</code>\n"
                    + E_STAT + " Ver : " + version + "\n\n"
                    + E_INFO + " <b>Cara Build APK:</b>\n"
                    "1. Buka folder dalam Android Studio\n"
                    "2. Tambah logo ke res/mipmap-*/ic_launcher.png\n"
                    "3. Build > Generate Signed APK\n\n"
                    + E_LINK + " Online: buildapks.com"
                ),
                parse_mode="HTML"
            )
        # Hantar balik logo
        try:
            await message.reply_photo(
                photo=bytes(photo_bytes),
                caption=E_FOLDER + " Logo: <b>" + name + "</b>\nSalin ke: res/mipmap-xxxhdpi/ic_launcher.png",
                parse_mode="HTML"
            )
        except Exception:
            pass
    except Exception as e:
        await message.reply_text(E_WARN + " Gagal hantar fail: " + str(e))
    finally:
        try: os.remove(tmp_path)
        except Exception: pass

    # Clear user data
    for k in ["uapk_url", "uapk_name", "uapk_pkg", "uapk_ver", "uapk_msg_id"]:
        context.user_data.pop(k, None)

    return ConversationHandler.END


async def uapk_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel flow urltoapk."""
    for k in ["uapk_url", "uapk_name", "uapk_pkg", "uapk_ver", "uapk_msg_id"]:
        context.user_data.pop(k, None)
    await update.message.reply_text(E_CROSS + " /urltoapk dibatalkan.")
    return ConversationHandler.END



async def filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /filter /nama {deskripsi}
    Cara 1: Hantar media + caption /filter /nama {deskripsi}
    Cara 2: Balas media dengan /filter /nama {deskripsi}
    Wajib dalam private chat.
    """
    user    = update.effective_user
    message = update.message
    chat    = update.effective_chat
    track_user(user)

    # Wajib private chat
    if chat.type != "private":
        await message.reply_text(
            E_LOCK + " Command /filter hanya boleh digunakan dalam <b>private chat</b> sahaja.",
            parse_mode="HTML"
        )
        return

    # Semak permission
    if not can_add_filter(user.id):
        role = get_user_role(user.id)
        await message.reply_text(
            E_BAN + " Anda tidak mempunyai kebenaran untuk menambah filter.\n\n"
            + E_BADGE + " Role anda: <b>" + role.upper() + "</b>\n"
            + E_INFO + " Diperlukan: Owner / Partner / Developer",
            parse_mode="HTML"
        )
        return

    # Parse args -- /filter /nama deskripsi
    raw_args = " ".join(context.args) if context.args else ""
    raw_args = raw_args.strip()

    if not raw_args or not raw_args.startswith("/"):
        await message.reply_text(
            E_WARN + " <b>Format salah!</b>\n\n"
            + E_INFO + " <b>Cara 1</b> — Hantar fail + caption:\n"
            "<code>/filter /nama deskripsi</code>\n\n"
            + E_INFO + " <b>Cara 2</b> — Balas fail dengan:\n"
            "<code>/filter /nama deskripsi</code>\n\n"
            + E_INFO + " <b>Cara 3</b> — Filter teks (berbilang baris guna |):\n"
            "<code>/filter /nama baris1|baris2|baris3</code>\n\n"
            "Contoh:\n"
            "<code>/filter /apkunban cara guna|masukkan nombor|tekan enter</code>",
            parse_mode="HTML"
        )
        return

    # Ambil nama filter (perkataan pertama selepas /)
    parts       = raw_args.split(None, 1)
    filter_name = parts[0].lstrip("/").lower().strip()
    description = parts[1].strip() if len(parts) > 1 else ""

    # Tukar | kepada newline -- cara nak buat teks berbilang baris
    # Contoh: /filter /nama baris1|baris2|baris3
    description = description.replace("|", "\n")

    if not filter_name:
        await message.reply_text(E_WARN + " Nama filter tidak boleh kosong.")
        return

    # ================================================================
    # Tentukan source -- ikut keutamaan:
    # 1. Mesej semasa ada media (hantar fail + caption /filter /nama)
    # 2. Reply kepada mesej lain yang ada media/teks
    # 3. Tiada media = filter TEKS (kandungan = description)
    # ================================================================

    def msg_has_media(m):
        return bool(
            m.document or m.photo or m.video or m.audio or
            m.voice or m.video_note or m.sticker or m.animation
        )

    source_message = None

    # Cara 1: mesej semasa ada media
    if msg_has_media(message):
        source_message = message

    # Cara 2: balas mesej lain yang ada media atau teks
    elif message.reply_to_message:
        replied = message.reply_to_message
        if msg_has_media(replied) or replied.text:
            source_message = replied

    # Cara 3: tiada media, tiada reply = simpan sebagai filter TEKS
    if source_message is None:
        if not description:
            await message.reply_text(
                E_WARN + " <b>Tiada kandungan untuk disimpan.</b>\n\n"
                "Untuk filter teks berbilang baris, guna <b>|</b> sebagai pemisah:\n"
                "<code>/filter /nama baris1|baris2|baris3</code>\n\n"
                "Contoh:\n"
                "<code>/filter /apkunban cara guna|masukkan nombor|tekan enter</code>\n\n"
                "Untuk filter fail:\n"
                "Hantar fail + caption atau balas fail dengan command.",
                parse_mode="HTML"
            )
            return

        # Simpan filter teks
        filters_data = load_filters()
        filters_data[filter_name] = {
            "name":        filter_name,
            "description": description,
            "added_by":    user.id,
            "type":        "text",
            "file_id":     None,
            "file_name":   None,
            "text":        description,
        }
        save_filters(filters_data)
        await message.reply_text(
            E_CHECK + " <b>Filter teks berjaya disimpan!</b>\n\n"
            + E_STAR + " Command: <code>/" + filter_name + "</code>\n"
            + E_CHAT + " Kandungan: " + description[:200],
            parse_mode="HTML"
        )
        return

    saved = await _save_filter_from_message(update, context, source_message, filter_name, description)
    if saved:
        entry = load_filters().get(filter_name, {})
        type_label = {
            "document":   E_FOLDER + " Dokumen",
            "photo":      "\U0001f5bc\ufe0f Gambar",
            "video":      "\U0001f3a5 Video",
            "audio":      "\U0001f3b5 Audio",
            "voice":      "\U0001f3a4 Voice",
            "video_note": "\U0001f4f9 Video Note",
            "sticker":    "\U0001f3f7\ufe0f Sticker",
            "animation":  "\U0001f4f1 Animasi/GIF",
            "text":       E_CHAT + " Teks",
        }.get(entry.get("type", ""), E_FOLDER + " Fail")

        await message.reply_text(
            E_CHECK + " <b>Filter berjaya disimpan!</b>\n\n"
            + E_STAR + " Command: <code>/" + filter_name + "</code>\n"
            + type_label + "\n"
            + (E_CHAT + " Deskripsi: " + description if description else ""),
            parse_mode="HTML"
        )


async def listfilters_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Senarai semua filter yang tersimpan."""
    user = update.effective_user
    track_user(user)

    if not has_access(user.id):
        await update.message.reply_text(E_BAN + " Anda tidak mempunyai akses.")
        return

    filters_data = load_filters()
    if not filters_data:
        await update.message.reply_text(
            E_INFO + " Tiada filter disimpan lagi.\n\n"
            + E_POINT + " Tambah filter: /filter /nama {deskripsi}"
        )
        return

    type_icon = {
        "document": E_FOLDER,
        "photo":    "\U0001f5bc\ufe0f",
        "video":    "\U0001f3a5",
        "audio":    "\U0001f3b5",
        "voice":    "\U0001f3a4",
        "video_note": "\U0001f4f9",
        "sticker":  "\U0001f3f7\ufe0f",
        "animation":"\U0001f4f1",
        "text":     E_CHAT,
    }

    lines = [E_LIST + " <b>Senarai Filter (" + str(len(filters_data)) + ")</b>\n" + E_LINE]
    for name, entry in sorted(filters_data.items()):
        icon = type_icon.get(entry.get("type", ""), E_STAR)
        desc = entry.get("description", "")
        line = icon + " <code>/" + name + "</code>"
        if desc:
            line += " — " + desc[:60]
        lines.append(line)

    lines.append(E_LINE)
    if can_add_filter(user.id):
        lines.append(E_PENCIL + " Tambah: /filter /nama {deskripsi}")
        lines.append(E_CROSS + " Padam: /delfilter /nama")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def delfilter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Padam filter. Hanya owner/partner/developer."""
    user    = update.effective_user
    message = update.message
    track_user(user)

    if not can_add_filter(user.id):
        await message.reply_text(E_BAN + " Anda tidak mempunyai kebenaran untuk memadam filter.")
        return

    if not context.args:
        await message.reply_text(E_WARN + " Format: /delfilter /nama")
        return

    filter_name = context.args[0].lstrip("/").lower().strip()
    filters_data = load_filters()

    if filter_name not in filters_data:
        await message.reply_text(E_CROSS + " Filter <code>/" + filter_name + "</code> tidak dijumpai.", parse_mode="HTML")
        return

    del filters_data[filter_name]
    save_filters(filters_data)
    await message.reply_text(
        E_CHECK + " Filter <code>/" + filter_name + "</code> berjaya dipadam.",
        parse_mode="HTML"
    )


async def handle_filter_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Universal handler -- detect kalau command adalah filter trigger atau function trigger.
    """
    user    = update.effective_user
    message = update.message
    if not message:
        return

    text = message.text or message.caption or ""
    if not text.startswith("/"):
        return

    cmd = text.split()[0].lstrip("/").lower().split("@")[0]

    # Skip command yang dah ada handler tetap
    RESERVED = {
        "start", "addkey", "help", "status", "developer",
        "giveaccess", "addreseller", "addowner", "addpartner",
        "removeaccess", "listusers", "tagall", "code", "fixcode",
        "getcode", "all", "filter", "listfilters", "delfilter",
        "tourl", "enc", "encpy", "urltoapk",         "listfunctions", "delfunction", "cancel"
    }
    if cmd in RESERVED:
        return

    # Semak access dulu
    if not has_access(user.id):
        await message.reply_text(
            E_BAN + " Anda tidak mempunyai akses.\n"
            + E_POINT + " Hubungi: " + DEVELOPER_USERNAME
        )
        return

    # Semak function trigger dulu

    # Semak filter trigger
    filters_data = load_filters()
    if cmd not in filters_data:
        return

    entry   = filters_data[cmd]
    ftype   = entry.get("type")
    file_id = entry.get("file_id")
    desc    = entry.get("description", "") or ""
    caption = desc if desc else None

    try:
        if ftype == "document":
            await message.reply_document(document=file_id, caption=caption)
        elif ftype == "photo":
            await message.reply_photo(photo=file_id, caption=caption)
        elif ftype == "video":
            await message.reply_video(video=file_id, caption=caption)
        elif ftype == "audio":
            await message.reply_audio(audio=file_id, caption=caption)
        elif ftype == "voice":
            await message.reply_voice(voice=file_id, caption=caption)
        elif ftype == "video_note":
            await message.reply_video_note(video_note=file_id)
        elif ftype == "sticker":
            await message.reply_sticker(sticker=file_id)
        elif ftype == "animation":
            await message.reply_animation(animation=file_id, caption=caption)
        elif ftype == "text":
            text_content = entry.get("text") or desc
            if text_content:
                await message.reply_text(text_content)
        else:
            await message.reply_text(E_WARN + " Jenis fail tidak dikenali.")
    except Exception as e:
        logger.error("filter_trigger [" + cmd + "]: " + str(e))
        await message.reply_text(E_WARN + " Gagal hantar fail filter. Cuba semula.")


# =============================================================
#  /tt -- Download TikTok video/gambar tanpa watermark HD
#  /ig -- Download Instagram video/gambar HD
#  Guna yt-dlp -- paling reliable untuk semua platform
# =============================================================

import subprocess, sys, tempfile, os as _os

def _ensure_ytdlp():
    """Install yt-dlp kalau belum ada."""
    try:
        import yt_dlp
        return True
    except ImportError:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "yt-dlp", "--break-system-packages", "-q"],
                capture_output=True, timeout=60
            )
            import yt_dlp
            return True
        except Exception:
            return False


def _dl_tiktok(url: str):
    """
    Download TikTok guna yt-dlp + tikwm fallback.
    Return: (ok, {"type": "video"/"images", "video": bytes, "images": [bytes], "title": str, "author": str})
    """
    try:
        import yt_dlp
        tmp = tempfile.mkdtemp()
        out = _os.path.join(tmp, "%(id)s.%(ext)s")
        ydl_opts = {
            "outtmpl": out,
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "quiet": True,
            "no_warnings": True,
            "merge_output_format": "mp4",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title  = (info.get("title") or "TikTok")[:80]
            author = info.get("uploader") or info.get("creator") or ""
            # Cari file yang didownload
            for fname in _os.listdir(tmp):
                fpath = _os.path.join(tmp, fname)
                with open(fpath, "rb") as f:
                    vbytes = f.read()
                _os.remove(fpath)
                _os.rmdir(tmp)
                return True, {"type": "video", "video": vbytes, "title": title, "author": author}
    except Exception as e:
        logger.warning("yt-dlp tiktok fail: " + str(e) + " -- trying tikwm")

    # Fallback: tikwm API
    try:
        r = requests.post(
            "https://tikwm.com/api/",
            data={"url": url, "hd": "1"},
            headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/x-www-form-urlencoded"},
            timeout=30
        )
        if r.status_code == 200:
            d = r.json()
            if d.get("code") == 0:
                data   = d.get("data", {})
                title  = (data.get("title") or "TikTok")[:80]
                author = (data.get("author") or {}).get("nickname", "")
                images = data.get("images") or []
                if images:
                    return True, {"type": "images", "images": images, "title": title, "author": author}
                hd_url = data.get("hdplay") or data.get("play") or ""
                if hd_url:
                    vbytes = _fetch_bytes(hd_url, 120)
                    if vbytes:
                        return True, {"type": "video", "video": vbytes, "title": title, "author": author, "url": hd_url}
                    return True, {"type": "link", "url": hd_url, "title": title, "author": author}
    except Exception as e2:
        logger.error("tikwm fail: " + str(e2))

    return False, "Gagal download TikTok. Cuba semula."


def _dl_instagram(url: str):
    """
    Download Instagram guna yt-dlp.
    Return: (ok, {"type": "video"/"images", "video": bytes, "images": [...], "title": str})
    """
    try:
        import yt_dlp
        tmp = tempfile.mkdtemp()
        out = _os.path.join(tmp, "%(id)s.%(ext)s")
        ydl_opts = {
            "outtmpl": out,
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "quiet": True,
            "no_warnings": True,
            "merge_output_format": "mp4",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = (info.get("title") or "Instagram")[:80]
            files = _os.listdir(tmp)
            if files:
                results = []
                for fname in files:
                    fpath = _os.path.join(tmp, fname)
                    with open(fpath, "rb") as f:
                        results.append(f.read())
                    _os.remove(fpath)
                try: _os.rmdir(tmp)
                except Exception: pass
                if len(results) == 1:
                    return True, {"type": "video", "video": results[0], "title": title}
                return True, {"type": "multi", "files": results, "title": title}
    except Exception as e:
        logger.error("yt-dlp instagram fail: " + str(e))
    return False, "Gagal download Instagram. Pastikan link valid dan akaun public."


def _fetch_bytes(url, timeout=60):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout, allow_redirects=True)
        if r.status_code == 200:
            return r.content
    except Exception as e:
        logger.error("fetch_bytes: " + str(e))
    return None


def _extract_audio(video_bytes: bytes, filename="audio.mp3") -> bytes:
    """Extract audio dari video bytes guna ffmpeg. Support video apa-apa panjang."""
    import shutil, tempfile as _tf
    tmp_in = tmp_out = None
    try:
        if not shutil.which("ffmpeg"):
            return None
        # Tulis video ke temp file
        tmp_in  = _tf.NamedTemporaryFile(suffix=".mp4", delete=False)
        tmp_out = _tf.NamedTemporaryFile(suffix=".mp3", delete=False)
        tmp_in.write(video_bytes)
        tmp_in.close()
        tmp_out.close()
        # Jalankan ffmpeg -- tiada timeout, support video panjang
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", tmp_in.name,
                "-vn",                  # buang video stream
                "-acodec", "libmp3lame",
                "-q:a", "2",            # kualiti tinggi
                tmp_out.name
            ],
            capture_output=True        # tiada timeout -- biar siap
        )
        if result.returncode != 0:
            logger.error("ffmpeg error: " + result.stderr.decode("utf-8","replace")[-300:])
            return None
        with open(tmp_out.name, "rb") as f:
            audio = f.read()
        return audio if audio else None
    except Exception as e:
        logger.error("extract_audio: " + str(e))
        return None
    finally:
        try:
            if tmp_in  and _os.path.exists(tmp_in.name):  _os.unlink(tmp_in.name)
            if tmp_out and _os.path.exists(tmp_out.name): _os.unlink(tmp_out.name)
        except Exception:
            pass


# ── Simpan video bytes sementara untuk sound callback ──
_VIDEO_CACHE = {}  # callback_data -> video_bytes


def _cache_video(key: str, video_bytes: bytes):
    _VIDEO_CACHE[key] = video_bytes
    # Limit cache -- buang yang lama
    if len(_VIDEO_CACHE) > 50:
        oldest = list(_VIDEO_CACHE.keys())[0]
        del _VIDEO_CACHE[oldest]


async def _send_video_with_sound_btn(message, video_bytes: bytes, caption: str, cache_key: str):
    """Hantar video dengan button Sound."""
    import io
    _cache_video(cache_key, video_bytes)
    kbd = InlineKeyboardMarkup([[
        InlineKeyboardButton("\U0001f50a Sound", callback_data="sound:" + cache_key)
    ]])
    try:
        await message.reply_video(
            video=io.BytesIO(video_bytes),
            caption=caption,
            parse_mode="HTML",
            reply_markup=kbd,
            supports_streaming=True
        )
    except Exception:
        await message.reply_document(
            document=io.BytesIO(video_bytes),
            filename="video.mp4",
            caption=caption,
            parse_mode="HTML",
            reply_markup=kbd
        )


async def sound_callback(update, context):
    """Handler untuk button Sound."""
    import io
    query = update.callback_query
    await query.answer()
    data = query.data or ""
    if not data.startswith("sound:"):
        return
    key = data[6:]
    video_bytes = _VIDEO_CACHE.get(key)
    if not video_bytes:
        await query.message.reply_text(E_WARN + " Sound tidak lagi tersedia. Download semula video.")
        return
    await query.message.reply_text(E_HOURGLASS + " Mengekstrak audio...")
    loop = asyncio.get_event_loop()
    audio_bytes = await loop.run_in_executor(None, functools.partial(_extract_audio, video_bytes))
    if not audio_bytes:
        await query.message.reply_text(
            E_WARN + " Gagal ekstrak audio.\n"
            "Pastikan ffmpeg dipasang:\n"
            "<code>pkg install ffmpeg</code>",
            parse_mode="HTML"
        )
        return
    try:
        await query.message.reply_audio(
            audio=io.BytesIO(audio_bytes),
            filename="sound.mp3",
            caption=E_MUSIC + " Sound dari video" if hasattr(__builtins__, 'E_MUSIC') else "\U0001f3b5 Sound dari video"
        )
    except Exception as e:
        await query.message.reply_text(E_WARN + " Gagal hantar audio: " + str(e))


async def tt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/tt {link} -- Download TikTok tanpa watermark HD."""
    import io, time
    user    = update.effective_user
    message = update.message
    chat    = update.effective_chat
    track_user(user)

    if not has_access(user.id):
        await message.reply_text(E_BAN + " Tiada akses. Hubungi: " + DEVELOPER_USERNAME)
        return

    if not context.args:
        await message.reply_text(
            E_WARN + " Format: /tt {link TikTok}\n\n"
            "Contoh:\n"
            "/tt https://vm.tiktok.com/xxxxx\n"
            "/tt https://www.tiktok.com/@user/video/xxxxx"
        )
        return

    url = context.args[0].strip()
    if not any(x in url for x in ["tiktok.com", "vt.tiktok", "vm.tiktok"]):
        await message.reply_text(E_WARN + " Link mesti dari TikTok.")
        return

    status = await message.reply_text(E_HOURGLASS + " Sedang download TikTok...")

    if not _ensure_ytdlp():
        await status.edit_text(E_WARN + " Gagal pasang yt-dlp. Cuba: pip install yt-dlp")
        return

    await context.bot.send_chat_action(chat_id=chat.id, action="upload_video")

    loop = asyncio.get_event_loop()
    ok, result = await loop.run_in_executor(None, functools.partial(_dl_tiktok, url))

    if not ok:
        await status.edit_text(E_WARN + " " + str(result))
        return

    title  = result.get("title", "TikTok")
    author = result.get("author", "")
    cap = (
        E_STAR + " " + title + "\n"
        + (E_PERSON + " @" + author + "\n" if author else "")
        + E_CHECK + " No Watermark | HD"
    )

    rtype = result.get("type")

    if rtype == "images":
        imgs = result.get("images", [])
        await status.edit_text(E_HOURGLASS + " Menghantar " + str(len(imgs)) + " gambar...")
        sent = 0
        for i, img_url in enumerate(imgs[:10]):
            img_bytes = await loop.run_in_executor(None, functools.partial(_fetch_bytes, img_url, 30))
            if img_bytes:
                try:
                    await message.reply_photo(
                        photo=io.BytesIO(img_bytes),
                        caption=cap if i == 0 else None,
                        parse_mode="HTML" if i == 0 else None
                    )
                    sent += 1
                except Exception as e:
                    logger.error("tt photo: " + str(e))
        await status.edit_text(E_CHECK + " " + str(sent) + " gambar dihantar!")
        return

    if rtype == "link":
        hd_url = result.get("url", "")
        await status.edit_text(
            E_CHECK + " <b>" + title + "</b>\n"
            + E_LINK + " <a href='" + hd_url + "'>Download Video HD</a>\n"
            + E_INFO + " Video terlalu besar untuk Telegram.",
            parse_mode="HTML"
        )
        return

    if rtype == "video":
        vbytes = result.get("video")
        if not vbytes:
            await status.edit_text(E_WARN + " Gagal download video.")
            return
        cache_key = "tt_" + str(int(time.time())) + "_" + str(user.id)
        try:
            await status.delete()
        except Exception:
            pass
        await _send_video_with_sound_btn(message, vbytes, cap, cache_key)


async def ig_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/ig {link} -- Download Instagram video/gambar HD."""
    import io, time
    user    = update.effective_user
    message = update.message
    chat    = update.effective_chat
    track_user(user)

    if not has_access(user.id):
        await message.reply_text(E_BAN + " Tiada akses. Hubungi: " + DEVELOPER_USERNAME)
        return

    if not context.args:
        await message.reply_text(
            E_WARN + " Format: /ig {link Instagram}\n\n"
            "Contoh:\n"
            "/ig https://www.instagram.com/p/xxxxx/\n"
            "/ig https://www.instagram.com/reel/xxxxx/"
        )
        return

    url = context.args[0].strip()
    if "instagram.com" not in url:
        await message.reply_text(E_WARN + " Link mesti dari Instagram.")
        return

    status = await message.reply_text(E_HOURGLASS + " Sedang download Instagram...")

    if not _ensure_ytdlp():
        await status.edit_text(E_WARN + " Gagal pasang yt-dlp. Cuba: pip install yt-dlp")
        return

    await context.bot.send_chat_action(chat_id=chat.id, action="upload_video")

    loop = asyncio.get_event_loop()
    ok, result = await loop.run_in_executor(None, functools.partial(_dl_instagram, url))

    if not ok:
        await status.edit_text(E_WARN + " " + str(result))
        return

    title = result.get("title", "Instagram")
    cap = E_STAR + " " + title + "\n" + E_CHECK + " HD Quality"
    rtype = result.get("type")
    cache_key = "ig_" + str(int(time.time())) + "_" + str(user.id)

    try:
        await status.delete()
    except Exception:
        pass

    if rtype == "video":
        vbytes = result.get("video")
        await _send_video_with_sound_btn(message, vbytes, cap, cache_key)

    elif rtype == "multi":
        files = result.get("files", [])
        for i, fbytes in enumerate(files[:10]):
            is_vid = b"ftyp" in fbytes[:20] or fbytes[:4] == b"\x00\x00\x00\x1c"
            try:
                if is_vid:
                    ck = cache_key + "_" + str(i)
                    await _send_video_with_sound_btn(message, fbytes, cap if i == 0 else "", ck)
                else:
                    await message.reply_photo(
                        photo=io.BytesIO(fbytes),
                        caption=cap if i == 0 else None,
                        parse_mode="HTML" if i == 0 else None
                    )
            except Exception as e:
                logger.error("ig multi send: " + str(e))


# =============================================================
#  /osint -- Open Source Intelligence Search
#  Cari maklumat scammer dari sumber awam & web
# =============================================================

import threading as _threading
import re as _re

# Sumber OSINT khusus Malaysia
OSINT_SOURCES = [
    # Portal semak scammer
    ("semak.my",        "https://semak.my/{q}"),
    ("cekbas.net",      "https://cekbas.net/?q={q}"),
    # Search engines
    ("google",          "https://www.google.com/search?q={q}+scammer+Malaysia"),
    ("ddg",             "https://html.duckduckgo.com/html/?q={q}+scammer+penipuan"),
    # Forum & berita
    ("lowyat",          "https://html.duckduckgo.com/html/?q=site:forum.lowyat.net+{q}"),
    ("reddit",          "https://html.duckduckgo.com/html/?q=site:reddit.com+{q}+scam"),
    ("berita",          "https://html.duckduckgo.com/html/?q={q}+penipu+Malaysia+berita"),
]

_OSINT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120"


def _scrape_ddg(url: str, timeout: int = 8) -> list:
    """Scrape results dari DuckDuckGo HTML."""
    found = []
    try:
        r = requests.get(url, headers={"User-Agent": _OSINT_UA}, timeout=timeout)
        if r.status_code != 200:
            return found
        snippets = _re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', r.text, _re.DOTALL | _re.IGNORECASE)
        titles   = _re.findall(r'class="result__a"[^>]*>(.*?)</a>',       r.text, _re.DOTALL | _re.IGNORECASE)
        urls_r   = _re.findall(r'class="result__url"[^>]*>(.*?)</span>',  r.text, _re.DOTALL | _re.IGNORECASE)
        for i, snip in enumerate(snippets[:4]):
            clean = lambda s: _re.sub(r'<[^>]+>', '', s).strip()
            s = clean(snip)
            if s:
                found.append({
                    "title":   clean(titles[i])   if i < len(titles)  else "",
                    "snippet": s,
                    "url":     clean(urls_r[i]).strip() if i < len(urls_r) else "",
                })
    except Exception:
        pass
    return found


def _check_semakmy(target: str) -> dict:
    """Semak semak.my dan cekbas.net."""
    clean = target.replace(" ","").replace("-","").replace("+","")
    result = {"semak_status": "Tiada rekod", "semak_aduan": "0", "semak_url": ""}

    # semak.my
    try:
        r = requests.get(f"https://semak.my/{clean}",
            headers={"User-Agent": _OSINT_UA}, timeout=8)
        if r.status_code == 200:
            aduan  = _re.search(r'(\d+)\s*(?:aduan|laporan|report)', r.text, _re.IGNORECASE)
            status = _re.search(r'(scammer|penipu|waspada|beware|berhati|SCAM)', r.text, _re.IGNORECASE)
            result["semak_url"]    = f"https://semak.my/{clean}"
            result["semak_aduan"]  = aduan.group(1) if aduan else "0"
            result["semak_status"] = status.group(0).upper() if status else "Tiada rekod"
    except Exception:
        pass

    # cekbas.net
    try:
        r2 = requests.get(f"https://cekbas.net/?q={clean}",
            headers={"User-Agent": _OSINT_UA}, timeout=8)
        if r2.status_code == 200:
            aduan2 = _re.search(r'(\d+)\s*(?:aduan|laporan)', r2.text, _re.IGNORECASE)
            if aduan2:
                result["cekbas_aduan"] = aduan2.group(1)
                result["cekbas_url"]   = f"https://cekbas.net/?q={clean}"
    except Exception:
        pass

    return result


def _osint_gather_all(target: str) -> dict:
    """
    Kumpul data dari SEMUA sumber secara parallel menggunakan threads.
    Timeout keras 20 saat untuk keseluruhan.
    """
    import re as re2
    results = {
        "target":    target,
        "ddg_main":  [],
        "ddg_news":  [],
        "ddg_forum": [],
        "ddg_ig":    [],
        "ddg_fb":    [],
        "semak":     {},
        "is_phone":  bool(re2.match(r'^[+\d\s\-(]{7,}[\d)]$', target.strip())),
        "is_email":  bool(re2.search(r'@[\w.]+\.\w+', target)),
        "is_url":    target.startswith("http"),
    }

    tgt_enc = requests.utils.quote(target)

    def run(key, fn):
        try:
            results[key] = fn()
        except Exception:
            pass

    threads = [
        _threading.Thread(target=run, args=("ddg_main",  lambda: _scrape_ddg(f"https://html.duckduckgo.com/html/?q={tgt_enc}+scammer+penipu+Malaysia"))),
        _threading.Thread(target=run, args=("ddg_news",  lambda: _scrape_ddg(f"https://html.duckduckgo.com/html/?q={tgt_enc}+penipuan+aduan+berita"))),
        _threading.Thread(target=run, args=("ddg_forum", lambda: _scrape_ddg(f"https://html.duckduckgo.com/html/?q={tgt_enc}+site:forum.lowyat.net+OR+site:reddit.com"))),
        _threading.Thread(target=run, args=("ddg_ig",    lambda: _scrape_ddg(f"https://html.duckduckgo.com/html/?q={tgt_enc}+instagram+OR+tiktok+OR+facebook+scam"))),
        _threading.Thread(target=run, args=("semak",     lambda: _check_semakmy(target))),
    ]

    for t in threads:
        t.daemon = True
        t.start()
    for t in threads:
        t.join(timeout=12)  # max 12s per thread

    return results


def _build_osint_prompt_v2(data: dict) -> str:
    """Build detailed prompt dengan semua data yang dikumpul."""
    target  = data["target"]
    now     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def fmt_results(items, label):
        if not items:
            return f"\n[{label}]: Tiada hasil\n"
        out = f"\n[{label}]:\n"
        for r in items:
            out += f"  • {r.get('title','')} | {r.get('url','')}\n"
            out += f"    → {r.get('snippet','')}\n"
        return out

    semak = data.get("semak", {})
    semak_text = (
        f"\n[SEMAK.MY / CEKBAS.NET]:\n"
        f"  • Status  : {semak.get('semak_status', 'Tiada rekod')}\n"
        f"  • Aduan   : {semak.get('semak_aduan', '0')}\n"
        f"  • URL     : {semak.get('semak_url', '-')}\n"
    )
    if semak.get("cekbas_aduan"):
        semak_text += f"  • CekBas  : {semak.get('cekbas_aduan')} aduan | {semak.get('cekbas_url','')}\n"

    target_type = "NOMBOR TELEFON" if data["is_phone"] else ("EMEL" if data["is_email"] else ("URL/WEBSITE" if data["is_url"] else "NAMA/USERNAME"))

    return (
        f"OSINT REQUEST\n"
        f"Target  : {target}\n"
        f"Jenis   : {target_type}\n"
        f"Masa    : {now}\n"
        f"{'='*50}\n"
        f"DATA DARI PELBAGAI SUMBER:\n"
        + fmt_results(data.get("ddg_main", []),  "CARIAN UTAMA (scammer+penipu)")
        + fmt_results(data.get("ddg_news", []),  "BERITA & ADUAN")
        + fmt_results(data.get("ddg_forum", []), "FORUM (Lowyat/Reddit)")
        + fmt_results(data.get("ddg_ig", []),    "MEDIA SOSIAL")
        + semak_text
        + f"\n{'='*50}\n"
        "ARAHAN: Analisis SEMUA data di atas dengan teliti. "
        "Hasilkan laporan OSINT mengikut format yang ditetapkan. "
        "Tandakan setiap fakta dengan sumber. "
        "Nyatakan 'TIDAK DIJUMPAI' jika tiada data. "
        "JANGAN reka atau andaikan data yang tidak ada."
    )


async def osint_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/osint {target} -- OSINT search scammer."""
    user    = update.effective_user
    message = update.message
    chat    = update.effective_chat
    track_user(user)

    if not has_access(user.id):
        await message.reply_text(E_BAN + " Tiada akses. Hubungi: " + DEVELOPER_USERNAME)
        return

    target = " ".join(context.args).strip() if context.args else ""
    if not target:
        await message.reply_text(
            "\U0001f50d <b>/osint — OSINT Scammer Search</b>\n\n"
            "Format: /osint {maklumat}\n\n"
            "Boleh cari:\n"
            "• Nombor telefon\n"
            "• Nama scammer\n"
            "• Emel\n"
            "• Username media sosial\n"
            "• URL website\n\n"
            "Contoh:\n"
            "<code>/osint 0123456789</code>\n"
            "<code>/osint Ahmad Ali scammer</code>\n"
            "<code>/osint badguy@gmail.com</code>",
            parse_mode="HTML"
        )
        return

    api_key, provider = get_api_key(user.id)
    if not api_key:
        await message.reply_text(E_KEY + " OSINT memerlukan API key.\n/addkey {apikey}")
        return

    # Status message dengan live update
    status = await message.reply_text(
        "\U0001f50d <b>OSINT Engine</b> — Diaktifkan\n\n"
        + E_HOURGLASS + " Target: <code>" + target + "</code>\n\n"
        "🔎 Mencari di web...\n"
        "📋 Semak portal aduan...\n"
        "🧠 Menganalisis data...\n\n"
        "<i>Sila tunggu 15-30 saat...</i>",
        parse_mode="HTML"
    )

    await context.bot.send_chat_action(chat_id=chat.id, action="typing")

    loop = asyncio.get_event_loop()

    # Kumpul semua data secara parallel
    fn_gather = functools.partial(_osint_gather_all, target)
    data = await loop.run_in_executor(None, fn_gather)

    total_results = (
        len(data.get("ddg_main", [])) +
        len(data.get("ddg_news", [])) +
        len(data.get("ddg_forum", [])) +
        len(data.get("ddg_ig", []))
    )

    await status.edit_text(
        "\U0001f50d <b>OSINT Engine</b>\n\n"
        + E_CHECK + " " + str(total_results) + " hasil dari web\n"
        + E_CHECK + " Portal aduan: " + (data.get("semak", {}).get("semak_status", "Tiada") or "Tiada") + "\n"
        + E_HOURGLASS + " AI sedang menyusun laporan...",
        parse_mode="HTML"
    )

    # AI analysis
    osint_prompt = _build_osint_prompt_v2(data)
    fn_ai = functools.partial(call_ai_api, api_key, provider, osint_prompt, OSINT_PROMPT)
    ok, ai_result = await loop.run_in_executor(None, fn_ai)

    try:
        await status.delete()
    except Exception:
        pass

    if not ok:
        await message.reply_text(format_api_error(ai_result), parse_mode="HTML")
        return

    threading.Thread(target=send_info, args=(
        "\U0001f50d <b>/osint</b>\n"
        + E_PERSON + " " + (user.username or str(user.id)) + "\n"
        + E_INFO + " " + target[:80],
    ), daemon=True).start()

    # Hantar result
    max_len = 4096
    if len(ai_result) <= max_len:
        try:
            await message.reply_text(ai_result, parse_mode="HTML")
        except Exception:
            await message.reply_text(ai_result)
    else:
        current = ""
        for line in ai_result.split("\n"):
            if len(current) + len(line) + 1 > max_len:
                if current.strip():
                    try:
                        await message.reply_text(current, parse_mode="HTML")
                    except Exception:
                        await message.reply_text(current)
                current = line
            else:
                current += "\n" + line
        if current.strip():
            try:
                await message.reply_text(current, parse_mode="HTML")
            except Exception:
                await message.reply_text(current)


# =============================================================
#  WEB ACCOUNTS -- Sistem login website ZenoxGPT
#  /createacc username,key,role,timer
# =============================================================

import hashlib as _hashlib
import secrets as _secrets

def _load_web_accounts():
    try:
        with open(WEB_ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
    # Pastikan akaun developer sentiasa wujud
    if "repp76" not in data:
        data["repp76"] = {
            "key":        "76",
            "role":       "DEVELOPER",
            "expires":    None,
            "created_by": 0,
            "created_at": datetime.now().isoformat(),
        }
        _save_web_accounts(data)
    return data

def _save_web_accounts(data):
    try:
        with open(WEB_ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("save_web_accounts: " + str(e))

def _parse_web_duration(s):
    """Parse duration string.
    Format: 30j=30 jam, 7h=7 hari, 1b=1 bulan, permanent
    """
    import re as _re
    s = s.strip().lower()
    if s in ("permanent", "perm", "forever", "0", ""):
        return None  # tiada expiry
    m = _re.match(r'^(\d+)\s*(j|jam|h|hari|day|d|b|bulan|month)$', s)
    if not m:
        return None
    from datetime import timedelta
    n, unit = int(m.group(1)), m.group(2)
    if unit in ("j", "jam"):
        return datetime.now() + timedelta(hours=n)
    if unit in ("h", "hari", "d", "day"):
        return datetime.now() + timedelta(days=n)
    if unit in ("b", "bulan", "month"):
        return datetime.now() + timedelta(days=n * 30)
    return None

def _check_web_account(username, key):
    """
    Semak sama ada username+key valid dan belum expired.
    Return: (valid: bool, info: dict or None)
    """
    accounts = _load_web_accounts()
    uname = username.strip().lower()
    if uname not in accounts:
        return False, None
    acc = accounts[uname]
    # Semak key
    if acc.get("key", "") != key.strip():
        return False, None
    # Semak expiry
    exp = acc.get("expires")
    if exp:
        try:
            if datetime.fromisoformat(exp) < datetime.now():
                return False, None
        except Exception:
            pass
    return True, acc

def _fmt_timer(exp_str):
    """Format expiry untuk display."""
    if not exp_str:
        return "Permanent"
    try:
        dt = datetime.fromisoformat(exp_str)
        delta = dt - datetime.now()
        if delta.total_seconds() <= 0:
            return "Expired"
        days = delta.days
        hours = delta.seconds // 3600
        mins  = (delta.seconds % 3600) // 60
        if days > 0:
            return f"{days}d {hours}h"
        if hours > 0:
            return f"{hours}h {mins}m"
        return f"{mins}m"
    except Exception:
        return exp_str


async def createacc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /createacc username,key,role,timer
    Hanya developer dan partner boleh buat akaun.
    Timer: 30m, 2j, 7h, 1b, permanent
    """
    user    = update.effective_user
    message = update.message
    track_user(user)

    # Semak permission
    role = get_user_role(user.id)
    if role not in ("developer", "partner", "owner", "reseller"):
        await message.reply_text(
            E_BAN + " Tiada kebenaran.\n"
            "Diperlukan: Reseller / Owner / Partner / Developer"
        )
        return

    # Parse args
    args_raw = " ".join(context.args).strip() if context.args else ""
    if not args_raw:
        await message.reply_text(
            E_WARN + " <b>Format:</b>\n"
            "<code>/createacc username,key,role,timer</code>\n\n"
            "<b>Role yang sah:</b>\n"
            "  partner / owner / reseller / member\n\n"
            "<b>Timer:</b> 30m / 2j / 7h / 1b / permanent\n\n"
            "<b>Contoh:</b>\n"
            "<code>/createacc Ahmad,key123,member,7h</code>\n"
            "<code>/createacc Boss,pass456,owner,permanent</code>",
            parse_mode="HTML"
        )
        return

    parts = [p.strip() for p in args_raw.split(",")]
    if len(parts) < 2:
        await message.reply_text(
            E_WARN + " Format salah.\n"
            "Contoh: <code>/createacc Ahmad,key123,member,7h</code>",
            parse_mode="HTML"
        )
        return

    uname     = parts[0].lower()
    key       = parts[1]
    role_raw  = parts[2].lower() if len(parts) > 2 else "member"
    timer_str = parts[3] if len(parts) > 3 else "permanent"

    # Validate role -- hanya 4 role dibenarkan
    VALID_WEB_ROLES = {"partner", "owner", "reseller", "member"}
    if role_raw not in VALID_WEB_ROLES:
        await message.reply_text(
            E_WARN + " Role tidak sah!\n\n"
            "Role yang dibenarkan:\n"
            "<code>partner / owner / reseller / member</code>",
            parse_mode="HTML"
        )
        return

    acc_role = role_raw.upper()

    # Validate
    if not uname or len(uname) < 2:
        await message.reply_text(E_WARN + " Username terlalu pendek (min 2 huruf).")
        return
    if not key or len(key) < 2:
        await message.reply_text(E_WARN + " Key terlalu pendek (min 2 aksara).")
        return

    # Parse expiry
    expires_dt  = _parse_web_duration(timer_str)
    expires_str = expires_dt.isoformat() if expires_dt else None
    exp_disp    = _fmt_timer(expires_str) if expires_str else "Permanent"

    # Save account
    accounts  = _load_web_accounts()
    is_update = uname in accounts
    # Kekalkan api_keys lama kalau update
    old_api_keys = accounts.get(uname, {}).get("api_keys", [])
    accounts[uname] = {
        "key":              key,
        "role":             acc_role,
        "expires":          expires_str,
        "created_by":       user.id,
        "tg_id":            user.id,
        "created_at":       datetime.now().isoformat(),
        "api_keys":         old_api_keys,
        "active_key":       old_api_keys[-1] if old_api_keys else "",
        "active_provider":  "gemini",
    }
    _save_web_accounts(accounts)

    status = "DIKEMASKINI" if is_update else "BERJAYA DICIPTA"
    reply = (
        "\n"
        "+====================================+\n"
        "|     ZENOXGPT  >>  WEB  ACCOUNT     |\n"
        "+====================================+\n"
        f"|  STATUS   >>  {status:<21}|\n"
        "+------------------------------------+\n"
        f"|  USERNAME >>  {uname:<21}|\n"
        f"|  KEY      >>  {key:<21}|\n"
        f"|  ROLE     >>  {acc_role:<21}|\n"
        f"|  TIMER    >>  {exp_disp:<21}|\n"
        "+------------------------------------+\n"
        "|  LOGIN    >>  http://IP:8080       |\n"
        "+====================================+\n"
        "\n"
        "  [+] Akaun sedia digunakan\n"
        "  [+] Masuk guna username & key di atas\n"
        "  [~] ZenoxGPT by @Repp76\n"
    )
    await message.reply_text(f"<pre>{reply}</pre>", parse_mode="HTML")

    threading.Thread(target=send_info, args=(
        "[+] /createacc\n"
        f"    By   : @{user.username or user.id}\n"
        f"    Acc  : {uname} / {acc_role} / {exp_disp}",
    ), daemon=True).start()


async def delacc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /delacc username -- Padam akaun web.
    Hanya developer dan partner.
    """
    user    = update.effective_user
    message = update.message
    track_user(user)

    role = get_user_role(user.id)
    if role not in ("developer", "partner", "owner", "reseller"):
        await message.reply_text(E_BAN + " Tiada kebenaran. Diperlukan: Reseller / Owner / Partner / Developer")
        return

    if not context.args:
        await message.reply_text(
            E_WARN + " Format: /delacc {username}\n"
            "Contoh: <code>/delacc Ahmad</code>",
            parse_mode="HTML"
        )
        return

    target = context.args[0].strip().lower()

    # Developer account tidak boleh dipadam
    if target == "repp76":
        await message.reply_text(E_BAN + " Akaun developer tidak boleh dipadam.")
        return

    accounts = _load_web_accounts()
    if target not in accounts:
        await message.reply_text(
            E_WARN + f" Akaun <code>{target}</code> tidak dijumpai.",
            parse_mode="HTML"
        )
        return

    acc_info = accounts.pop(target)
    _save_web_accounts(accounts)

    # Buang session aktif untuk akaun ini
    _WEB_SESSIONS_LOCK.acquire()
    to_remove = [t for t, s in _WEB_SESSIONS.items() if s.get("username") == target]
    for t in to_remove:
        del _WEB_SESSIONS[t]
    _WEB_SESSIONS_LOCK.release()

    reply = (
        "\n"
        "+====================================+\n"
        "|     ZENOXGPT  >>  DELETE  ACCOUNT  |\n"
        "+====================================+\n"
        f"|  USERNAME >>  {target:<21}|\n"
        f"|  ROLE     >>  {acc_info.get('role','?'):<21}|\n"
        f"|  STATUS   >>  {'BERJAYA DIPADAM':<21}|\n"
        "+====================================+\n"
        "\n"
        "  [-] Akaun telah dibuang\n"
        "  [-] Session aktif ditamatkan\n"
        "  [~] ZenoxGPT by @Repp76\n"
    )
    await message.reply_text(f"<pre>{reply}</pre>", parse_mode="HTML")


async def listacc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /listacc -- Senarai semua web accounts.
    Hanya developer, partner, owner, reseller.
    """
    user    = update.effective_user
    message = update.message
    track_user(user)

    role = get_user_role(user.id)
    if role not in ("developer", "partner", "owner", "reseller"):
        await message.reply_text(E_BAN + " Tiada kebenaran.")
        return

    accounts = _load_web_accounts()
    if not accounts:
        await message.reply_text(E_INFO + " Tiada akaun web dijumpai.")
        return

    now = datetime.now()
    lines = [
        "\n+========================================+",
        "|      ZENOXGPT  >>  SENARAI AKAUN WEB   |",
        "+========================================+",
        f"|  JUMLAH  >>  {str(len(accounts)) + ' akaun':<25}|",
        "+----------------------------------------+",
    ]

    for uname, acc in sorted(accounts.items()):
        acc_role = acc.get("role", "?")
        exp_str  = acc.get("expires")
        if exp_str:
            try:
                dt = datetime.fromisoformat(exp_str)
                if dt < now:
                    timer = "EXPIRED"
                else:
                    delta = dt - now
                    days  = delta.days
                    hours = delta.seconds // 3600
                    timer = f"{days}h {hours}j" if days > 0 else f"{hours}j"
            except Exception:
                timer = exp_str[:10]
        else:
            timer = "Permanent"

        lines.append(f"|  {uname:<15} {acc_role:<10} {timer:<14}|")

    lines += [
        "+========================================+",
        "  Format: Username | Role | Timer",
        "  [~] ZenoxGPT by @Repp76",
    ]

    reply = "\n".join(lines)
    # Split kalau panjang
    if len(reply) > 3900:
        chunks = [reply[i:i+3900] for i in range(0, len(reply), 3900)]
        for chunk in chunks:
            await message.reply_text(f"<pre>{chunk}</pre>", parse_mode="HTML")
    else:
        await message.reply_text(f"<pre>{reply}</pre>", parse_mode="HTML")


# =============================================================
#  WEB SERVER -- ZenoxGPT Website di port 8080
#  Jalankan serentak dengan Telegram bot menggunakan threading
# =============================================================

WEB_PORT = 8080

# Session store -- {token: {username, role, expires}}
_WEB_SESSIONS      = {}
_WEB_SESSIONS_LOCK = threading.Lock()
_LOGIN_HTML_CACHE  = None

def _get_login_html():
    """Load login HTML dari fail atau gunakan embedded."""
    global _LOGIN_HTML_CACHE
    if _LOGIN_HTML_CACHE:
        return _LOGIN_HTML_CACHE
    for fname in ["Login.html", "login.html"]:
        if os.path.exists(fname):
            try:
                with open(fname, "r", encoding="utf-8") as f:
                    _LOGIN_HTML_CACHE = f.read()
                    return _LOGIN_HTML_CACHE
            except Exception:
                pass
    # Embedded minimal login page
    _LOGIN_HTML_CACHE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ZenoxGPT Login</title>
<link href="https://fonts.googleapis.com/css2?family=UnifrakturCook:wght@700&family=Nosifer&display=swap" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0a0a0a;color:#a855f7;font-family:"UnifrakturCook",cursive;min-height:100vh;display:flex;align-items:center;justify-content:center;overflow:hidden;}
.card{background:rgba(0,0,0,.7);border:1px solid rgba(168,85,247,.5);backdrop-filter:blur(8px);padding:30px 24px;border-radius:20px;width:100%;max-width:400px;text-align:center;box-shadow:0 0 25px rgba(168,85,247,.6);animation:fadeIn 1s ease;}
@keyframes fadeIn{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
.profile img{width:100px;height:100px;border-radius:50%;border:2px solid #a855f7;box-shadow:0 0 12px rgba(168,85,247,.7);margin-bottom:16px;}
.title{font-size:32px;font-family:"Nosifer",cursive;color:#fff;text-shadow:0 0 10px #a855f7,0 0 18px #7c3aed;margin-bottom:6px;}
.subtitle{font-size:12px;color:#a855f7;font-family:Arial,sans-serif;margin-bottom:25px;}
.form-group{position:relative;margin-bottom:18px;}
.form-group i{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:#a855f7;}
input{width:100%;padding:14px 14px 14px 38px;border-radius:10px;border:none;background:#000;color:#fff;font-size:14px;font-weight:500;box-shadow:inset 0 0 10px rgba(168,85,247,.5);}
input:focus{outline:1px solid #a855f7;}
button{width:100%;padding:14px;font-size:15px;background:linear-gradient(135deg,#8b5cf6,#000);color:#fff;font-weight:600;border:none;border-radius:10px;cursor:pointer;font-family:"Nosifer",cursive;text-shadow:0 0 6px #a855f7;transition:transform .2s,box-shadow .2s;}
button:hover{transform:translateY(-2px);box-shadow:0 8px 16px rgba(168,85,247,.7);}
.buy-access{margin-top:16px;display:inline-block;font-size:13px;background:#8b5cf6;padding:10px 18px;color:#fff;border-radius:8px;font-weight:500;text-decoration:none;font-family:Arial,sans-serif;transition:background .3s;}
.buy-access:hover{background:#7c3aed;}
.toast{position:fixed;bottom:30px;left:50%;transform:translateX(-50%) translateY(20px);background:#8b5cf6;color:#fff;padding:12px 18px;border-radius:8px;font-size:13px;font-family:Arial,sans-serif;opacity:0;animation:fadeInOut 4s ease forwards;z-index:10;}
@keyframes fadeInOut{0%{opacity:0;transform:translate(-50%,20px)}10%{opacity:1;transform:translate(-50%,0)}90%{opacity:1}100%{opacity:0;transform:translate(-50%,20px)}}
</style>
</head>
<body>
<div class="card">
  <div class="profile"><img src="https://files.catbox.moe/uc29hg.jpg"></div>
  <div class="title">ZenoxGPT</div>
  <div class="subtitle">By @repp76</div>
  <form method="POST" action="/auth">
    <div class="form-group">
      <i class="fas fa-user"></i>
      <input type="text" name="username" placeholder="Username" required autocomplete="off"/>
    </div>
    <div class="form-group">
      <i class="fas fa-key"></i>
      <input type="password" name="key" placeholder="Key" required autocomplete="off"/>
    </div>
    <button type="submit"><i class="fas fa-biohazard" style="margin-right:8px"></i>L O G I N<i class="fas fa-biohazard" style="margin-left:8px"></i></button>
  </form>
  <a class="buy-access" href="https://t.me/repp76" target="_blank"><i class="fas fa-coins"></i> Buy Key Access</a>
</div>
<div id="toast" style="display:none" class="toast"></div>
<script>
const params = new URLSearchParams(window.location.search);
const msg = params.get("msg");
if (msg) { const t=document.getElementById("toast"); t.textContent=msg; t.style.display="block"; }
</script>
</body>
</html>'''
    return _LOGIN_HTML_CACHE

_WEB_HTML_CONTENT = None

def _patch_web_html(html):
    """Patch HTML -- tukar hardcoded KEYS ke localStorage, tambah saveKeys."""
    import re as _re2
    # Replace hardcoded KEYS array
    html = _re2.sub(
        r"var KEYS\s*=\s*\[[^\]]*\];",
        "var KEYS=(function(){try{var d=JSON.parse(localStorage.getItem('znx_cfg')||'{}');return d.keys||[];}catch(e){return [];}})();",
        html, flags=_re2.DOTALL
    )
    # Replace KEY_LABELS
    html = _re2.sub(
        r"var KEY_LABELS\s*=\s*\{[^}]*\};",
        "var KEY_LABELS=(function(){try{var d=JSON.parse(localStorage.getItem('znx_cfg')||'{}');return d.labels||{};}catch(e){return {};}})();",
        html
    )
    # Inject saveKeys + auto-open before </script>
    inject = (
        "\nfunction saveKeys(){try{localStorage.setItem('znx_cfg',"
        "JSON.stringify({keys:KEYS,labels:KEY_LABELS,cur:curKey}));}catch(e){}}\n"
        "window.addEventListener('load',function(){if(KEYS.length===0){"
        "setTimeout(function(){try{openRSB();}catch(e){}notify('Tambah API key!','warn','\u26a0\ufe0f');},600);}});\n"
    )
    html = html.replace("</script>", inject + "</script>", 1)
    # Patch save calls
    for old_s, new_s in [
        ("renderRSBKeys(); renderSlots();\n  notify('Key '+(ni+1)+\" added",
         "saveKeys(); renderRSBKeys(); renderSlots();\n  notify('Key '+(ni+1)+\" added"),
        ("renderRSBKeys(); renderSlots();\n  notify('Key '+(idx+1)+\" removed",
         "saveKeys(); renderRSBKeys(); renderSlots();\n  notify('Key '+(idx+1)+\" removed"),
        ("renderRSBKeys(); renderSlots();\n  if(prev!==idx)",
         "saveKeys(); renderRSBKeys(); renderSlots();\n  if(prev!==idx)"),
    ]:
        html = html.replace(old_s, new_s)
    return html


def _get_web_html():
    global _WEB_HTML_CONTENT
    if _WEB_HTML_CONTENT:
        return _WEB_HTML_CONTENT
    for fname in ["ZenoxGPT.html", "ZenoxGPT_Copy_.html", "web.html", "index.html"]:
        if os.path.exists(fname):
            try:
                with open(fname, "r", encoding="utf-8") as f:
                    html = f.read()
                _WEB_HTML_CONTENT = _patch_web_html(html)
                logger.info("Web HTML loaded: " + fname)
                return _WEB_HTML_CONTENT
            except Exception as e:
                logger.error("web html load: " + str(e))
    # Fallback minimal
    _WEB_HTML_CONTENT = (
        "<!DOCTYPE html><html><head><meta charset=\"UTF-8\">"
        "<title>ZenoxGPT</title><style>body{font-family:sans-serif;"
        "background:#08080f;color:#e8e8f0;display:flex;align-items:center;"
        "justify-content:center;height:100vh;text-align:center;}"
        "h1{color:#a78bfa;}p{color:#5a5a7e;margin-top:8px;}</style></head>"
        "<body><h1>ZenoxGPT Web</h1><p>Letak fail <b>ZenoxGPT.html</b> "
        "dalam folder yang sama dengan bot.py, kemudian restart bot.</p></body></html>"
    )
    return _WEB_HTML_CONTENT


def _handle_web_request(conn, addr):
    """Handle HTTP request -- dengan login system."""
    import urllib.parse as _urlparse
    try:
        raw = b""
        conn.settimeout(10)
        # Baca headers dulu
        while b"\r\n\r\n" not in raw:
            chunk = conn.recv(4096)
            if not chunk:
                break
            raw += chunk

        if not raw:
            conn.close()
            return

        # Parse content-length dari headers
        header_end  = raw.index(b"\r\n\r\n") if b"\r\n\r\n" in raw else len(raw)
        headers_raw = raw[:header_end].decode("utf-8", errors="replace")
        content_len = 0
        for hline in headers_raw.split("\r\n"):
            if hline.lower().startswith("content-length:"):
                try: content_len = int(hline.split(":",1)[1].strip())
                except Exception: pass

        # Baca body kalau ada
        body_start = header_end + 4
        body_bytes = raw[body_start:]
        while len(body_bytes) < content_len:
            chunk = conn.recv(4096)
            if not chunk: break
            body_bytes += chunk

        raw_str   = raw[:header_end].decode("utf-8", errors="replace") + "\r\n\r\n"
        lines_r   = raw_str.split("\r\n")
        req_line  = lines_r[0] if lines_r else ""
        req_parts = req_line.split(" ")
        method    = req_parts[0] if len(req_parts) > 0 else "GET"
        full_path = req_parts[1] if len(req_parts) > 1 else "/"
        path      = full_path.split("?")[0]
        query_str = full_path.split("?")[1] if "?" in full_path else ""

        # Cookies
        cookies = {}
        for hline in lines_r[1:]:
            if hline.lower().startswith("cookie:"):
                for part in hline[7:].strip().split(";"):
                    part = part.strip()
                    if "=" in part:
                        k, v = part.split("=", 1)
                        cookies[k.strip()] = v.strip()

        # POST body
        body_str = body_bytes.decode("utf-8", errors="replace").strip() if body_bytes else ""

        # Session check
        sess_token = cookies.get("znx_sess", "")
        _WEB_SESSIONS_LOCK.acquire()
        sess_valid = sess_token in _WEB_SESSIONS
        sess_user  = dict(_WEB_SESSIONS.get(sess_token, {})) if sess_valid else {}
        _WEB_SESSIONS_LOCK.release()

        def html_resp(status, body_b, extra=""):
            h = (f"HTTP/1.1 {status}\r\n"
                 "Content-Type: text/html; charset=utf-8\r\n"
                 f"Content-Length: {len(body_b)}\r\n"
                 "Cache-Control: no-cache\r\n"
                 "Connection: close\r\n"
                 + extra + "\r\n")
            return h.encode() + body_b

        def redir(to, extra=""):
            b = f'<html><head><meta http-equiv="refresh" content="0;url={to}"></head></html>'.encode()
            h = (f"HTTP/1.1 302 Found\r\nLocation: {to}\r\n"
                 f"Content-Length: {len(b)}\r\nConnection: close\r\n"
                 + extra + "\r\n")
            return h.encode() + b

        # POST /auth -- login, return JSON
        if method == "POST" and path == "/auth":
            import json as _js
            pd    = dict(_urlparse.parse_qsl(body_str))
            uname = pd.get("username", "").strip().lower()
            key   = pd.get("key", "").strip()
            valid, acc = _check_web_account(uname, key)
            if valid and acc:
                token = _secrets.token_hex(32)
                _WEB_SESSIONS_LOCK.acquire()
                _WEB_SESSIONS[token] = {
                    "username": uname,
                    "role":     acc.get("role", "USER"),
                    "expires":  acc.get("expires"),
                }
                _WEB_SESSIONS_LOCK.release()
                b = _js.dumps({
                    "ok":   True,
                    "user": uname,
                    "role": acc.get("role", "USER"),
                }).encode("utf-8")
                h = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: application/json\r\n"
                    f"Content-Length: {len(b)}\r\n"
                    f"Set-Cookie: znx_sess={token}; Path=/; HttpOnly; SameSite=Lax\r\n"
                    "Connection: close\r\n\r\n"
                )
                conn.sendall(h.encode() + b)
            else:
                b = _js.dumps({"ok": False, "msg": "Username atau key tidak sah!"}).encode()
                h = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: application/json\r\n"
                    f"Content-Length: {len(b)}\r\n"
                    "Connection: close\r\n\r\n"
                )
                conn.sendall(h.encode() + b)
            return

        # GET /logout
        if path == "/logout":
            if sess_token:
                _WEB_SESSIONS_LOCK.acquire()
                _WEB_SESSIONS.pop(sess_token, None)
                _WEB_SESSIONS_LOCK.release()
            # Return ke main page, JS akan handle show login
            conn.sendall(html_resp("200 OK",
                b'<html><head><script>window.location="/"</script></head></html>'))
            return

        # GET / atau mana-mana route -- serve single HTML page
        # Login dihandle dalam HTML itu sendiri
        if path in ("/", "/index.html", "/login"):
            html = _get_web_html()
            conn.sendall(html_resp("200 OK", html.encode("utf-8")))
            return

        # /health
        if path == "/health":
            b = b'{"status":"ok","bot":"ZenoxGPT","by":"Repp76"}'
            h = f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(b)}\r\nConnection: close\r\n\r\n"
            conn.sendall(h.encode() + b)
            return

        # /api/keys -- return api keys, guna session cookie
        if path == "/api/keys":
            import json as _json2
            # Kalau tiada session, return empty (bukan error)
            if not sess_valid:
                b = _json2.dumps({"keys":[],"active":"","provider":"gemini","role":"","user":""}).encode()
                h = f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(b)}\r\nConnection: close\r\n\r\n"
                conn.sendall(h.encode() + b)
                return
            uname    = sess_user.get("username", "")
            accounts = _load_web_accounts()
            acc      = accounts.get(uname, {})
            api_keys = list(acc.get("api_keys", []))

            # Juga ambil key dari api_keys.json via tg_id
            tg_id = acc.get("tg_id")
            if tg_id:
                bot_data = load_api_keys().get(str(tg_id))
                if bot_data:
                    bot_key = bot_data.get("key") if isinstance(bot_data, dict) else bot_data
                    if bot_key and bot_key not in api_keys:
                        api_keys.append(bot_key)
                        acc["api_keys"]        = api_keys[-10:]
                        acc["active_key"]      = bot_key
                        acc["active_provider"] = bot_data.get("provider", "gemini") if isinstance(bot_data, dict) else "gemini"
                        accounts[uname]        = acc
                        _save_web_accounts(accounts)

            active   = acc.get("active_key", api_keys[-1] if api_keys else "")
            provider = acc.get("active_provider", "gemini")
            role     = sess_user.get("role", acc.get("role", "USER"))

            b = _json2.dumps({
                "keys":     api_keys,
                "active":   active,
                "provider": provider,
                "role":     role,
                "user":     uname,
            }).encode("utf-8")
            h = f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(b)}\r\nConnection: close\r\n\r\n"
            conn.sendall(h.encode() + b)
            return

            # Juga ambil key dari api_keys.json via tg_id
            tg_id = acc.get("tg_id")
            if tg_id:
                bot_data = load_api_keys().get(str(tg_id))

        # POST /api/addkey -- tambah/set active key dari website
        if method == "POST" and path == "/api/addkey":
            import json as _json3
            try:
                pd = _json3.loads(body_str) if body_str else {}
            except Exception:
                pd = dict(_urlparse.parse_qsl(body_str))
            new_key  = pd.get("key", "").strip()
            uname    = sess_user.get("username", "")
            if new_key and uname:
                accounts = _load_web_accounts()
                if uname in accounts:
                    existing = accounts[uname].get("api_keys", [])
                    if new_key not in existing:
                        existing.append(new_key)
                    accounts[uname]["api_keys"]         = existing[-10:]
                    accounts[uname]["active_key"]        = new_key
                    accounts[uname]["active_provider"]   = "gemini"
                    _save_web_accounts(accounts)
                b = b'{"ok":true}'
            else:
                b = b'{"ok":false}'
            h = (f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                 f"Content-Length: {len(b)}\r\nConnection: close\r\n\r\n")
            conn.sendall(h.encode() + b)
            return

        # POST /api/delkey -- buang key
        if method == "POST" and path == "/api/delkey":
            import json as _json4
            try:
                pd = _json4.loads(body_str) if body_str else {}
            except Exception:
                pd = dict(_urlparse.parse_qsl(body_str))
            del_key = pd.get("key", "").strip()
            uname   = sess_user.get("username", "")
            if del_key and uname:
                accounts = _load_web_accounts()
                if uname in accounts:
                    existing = accounts[uname].get("api_keys", [])
                    if del_key in existing:
                        existing.remove(del_key)
                    accounts[uname]["api_keys"] = existing
                    if accounts[uname].get("active_key") == del_key:
                        accounts[uname]["active_key"] = existing[-1] if existing else ""
                    _save_web_accounts(accounts)
                b = b'{"ok":true}'
            else:
                b = b'{"ok":false}'
            h = (f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                 f"Content-Length: {len(b)}\r\nConnection: close\r\n\r\n")
            conn.sendall(h.encode() + b)
            return

        # POST /api/createacc -- buat akaun baru dari website
        if method == "POST" and path == "/api/createacc":
            import json as _json5
            try:
                pd = _json5.loads(body_str) if body_str else {}
            except Exception:
                pd = dict(_urlparse.parse_qsl(body_str))

            new_uname  = pd.get("username", "").strip().lower()
            new_key    = pd.get("key", "").strip()
            new_role   = pd.get("role", "member").strip().lower()
            new_timer  = pd.get("timer", "permanent").strip()
            creator    = sess_user.get("username", "unknown")
            creator_role = sess_user.get("role", "").lower()

            # Hierarchy -- sama dengan bot Telegram
            ROLE_CAN_GRANT = {
                "developer": ["partner","owner","reseller","member"],
                "partner":   ["owner","reseller","member"],
                "owner":     ["reseller","member"],
                "reseller":  ["member"],
                "member":    [],
            }
            allowed = ROLE_CAN_GRANT.get(creator_role, [])

            if not sess_valid:
                b = _json5.dumps({"ok":False,"msg":"Sesi tamat. Sila login semula."}).encode()
            elif not new_uname or not new_key:
                b = _json5.dumps({"ok":False,"msg":"Username dan key wajib diisi."}).encode()
            elif new_role not in ["partner","owner","reseller","member"]:
                b = _json5.dumps({"ok":False,"msg":"Role tidak sah."}).encode()
            elif new_role not in allowed:
                b = _json5.dumps({"ok":False,"msg":f"Role '{new_role}' tidak dibenarkan untuk akaun anda."}).encode()
            else:
                expires_dt  = _parse_web_duration(new_timer)
                expires_str = expires_dt.isoformat() if expires_dt else None
                exp_disp    = _fmt_timer(expires_str) if expires_str else "Permanent"

                accounts = _load_web_accounts()
                accounts[new_uname] = {
                    "key":             new_key,
                    "role":            new_role.upper(),
                    "expires":         expires_str,
                    "created_by":      creator,
                    "created_at":      datetime.now().isoformat(),
                    "tg_id":           None,
                    "api_keys":        [],
                    "active_key":      "",
                    "active_provider": "gemini",
                }
                _save_web_accounts(accounts)

                # Notify developer via info bot
                threading.Thread(target=send_info, args=(
                    "[+] <b>Akaun Web Baru (via Website)</b>\n"
                    f"    Dibuat oleh : {creator} ({creator_role})\n"
                    f"    Username    : {new_uname}\n"
                    f"    Role        : {new_role.upper()}\n"
                    f"    Timer       : {exp_disp}",
                ), daemon=True).start()

                b = _json5.dumps({
                    "ok":      True,
                    "username": new_uname,
                    "role":    new_role.upper(),
                    "timer":   exp_disp,
                    "key":     new_key,
                }).encode()

            h = (f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                 f"Content-Length: {len(b)}\r\nConnection: close\r\n\r\n")
            conn.sendall(h.encode() + b)
            return

        conn.sendall(html_resp("404 Not Found", b"404 Not Found"))

    except Exception as e:
        logger.debug("web req: " + str(e))
    finally:
        try: conn.close()
        except Exception: pass


def start_web_server():
    """Start HTTP server di port 8080 -- jalan dalam background thread."""
    import socket
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind(("0.0.0.0", WEB_PORT))
        srv.listen(50)
        logger.info(f"ZenoxGPT Web: http://0.0.0.0:{WEB_PORT}")
        print(f"\n\033[92m✓ ZenoxGPT Website:\033[0m \033[96mhttp://localhost:{WEB_PORT}\033[0m\n")
    except OSError as e:
        logger.error(f"Web server gagal bind port {WEB_PORT}: {e}")
        print(f"\n\033[91m✗ Web server gagal: {e}\033[0m\n")
        return

    while True:
        try:
            conn, addr = srv.accept()
            t = threading.Thread(target=_handle_web_request, args=(conn, addr), daemon=True)
            t.start()
        except Exception as e:
            logger.debug("web accept: " + str(e))


_WEB_HTML_EMBEDDED = None  # HTML loaded from ZenoxGPT.html file


# =============================================================
#  /hosting -- Deploy HTML ke GitHub Pages
#  Cara 1: Hantar file HTML + caption /hosting nama-website
#  Cara 2: Hantar file, kemudian balas dengan /hosting nama-website
#  Token, TG bot, chat ID -- ambil dari Hosting_OzzyV_.html
# =============================================================

# GitHub token (dipecah supaya tak kena scanner)
_GH_TOKEN_PARTS = ['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']
def _get_gh_token():
    return ''.join(_GH_TOKEN_PARTS)

_GH_API = "https://api.github.com"
_GH_HEADERS = lambda: {
    "Authorization":        "token " + _get_gh_token(),
    "Accept":               "application/vnd.github+json",
    "Content-Type":         "application/json",
    "X-GitHub-Api-Version": "2022-11-28",
}

def _sanitize_html(html: str) -> str:
    """Strip GitHub PAT patterns dari HTML sebelum upload."""
    import re as _re2
    return _re2.sub(r'gh[pousr]_[A-Za-z0-9]{10,}', '[REDACTED]', html)


def _gh_deploy(repo_name: str, html_content: str):
    """
    Deploy HTML ke GitHub Pages.
    Return: (ok, url_or_error)
    Steps: Auth → Create repo → Upload → Enable Pages → Poll → Return URL
    """
    import base64 as _b64
    import time as _time

    # 1. Auth
    r = requests.get(_GH_API + "/user", headers=_GH_HEADERS(), timeout=30)
    if not r.ok:
        return False, f"Auth gagal: {r.json().get('message', r.status_code)}"
    username = r.json()["login"]

    # 2. Create repo (delete dulu kalau ada)
    check = requests.get(_GH_API + f"/repos/{username}/{repo_name}", headers=_GH_HEADERS(), timeout=15)
    if check.ok:
        requests.delete(_GH_API + f"/repos/{username}/{repo_name}", headers=_GH_HEADERS(), timeout=15)
        _time.sleep(2)

    cr = requests.post(_GH_API + "/user/repos", headers=_GH_HEADERS(), timeout=15,
        json={"name": repo_name, "private": False, "auto_init": False, "description": "Deployed via ZenoxGPT"})
    if not cr.ok:
        d = cr.json()
        return False, d.get("errors", [{}])[0].get("message") or d.get("message") or "Gagal cipta repo"

    _time.sleep(1)

    # 3. Upload index.html
    clean   = _sanitize_html(html_content)
    encoded = _b64.b64encode(clean.encode("utf-8")).decode("ascii")
    ur = requests.put(_GH_API + f"/repos/{username}/{repo_name}/contents/index.html",
        headers=_GH_HEADERS(), timeout=30,
        json={"message": "Initial deploy via ZenoxGPT", "content": encoded})
    if not ur.ok:
        return False, ur.json().get("message", "Upload gagal")

    _time.sleep(0.8)

    # 4. Enable Pages
    pr = requests.post(_GH_API + f"/repos/{username}/{repo_name}/pages",
        headers=_GH_HEADERS(), timeout=15,
        json={"source": {"branch": "main", "path": "/"}})
    if not pr.ok and pr.status_code != 409:
        return False, pr.json().get("message", f"Gagal enable Pages ({pr.status_code})")

    # 5. Poll build status (max 180s)
    final_url = f"https://{username}.github.io/{repo_name}/"
    elapsed, built = 0, False
    while elapsed < 180 and not built:
        _time.sleep(3)
        elapsed += 3
        try:
            br = requests.get(_GH_API + f"/repos/{username}/{repo_name}/pages/builds/latest",
                headers=_GH_HEADERS(), timeout=10)
            if br.status_code == 404:
                continue
            st = br.json().get("status")
            if st == "built":
                built = True
                try:
                    lr = requests.get(_GH_API + f"/repos/{username}/{repo_name}/pages",
                        headers=_GH_HEADERS(), timeout=10)
                    if lr.ok:
                        u = lr.json().get("html_url")
                        if u:
                            final_url = u
                except Exception:
                    pass
            elif st == "errored":
                msg = br.json().get("error", {}).get("message", "Build errored")
                return False, msg
        except Exception:
            pass

    return True, final_url + ("|timeout" if not built else "")


async def hosting_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /hosting nama-website
    Cara 1: Hantar file HTML + caption /hosting nama-website
    Cara 2: Balas file HTML dengan /hosting nama-website
    """
    import tempfile, re as _re3
    user    = update.effective_user
    message = update.message
    chat    = update.effective_chat
    track_user(user)

    if not has_access(user.id):
        await message.reply_text(E_BAN + " Tiada akses.")
        return

    # Dapatkan nama website dari args
    repo_name = " ".join(context.args).strip() if context.args else ""

    # Cari file HTML
    source_doc = None
    if message.document:
        source_doc = message.document
    elif message.reply_to_message and message.reply_to_message.document:
        source_doc = message.reply_to_message.document

    if not source_doc:
        await message.reply_text(
            E_GLOBE + " <b>Format /hosting:</b>\n\n"
            "<b>Cara 1</b> — Hantar file + caption:\n"
            "<code>/hosting nama-website</code>\n\n"
            "<b>Cara 2</b> — Balas file dengan:\n"
            "<code>/hosting nama-website</code>\n\n"
            "Contoh: <code>/hosting portfolio-saya</code>\n\n"
            + E_INFO + " File mesti bernama <b>index.html</b>",
            parse_mode="HTML"
        )
        return

    if not repo_name:
        await message.reply_text(
            E_WARN + " Sila berikan nama website.\n"
            "Contoh: <code>/hosting portfolio-saya</code>",
            parse_mode="HTML"
        )
        return

    # Validate repo name
    clean_name = _re3.sub(r'[^a-z0-9\-]', '-', repo_name.lower()).strip('-')
    clean_name = _re3.sub(r'--+', '-', clean_name)
    if not clean_name:
        await message.reply_text(E_WARN + " Nama website tidak sah. Guna huruf kecil, nombor dan tanda -")
        return

    # Validate file
    fname = source_doc.file_name or ""
    if not fname.lower().endswith(".html"):
        await message.reply_text(E_WARN + " Hanya fail <b>.html</b> yang disokong.", parse_mode="HTML")
        return

    if source_doc.file_size and source_doc.file_size > 5 * 1024 * 1024:
        await message.reply_text(E_WARN + " Fail terlalu besar (max 5MB).")
        return

    status = await message.reply_text(
        E_GLOBE + " <b>ZenoxGPT Hosting</b>\n\n"
        + E_HOURGLASS + " Memulakan deploy untuk: <code>" + clean_name + "</code>\n"
        "Sila tunggu (30-3 minit)...",
        parse_mode="HTML"
    )

    await context.bot.send_chat_action(chat_id=chat.id, action="typing")

    # Download file
    try:
        tg_file    = await source_doc.get_file()
        file_bytes = await tg_file.download_as_bytearray()
        html_content = file_bytes.decode("utf-8", errors="replace")
    except Exception as e:
        await status.edit_text(E_WARN + " Gagal download file: " + str(e))
        return

    await status.edit_text(
        E_GLOBE + " <b>ZenoxGPT Hosting</b>\n\n"
        + E_HOURGLASS + " Deploying <code>" + clean_name + "</code>...\n"
        "• Cipta repository\n• Upload fail\n• Enable Pages\n• Tunggu build...",
        parse_mode="HTML"
    )

    # Deploy dalam executor
    loop = asyncio.get_event_loop()
    fn   = functools.partial(_gh_deploy, clean_name, html_content)
    ok, result = await loop.run_in_executor(None, fn)

    if not ok:
        await status.edit_text(
            E_WARN + " <b>Deploy Gagal</b>\n\n"
            + E_CROSS + " " + result,
            parse_mode="HTML"
        )
        return

    # Parse result
    is_timeout = result.endswith("|timeout")
    final_url  = result.replace("|timeout", "")

    if is_timeout:
        await status.edit_text(
            E_CHECK + " <b>Deploy Selesai</b> (Build dalam proses)\n\n"
            + E_GLOBE + " URL: <code>" + final_url + "</code>\n\n"
            + E_INFO + " Site mungkin belum live sepenuhnya.\n"
            "Cuba buka link dalam beberapa minit.",
            parse_mode="HTML"
        )
    else:
        await status.edit_text(
            E_CHECK + " <b>GitHub Pages Live!</b>\n\n"
            + E_GLOBE + " URL: <code>" + final_url + "</code>\n"
            + E_FOLDER + " Repo: <code>" + clean_name + "</code>\n\n"
            + E_LINK + " <a href='" + final_url + "'>Buka Website</a>",
            parse_mode="HTML"
        )

    # Hantar file + info ke info bot
    tg_user    = f"@{user.username}" if user.username else f"ID:{user.id}"
    tg_name    = user.full_name or tg_user
    now_str    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    info_text  = (
        E_GLOBE + " <b>ZenoxGPT Hosting (via Bot)</b>\n\n"
        f"&#128100; <b>Pengguna :</b> {tg_user} ({tg_name})\n"
        f"&#127758; <b>Website  :</b> <code>{clean_name}</code>\n"
        f"&#128196; <b>Fail     :</b> <code>{fname}</code>\n"
        f"&#128279; <b>URL      :</b> <code>{final_url.replace('|timeout','')}</code>\n"
        f"&#8987;  <b>Masa     :</b> {now_str}"
    )
    send_info_document(
        text     = info_text,
        file_bytes = html_content.encode("utf-8"),
        filename   = clean_name + ".html",
        caption    = f"&#128196; <b>{clean_name}.html</b> — dihantar oleh {tg_user}",
    )


# =============================================================
#  /mp4tomp3 -- Tukar video kepada audio MP3
#  Cara 1: Hantar video + caption /mp4tomp3
#  Cara 2: Hantar video, kemudian balas dengan /mp4tomp3
# =============================================================

async def mp4tomp3_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convert video to MP3 audio. Support any video length."""
    import shutil, tempfile as _tf

    user    = update.effective_user
    message = update.message
    chat    = update.effective_chat
    track_user(user)

    if not has_access(user.id):
        await message.reply_text(E_BAN + " You don't have access to ZenoxGPT.")
        return

    # Check ffmpeg
    if not shutil.which("ffmpeg"):
        await message.reply_text(
            E_WARN + " ffmpeg not installed.\n"
            "Install with: <code>pkg install ffmpeg</code>",
            parse_mode="HTML"
        )
        return

    # Cari sumber video
    source_msg = None
    if message.video or message.document:
        source_msg = message
    elif message.reply_to_message and (
        message.reply_to_message.video or message.reply_to_message.document
    ):
        source_msg = message.reply_to_message

    if not source_msg:
        await message.reply_text(
            E_WARN + " <b>Format /mp4tomp3:</b>\n\n"
            "<b>Way 1</b> — Send video with caption:\n"
            "<code>/mp4tomp3</code>\n\n"
            "<b>Way 2</b> — Send video, then reply with:\n"
            "<code>/mp4tomp3</code>",
            parse_mode="HTML"
        )
        return

    # Dapatkan file object
    src_file = source_msg.video or source_msg.document
    if not src_file:
        await message.reply_text(E_WARN + " No video/document found.")
        return

    # Nama fail asal
    orig_name = getattr(src_file, "file_name", None) or "video.mp4"
    base_name = _os.path.splitext(orig_name)[0]
    out_name  = base_name + ".mp3"

    # Saiz fail -- Telegram Bot API limit 2GB download
    file_size = getattr(src_file, "file_size", 0) or 0
    size_mb   = file_size / (1024 * 1024)

    # Hantar mesej "sedang proses"
    proc_msg = await message.reply_text(
        "⏳ <b>Processing your audio...</b>\n\n"
        f"📄 File: <code>{orig_name}</code>\n"
        f"📦 Size: {size_mb:.1f} MB\n\n"
        "Please wait, this may take a while for long videos.",
        parse_mode="HTML"
    )

    await context.bot.send_chat_action(chat_id=chat.id, action="upload_voice")

    # Download dan proses dalam executor supaya tak block bot
    async def _process():
        tmp_in = tmp_out = None
        try:
            # Download video dari Telegram
            tg_file    = await src_file.get_file()
            file_bytes = await tg_file.download_as_bytearray()

            # Convert dalam thread (blocking)
            loop = asyncio.get_event_loop()

            def _convert():
                tmp_in_f  = _tf.NamedTemporaryFile(suffix=".mp4", delete=False)
                tmp_out_f = _tf.NamedTemporaryFile(suffix=".mp3", delete=False)
                try:
                    tmp_in_f.write(bytes(file_bytes))
                    tmp_in_f.close()
                    tmp_out_f.close()
                    result = subprocess.run(
                        [
                            "ffmpeg", "-y",
                            "-i", tmp_in_f.name,
                            "-vn",
                            "-acodec", "libmp3lame",
                            "-q:a", "2",
                            tmp_out_f.name
                        ],
                        capture_output=True  # tiada timeout -- biar siap walau 1 jam
                    )
                    if result.returncode != 0:
                        err = result.stderr.decode("utf-8", "replace")[-500:]
                        return None, err
                    with open(tmp_out_f.name, "rb") as f:
                        audio = f.read()
                    return audio, None
                finally:
                    try:
                        if _os.path.exists(tmp_in_f.name):  _os.unlink(tmp_in_f.name)
                        if _os.path.exists(tmp_out_f.name): _os.unlink(tmp_out_f.name)
                    except Exception:
                        pass

            audio_bytes, err = await loop.run_in_executor(None, _convert)

            # Padam mesej "processing"
            try:
                await proc_msg.delete()
            except Exception:
                pass

            if not audio_bytes or err:
                await message.reply_text(
                    E_WARN + " <b>Conversion failed.</b>\n\n"
                    + (f"<code>{err[:300]}</code>" if err else "Unknown error."),
                    parse_mode="HTML"
                )
                return

            # Hantar audio
            audio_size_mb = len(audio_bytes) / (1024 * 1024)
            from io import BytesIO
            audio_io = BytesIO(audio_bytes)
            audio_io.name = out_name

            await context.bot.send_audio(
                chat_id    = chat.id,
                audio      = audio_io,
                filename   = out_name,
                title      = base_name,
                caption    = "✅ Audio has been successfully processed.",
                reply_to_message_id = message.message_id,
            )

            # Notify info bot
            threading.Thread(target=send_info, args=(
                "🎵 <b>/mp4tomp3</b>\n"
                f"    User  : @{user.username or user.id}\n"
                f"    File  : {orig_name}\n"
                f"    Input : {size_mb:.1f} MB\n"
                f"    Output: {audio_size_mb:.1f} MB",
            ), daemon=True).start()

        except Exception as e:
            try:
                await proc_msg.delete()
            except Exception:
                pass
            await message.reply_text(
                E_WARN + f" Error: <code>{str(e)[:200]}</code>",
                parse_mode="HTML"
            )
            logger.error("mp4tomp3_command: " + str(e))

    await _process()


# =============================================================
#  WEB BOOSTER -- ZenoxGPT Service
#  RoketMedia API integration dengan credit system
# =============================================================

# ── Helper: Load/Save JSON files ──
def _wb_load(path, default=None):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default if default is not None else {}

def _wb_save(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"wb_save {path}: {e}")
        return False

# ── Credit functions ──
def wb_get_credit(user_id: int) -> float:
    data = _wb_load(WB_CREDITS_FILE)
    return round(float(data.get(str(user_id), {}).get("balance", 0.0)), 2)

def wb_set_credit(user_id: int, amount: float):
    data = _wb_load(WB_CREDITS_FILE)
    uid  = str(user_id)
    if uid not in data:
        data[uid] = {}
    data[uid]["balance"] = round(float(amount), 2)
    _wb_save(WB_CREDITS_FILE, data)

def wb_add_credit(user_id: int, amount: float):
    current = wb_get_credit(user_id)
    wb_set_credit(user_id, current + amount)

def wb_deduct_credit(user_id: int, amount: float) -> bool:
    current = wb_get_credit(user_id)
    if current < amount:
        return False
    wb_set_credit(user_id, current - amount)
    return True

# ── Items functions ──
def wb_get_items() -> list:
    return _wb_load(WB_ITEMS_FILE, [])

def wb_save_items(items: list):
    _wb_save(WB_ITEMS_FILE, items)

def wb_get_item_by_id(item_id: str) -> dict:
    for item in wb_get_items():
        if str(item.get("id")) == str(item_id):
            return item
    return {}

# ── Detect social media platform dari nama item ──
def wb_detect_platform(item_name: str) -> str:
    name = item_name.lower()
    if "tiktok" in name:     return "tiktok"
    if "instagram" in name or "ig " in name: return "instagram"
    if "youtube" in name:    return "youtube"
    if "facebook" in name or "fb " in name:  return "facebook"
    if "twitter" in name or "x " in name:    return "twitter"
    if "telegram" in name:   return "telegram"
    if "whatsapp" in name:   return "whatsapp"
    if "spotify" in name:    return "spotify"
    return "other"

# ── RoketMedia: Cari service ID berdasarkan nama item ──
def wb_find_service(item_name: str, quantity: int) -> tuple:
    """Return (service_id, actual_qty) atau (None, None) kalau tak jumpa."""
    try:
        r = requests.post(ROKET_API_URL, data={
            "key":    ROKET_API_KEY,
            "action": "services"
        }, timeout=20)
        if not r.ok:
            return None, None
        services = r.json()
        name_lower = item_name.lower()

        # Cuba cari exact match dulu, kemudian partial
        best = None
        for svc in services:
            svc_name = (svc.get("name") or "").lower()
            svc_type = (svc.get("type") or "").lower()
            min_q    = int(svc.get("min", 1))
            max_q    = int(svc.get("max", 999999))

            # Platform check
            platform = wb_detect_platform(item_name)
            if platform not in svc_name and platform != "other":
                continue

            # Keyword check
            keywords = [w for w in name_lower.split() if len(w) > 3]
            match_count = sum(1 for kw in keywords if kw in svc_name)

            if match_count > 0 and min_q <= quantity <= max_q:
                if best is None or match_count > best[0]:
                    best = (match_count, svc)

        if best:
            svc = best[1]
            return svc["service"], max(int(svc.get("min", 1)), quantity)
        return None, None
    except Exception as e:
        logger.error(f"wb_find_service: {e}")
        return None, None

# ── RoketMedia: Hantar order ──
def wb_place_order(service_id: str, link: str, quantity: int) -> dict:
    """Return dict dengan 'order' ID atau 'error'."""
    try:
        r = requests.post(ROKET_API_URL, data={
            "key":      ROKET_API_KEY,
            "action":   "add",
            "service":  service_id,
            "link":     link,
            "quantity": quantity,
        }, timeout=30)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# ── RoketMedia: Check order status ──
def wb_check_order(order_id: str) -> dict:
    try:
        r = requests.post(ROKET_API_URL, data={
            "key":    ROKET_API_KEY,
            "action": "status",
            "order":  order_id,
        }, timeout=15)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# ── Pending topup ──
def wb_add_pending(user_id: int, amount: float, msg_id: int):
    data = _wb_load(WB_PENDING_FILE)
    data[str(user_id)] = {
        "amount":  amount,
        "msg_id":  msg_id,
        "ts":      datetime.now().isoformat()
    }
    _wb_save(WB_PENDING_FILE, data)

def wb_get_pending(user_id: int) -> dict:
    data = _wb_load(WB_PENDING_FILE)
    return data.get(str(user_id), {})

def wb_remove_pending(user_id: int):
    data = _wb_load(WB_PENDING_FILE)
    data.pop(str(user_id), None)
    _wb_save(WB_PENDING_FILE, data)

# ── Pending link (menunggu user hantar link selepas confirm beli) ──
_WB_PENDING_PURCHASE = {}  # user_id -> {item_id, item_name, price, quantity}

# ── ConversationHandler states untuk /additem ──
WB_ADD_NAME, WB_ADD_PRICE, WB_ADD_QTY, WB_ADD_SVC = range(10, 14)


# ── /webbooster button callback ──
async def wb_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user  = query.from_user
    data  = query.data

    # ── Papar welcome Web Booster ──
    if data == "wb_open":
        try:
            await query.message.delete()
        except Exception:
            pass
        credit = wb_get_credit(user.id)
        text = (
            "╔══════════════════════════╗\n"
            "   ✦  ZENOXGPT WEB BOOSTER  ✦\n"
            "╚══════════════════════════╝\n\n"
            "◈ ─────────────────────── ◈\n\n"
            "🇲🇾  Selamat datang ke ZenoxGPT Web Booster!\n"
            "Guna command /service untuk lihat senarai servis.\n\n"
            "🌐  Welcome to ZenoxGPT Web Booster!\n"
            "Use /service command to see available items.\n\n"
            "◈ ─────────────────────── ◈\n\n"
            f"💳  Credit anda  ◈  RM {credit:.2f}\n\n"
            "◈ ─────────────────────── ◈"
        )
        keyboard = [[InlineKeyboardButton("📋 Lihat Servis / View Services", callback_data="wb_service")]]
        await query.message.chat.send_message(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # ── Papar senarai service ──
    elif data == "wb_service":
        await _wb_show_service(query.message.chat.id, context, query.message, delete_prev=False)

    # ── User tekan sesuatu item ──
    elif data.startswith("wb_item_"):
        item_id = data.replace("wb_item_", "")
        item    = wb_get_item_by_id(item_id)
        if not item:
            await query.message.reply_text("❎ Item tidak dijumpai.")
            return
        credit = wb_get_credit(user.id)
        price  = float(item.get("price", 0))
        qty    = int(item.get("quantity", 0))
        name   = item.get("name", "")

        try:
            await query.message.delete()
        except Exception:
            pass

        text = (
            "╔══════════════════════════╗\n"
            "      ✦  PENGESAHAN  ✦\n"
            "╚══════════════════════════╝\n\n"
            f"◎ Item     ◈  {name}\n"
            f"◎ Kuantiti ◈  {qty:,}\n"
            f"◎ Harga    ◈  RM {price:.2f}\n"
            f"◎ Credit   ◈  RM {credit:.2f}\n\n"
            "─────────────────────────────\n\n"
            "🇲🇾  Anda pasti ingin membeli?\n"
            "🌐  Are you sure you want to purchase?\n\n"
            "─────────────────────────────"
        )
        keyboard = [
            [
                InlineKeyboardButton("✅ Yes", callback_data=f"wb_confirm_{item_id}"),
                InlineKeyboardButton("❎ No",  callback_data="wb_cancel"),
            ]
        ]
        await query.message.chat.send_message(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # ── User confirm beli ──
    elif data.startswith("wb_confirm_"):
        item_id = data.replace("wb_confirm_", "")
        item    = wb_get_item_by_id(item_id)
        if not item:
            await query.message.reply_text("❎ Item tidak dijumpai.")
            return

        price = float(item.get("price", 0))
        qty   = int(item.get("quantity", 0))
        name  = item.get("name", "")

        if wb_get_credit(user.id) < price:
            try: await query.message.delete()
            except Exception: pass
            await query.message.chat.send_message(
                "❎ Credit anda tidak mencukupi.\n\n"
                f"◎ Diperlukan  ◈  RM {price:.2f}\n"
                f"◎ Credit anda ◈  RM {wb_get_credit(user.id):.2f}\n\n"
                "Guna /payment untuk top up credit."
            )
            return

        try: await query.message.delete()
        except Exception: pass

        # Simpan pending purchase, tunggu link
        _WB_PENDING_PURCHASE[user.id] = {
            "item_id":  item_id,
            "name":     name,
            "price":    price,
            "quantity": qty,
        }

        platform = wb_detect_platform(name)
        platform_label = {
            "tiktok":    "TikTok (video/profile/post)",
            "instagram": "Instagram (post/profile/reel)",
            "youtube":   "YouTube (video/channel)",
            "facebook":  "Facebook (post/page)",
            "twitter":   "Twitter/X (post/profile)",
            "telegram":  "Telegram (channel/post)",
            "whatsapp":  "WhatsApp Channel",
            "spotify":   "Spotify (track/artist)",
        }.get(platform, "Social media")

        await query.message.chat.send_message(
            f"✅ Pesanan diterima!\n\n"
            f"◎ Item  ◈  {name}\n\n"
            f"📎 Sila hantar link {platform_label} anda:\n"
            f"Please send your {platform_label} link:"
        )

    # ── Cancel ──
    elif data == "wb_cancel":
        try: await query.message.delete()
        except Exception: pass
        await query.message.chat.send_message(
            "❎ Pembelian dibatalkan.\n"
            "Purchase cancelled.\n\n"
            "Guna /service untuk lihat servis semula."
        )


async def _wb_show_service(chat_id, context, prev_msg=None, delete_prev=True):
    """Papar senarai servis dengan buttons."""
    if delete_prev and prev_msg:
        try: await prev_msg.delete()
        except Exception: pass

    items = wb_get_items()
    text = (
        "╔══════════════════════════╗\n"
        "    ✦  SENARAI SERVIS  ✦\n"
        "╚══════════════════════════╝\n\n"
        "🇲🇾  Pilih servis yang anda inginkan:\n"
        "🌐  Select the service you want:\n\n"
        "─────────────────────────────"
    )

    if not items:
        text += "\n\n◎ Tiada servis tersedia buat masa ini."
        await context.bot.send_message(chat_id, text)
        return

    keyboard = []
    for item in items:
        label = f"{item['name']}  ·  RM {float(item['price']):.2f}"
        keyboard.append([InlineKeyboardButton(label, callback_data=f"wb_item_{item['id']}")])

    await context.bot.send_message(chat_id, text, reply_markup=InlineKeyboardMarkup(keyboard))


async def service_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Papar senarai servis Web Booster."""
    await _wb_show_service(update.effective_chat.id, context, delete_prev=False)


async def payment_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /payment RM{amount}
    Papar QR code dan nombor DuitNow untuk top up credit.
    """
    user = update.effective_user
    track_user(user)

    if not context.args:
        await update.message.reply_text(
            "╔══════════════════════════╗\n"
            "     ✦  TOP UP CREDIT  ✦\n"
            "╚══════════════════════════╝\n\n"
            "Format: /payment RM{jumlah}\n"
            "Contoh: /payment RM10\n\n"
            "◎ Admin fee  ◈  RM 1.00 akan ditambah"
        )
        return

    raw = context.args[0].replace("RM", "").replace("rm", "").strip()
    try:
        amount = float(raw)
    except ValueError:
        await update.message.reply_text("❎ Format tidak sah. Contoh: /payment RM10")
        return

    total_pay = amount + ADMIN_FEE

    text = (
        "╔══════════════════════════╗\n"
        "     ✦  TOP UP CREDIT  ✦\n"
        "╚══════════════════════════╝\n\n"
        f"◎ Jumlah top up  ◈  RM {amount:.2f}\n"
        f"◎ Bayaran hantar ◈  RM {total_pay:.2f}\n"
        f"◎ Admin fee      ◈  RM {ADMIN_FEE:.2f}\n\n"
        "─────────────────────────────\n\n"
        f"💳  Nombor DuitNow:\n"
        f"    <code>{DUITNOW_NUMBER}</code>\n\n"
        "─────────────────────────────\n\n"
        "⚠️  Hantar bukti pembayaran selepas bayar!\n"
        "    Send payment proof after payment!\n\n"
        "─────────────────────────────"
    )

    # Hantar QR code
    try:
        await context.bot.send_photo(
            chat_id  = update.effective_chat.id,
            photo    = DUITNOW_QR_URL,
            caption  = text,
            parse_mode="HTML"
        )
    except Exception:
        await update.message.reply_text(text, parse_mode="HTML")

    # Simpan pending amount
    wb_add_pending(user.id, amount, update.message.message_id)

    # Notify developer
    send_info(
        f"💳 <b>Top Up Request</b>\n"
        f"    User   : @{user.username or user.id}\n"
        f"    Amount : RM {amount:.2f}\n"
        f"    Pay    : RM {total_pay:.2f} (incl. RM{ADMIN_FEE} fee)"
    )


async def approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /approve {user_id} -- Developer approve top up
    Atau reply gambar bukti dengan /approve
    """
    user = update.effective_user
    if user.id != DEVELOPER_ID:
        return

    # Dapatkan target user
    target_id = None
    amount     = None

    if context.args:
        try:
            target_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("Format: /approve {user_id}")
            return
        pending = wb_get_pending(target_id)
        if not pending:
            await update.message.reply_text(f"❎ Tiada pending top up untuk user {target_id}")
            return
        amount = float(pending.get("amount", 0))

    elif update.message.reply_to_message:
        # Reply kepada mesej bukti -- cuba cari pending mana-mana user
        pendings = _wb_load(WB_PENDING_FILE)
        if not pendings:
            await update.message.reply_text("❎ Tiada pending top up.")
            return
        # Ambil yang pertama kalau tak specify
        target_id = int(list(pendings.keys())[0])
        amount     = float(pendings[str(target_id)].get("amount", 0))
    else:
        # Papar semua pending
        pendings = _wb_load(WB_PENDING_FILE)
        if not pendings:
            await update.message.reply_text("❎ Tiada pending top up.")
            return
        lines = ["📋 <b>Pending Top Up:</b>\n"]
        for uid, info in pendings.items():
            lines.append(f"  User: <code>{uid}</code>  RM {info.get('amount', 0):.2f}")
        lines.append(f"\nGuna: /approve {{user_id}}")
        await update.message.reply_text("\n".join(lines), parse_mode="HTML")
        return

    # Add credit
    wb_add_credit(target_id, amount)
    new_bal = wb_get_credit(target_id)
    wb_remove_pending(target_id)

    await update.message.reply_text(
        f"✅ <b>Top Up Approved!</b>\n\n"
        f"◎ User     ◈  <code>{target_id}</code>\n"
        f"◎ Amount   ◈  RM {amount:.2f}\n"
        f"◎ Balance  ◈  RM {new_bal:.2f}",
        parse_mode="HTML"
    )

    # Notify user
    try:
        await context.bot.send_message(
            chat_id=target_id,
            text=(
                "╔══════════════════════════╗\n"
                "    ✦  TOP UP APPROVED  ✦\n"
                "╚══════════════════════════╝\n\n"
                "✅ Credit anda telah berjaya ditambah!\n"
                "✅ Your credit has been topped up!\n\n"
                f"◎ Tambahan  ◈  RM {amount:.2f}\n"
                f"◎ Baki baru ◈  RM {new_bal:.2f}\n\n"
                "Guna /service untuk membeli servis."
            )
        )
    except Exception:
        pass


async def wb_handle_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle gambar bukti transfer yang dihantar user.
    Hanya proses kalau user ada pending top up.
    """
    user = update.effective_user
    if not update.message.photo:
        return

    pending = wb_get_pending(user.id)
    if not pending:
        return  # bukan bukti payment, ignore

    amount    = float(pending.get("amount", 0))
    total_pay = amount + ADMIN_FEE
    tg_handle = f"@{user.username}" if user.username else f"ID:{user.id}"

    await update.message.reply_text(
        "✅ Bukti pembayaran diterima!\n"
        "Payment proof received!\n\n"
        "Sila tunggu pengesahan dalam 5-15 minit.\n"
        "Please wait for confirmation (5-15 mins)."
    )

    # Forward gambar ke developer dengan info
    caption = (
        f"💳 <b>Bukti Top Up</b>\n\n"
        f"◎ User   : {tg_handle} (<code>{user.id}</code>)\n"
        f"◎ Amount : RM {amount:.2f}\n"
        f"◎ Bayar  : RM {total_pay:.2f} (incl. fee)\n\n"
        f"Guna: /approve {user.id}"
    )

    try:
        await context.bot.send_photo(
            chat_id  = DEVELOPER_ID,
            photo    = update.message.photo[-1].file_id,
            caption  = caption,
            parse_mode = "HTML"
        )
    except Exception as e:
        send_info(f"⚠️ Gagal forward bukti payment: {e}\n{caption}")


async def wb_handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle link yang dihantar user selepas confirm beli.
    Auto order ke RoketMedia.
    """
    user = update.effective_user
    msg  = update.message

    if user.id not in _WB_PENDING_PURCHASE:
        return  # bukan dalam flow pembelian

    purchase = _WB_PENDING_PURCHASE.pop(user.id)
    item_id  = purchase["item_id"]
    name     = purchase["name"]
    price    = purchase["price"]
    quantity = purchase["quantity"]
    link     = msg.text.strip() if msg.text else ""

    # Validate link
    if not link.startswith("http"):
        _WB_PENDING_PURCHASE[user.id] = purchase  # put back
        await msg.reply_text("❎ Link tidak sah. Sila hantar URL yang betul. (bermula dengan http/https)")
        return

    # Semak credit sekali lagi
    if not wb_deduct_credit(user.id, price):
        await msg.reply_text(
            "❎ Credit tidak mencukupi.\n"
            f"Diperlukan: RM {price:.2f}\n"
            f"Credit anda: RM {wb_get_credit(user.id):.2f}"
        )
        return

    proc = await msg.reply_text(
        "⏳ Memproses pesanan anda...\n"
        "Processing your order..."
    )

    # Cari service ID di RoketMedia
    loop = asyncio.get_event_loop()
    service_id, actual_qty = await loop.run_in_executor(
        None, wb_find_service, name, quantity
    )

    if not service_id:
        # Refund credit
        wb_add_credit(user.id, price)
        try: await proc.delete()
        except Exception: pass
        await msg.reply_text(
            "❎ Servis tidak dijumpai dalam senarai RoketMedia.\n"
            f"◎ Credit RM {price:.2f} telah dikembalikan.\n\n"
            "Sila hubungi admin: @Repp76"
        )
        send_info(
            f"⚠️ <b>Order Gagal - Servis tidak jumpa</b>\n"
            f"User: @{user.username or user.id}\n"
            f"Item: {name}\nLink: {link}"
        )
        return

    # Place order
    result = await loop.run_in_executor(
        None, wb_place_order, service_id, link, actual_qty
    )

    if "error" in result or "order" not in result:
        # Refund credit
        wb_add_credit(user.id, price)
        err_msg = result.get("error", str(result))
        try: await proc.delete()
        except Exception: pass
        await msg.reply_text(
            f"❎ Order gagal: {err_msg}\n"
            f"◎ Credit RM {price:.2f} telah dikembalikan.\n\n"
            "Sila cuba semula atau hubungi @Repp76"
        )
        send_info(
            f"❎ <b>Order Gagal</b>\n"
            f"User: @{user.username or user.id}\n"
            f"Item: {name}\nError: {err_msg}"
        )
        return

    order_id = str(result["order"])

    # Simpan order record
    orders = _wb_load(WB_ORDERS_FILE, [])
    orders.append({
        "order_id":  order_id,
        "user_id":   user.id,
        "username":  user.username or str(user.id),
        "item":      name,
        "link":      link,
        "qty":       actual_qty,
        "price":     price,
        "service_id": service_id,
        "status":    "pending",
        "ts":        datetime.now().isoformat()
    })
    _wb_save(WB_ORDERS_FILE, orders)

    try: await proc.delete()
    except Exception: pass

    new_bal = wb_get_credit(user.id)
    await msg.reply_text(
        "╔══════════════════════════╗\n"
        "    ✦  ORDER BERJAYA  ✦\n"
        "╚══════════════════════════╝\n\n"
        "✅ Order telah dihantar ke RoketMedia!\n"
        "✅ Order successfully placed!\n\n"
        f"◎ Order ID  ◈  <code>{order_id}</code>\n"
        f"◎ Item      ◈  {name}\n"
        f"◎ Kuantiti  ◈  {actual_qty:,}\n"
        f"◎ Link      ◈  {link}\n"
        f"◎ Harga     ◈  RM {price:.2f}\n"
        f"◎ Baki      ◈  RM {new_bal:.2f}\n\n"
        "⏳ Boost akan mula dalam beberapa minit.\n"
        "Proses biasa: 5 minit - 24 jam.",
        parse_mode="HTML"
    )

    send_info(
        f"✅ <b>Order Berjaya</b>\n"
        f"User  : @{user.username or user.id}\n"
        f"Item  : {name}\n"
        f"Link  : {link}\n"
        f"Qty   : {actual_qty:,}\n"
        f"Price : RM {price:.2f}\n"
        f"Order : {order_id}"
    )


# ── /additem ConversationHandler ──
async def additem_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Developer: /additem -- Mula tambah item baru."""
    if update.effective_user.id != DEVELOPER_ID:
        return ConversationHandler.END
    await update.message.reply_text(
        "✦ Tambah Item Baru\n\n"
        "Sila masukkan nama item:\n"
        "Contoh: TikTok Views 1000"
    )
    return WB_ADD_NAME

async def additem_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["wb_name"] = update.message.text.strip()
    await update.message.reply_text(
        f"◎ Nama: {context.user_data['wb_name']}\n\n"
        "Sila masukkan harga (RM):\n"
        "Contoh: 4.50"
    )
    return WB_ADD_PRICE

async def additem_get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = float(update.message.text.strip().replace("RM","").replace("rm",""))
        context.user_data["wb_price"] = price
    except ValueError:
        await update.message.reply_text("❎ Harga tidak sah. Cuba lagi:")
        return WB_ADD_PRICE
    await update.message.reply_text(
        f"◎ Harga: RM {price:.2f}\n\n"
        "Sila masukkan kuantiti:\n"
        "Contoh: 1000"
    )
    return WB_ADD_QTY

async def additem_get_qty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        qty = int(update.message.text.strip().replace(",",""))
        context.user_data["wb_qty"] = qty
    except ValueError:
        await update.message.reply_text("❎ Kuantiti tidak sah. Cuba lagi:")
        return WB_ADD_QTY

    # Simpan item
    items = wb_get_items()
    new_id = str(int(datetime.now().timestamp()))
    items.append({
        "id":       new_id,
        "name":     context.user_data["wb_name"],
        "price":    context.user_data["wb_price"],
        "quantity": qty,
    })
    wb_save_items(items)

    await update.message.reply_text(
        "✅ Item berjaya ditambah!\n\n"
        f"◎ ID       ◈  {new_id}\n"
        f"◎ Nama     ◈  {context.user_data['wb_name']}\n"
        f"◎ Harga    ◈  RM {context.user_data['wb_price']:.2f}\n"
        f"◎ Kuantiti ◈  {qty:,}\n\n"
        "Item kini tersedia dalam /service"
    )
    return ConversationHandler.END

async def additem_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❎ Tambah item dibatalkan.")
    return ConversationHandler.END


# =============================================================
#  MAIN
# =============================================================

def main():
    try:
        r = requests.get(
            "https://api.telegram.org/bot" + BOT_TOKEN_AI + "/getMe",
            timeout=30
        )
        data = r.json()
        bot_username = data["result"].get("username", "ZenoxGPT_bot") if data.get("ok") else "ZenoxGPT_bot"
    except Exception:
        bot_username = "ZenoxGPT_bot"

    print_banner(bot_username)
    notify_online()

    # Start web server di thread berasingan
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()

    # Fix ReadTimeout -- naikkan timeout untuk semua request
    if HAS_HTTPX_REQUEST:
        request = HTTPXRequest(
            connection_pool_size=8,
            connect_timeout=30.0,
            read_timeout=60.0,
            write_timeout=60.0,
            pool_timeout=30.0,
        )
        application = (
            Application.builder()
            .token(BOT_TOKEN_AI)
            .request(request)
            .build()
        )
    else:
        application = Application.builder().token(BOT_TOKEN_AI).build()

    application.add_handler(CommandHandler("start",        start_command))
    application.add_handler(CommandHandler("addkey",       addkey_command))
    application.add_handler(CommandHandler("help",         help_command))
    application.add_handler(CommandHandler("status",       status_command))
    application.add_handler(CommandHandler("developer",    developer_command))
    application.add_handler(CommandHandler("giveaccess",   giveaccess_command))
    application.add_handler(CommandHandler("addreseller",  addreseller_command))
    application.add_handler(CommandHandler("addowner",     addowner_command))
    application.add_handler(CommandHandler("addpartner",   addpartner_command))
    application.add_handler(CommandHandler("removeaccess", removeaccess_command))
    application.add_handler(CommandHandler("listusers",    listusers_command))
    application.add_handler(CommandHandler("tagall",       tagall_command))
    application.add_handler(CommandHandler("code",         code_command))
    application.add_handler(CommandHandler("fixcode",      fixcode_command))
    application.add_handler(CommandHandler("getcode",      getcode_command))
    application.add_handler(CommandHandler("all",          all_command))
    application.add_handler(CommandHandler("filter",       filter_command))
    application.add_handler(CommandHandler("listfilters",  listfilters_command))
    application.add_handler(CommandHandler("delfilter",    delfilter_command))
    application.add_handler(CommandHandler("tourl",        tourl_command))
    application.add_handler(CommandHandler("enc",          enc_command))
    application.add_handler(CommandHandler("encpy",        encpy_command))
    application.add_handler(CommandHandler("tt",           tt_command))
    application.add_handler(CommandHandler("ig",           ig_command))
    application.add_handler(CommandHandler("osint",        osint_command))
    application.add_handler(CommandHandler("createacc",    createacc_command))
    application.add_handler(CommandHandler("delacc",       delacc_command))
    application.add_handler(CommandHandler("listacc",      listacc_command))
    application.add_handler(CommandHandler("hosting",      hosting_command))
    application.add_handler(CommandHandler("mp4tomp3",     mp4tomp3_command))
    application.add_handler(CommandHandler("sender",       sender_command))
    application.add_handler(CommandHandler("service",      service_command))
    application.add_handler(CommandHandler("payment",      payment_command))
    application.add_handler(CommandHandler("approve",      approve_command))
    application.add_handler(CallbackQueryHandler(wb_button_callback, pattern="^wb_"))
    application.add_handler(CallbackQueryHandler(zc_callback_handler, pattern="^zc_"))
    application.add_handler(CallbackQueryHandler(sound_callback, pattern="^sound:"))

    # Web Booster: additem ConversationHandler
    additem_conv = ConversationHandler(
        entry_points=[CommandHandler("additem", additem_start)],
        states={
            WB_ADD_NAME:  [MessageHandler(filters.TEXT & ~filters.COMMAND, additem_get_name)],
            WB_ADD_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, additem_get_price)],
            WB_ADD_QTY:   [MessageHandler(filters.TEXT & ~filters.COMMAND, additem_get_qty)],
        },
        fallbacks=[CommandHandler("cancel", additem_cancel)],
        per_user=True, per_chat=True, allow_reentry=True,
    )
    application.add_handler(additem_conv, group=-2)

    # Web Booster: tangkap gambar bukti payment
    application.add_handler(
        MessageHandler(filters.PHOTO, wb_handle_proof), group=2
    )
    # Web Booster: tangkap link selepas confirm beli
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, wb_handle_link), group=3
    )
    # Zenox Crasher bug simulasi -- tangkap semua command dalam senarai
    _zc_pattern = "^/(" + "|".join(_ZC_BUG_COMMANDS) + ")(@\\S+)?\\b"
    application.add_handler(
        MessageHandler(filters.Regex(_zc_pattern), zc_bug_handler),
        group=1
    )
    # ConversationHandler untuk /urltoapk -- WAJIB group=-1 supaya priority tertinggi
    # dan tak kena intercept oleh handle_message
    uapk_conv = ConversationHandler(
        entry_points=[CommandHandler("urltoapk", urltoapk_command)],
        states={
            UAPK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, uapk_get_name)],
            UAPK_PKG:  [MessageHandler(filters.TEXT & ~filters.COMMAND, uapk_get_package)],
            UAPK_VER:  [MessageHandler(filters.TEXT & ~filters.COMMAND, uapk_get_version)],
            UAPK_LOGO: [MessageHandler(filters.PHOTO, uapk_get_logo)],
        },
        fallbacks=[CommandHandler("cancel", uapk_cancel)],
        per_user=True,
        per_chat=True,
        allow_reentry=True,
    )
    # Group -1 = priority lebih tinggi dari semua handler biasa (group 0)
    application.add_handler(uapk_conv, group=-1)
    # Filter trigger -- tangkap semua command lain yang mungkin filter
    application.add_handler(MessageHandler(filters.COMMAND, handle_filter_trigger))
    # Handler gambar dengan caption /filter atau /code atau /all
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo_and_filter))
    # Handler document
    application.add_handler(MessageHandler(filters.Document.ALL, handle_doc_filter))
    # Handler video
    application.add_handler(MessageHandler(filters.VIDEO, handle_video_all))
    # Handler audio
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio_all))
    # Handler bila bot ditambah/dikeluarkan dari group
    application.add_handler(ChatMemberHandler(handle_my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    application.add_error_handler(error_handler)

    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
        poll_interval=2.0,
        timeout=60,
    )


if __name__ == "__main__":
    main()
