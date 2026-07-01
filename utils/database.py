import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables and seed default admin if not present."""
    conn = get_connection()
    c = conn.cursor()

    # ── users ──────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name     TEXT    NOT NULL,
            email         TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            profile_image TEXT    DEFAULT NULL,
            is_admin      INTEGER DEFAULT 0,
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── predictions ────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            prediction  TEXT    NOT NULL,
            confidence  REAL    NOT NULL,
            risk_level  TEXT    NOT NULL,
            features    TEXT    DEFAULT NULL,
            created_at  TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # ── reports ────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            report_file TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    conn.commit()

    # ── Seed admin ─────────────────────────────────────────────────────────
    existing = c.execute("SELECT id FROM users WHERE email='admin@oncosight.ai'").fetchone()
    if not existing:
        import bcrypt
        pw_hash = bcrypt.hashpw(b"Admin@123", bcrypt.gensalt()).decode()
        c.execute(
            "INSERT INTO users (full_name, email, password_hash, is_admin) VALUES (?,?,?,1)",
            ("System Admin", "admin@oncosight.ai", pw_hash)
        )
        conn.commit()

    conn.close()


# ── CRUD helpers ───────────────────────────────────────────────────────────

def create_user(full_name: str, email: str, password_hash: str) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (full_name, email, password_hash) VALUES (?,?,?)",
        (full_name, email, password_hash)
    )
    conn.commit()
    uid = c.lastrowid
    conn.close()
    return uid


def get_user_by_email(email: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(uid: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_user_profile(uid: int, full_name: str, email: str):
    conn = get_connection()
    conn.execute(
        "UPDATE users SET full_name=?, email=? WHERE id=?",
        (full_name, email, uid)
    )
    conn.commit()
    conn.close()


def update_user_password(uid: int, new_hash: str):
    conn = get_connection()
    conn.execute("UPDATE users SET password_hash=? WHERE id=?", (new_hash, uid))
    conn.commit()
    conn.close()


def update_profile_image(uid: int, path: str):
    conn = get_connection()
    conn.execute("UPDATE users SET profile_image=? WHERE id=?", (path, uid))
    conn.commit()
    conn.close()


def save_prediction(user_id: int, prediction: str, confidence: float,
                    risk_level: str, features_json: str = None):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO predictions (user_id, prediction, confidence, risk_level, features) VALUES (?,?,?,?,?)",
        (user_id, prediction, confidence, risk_level, features_json)
    )
    conn.commit()
    pid = c.lastrowid
    conn.close()
    return pid


def get_user_predictions(user_id: int, limit: int = 500):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM predictions WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_predictions(limit: int = 1000):
    conn = get_connection()
    rows = conn.execute(
        """SELECT p.*, u.full_name, u.email
           FROM predictions p JOIN users u ON p.user_id=u.id
           ORDER BY p.created_at DESC LIMIT ?""",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_users():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, full_name, email, is_admin, created_at FROM users ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_user(uid: int):
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE id=?", (uid,))
    conn.commit()
    conn.close()


def save_report(user_id: int, report_file: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO reports (user_id, report_file) VALUES (?,?)",
        (user_id, report_file)
    )
    conn.commit()
    rid = c.lastrowid
    conn.close()
    return rid


def get_user_reports(user_id: int):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM reports WHERE user_id=? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats():
    conn = get_connection()
    total_users = conn.execute("SELECT COUNT(*) FROM users WHERE is_admin=0").fetchone()[0]
    total_preds = conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
    malignant   = conn.execute("SELECT COUNT(*) FROM predictions WHERE prediction='Malignant'").fetchone()[0]
    benign      = conn.execute("SELECT COUNT(*) FROM predictions WHERE prediction='Benign'").fetchone()[0]
    conn.close()
    return {
        "total_users": total_users,
        "total_predictions": total_preds,
        "malignant": malignant,
        "benign": benign,
    }
