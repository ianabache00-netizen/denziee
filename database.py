import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Optional

# Philippine Time (UTC+8)
PHT = timezone(timedelta(hours=8))

DB_PATH = "database.db"


def now_pht() -> datetime:
    return datetime.now(PHT)


def fmt_pht(dt: Optional[datetime]) -> str:
    if dt is None:
        return "No Expiry"
    return dt.astimezone(PHT).strftime("%Y-%m-%d %I:%M:%S %p PHT")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Keys table
    c.execute("""
        CREATE TABLE IF NOT EXISTS keys (
            key TEXT PRIMARY KEY,
            tier TEXT NOT NULL,
            duration TEXT NOT NULL,
            created_at TEXT NOT NULL,
            redeemed_by INTEGER,
            redeemed_at TEXT,
            expires_at TEXT,
            active INTEGER DEFAULT 1
        )
    """)

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            tier TEXT,
            key_used TEXT,
            expires_at TEXT,
            last_generate TEXT
        )
    """)

    # History table
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            filename TEXT,
            lines INTEGER,
            generated_at TEXT
        )
    """)

    # Feedback table
    c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            message TEXT,
            created_at TEXT
        )
    """)

    # Vouches table
    c.execute("""
        CREATE TABLE IF NOT EXISTS vouches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER,
            seller_name TEXT,
            from_user INTEGER,
            from_name TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


# ==========================================
# KEY OPERATIONS
# ==========================================
def add_key(key: str, tier: str, duration: str, created_by: int = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO keys (key, tier, duration, created_at) VALUES (?, ?, ?, ?)",
        (key, tier, duration, now_pht().isoformat()),
    )
    conn.commit()
    conn.close()


def get_key(key: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM keys WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row


def redeem_key(key: str, user_id: int) -> tuple[bool, str]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM keys WHERE key = ?", (key,))
    row = c.fetchone()

    if not row:
        conn.close()
        return False, "❌ Invalid key."

    key_str, tier, duration, created_at, redeemed_by, redeemed_at, expires_at, active = row

    if not active:
        conn.close()
        return False, "❌ This key has been revoked."

    if redeemed_by is not None:
        conn.close()
        return False, "❌ This key is already redeemed."

    # Calculate expiry
    from config import DURATIONS
    dur_cfg = DURATIONS.get(duration)
    if dur_cfg and dur_cfg["seconds"] is not None:
        exp_dt = now_pht() + timedelta(seconds=dur_cfg["seconds"])
        exp_iso = exp_dt.isoformat()
    else:
        exp_iso = None

    c.execute(
        "UPDATE keys SET redeemed_by = ?, redeemed_at = ?, expires_at = ? WHERE key = ?",
        (user_id, now_pht().isoformat(), exp_iso, key),
    )

    c.execute("""
        INSERT INTO users (user_id, tier, key_used, expires_at, last_generate)
        VALUES (?, ?, ?, ?, NULL)
        ON CONFLICT(user_id) DO UPDATE SET
            tier = excluded.tier,
            key_used = excluded.key_used,
            expires_at = excluded.expires_at
    """, (user_id, tier, key, exp_iso))

    conn.commit()
    conn.close()
    return True, "✅ Key redeemed successfully!"


def get_user(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row


def update_last_generate(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET last_generate = ? WHERE user_id = ?",
              (now_pht().isoformat(), user_id))
    conn.commit()
    conn.close()


def revoke_user(user_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    rows = c.fetchall()
    conn.close()
    return rows


def get_all_keys():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM keys ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def revoke_key(key: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE keys SET active = 0 WHERE key = ?", (key,))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected > 0


# ==========================================
# HISTORY
# ==========================================
def add_history(user_id: int, filename: str, lines: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO history (user_id, filename, lines, generated_at) VALUES (?, ?, ?, ?)",
        (user_id, filename, lines, now_pht().isoformat()),
    )
    conn.commit()
    conn.close()


def get_history(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM history WHERE user_id = ? ORDER BY generated_at DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows


def get_all_history():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY generated_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows


# ==========================================
# FEEDBACK
# ==========================================
def add_feedback(user_id: int, username: str, message: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO feedback (user_id, username, message, created_at) VALUES (?, ?, ?, ?)",
        (user_id, username, message, now_pht().isoformat()),
    )
    conn.commit()
    conn.close()


# ==========================================
# VOUCHES
# ==========================================
def add_vouch(seller_id: int, seller_name: str, from_id: int, from_name: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO vouches (seller_id, seller_name, from_user, from_name, created_at) VALUES (?, ?, ?, ?, ?)",
        (seller_id, seller_name, from_id, from_name, now_pht().isoformat()),
    )
    conn.commit()
    conn.close()


def get_vouches(seller_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM vouches WHERE seller_id = ? ORDER BY created_at DESC", (seller_id,))
    rows = c.fetchall()
    conn.close()
    return rows
