import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# BOT CONFIG
# ==========================================
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "0"))
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

# ==========================================
# TIER CONFIG
# ==========================================
TIERS = {
    "Platinum": {
        "lines_per_file": 2500,
        "cooldown": 30,        # seconds
        "no_expiry": True,
        "emoji": "💎",
        "color": 0x00BFFF,
    },
    "Premium": {
        "lines_per_file": 5000,
        "cooldown": 15,
        "no_expiry": True,
        "emoji": "👑",
        "color": 0xFFD700,
    },
}

# ==========================================
# KEY DURATION CONFIG
# ==========================================
DURATIONS = {
    "30m":   {"seconds": 30 * 60,           "label": "30 Minutes"},
    "1h":    {"seconds": 60 * 60,           "label": "1 Hour"},
    "3h":    {"seconds": 3 * 60 * 60,       "label": "3 Hours"},
    "7d":    {"seconds": 7 * 24 * 60 * 60,  "label": "7 Days"},
    "1mo":   {"seconds": 30 * 24 * 60 * 60, "label": "1 Month"},
    "lifetime": {"seconds": None,           "label": "Lifetime (No Expiry)"},
}

# ==========================================
# PATHS
# ==========================================
STOCK_DIR = "stock"
DB_PATH = "database.db"
