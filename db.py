"""
db.py — SwasthyaSetu AI
Dual-database layer: PostgreSQL (primary) with automatic SQLite fallback.
Configuration via .env file (DATABASE_URL / PGHOST / PGUSER / PGPASSWORD / PGDATABASE).
If PostgreSQL is unavailable, transparently falls back to local swasthyasetu.db (SQLite).
"""

import sqlite3
import json
import os
import re
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass

# ─────────────────────────────────────────────────────────────────
# Database backend detection
# ─────────────────────────────────────────────────────────────────

SQLITE_PATH = os.path.join(os.path.dirname(__file__), "swasthyasetu.db")
_DB_TYPE = os.environ.get("DB_TYPE", "sqlite").strip().lower()
_PG_AVAILABLE = False
_PG_CONN_PARAMS = {}

_db_url = os.environ.get("DATABASE_URL")
if _DB_TYPE == "postgres" or _db_url:
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        if _db_url:
            # Fix Render postgres:// URI prefix for psycopg2 compatibility
            if _db_url.startswith("postgres://"):
                _db_url = _db_url.replace("postgres://", "postgresql://", 1)
            _test = psycopg2.connect(_db_url, connect_timeout=5)
            _test.close()
            _PG_CONN_PARAMS = {"dsn": _db_url}
        else:
            _PG_CONN_PARAMS = {
                "host": os.environ.get("PGHOST", "localhost"),
                "port": int(os.environ.get("PGPORT", "5432")),
                "dbname": os.environ.get("PGDATABASE", "swasthyasetu"),
                "user": os.environ.get("PGUSER", "postgres"),
                "password": os.environ.get("PGPASSWORD", ""),
            }
            _test = psycopg2.connect(**_PG_CONN_PARAMS, connect_timeout=3)
            _test.close()
        _PG_AVAILABLE = True
        print("[db] OK Using PostgreSQL backend")
    except Exception as _pg_err:
        print(f"[db] WARN PostgreSQL unavailable ({_pg_err}). Falling back to SQLite.")
        _PG_AVAILABLE = False
else:
    print("[db] INFO Using SQLite backend (DB_TYPE not set to 'postgres')")


# ─────────────────────────────────────────────────────────────────
# Unified connection helpers
# ─────────────────────────────────────────────────────────────────

def _pg_conn():
    """Open and return a psycopg2 connection."""
    import psycopg2
    if "dsn" in _PG_CONN_PARAMS:
        conn = psycopg2.connect(_PG_CONN_PARAMS["dsn"])
    else:
        conn = psycopg2.connect(**_PG_CONN_PARAMS)
    conn.autocommit = False
    return conn


def _sqlite_conn():
    """Open and return a sqlite3 connection."""
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def get_db():
    """Return a connection object appropriate for the current backend."""
    if _PG_AVAILABLE:
        return _pg_conn()
    return _sqlite_conn()


def _adapt_sql(sql, params=None):
    """
    Convert SQLite-style SQL to PostgreSQL-style:
      - ? → %s  (positional)
      - :name → %(name)s  (named)
      - datetime('now') → NOW()
    Returns (sql, params) tuple ready for psycopg2.
    """
    if not _PG_AVAILABLE:
        return sql, params  # SQLite uses the original format

    # Replace SQLite datetime expressions
    sql = re.sub(r"datetime\('now'\)", "NOW()", sql, flags=re.IGNORECASE)
    # AUTOINCREMENT not supported in Postgres (handled via SERIAL in DDL)
    sql = re.sub(r"\bAUTOINCREMENT\b", "", sql, flags=re.IGNORECASE)
    # INTEGER PRIMARY KEY → handled at table creation time (SERIAL)

    if params is None:
        return sql, params
    if isinstance(params, dict):
        # :name → %(name)s
        sql = re.sub(r":([a-zA-Z_][a-zA-Z0-9_]*)", r"%(\1)s", sql)
        return sql, params
    else:
        # ? → %s (positional)
        sql = sql.replace("?", "%s")
        return sql, tuple(params)


def _fetchall(cur):
    """Return all rows as list of dicts, regardless of backend."""
    rows = cur.fetchall()
    result = []
    for r in rows:
        if isinstance(r, dict):
            result.append(r)
        elif hasattr(r, 'keys'):  # sqlite3.Row
            result.append(dict(r))
        else:  # plain tuple from psycopg2 regular cursor
            cols = [d[0] for d in cur.description]
            result.append(dict(zip(cols, r)))
    return result


def _fetchone(cur):
    """Return one row as dict, or None."""
    row = cur.fetchone()
    if row is None:
        return None
    if isinstance(row, dict):
        return row
    if hasattr(row, 'keys'):  # sqlite3.Row
        return dict(row)
    # plain tuple from psycopg2 regular cursor
    cols = [d[0] for d in cur.description]
    return dict(zip(cols, row))


def _execute(conn, sql, params=None):
    """Execute a statement and return the cursor (handles both backends)."""
    sql_a, params_a = _adapt_sql(sql, params)
    if _PG_AVAILABLE:
        from psycopg2.extras import RealDictCursor
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if params_a is None:
            cur.execute(sql_a)
        else:
            cur.execute(sql_a, params_a)
        return cur
    else:
        if params_a is None:
            return conn.execute(sql_a)
        return conn.execute(sql_a, params_a)


def _commit(conn):
    conn.commit()


def _close(conn):
    conn.close()


# ─────────────────────────────────────────────────────────────────
# Database Initialisation
# ─────────────────────────────────────────────────────────────────

def init_db():
    """Create tables if they don't exist (runs for both backends on startup)."""
    if _PG_AVAILABLE:
        _init_postgres()
    else:
        _init_sqlite()


def _init_postgres():
    """Create PostgreSQL tables and seed default data if needed."""
    conn = _pg_conn()
    try:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS schemes (
                id                  SERIAL PRIMARY KEY,
                name                TEXT NOT NULL,
                short_tag           TEXT NOT NULL DEFAULT '',
                category            TEXT NOT NULL DEFAULT 'General',
                govt_level          TEXT NOT NULL DEFAULT 'Central Government',
                description         TEXT NOT NULL DEFAULT '',
                who_benefits        TEXT NOT NULL DEFAULT '',
                eligibility_rules   TEXT NOT NULL DEFAULT '[]',
                required_documents  TEXT NOT NULL DEFAULT '[]',
                benefits_text       TEXT NOT NULL DEFAULT '',
                covered_treatments  TEXT NOT NULL DEFAULT '[]',
                official_website    TEXT NOT NULL DEFAULT 'https://mohfw.gov.in/',
                application_process TEXT NOT NULL DEFAULT '',
                states_applicable   TEXT NOT NULL DEFAULT 'All',
                age_min             INTEGER DEFAULT 0,
                age_max             INTEGER DEFAULT 120,
                income_limit        TEXT DEFAULT 'No income limit',
                match_tags          TEXT NOT NULL DEFAULT '[]',
                is_active           INTEGER NOT NULL DEFAULT 1,
                color               TEXT NOT NULL DEFAULT 'blue',
                added_by            TEXT NOT NULL DEFAULT 'Administrator',
                created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id          SERIAL PRIMARY KEY,
                email       TEXT NOT NULL UNIQUE,
                username    TEXT,
                password    TEXT NOT NULL,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            SERIAL PRIMARY KEY,
                name          TEXT NOT NULL,
                email         TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                mobile        TEXT,
                state         TEXT NOT NULL,
                district      TEXT NOT NULL,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id                    SERIAL PRIMARY KEY,
                user_id               INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                dob                   TEXT,
                age                   INTEGER,
                gender                TEXT,
                residence_type        TEXT,
                beneficiary_type      TEXT DEFAULT 'myself',
                family_size           INTEGER,
                income_range          TEXT,
                ration_card_category  TEXT,
                has_health_card       TEXT,
                other_coverage        TEXT,
                occupation            TEXT,
                welfare_board_reg     TEXT,
                special_category      TEXT,
                healthcare_needs      TEXT DEFAULT '[]',
                treatment_context     TEXT DEFAULT '{}',
                notes                 TEXT,
                document_availability TEXT DEFAULT '{}',
                completion_pct        INTEGER DEFAULT 20,
                updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS empanelled_hospitals (
                id                      SERIAL PRIMARY KEY,
                name                    TEXT NOT NULL,
                hospital_type           TEXT NOT NULL,
                state                   TEXT NOT NULL,
                district                TEXT NOT NULL,
                city                    TEXT NOT NULL,
                address                 TEXT NOT NULL,
                pincode                 TEXT NOT NULL,
                phone                   TEXT NOT NULL,
                emergency_helpline      TEXT NOT NULL,
                schemes_empanelled      TEXT NOT NULL DEFAULT '[]',
                total_capacity          INTEGER NOT NULL DEFAULT 100,
                general_beds_available  INTEGER NOT NULL DEFAULT 10,
                icu_beds_available      INTEGER NOT NULL DEFAULT 2,
                oxygen_beds_available   INTEGER NOT NULL DEFAULT 5,
                specialties             TEXT NOT NULL DEFAULT '[]',
                latitude                DOUBLE PRECISION NOT NULL DEFAULT 19.8762,
                longitude               DOUBLE PRECISION NOT NULL DEFAULT 75.3433,
                distance_km             DOUBLE PRECISION NOT NULL DEFAULT 2.5
            );
        """)

        # Indexes
        for idx_sql in [
            "CREATE INDEX IF NOT EXISTS idx_schemes_active ON schemes(is_active);",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
            "CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON user_profiles(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_hospitals_state ON empanelled_hospitals(state, district);",
        ]:
            cur.execute(idx_sql)

        # Ensure admin accounts exist
        from psycopg2.extras import RealDictCursor
        for email_val, uname_val in [("admin@123", "admin@123"), ("admin@swasthyasetu.gov.in", "admin")]:
            rcur = conn.cursor(cursor_factory=RealDictCursor)
            rcur.execute("SELECT id FROM admin_users WHERE email=%s OR username=%s", (email_val, uname_val))
            existing = rcur.fetchone()
            if existing:
                rcur.execute(
                    "UPDATE admin_users SET email=%s, username=%s, password=%s WHERE id=%s",
                    (email_val, uname_val, "admin@123", existing["id"])
                )
            else:
                rcur.execute(
                    "INSERT INTO admin_users (email, username, password) VALUES (%s, %s, %s)",
                    (email_val, uname_val, "admin@123")
                )
            rcur.close()

        # Auto-seed default schemes from SCHEME_CATALOGUE if table is empty (e.g. fresh Render deployment)
        cur.execute("SELECT COUNT(*) FROM schemes")
        cnt = cur.fetchone()
        num_schemes = cnt[0] if isinstance(cnt, tuple) else (cnt.get("count", 0) if cnt else 0)
        if num_schemes == 0:
            print("[db] Fresh database detected. Seeding 315 schemes into PostgreSQL...")
            from scheme_catalogue import SCHEME_CATALOGUE
            for s in SCHEME_CATALOGUE:
                cur.execute("""
                    INSERT INTO schemes
                        (name, short_tag, category, govt_level, description, who_benefits,
                         eligibility_rules, required_documents, benefits_text, covered_treatments,
                         official_website, application_process, states_applicable,
                         age_min, age_max, income_limit, match_tags, is_active, color, added_by)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    s.get("name", ""),
                    s.get("short_tag", ""),
                    s.get("category", "General"),
                    s.get("govt_level", "Central Government"),
                    s.get("description", ""),
                    s.get("who_benefits", ""),
                    json.dumps(s.get("eligibility_rules", [])),
                    json.dumps(s.get("required_documents", [])),
                    s.get("benefits_text", ""),
                    json.dumps(s.get("covered_treatments", [])),
                    s.get("official_website", "https://mohfw.gov.in/"),
                    s.get("application_process", ""),
                    s.get("states_applicable", "All"),
                    s.get("age_min", 0),
                    s.get("age_max", 120),
                    s.get("income_limit", "No income limit"),
                    json.dumps(s.get("match_tags", [])),
                    1,
                    s.get("color", "blue"),
                    s.get("added_by", "Administrator")
                ))
            print("[db] OK Auto-seeded 315 schemes.")

        # Auto-seed default empanelled hospitals if table is empty
        cur.execute("SELECT COUNT(*) FROM empanelled_hospitals")
        hcnt = cur.fetchone()
        num_hospitals = hcnt[0] if isinstance(hcnt, tuple) else (hcnt.get("count", 0) if hcnt else 0)
        if num_hospitals == 0:
            default_hospitals = [
                ("All India Institute of Medical Sciences (AIIMS)", "Central Government Apex Hospital", "Delhi", "New Delhi", "New Delhi", "Sri Aurobindo Marg, Ansari Nagar", "110029", "011-26588500", "102 / 108", json.dumps(["PM-JAY", "CGHS", "RAN", "Universal Access"]), 2478, 120, 24, 80, json.dumps(["Oncology", "Cardiology", "Neurology", "Nephrology", "Organ Transplant"]), 28.5672, 77.2100, 4.2),
                ("Tata Memorial Hospital", "Autonomous Cancer Care Institute", "Maharashtra", "Mumbai", "Mumbai", "Dr. E Borges Road, Parel", "400012", "022-24177000", "022-24177000", json.dumps(["PM-JAY", "MJPJAY", "RAN", "HMDG"]), 700, 35, 12, 45, json.dumps(["Medical Oncology", "Surgical Oncology", "Radiation Oncology", "Bone Marrow Transplant"]), 19.0028, 72.8427, 3.8),
                ("Postgraduate Institute of Medical Education and Research (PGIMER)", "Central Autonomous Institute", "Chandigarh", "Chandigarh", "Chandigarh", "Sector 12", "160012", "0172-2747585", "108", json.dumps(["PM-JAY", "CGHS", "Universal Access"]), 1948, 85, 18, 60, json.dumps(["Cardiology", "Neurosurgery", "Renal Transplant", "Pediatrics"]), 30.7634, 76.7821, 5.1),
                ("King Edward Memorial (KEM) Hospital", "Municipal Corporation Super-Specialty", "Maharashtra", "Mumbai", "Mumbai", "Acharya Donde Marg, Parel", "400012", "022-24107000", "108", json.dumps(["MJPJAY", "PM-JAY", "National Dialysis"]), 1800, 90, 15, 50, json.dumps(["Emergency Medicine", "General Surgery", "Cardiology", "Dialysis", "Burn Care"]), 19.0033, 72.8411, 2.1),
                ("NIMHANS (National Institute of Mental Health and Neuro-Sciences)", "National Institute of Eminence", "Karnataka", "Bengaluru Urban", "Bengaluru", "Hosur Road", "560029", "080-26995000", "080-46110007 (Kiran)", json.dumps(["PM-JAY", "Tele-MANAS", "National Mental Health"]), 850, 40, 8, 20, json.dumps(["Psychiatry", "Neurology", "Neurosurgery", "Addiction Medicine"]), 12.9372, 77.5956, 3.5),
                ("Sanjay Gandhi Postgraduate Institute of Medical Sciences (SGPGIMS)", "State Autonomous Apex Center", "Uttar Pradesh", "Lucknow", "Lucknow", "Raebareli Road", "226014", "0522-2668700", "108", json.dumps(["PM-JAY", "State Illness Assistance"]), 1200, 60, 14, 40, json.dumps(["Gastroenterology", "Endocrinology", "Cardiovascular", "Nephrology"]), 26.7497, 80.9388, 6.2),
                ("Chhatrapati Shivaji Maharaj General Hospital & Rajiv Gandhi Medical College", "Municipal Medical College Hospital", "Maharashtra", "Thane", "Thane", "Kalwa", "400605", "022-25372338", "108", json.dumps(["MJPJAY", "PM-JAY", "Janani Shishu Suraksha"]), 500, 45, 6, 25, json.dumps(["General Medicine", "Obstetrics & Gynecology", "Pediatrics", "Trauma Care"]), 19.1973, 72.9866, 1.8),
                ("Government Medical College and Hospital (GMCH)", "State Government Medical Center", "Maharashtra", "Nagpur", "Nagpur", "Hanuman Nagar", "440003", "0712-2744671", "108", json.dumps(["MJPJAY", "PM-JAY", "National Dialysis"]), 1400, 70, 10, 35, json.dumps(["Cardiology", "Dialysis", "Orthopedics", "General Surgery"]), 21.1272, 79.0964, 4.0),
                ("District Civil Hospital Nashik", "State Civil Hospital", "Maharashtra", "Nashik", "Nashik", "Trimbak Road", "422002", "0253-2576106", "108", json.dumps(["MJPJAY", "PM-JAY", "National TB Elimination"]), 650, 50, 8, 30, json.dumps(["General Surgery", "Maternity", "Pediatric ICU", "Emergency Care"]), 19.9975, 73.7898, 2.5),
                ("District General Hospital Pune (Aundh)", "District Hospital", "Maharashtra", "Pune", "Pune", "Aundh Chest Hospital Campus", "411027", "020-27282255", "108", json.dumps(["MJPJAY", "PM-JAY", "National Dialysis"]), 450, 35, 5, 20, json.dumps(["Chest Diseases", "Dialysis", "General Medicine", "Gynecology"]), 18.5714, 73.8058, 3.1)
            ]
            for h in default_hospitals:
                cur.execute("""
                    INSERT INTO empanelled_hospitals
                        (name, hospital_type, state, district, city, address, pincode, phone, emergency_helpline,
                         schemes_empanelled, total_capacity, general_beds_available, icu_beds_available, oxygen_beds_available,
                         specialties, latitude, longitude, distance_km)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, h)
            print("[db] OK Auto-seeded 10 empanelled hospitals.")

        conn.commit()
    finally:
        conn.close()



def _init_sqlite():
    """Create SQLite tables (legacy path)."""
    conn = _sqlite_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS schemes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            short_tag   TEXT NOT NULL DEFAULT '',
            category    TEXT NOT NULL DEFAULT 'General',
            govt_level  TEXT NOT NULL DEFAULT 'Central Government',
            description TEXT NOT NULL DEFAULT '',
            who_benefits TEXT NOT NULL DEFAULT '',
            eligibility_rules TEXT NOT NULL DEFAULT '[]',
            required_documents TEXT NOT NULL DEFAULT '[]',
            benefits_text TEXT NOT NULL DEFAULT '',
            covered_treatments TEXT NOT NULL DEFAULT '[]',
            official_website TEXT NOT NULL DEFAULT 'https://mohfw.gov.in/',
            application_process TEXT NOT NULL DEFAULT '',
            states_applicable TEXT NOT NULL DEFAULT 'All',
            age_min     INTEGER DEFAULT 0,
            age_max     INTEGER DEFAULT 120,
            income_limit TEXT DEFAULT 'No income limit',
            match_tags  TEXT NOT NULL DEFAULT '[]',
            is_active   INTEGER NOT NULL DEFAULT 1,
            color       TEXT NOT NULL DEFAULT 'blue',
            added_by    TEXT NOT NULL DEFAULT 'Administrator',
            created_at  TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS admin_users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            email    TEXT NOT NULL UNIQUE,
            username TEXT,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            email         TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            mobile        TEXT,
            state         TEXT NOT NULL,
            district      TEXT NOT NULL,
            created_at    TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at    TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS user_profiles (
            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id               INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            dob                   TEXT,
            age                   INTEGER,
            gender                TEXT,
            residence_type        TEXT,
            beneficiary_type      TEXT DEFAULT 'myself',
            family_size           INTEGER,
            income_range          TEXT,
            ration_card_category  TEXT,
            has_health_card       TEXT,
            other_coverage        TEXT,
            occupation            TEXT,
            welfare_board_reg     TEXT,
            special_category      TEXT,
            healthcare_needs      TEXT DEFAULT '[]',
            treatment_context     TEXT DEFAULT '{}',
            notes                 TEXT,
            document_availability TEXT DEFAULT '{}',
            completion_pct        INTEGER DEFAULT 20,
            updated_at            TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS empanelled_hospitals (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            name                    TEXT NOT NULL,
            hospital_type           TEXT NOT NULL,
            state                   TEXT NOT NULL,
            district                TEXT NOT NULL,
            city                    TEXT NOT NULL,
            address                 TEXT NOT NULL,
            pincode                 TEXT NOT NULL,
            phone                   TEXT NOT NULL,
            emergency_helpline      TEXT NOT NULL,
            schemes_empanelled      TEXT NOT NULL DEFAULT '[]',
            total_capacity          INTEGER NOT NULL DEFAULT 100,
            general_beds_available  INTEGER NOT NULL DEFAULT 10,
            icu_beds_available      INTEGER NOT NULL DEFAULT 2,
            oxygen_beds_available   INTEGER NOT NULL DEFAULT 5,
            specialties             TEXT NOT NULL DEFAULT '[]',
            latitude                REAL NOT NULL DEFAULT 19.8762,
            longitude               REAL NOT NULL DEFAULT 75.3433,
            distance_km             REAL NOT NULL DEFAULT 2.5
        );
    """)

    # Migrate: add added_by column if missing
    try:
        scheme_cols = [c[1] for c in conn.execute("PRAGMA table_info(schemes)").fetchall()]
        if "added_by" not in scheme_cols:
            conn.execute("ALTER TABLE schemes ADD COLUMN added_by TEXT NOT NULL DEFAULT 'Administrator'")
    except Exception:
        pass

    # Ensure admin accounts
    for email_val, uname_val in [("admin@123", "admin@123"), ("admin@swasthyasetu.gov.in", "admin")]:
        existing = conn.execute(
            "SELECT id FROM admin_users WHERE email=? OR username=?", (email_val, uname_val)
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE admin_users SET email=?, username=?, password=? WHERE id=?",
                (email_val, uname_val, "admin@123", existing[0])
            )
        else:
            conn.execute(
                "INSERT INTO admin_users (email, username, password) VALUES (?, ?, ?)",
                (email_val, uname_val, "admin@123")
            )

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────────
# SCHEME CRUD HELPERS
# ─────────────────────────────────────────────────────────────────

def get_all_schemes(active_only=True):
    conn = get_db()
    try:
        if active_only:
            cur = _execute(conn, "SELECT * FROM schemes WHERE is_active=1 ORDER BY name ASC")
        else:
            cur = _execute(conn, "SELECT * FROM schemes ORDER BY is_active DESC, name ASC")
        return _fetchall(cur)
    finally:
        _close(conn)


def get_scheme_by_id(scheme_id):
    conn = get_db()
    try:
        cur = _execute(conn, "SELECT * FROM schemes WHERE id=?", (scheme_id,))
        row = _fetchone(cur)
        return row
    finally:
        _close(conn)


def create_scheme(data: dict):
    conn = get_db()
    if "added_by" not in data or not data["added_by"]:
        data["added_by"] = "Administrator"
    now_dt = datetime.now()
    if "created_at" not in data or not data["created_at"]:
        data["created_at"] = now_dt
    if "updated_at" not in data or not data["updated_at"]:
        data["updated_at"] = now_dt
    scheme_id = None
    try:
        if _PG_AVAILABLE:
            sql, p = _adapt_sql("""
                INSERT INTO schemes
                    (name, short_tag, category, govt_level, description, who_benefits,
                     eligibility_rules, required_documents, benefits_text, covered_treatments,
                     official_website, application_process, states_applicable,
                     age_min, age_max, income_limit, match_tags, is_active, color, added_by,
                     created_at, updated_at)
                VALUES
                    (:name, :short_tag, :category, :govt_level, :description, :who_benefits,
                     :eligibility_rules, :required_documents, :benefits_text, :covered_treatments,
                     :official_website, :application_process, :states_applicable,
                     :age_min, :age_max, :income_limit, :match_tags, :is_active, :color, :added_by,
                     :created_at, :updated_at)
                RETURNING id
            """, data)
            from psycopg2.extras import RealDictCursor
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(sql, p)
            row = cur.fetchone()
            scheme_id = row["id"] if row else None
            _commit(conn)
        else:
            cur = _execute(conn, """
                INSERT INTO schemes
                    (name, short_tag, category, govt_level, description, who_benefits,
                     eligibility_rules, required_documents, benefits_text, covered_treatments,
                     official_website, application_process, states_applicable,
                     age_min, age_max, income_limit, match_tags, is_active, color, added_by,
                     created_at, updated_at)
                VALUES
                    (:name, :short_tag, :category, :govt_level, :description, :who_benefits,
                     :eligibility_rules, :required_documents, :benefits_text, :covered_treatments,
                     :official_website, :application_process, :states_applicable,
                     :age_min, :age_max, :income_limit, :match_tags, :is_active, :color, :added_by,
                     :created_at, :updated_at)
            """, data)
            scheme_id = cur.lastrowid
            _commit(conn)
    finally:
        _close(conn)
    return scheme_id


def get_newly_launched_schemes(limit: int = 6, days: int = 60):
    """
    Return recently created / launched schemes so beneficiaries can see
    what new schemes the government has introduced, when they were launched,
    and who may benefit.
    """
    conn = get_db()
    try:
        cur = _execute(conn, """
            SELECT * FROM schemes
            WHERE is_active = 1
            ORDER BY created_at DESC, id DESC
            LIMIT ?
        """, (limit,))
        rows = _fetchall(cur)
    finally:
        _close(conn)

    results = []
    now = datetime.now()
    for row in rows:
        d = dict(row)
        for field in ["eligibility_rules", "required_documents", "covered_treatments", "match_tags"]:
            val = d.get(field)
            if isinstance(val, str):
                try:
                    d[field + "_list"] = json.loads(val)
                except Exception:
                    d[field + "_list"] = []
            elif isinstance(val, list):
                d[field + "_list"] = val
            else:
                d[field + "_list"] = []

        cat = d.get("created_at")
        formatted_date = ""
        time_ago = ""
        is_new = False
        if cat:
            if isinstance(cat, str):
                try:
                    dt = datetime.fromisoformat(cat.replace("Z", ""))
                except Exception:
                    try:
                        dt = datetime.strptime(cat[:19], "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        dt = None
            elif isinstance(cat, datetime):
                dt = cat
            else:
                dt = None

            if dt:
                dt_naive = dt.replace(tzinfo=None) if dt.tzinfo else dt
                formatted_date = dt_naive.strftime("%d %b %Y")
                diff = now - dt_naive
                days_old = diff.days
                if days_old <= 0:
                    time_ago = "Today"
                    is_new = True
                elif days_old == 1:
                    time_ago = "Yesterday"
                    is_new = True
                elif days_old < 7:
                    time_ago = f"{days_old} days ago"
                    is_new = True
                elif days_old < 30:
                    time_ago = f"{days_old // 7} weeks ago"
                    is_new = True
                elif days_old < 60:
                    time_ago = "1 month ago"
                    is_new = True
                else:
                    time_ago = f"{days_old // 30} months ago"
                    is_new = False
            else:
                formatted_date = "Recently Added"
                time_ago = "Recent"
                is_new = True
        else:
            formatted_date = "Recently Added"
            time_ago = "Recent"
            is_new = True

        d["formatted_date"] = formatted_date
        d["time_ago"] = time_ago
        d["is_new"] = is_new
        results.append(d)

    return results


def update_scheme(scheme_id, data: dict):
    data["id"] = scheme_id
    data["updated_at"] = datetime.now().isoformat()
    conn = get_db()
    try:
        _execute(conn, """
            UPDATE schemes SET
                name=:name, short_tag=:short_tag, category=:category,
                govt_level=:govt_level, description=:description,
                who_benefits=:who_benefits, eligibility_rules=:eligibility_rules,
                required_documents=:required_documents, benefits_text=:benefits_text,
                covered_treatments=:covered_treatments, official_website=:official_website,
                application_process=:application_process, states_applicable=:states_applicable,
                age_min=:age_min, age_max=:age_max, income_limit=:income_limit,
                match_tags=:match_tags, is_active=:is_active, color=:color,
                updated_at=:updated_at
            WHERE id=:id
        """, data)
        _commit(conn)
    finally:
        _close(conn)


def delete_scheme(scheme_id):
    conn = get_db()
    try:
        _execute(conn, "DELETE FROM schemes WHERE id=?", (scheme_id,))
        _commit(conn)
    finally:
        _close(conn)


def toggle_scheme_status(scheme_id):
    conn = get_db()
    try:
        _execute(conn,
            "UPDATE schemes SET is_active = CASE WHEN is_active=1 THEN 0 ELSE 1 END WHERE id=?",
            (scheme_id,)
        )
        _commit(conn)
    finally:
        _close(conn)


def verify_admin(email_or_username, password):
    conn = get_db()
    ident = (email_or_username or "").strip().lower()
    try:
        cur = _execute(conn,
            "SELECT * FROM admin_users WHERE (LOWER(email)=? OR LOWER(username)=?) AND password=?",
            (ident, ident, password)
        )
        return _fetchone(cur)
    finally:
        _close(conn)


def count_schemes():
    conn = get_db()
    try:
        cur = _execute(conn, "SELECT COUNT(*) as total, SUM(is_active) as active FROM schemes")
        row = _fetchone(cur)
        if row:
            return {"total": row.get("total", 0) or 0, "active": row.get("active", 0) or 0}
        return {"total": 0, "active": 0}
    finally:
        _close(conn)


# ─────────────────────────────────────────────────────────────────
# EMPANELLED HOSPITALS
# ─────────────────────────────────────────────────────────────────

def get_empanelled_hospitals(scheme_id=None, scheme_tag=None, search_term=None, sort_by="distance"):
    """Retrieve empanelled network hospitals sorted by distance by default."""
    conn = get_db()
    try:
        cur = _execute(conn, "SELECT * FROM empanelled_hospitals ORDER BY distance_km ASC")
        rows = _fetchall(cur)
    finally:
        _close(conn)

    hospitals = []
    for h in rows:
        try:
            h["schemes_empanelled"] = json.loads(h["schemes_empanelled"])
        except Exception:
            h["schemes_empanelled"] = []
        try:
            h["specialties"] = json.loads(h["specialties"])
        except Exception:
            h["specialties"] = []
        h["is_empanelled"] = True
        hospitals.append(h)

    if scheme_tag:
        tag_lower = scheme_tag.lower().strip()
        for h in hospitals:
            h["is_empanelled"] = any(
                tag_lower in s.lower() or s.lower() in tag_lower
                for s in h["schemes_empanelled"]
            )
    elif scheme_id:
        scheme = get_scheme_by_id(scheme_id)
        if scheme:
            stag = (scheme.get("short_tag") or "").lower()
            sname = scheme.get("name", "").lower()
            for h in hospitals:
                matched = False
                for s in h["schemes_empanelled"]:
                    s_lower = s.lower()
                    if (stag and (stag in s_lower or s_lower in stag)) or (sname and (s_lower in sname or sname in s_lower)):
                        matched = True
                        break
                    if "universal" in s_lower or "pm-jay" in s_lower or "mjpjay" in s_lower:
                        matched = True
                        break
                h["is_empanelled"] = matched

    if search_term:
        st = search_term.lower().strip()
        hospitals = [
            h for h in hospitals
            if st in h["name"].lower() or st in h["city"].lower() or st in h["district"].lower() or st in h["address"].lower()
        ]

    if sort_by == "capacity":
        hospitals.sort(key=lambda x: x["total_capacity"], reverse=True)
    elif sort_by == "available_beds":
        hospitals.sort(key=lambda x: (x["general_beds_available"] + x["icu_beds_available"]), reverse=True)
    else:
        hospitals.sort(key=lambda x: x["distance_km"])

    return hospitals


def get_hospital_by_id(hospital_id):
    conn = get_db()
    try:
        cur = _execute(conn, "SELECT * FROM empanelled_hospitals WHERE id=?", (hospital_id,))
        h = _fetchone(cur)
    finally:
        _close(conn)
    if not h:
        return None
    try:
        h["schemes_empanelled"] = json.loads(h["schemes_empanelled"])
    except Exception:
        h["schemes_empanelled"] = []
    try:
        h["specialties"] = json.loads(h["specialties"])
    except Exception:
        h["specialties"] = []
    return h


# ─────────────────────────────────────────────────────────────────
# USER AUTHENTICATION & PROFILE
# ─────────────────────────────────────────────────────────────────

def create_user(name: str, email: str, password: str, mobile: str = "", state: str = "", district: str = ""):
    """Create a new user with securely hashed password and an initial profile."""
    email_clean = email.strip().lower()
    pw_hash = generate_password_hash(password, method="scrypt")
    conn = get_db()
    try:
        if _PG_AVAILABLE:
            # Use RETURNING id so we get the new row id directly from RealDictCursor
            cur = _execute(conn,
                "INSERT INTO users (name, email, password_hash, mobile, state, district) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                (name.strip(), email_clean, pw_hash, (mobile or "").strip(), state.strip(), district.strip())
            )
            row = _fetchone(cur)
            user_id = row["id"]
        else:
            cur = _execute(conn,
                "INSERT INTO users (name, email, password_hash, mobile, state, district) VALUES (?, ?, ?, ?, ?, ?)",
                (name.strip(), email_clean, pw_hash, (mobile or "").strip(), state.strip(), district.strip())
            )
            user_id = cur.lastrowid

        _execute(conn,
            "INSERT INTO user_profiles (user_id, beneficiary_type, completion_pct) VALUES (?, 'myself', 20)",
            (user_id,)
        )
        _commit(conn)
        return user_id
    except Exception as e:
        err_str = str(e).lower()
        if "unique" in err_str or "duplicate" in err_str:
            return None
        raise
    finally:
        _close(conn)


def verify_user(email: str, password: str):
    email_clean = email.strip().lower()
    conn = get_db()
    try:
        cur = _execute(conn, "SELECT * FROM users WHERE email=?", (email_clean,))
        row = _fetchone(cur)
    finally:
        _close(conn)
    if row and check_password_hash(row["password_hash"], password):
        return row
    return None


def get_user_by_id(user_id: int):
    conn = get_db()
    try:
        cur = _execute(conn,
            "SELECT id, name, email, mobile, state, district, created_at FROM users WHERE id=?",
            (user_id,)
        )
        return _fetchone(cur)
    finally:
        _close(conn)


def get_user_by_email(email: str):
    conn = get_db()
    try:
        cur = _execute(conn, "SELECT * FROM users WHERE email=?", (email.strip().lower(),))
        return _fetchone(cur)
    finally:
        _close(conn)


def update_user_basic(user_id: int, name: str, mobile: str = "", state: str = "", district: str = ""):
    conn = get_db()
    try:
        _execute(conn,
            "UPDATE users SET name=?, mobile=?, state=?, district=?, updated_at=datetime('now') WHERE id=?",
            (name.strip(), (mobile or "").strip(), state.strip(), district.strip(), user_id)
        )
        _commit(conn)
    finally:
        _close(conn)


def get_user_profile(user_id: int):
    conn = get_db()
    try:
        cur = _execute(conn, "SELECT * FROM user_profiles WHERE user_id=?", (user_id,))
        prof = _fetchone(cur)
    finally:
        _close(conn)
    if not prof:
        return None
    for json_field, default_val in [
        ("healthcare_needs", []),
        ("treatment_context", {}),
        ("document_availability", {})
    ]:
        val = prof.get(json_field)
        if isinstance(val, str):
            try:
                prof[json_field] = json.loads(val or "null") or default_val
            except Exception:
                prof[json_field] = default_val
        elif val is None:
            prof[json_field] = default_val
    return prof


def save_user_profile(user_id: int, form_data: dict, user_data: dict = None):
    """Save or update complete user profile and recalculate completion percentage."""
    if user_data is None:
        user_data = get_user_by_id(user_id) or {}

    needs = form_data.get("healthcare_needs", [])
    if isinstance(needs, str):
        needs = [needs]

    treatment_context = form_data.get("treatment_context", {})
    if not isinstance(treatment_context, dict):
        treatment_context = {}

    for ctx_f in ["dialysis_prescribed", "pregnancy_stage", "disability_cert_status", "treatment_stage"]:
        if form_data.get(ctx_f):
            treatment_context[ctx_f] = form_data.get(ctx_f)

    doc_avail = form_data.get("document_availability", {})
    if not isinstance(doc_avail, dict):
        doc_avail = {}

    dob = (form_data.get("dob") or "").strip()
    age = form_data.get("age")
    if dob:
        try:
            birth_year = int(dob.split("-")[0])
            current_year = datetime.now().year
            if 1900 <= birth_year <= current_year:
                age = current_year - birth_year
        except Exception:
            pass

    if age is not None and age != "":
        try:
            age = int(age)
        except ValueError:
            age = None

    beneficiary = form_data.get("beneficiary") or form_data.get("beneficiary_type") or "myself"
    income = form_data.get("household_income") or form_data.get("income_range") or ""
    ration_card = form_data.get("ration_card_category") or ""
    has_card = form_data.get("existing_health_coverage") or form_data.get("has_health_card") or ""
    other_cov = form_data.get("other_coverage") or ""
    occupation = form_data.get("occupation") or ""
    welfare_reg = form_data.get("worker_board") or form_data.get("welfare_board_reg") or ""
    special_cat = form_data.get("special_categories") or form_data.get("special_category") or ""
    if isinstance(special_cat, list):
        special_cat = ", ".join(special_cat)
    notes = form_data.get("healthcare_notes") or form_data.get("notes") or ""

    profile_dict_for_scoring = {
        "dob": dob, "age": age,
        "gender": form_data.get("gender", ""),
        "residence_type": form_data.get("residence_type", ""),
        "beneficiary_type": beneficiary,
        "family_size": form_data.get("family_size"),
        "income_range": income,
        "ration_card_category": ration_card,
        "has_health_card": has_card,
        "other_coverage": other_cov,
        "occupation": occupation,
        "welfare_board_reg": welfare_reg,
        "special_category": special_cat,
        "healthcare_needs": needs,
        "treatment_context": treatment_context,
        "notes": notes.strip(),
        "document_availability": doc_avail
    }

    completion_pct = calculate_profile_completion(user_data, profile_dict_for_scoring)

    params = {
        "user_id": user_id,
        "dob": dob,
        "age": age,
        "gender": form_data.get("gender", ""),
        "residence_type": form_data.get("residence_type", ""),
        "beneficiary_type": beneficiary,
        "family_size": form_data.get("family_size") if form_data.get("family_size") else None,
        "income_range": income,
        "ration_card_category": ration_card,
        "has_health_card": has_card,
        "other_coverage": other_cov,
        "occupation": occupation,
        "welfare_board_reg": welfare_reg,
        "special_category": special_cat,
        "healthcare_needs": json.dumps(needs),
        "treatment_context": json.dumps(treatment_context),
        "notes": notes.strip(),
        "document_availability": json.dumps(doc_avail),
        "completion_pct": completion_pct
    }

    conn = get_db()
    try:
        if _PG_AVAILABLE:
            _execute(conn, """
                INSERT INTO user_profiles (
                    user_id, dob, age, gender, residence_type, beneficiary_type,
                    family_size, income_range, ration_card_category, has_health_card,
                    other_coverage, occupation, welfare_board_reg, special_category,
                    healthcare_needs, treatment_context, notes, document_availability,
                    completion_pct, updated_at
                ) VALUES (
                    %(user_id)s, %(dob)s, %(age)s, %(gender)s, %(residence_type)s, %(beneficiary_type)s,
                    %(family_size)s, %(income_range)s, %(ration_card_category)s, %(has_health_card)s,
                    %(other_coverage)s, %(occupation)s, %(welfare_board_reg)s, %(special_category)s,
                    %(healthcare_needs)s, %(treatment_context)s, %(notes)s, %(document_availability)s,
                    %(completion_pct)s, NOW()
                )
                ON CONFLICT(user_id) DO UPDATE SET
                    dob=EXCLUDED.dob, age=EXCLUDED.age, gender=EXCLUDED.gender,
                    residence_type=EXCLUDED.residence_type, beneficiary_type=EXCLUDED.beneficiary_type,
                    family_size=EXCLUDED.family_size, income_range=EXCLUDED.income_range,
                    ration_card_category=EXCLUDED.ration_card_category, has_health_card=EXCLUDED.has_health_card,
                    other_coverage=EXCLUDED.other_coverage, occupation=EXCLUDED.occupation,
                    welfare_board_reg=EXCLUDED.welfare_board_reg, special_category=EXCLUDED.special_category,
                    healthcare_needs=EXCLUDED.healthcare_needs, treatment_context=EXCLUDED.treatment_context,
                    notes=EXCLUDED.notes, document_availability=EXCLUDED.document_availability,
                    completion_pct=EXCLUDED.completion_pct, updated_at=NOW()
            """, params)
        else:
            _execute(conn, """
                INSERT INTO user_profiles (
                    user_id, dob, age, gender, residence_type, beneficiary_type,
                    family_size, income_range, ration_card_category, has_health_card,
                    other_coverage, occupation, welfare_board_reg, special_category,
                    healthcare_needs, treatment_context, notes, document_availability,
                    completion_pct, updated_at
                ) VALUES (
                    :user_id, :dob, :age, :gender, :residence_type, :beneficiary_type,
                    :family_size, :income_range, :ration_card_category, :has_health_card,
                    :other_coverage, :occupation, :welfare_board_reg, :special_category,
                    :healthcare_needs, :treatment_context, :notes, :document_availability,
                    :completion_pct, datetime('now')
                )
                ON CONFLICT(user_id) DO UPDATE SET
                    dob=excluded.dob, age=excluded.age, gender=excluded.gender,
                    residence_type=excluded.residence_type, beneficiary_type=excluded.beneficiary_type,
                    family_size=excluded.family_size, income_range=excluded.income_range,
                    ration_card_category=excluded.ration_card_category, has_health_card=excluded.has_health_card,
                    other_coverage=excluded.other_coverage, occupation=excluded.occupation,
                    welfare_board_reg=excluded.welfare_board_reg, special_category=excluded.special_category,
                    healthcare_needs=excluded.healthcare_needs, treatment_context=excluded.treatment_context,
                    notes=excluded.notes, document_availability=excluded.document_availability,
                    completion_pct=excluded.completion_pct, updated_at=datetime('now')
            """, params)
        _commit(conn)
    finally:
        _close(conn)
    return completion_pct


def update_quick_answer(user_id: int, question_key: str, answer_value: str, user_data: dict = None):
    """Update a single answer from the recommendation missing-info card."""
    if user_data is None:
        user_data = get_user_by_id(user_id) or {}

    prof = get_user_profile(user_id) or {}
    updated = False

    if question_key in ["has_health_card", "existing_health_coverage"]:
        prof["has_health_card"] = answer_value
        updated = True
    elif question_key == "ration_card_category":
        prof["ration_card_category"] = answer_value
        updated = True
    elif question_key == "occupation":
        prof["occupation"] = answer_value
        updated = True
    elif question_key in ["special_category", "special_categories"]:
        prof["special_category"] = answer_value
        updated = True
    elif question_key in ["dialysis_prescribed", "pregnancy_stage", "disability_cert_status", "treatment_stage"]:
        ctx = prof.get("treatment_context", {})
        if not isinstance(ctx, dict):
            ctx = {}
        ctx[question_key] = answer_value
        prof["treatment_context"] = ctx
        updated = True
    elif question_key.startswith("doc_"):
        doc_key = question_key[4:]
        doc_avail = prof.get("document_availability", {})
        if not isinstance(doc_avail, dict):
            doc_avail = {}
        doc_avail[doc_key] = answer_value
        prof["document_availability"] = doc_avail
        updated = True
    elif question_key.startswith("ctx_"):
        ctx_key = question_key[4:]
        ctx = prof.get("treatment_context", {})
        if not isinstance(ctx, dict):
            ctx = {}
        ctx[ctx_key] = answer_value
        prof["treatment_context"] = ctx
        updated = True

    if updated:
        save_user_profile(user_id, prof, user_data)
        return True
    return False


def calculate_profile_completion(user: dict, profile: dict) -> int:
    """
    Calculate transparent profile completion percentage.
    Section A (40%): Name/State/District (15%), DOB/Age (10%), Gender (8%), Residence (7%)
    Section B (35%): Family size (8%), Income (10%), Ration card (9%), Health card (8%)
    Section C (25%): Occupation (15%), Welfare board (10%)
    """
    score = 0
    if user.get("name") and user.get("state") and user.get("district"):
        score += 15
    if profile.get("dob") or (profile.get("age") is not None and profile.get("age") != ""):
        score += 10
    if profile.get("gender") and profile.get("gender") != "":
        score += 8
    if profile.get("residence_type") and profile.get("residence_type") != "":
        score += 7
    if profile.get("family_size"):
        score += 8
    if profile.get("income_range") or profile.get("household_income"):
        score += 10
    if profile.get("ration_card_category") and profile.get("ration_card_category") != "":
        score += 9
    if profile.get("has_health_card") or profile.get("other_coverage"):
        score += 8
    if profile.get("occupation") and profile.get("occupation") != "":
        score += 15
    if profile.get("welfare_board_reg") and profile.get("welfare_board_reg") != "":
        score += 10
    return min(100, max(20, score))


# ─────────────────────────────────────────────────────────────────
# DYNAMIC RECOMMENDATION ENGINE (legacy dashboard path)
# ─────────────────────────────────────────────────────────────────

def recommend_schemes_from_db(profile: dict) -> list:
    """
    Match user profile against all active schemes in the database.
    Returns a list of enriched scheme recommendation dicts.
    """
    all_schemes = get_all_schemes(active_only=True)
    recommendations = []

    user_age = profile.get("age", 30)
    user_state = profile.get("state", "").strip().lower()
    user_treatments = [t.lower() for t in profile.get("treatments", [])]
    user_income = profile.get("income", "").lower()
    user_gender = profile.get("gender", "").lower()
    user_govt_employee = profile.get("govt_employee", "no")
    user_ration_card = profile.get("ration_card", "no")
    user_circumstances = [c.lower() for c in profile.get("circumstances", [])]
    user_docs = profile.get("documents", {})
    user_beneficiary = profile.get("beneficiary", "myself")
    patient_age = profile.get("patient_age", user_age)

    for scheme in all_schemes:
        score = 0
        reasons = []

        try:
            match_tags = json.loads(scheme.get("match_tags", "[]") or "[]")
        except Exception:
            match_tags = []
        try:
            eligibility_rules = json.loads(scheme.get("eligibility_rules", "[]") or "[]")
        except Exception:
            eligibility_rules = []
        try:
            required_documents = json.loads(scheme.get("required_documents", "[]") or "[]")
        except Exception:
            required_documents = []
        try:
            covered_treatments = json.loads(scheme.get("covered_treatments", "[]") or "[]")
        except Exception:
            covered_treatments = []

        states_applicable = scheme.get("states_applicable", "All")
        age_min = scheme.get("age_min", 0) or 0
        age_max = scheme.get("age_max", 120) or 120
        income_limit = (scheme.get("income_limit") or "").lower()

        if states_applicable and states_applicable.lower() != "all":
            applicable_states = [s.strip().lower() for s in states_applicable.split(",")]
            if user_state and not any(user_state in s or s in user_state for s in applicable_states):
                continue
            elif user_state:
                score += 15
                reasons.append(f"Applicable in {profile.get('state', 'your state')}")

        effective_age = patient_age if user_beneficiary != "myself" else user_age
        if age_min <= effective_age <= age_max:
            if age_min > 0 or age_max < 120:
                score += 10
                reasons.append(f"Age {effective_age} is within the scheme's target age range ({age_min}–{age_max} years)")
        else:
            continue

        treatment_match_count = 0
        scheme_searchable = f"{scheme.get('name', '')} {scheme.get('description', '')} {scheme.get('who_benefits', '')} {scheme.get('category', '')}".lower()
        for user_t in user_treatments:
            matched = False
            for tag in match_tags:
                tag_lower = tag.lower()
                if tag_lower in user_t or user_t in tag_lower:
                    treatment_match_count += 1
                    score += 20
                    reasons.append(f"You need '{tag}' — this scheme covers such care")
                    matched = True
                    break
            if not matched:
                for word in user_t.split():
                    w = word.strip(",.()\n").lower()
                    if len(w) > 3 and w not in ["care", "treatment", "disease", "other"]:
                        if w in scheme_searchable:
                            treatment_match_count += 1
                            score += 20
                            reasons.append(f"You need '{user_t}' — this scheme covers such care")
                            break

        if not treatment_match_count and "hospitalization" in (scheme_searchable + " ".join(match_tags).lower()):
            if any("hospitalization" in t or "surgery" in t or "treatment" in t for t in user_treatments):
                score += 8
                reasons.append("Scheme covers hospital-based medical treatment")

        if user_govt_employee == "yes":
            scheme_name_lower = scheme["name"].lower()
            if "cghs" in scheme_name_lower or "central government health" in scheme_name_lower:
                score += 35
                reasons.append("You are a government employee — CGHS is specifically designed for you")

        if income_limit and income_limit != "no income limit":
            if "bpl" in income_limit or "below" in income_limit:
                if "below" in user_income or "1 lakh" in user_income or "bpl" in " ".join(user_circumstances):
                    score += 15
                    reasons.append("Your income level matches the scheme's financial eligibility criteria")

        if user_ration_card == "yes":
            tags_str = " ".join(match_tags).lower()
            desc_lower = scheme.get("description", "").lower()
            if "ration" in tags_str or "bpl" in tags_str or "yellow" in desc_lower or "aay" in desc_lower:
                score += 12
                reasons.append("Your ration card helps establish household eligibility for this scheme")

        for circ in user_circumstances:
            if "construction" in circ and ("bocw" in " ".join(match_tags).lower() or "construction" in scheme["name"].lower()):
                score += 20
                reasons.append("Construction worker registration may unlock welfare board medical benefits")
            if "disability" in circ and ("disability" in " ".join(match_tags).lower() or "niramaya" in scheme["name"].lower()):
                score += 20
                reasons.append("Your disability status may qualify you for disability-specific health insurance")
            if "senior" in circ or effective_age >= 70:
                if "senior" in " ".join(match_tags).lower() or "elderly" in scheme.get("description", "").lower():
                    score += 15
                    reasons.append("Senior citizen status may qualify for additional benefits under this scheme")

        scheme_name_lower = scheme["name"].lower()
        scheme_desc_lower = scheme.get("description", "").lower()
        if user_gender == "female":
            if "maternity" in scheme_name_lower or "matru" in scheme_name_lower or "janani" in scheme_name_lower:
                score += 20
                reasons.append("This scheme is specifically designed for women's maternal healthcare needs")
        elif user_gender == "male":
            if "maternity" in scheme_name_lower or "matru" in scheme_name_lower:
                score -= 50

        universal_keywords = ["universal", "all residents", "everyone", "any patient", "all patients"]
        if any(kw in scheme_desc_lower for kw in universal_keywords):
            if score < 20:
                score = 20
                reasons.append("This scheme is available to all residents regardless of income or category")

        if score < 10 or not reasons:
            continue

        score = min(100, score)

        docs_ready = 0
        docs_total = len(required_documents)
        doc_status_details = []
        doc_key_map = {
            "aadhaar": "aadhaar", "identity": "aadhaar",
            "ration card": "ration_card",
            "income certificate": "income_cert",
            "residence": "residence_cert",
            "medical reports": "medical_reports", "diagnostic": "medical_reports",
            "prescription": "prescription",
            "hospital estimate": "hospital_estimate",
            "disability": "disability_cert",
            "health card": "govt_health_card", "ayushman": "govt_health_card",
        }
        for doc in required_documents:
            doc_lower = doc.lower()
            matched_key = None
            for keyword, key in doc_key_map.items():
                if keyword in doc_lower:
                    matched_key = key
                    break
            if matched_key:
                status_val = user_docs.get(matched_key, "not_sure")
                if status_val == "available":
                    docs_ready += 1
                    doc_status_details.append({"name": doc, "status": "Available ✓"})
                elif status_val == "not_available":
                    doc_status_details.append({"name": doc, "status": "Not Available"})
                else:
                    doc_status_details.append({"name": doc, "status": "Not Sure"})
            else:
                doc_status_details.append({"name": doc, "status": "Verify with scheme office"})

        if not reasons:
            reasons = ["Scheme parameters match your healthcare needs"]

        recommendations.append({
            "id": scheme["id"],
            "name": scheme["name"],
            "tag": scheme.get("short_tag") or scheme["name"][:20],
            "category": scheme.get("category", "General"),
            "govt_level": scheme.get("govt_level", "Central Government"),
            "color": "blue",
            "description": scheme.get("description", ""),
            "benefit_info": scheme.get("benefits_text") or scheme.get("who_benefits") or "Cashless / subsidized government healthcare support as per official guidelines.",
            "covered_treatment": ", ".join(covered_treatments) if covered_treatments else scheme.get("category", "Healthcare services"),
            "match_reasons": reasons[:5],
            "verification_needed": eligibility_rules[:4] if eligibility_rules else ["Verify eligibility with the scheme authority"],
            "intended_beneficiaries": scheme.get("who_benefits", ""),
            "verified_eligibility_conditions": eligibility_rules,
            "application_process": scheme.get("application_process", "Contact the scheme authority"),
            "official_website": scheme.get("official_website", "https://mohfw.gov.in/"),
            "source_of_rules": "Official Government Portal",
            "last_verified_date": "Oct 2026",
            "relevance_score": score,
            "docs_ready_count": docs_ready,
            "docs_total_count": docs_total,
            "doc_status_details": doc_status_details,
        })

    recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
    return recommendations[:12]
