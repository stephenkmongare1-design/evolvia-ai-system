"""
Evolvia Africa - Database Layer
SQLite for simplicity and easy deployment. Can be swapped to PostgreSQL later.
"""

import sqlite3
import secrets
from datetime import datetime
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
import os

try:
    import bcrypt
except ImportError:  # pragma: no cover
    bcrypt = None

DB_PATH = os.getenv("EVOLVIA_DB_PATH", "evolvia.db")
DEFAULT_ADMIN_USERNAME = os.getenv("EVOLVIA_ADMIN_USER", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("EVOLVIA_ADMIN_PASSWORD", "evolvia2026")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create all tables if they do not exist."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Schools / Principals
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                principal_name TEXT NOT NULL,
                phone TEXT NOT NULL UNIQUE,
                student_count INTEGER DEFAULT 0,
                location TEXT,
                status TEXT DEFAULT 'lead',  -- lead, demo_booked, training_done, active, inactive
                monthly_fee INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Trainers (real people)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trainers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL UNIQUE,
                email TEXT,
                location TEXT,
                active INTEGER DEFAULT 1,
                total_earnings INTEGER DEFAULT 0,
                trainings_completed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Bookings / Training sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school_id INTEGER NOT NULL,
                demo_date TEXT,
                training_date TEXT,
                location TEXT,
                assigned_trainer_id INTEGER,
                status TEXT DEFAULT 'pending',  -- pending, demo_scheduled, training_scheduled, completed, cancelled
                feedback TEXT,
                feedback_rating INTEGER,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (school_id) REFERENCES schools (id),
                FOREIGN KEY (assigned_trainer_id) REFERENCES trainers (id)
            )
        """)

        # Payments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                period TEXT,  -- e.g. "2026-08" or "First Term"
                status TEXT DEFAULT 'pending',  -- pending, paid, overdue
                payment_method TEXT,
                transaction_ref TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                paid_at TEXT,
                FOREIGN KEY (school_id) REFERENCES schools (id)
            )
        """)

        # Trainer payments / payouts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trainer_payouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trainer_id INTEGER NOT NULL,
                booking_id INTEGER,
                base_pay INTEGER DEFAULT 250,
                transport INTEGER DEFAULT 0,
                total INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',  -- pending, approved, paid
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                paid_at TEXT,
                FOREIGN KEY (trainer_id) REFERENCES trainers (id),
                FOREIGN KEY (booking_id) REFERENCES bookings (id)
            )
        """)

        # Agent activity log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                related_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Admin / staff users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'admin',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Generic key/value settings (WhatsApp link status, tokens, etc.)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

    _ensure_default_admin()


# ========== AUTH ==========

def _hash_password(password: str) -> str:
    if bcrypt:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    # Fallback (dev only, bcrypt should always be installed per requirements.txt)
    import hashlib
    return "plain$" + hashlib.sha256(password.encode()).hexdigest()


def _check_password(password: str, password_hash: str) -> bool:
    if password_hash.startswith("plain$"):
        import hashlib
        return password_hash == "plain$" + hashlib.sha256(password.encode()).hexdigest()
    if bcrypt:
        try:
            return bcrypt.checkpw(password.encode(), password_hash.encode())
        except ValueError:
            return False
    return False


def _ensure_default_admin():
    """Create a default admin account on first run so the dashboard is never locked out."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as c FROM users")
        if cursor.fetchone()["c"] == 0:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')",
                (DEFAULT_ADMIN_USERNAME, _hash_password(DEFAULT_ADMIN_PASSWORD)),
            )


def verify_admin(username: str, password: str) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if not row:
            return False
        return _check_password(password, row["password_hash"])


def change_admin_password(username: str, new_password: str) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE username = ?",
            (_hash_password(new_password), username),
        )
        return cursor.rowcount > 0


def create_admin_user(username: str, password: str, role: str = "admin") -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, _hash_password(password), role),
            )
            return True
        except sqlite3.IntegrityError:
            return False


# ========== SETTINGS / WHATSAPP LINK STATE ==========

def set_setting(key: str, value: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
        """, (key, value, datetime.now().isoformat()))


def get_setting(key: str, default: str = None) -> Optional[str]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else default


def new_pairing_token() -> str:
    token = secrets.token_urlsafe(16)
    set_setting("wa_pairing_token", token)
    return token


# ========== SCHOOLS ==========

def create_school(name: str, principal_name: str, phone: str, student_count: int = 0, location: str = None) -> int:
    fee = calculate_monthly_fee(student_count)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO schools (name, principal_name, phone, student_count, location, monthly_fee, status)
            VALUES (?, ?, ?, ?, ?, ?, 'lead')
        """, (name, principal_name, phone, student_count, location, fee))
        return cursor.lastrowid


def get_school(school_id: int) -> Optional[Dict]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM schools WHERE id = ?", (school_id,)).fetchone()
        return dict(row) if row else None


def get_school_by_phone(phone: str) -> Optional[Dict]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM schools WHERE phone = ?", (phone,)).fetchone()
        return dict(row) if row else None


def list_schools(status: str = None) -> List[Dict]:
    with get_db() as conn:
        if status:
            rows = conn.execute("SELECT * FROM schools WHERE status = ? ORDER BY created_at DESC", (status,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM schools ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]


def update_school_status(school_id: int, status: str):
    with get_db() as conn:
        conn.execute("""
            UPDATE schools SET status = ?, updated_at = ? WHERE id = ?
        """, (status, datetime.now().isoformat(), school_id))


def update_student_count(school_id: int, student_count: int):
    fee = calculate_monthly_fee(student_count)
    with get_db() as conn:
        conn.execute("""
            UPDATE schools SET student_count = ?, monthly_fee = ?, updated_at = ? WHERE id = ?
        """, (student_count, fee, datetime.now().isoformat(), school_id))


# ========== TRAINERS ==========

def create_trainer(name: str, phone: str, email: str = None, location: str = None) -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trainers (name, phone, email, location)
            VALUES (?, ?, ?, ?)
        """, (name, phone, email, location))
        return cursor.lastrowid


def get_trainer(trainer_id: int) -> Optional[Dict]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM trainers WHERE id = ?", (trainer_id,)).fetchone()
        return dict(row) if row else None


def list_trainers(active_only: bool = True) -> List[Dict]:
    with get_db() as conn:
        if active_only:
            rows = conn.execute("SELECT * FROM trainers WHERE active = 1 ORDER BY name").fetchall()
        else:
            rows = conn.execute("SELECT * FROM trainers ORDER BY name").fetchall()
        return [dict(r) for r in rows]


def update_trainer_earnings(trainer_id: int, amount: int):
    with get_db() as conn:
        conn.execute("""
            UPDATE trainers 
            SET total_earnings = total_earnings + ?, 
                trainings_completed = trainings_completed + 1
            WHERE id = ?
        """, (amount, trainer_id))


# ========== BOOKINGS ==========

def create_booking(school_id: int, demo_date: str = None, training_date: str = None, location: str = None) -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bookings (school_id, demo_date, training_date, location, status)
            VALUES (?, ?, ?, ?, 'pending')
        """, (school_id, demo_date, training_date, location))
        return cursor.lastrowid


def assign_trainer(booking_id: int, trainer_id: int):
    with get_db() as conn:
        conn.execute("""
            UPDATE bookings 
            SET assigned_trainer_id = ?, status = 'training_scheduled', updated_at = ?
            WHERE id = ?
        """, (trainer_id, datetime.now().isoformat(), booking_id))


def complete_training(booking_id: int, feedback: str = None, rating: int = None):
    with get_db() as conn:
        conn.execute("""
            UPDATE bookings 
            SET status = 'completed', feedback = ?, feedback_rating = ?, updated_at = ?
            WHERE id = ?
        """, (feedback, rating, datetime.now().isoformat(), booking_id))


def get_booking(booking_id: int) -> Optional[Dict]:
    with get_db() as conn:
        row = conn.execute("""
            SELECT b.*, s.name as school_name, s.principal_name, s.phone as school_phone,
                   t.name as trainer_name, t.phone as trainer_phone
            FROM bookings b
            LEFT JOIN schools s ON b.school_id = s.id
            LEFT JOIN trainers t ON b.assigned_trainer_id = t.id
            WHERE b.id = ?
        """, (booking_id,)).fetchone()
        return dict(row) if row else None


def get_booking_awaiting_feedback(school_id: int) -> Optional[Dict]:
    """Most recent training for this school that is done but has no feedback yet."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.*, s.name as school_name, s.principal_name, t.name as trainer_name
            FROM bookings b
            LEFT JOIN schools s ON b.school_id = s.id
            LEFT JOIN trainers t ON b.assigned_trainer_id = t.id
            WHERE b.school_id = ? AND b.status = 'completed' AND b.feedback IS NULL
            ORDER BY b.id DESC LIMIT 1
        """, (school_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def list_bookings(status: str = None) -> List[Dict]:
    with get_db() as conn:
        query = """
            SELECT b.*, s.name as school_name, s.principal_name, t.name as trainer_name
            FROM bookings b
            LEFT JOIN schools s ON b.school_id = s.id
            LEFT JOIN trainers t ON b.assigned_trainer_id = t.id
        """
        if status:
            query += " WHERE b.status = ?"
            rows = conn.execute(query + " ORDER BY b.created_at DESC", (status,)).fetchall()
        else:
            rows = conn.execute(query + " ORDER BY b.created_at DESC").fetchall()
        return [dict(r) for r in rows]


# ========== PAYMENTS ==========

def create_payment(school_id: int, amount: int, period: str, notes: str = None) -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO payments (school_id, amount, period, status, notes)
            VALUES (?, ?, ?, 'pending', ?)
        """, (school_id, amount, period, notes))
        return cursor.lastrowid


def mark_payment_paid(payment_id: int, method: str, ref: str = None):
    with get_db() as conn:
        conn.execute("""
            UPDATE payments 
            SET status = 'paid', payment_method = ?, transaction_ref = ?, paid_at = ?
            WHERE id = ?
        """, (method, ref, datetime.now().isoformat(), payment_id))


def list_payments(status: str = None) -> List[Dict]:
    with get_db() as conn:
        query = """
            SELECT p.*, s.name as school_name, s.principal_name
            FROM payments p
            JOIN schools s ON p.school_id = s.id
        """
        if status:
            rows = conn.execute(query + " WHERE p.status = ? ORDER BY p.created_at DESC", (status,)).fetchall()
        else:
            rows = conn.execute(query + " ORDER BY p.created_at DESC").fetchall()
        return [dict(r) for r in rows]


# ========== TRAINER PAYOUTS ==========

def create_trainer_payout(trainer_id: int, booking_id: int, transport: bool = True) -> int:
    base = 250
    transport_pay = 500 if transport else 0
    total = base + transport_pay
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trainer_payouts (trainer_id, booking_id, base_pay, transport, total, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (trainer_id, booking_id, base, transport_pay, total))
        return cursor.lastrowid


def approve_payout(payout_id: int):
    with get_db() as conn:
        conn.execute("""
            UPDATE trainer_payouts SET status = 'approved' WHERE id = ?
        """, (payout_id,))


def mark_payout_paid(payout_id: int):
    with get_db() as conn:
        conn.execute("""
            UPDATE trainer_payouts SET status = 'paid', paid_at = ? WHERE id = ?
        """, (datetime.now().isoformat(), payout_id))


def list_payouts(status: str = None) -> List[Dict]:
    with get_db() as conn:
        query = """
            SELECT tp.*, t.name as trainer_name, t.phone as trainer_phone,
                   b.id as booking_ref, s.name as school_name
            FROM trainer_payouts tp
            JOIN trainers t ON tp.trainer_id = t.id
            LEFT JOIN bookings b ON tp.booking_id = b.id
            LEFT JOIN schools s ON b.school_id = s.id
        """
        if status:
            rows = conn.execute(query + " WHERE tp.status = ? ORDER BY tp.created_at DESC", (status,)).fetchall()
        else:
            rows = conn.execute(query + " ORDER BY tp.created_at DESC").fetchall()
        return [dict(r) for r in rows]


# ========== AGENT LOGS ==========

def log_agent_action(agent_name: str, action: str, details: str = None, related_id: int = None):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO agent_logs (agent_name, action, details, related_id)
            VALUES (?, ?, ?, ?)
        """, (agent_name, action, details, related_id))


def get_recent_logs(limit: int = 50) -> List[Dict]:
    with get_db() as conn:
        rows = conn.execute("""
            SELECT * FROM agent_logs ORDER BY created_at DESC LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]


# ========== PRICING ==========

def calculate_monthly_fee(student_count: int) -> int:
    """Official Evolvia pricing rules."""
    if student_count <= 300:
        return 2500
    elif student_count <= 600:
        return 5000
    elif student_count <= 1000:
        return 7500
    else:
        return 10000


def get_dashboard_stats() -> Dict[str, Any]:
    with get_db() as conn:
        schools = conn.execute("SELECT COUNT(*) as c FROM schools").fetchone()["c"]
        active_schools = conn.execute("SELECT COUNT(*) as c FROM schools WHERE status = 'active'").fetchone()["c"]
        trainers = conn.execute("SELECT COUNT(*) as c FROM trainers WHERE active = 1").fetchone()["c"]
        pending_bookings = conn.execute("SELECT COUNT(*) as c FROM bookings WHERE status IN ('pending', 'demo_scheduled', 'training_scheduled')").fetchone()["c"]
        pending_payments = conn.execute("SELECT COUNT(*) as c FROM payments WHERE status = 'pending'").fetchone()["c"]
        pending_payouts = conn.execute("SELECT COUNT(*) as c FROM trainer_payouts WHERE status = 'pending'").fetchone()["c"]
        total_revenue = conn.execute("SELECT COALESCE(SUM(amount), 0) as s FROM payments WHERE status = 'paid'").fetchone()["s"]

        return {
            "total_schools": schools,
            "active_schools": active_schools,
            "active_trainers": trainers,
            "pending_bookings": pending_bookings,
            "pending_payments": pending_payments,
            "pending_payouts": pending_payouts,
            "total_revenue": total_revenue
        }
