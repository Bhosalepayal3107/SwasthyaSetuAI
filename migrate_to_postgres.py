"""
migrate_to_postgres.py — SwasthyaSetu AI
Migrates all tables and data from SQLite (swasthyasetu.db) to PostgreSQL.
Can be executed standalone:
    py -3 migrate_to_postgres.py
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

# Load .env file
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("Error: psycopg2 is not installed. Please run: pip install psycopg2-binary")
    sys.exit(1)

SQLITE_PATH = os.path.join(os.path.dirname(__file__), "swasthyasetu.db")


def get_pg_connection():
    """Establish connection to PostgreSQL using DATABASE_URL or individual PG* env vars."""
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        return psycopg2.connect(db_url)

    host = os.environ.get("PGHOST", "localhost")
    port = int(os.environ.get("PGPORT", "5432"))
    dbname = os.environ.get("PGDATABASE", "swasthyasetu")
    user = os.environ.get("PGUSER", "postgres")
    password = os.environ.get("PGPASSWORD", "")

    return psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )


def create_postgres_tables(pg_conn):
    """Create all required PostgreSQL tables and indices."""
    with pg_conn.cursor() as cur:
        # 1. schemes table
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

        # 2. admin_users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id                  SERIAL PRIMARY KEY,
                email               TEXT NOT NULL UNIQUE,
                username            TEXT,
                password            TEXT NOT NULL,
                created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 3. users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id                  SERIAL PRIMARY KEY,
                name                TEXT NOT NULL,
                email               TEXT UNIQUE NOT NULL,
                password_hash       TEXT NOT NULL,
                mobile              TEXT,
                state               TEXT NOT NULL,
                district            TEXT NOT NULL,
                created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 4. user_profiles table
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

        # 5. empanelled_hospitals table
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

        # Performance indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_schemes_active ON schemes(is_active);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_schemes_states ON schemes(states_applicable);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON user_profiles(user_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_hospitals_state_district ON empanelled_hospitals(state, district);")
        
    pg_conn.commit()
    print("PostgreSQL tables and indices created successfully.")


def migrate_data():
    if not os.path.exists(SQLITE_PATH):
        print(f"Error: SQLite database {SQLITE_PATH} not found.")
        sys.exit(1)

    print(f"Connecting to SQLite ({SQLITE_PATH})...")
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row

    print("Connecting to PostgreSQL...")
    try:
        pg_conn = get_pg_connection()
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")
        print("Please check your .env configuration (DATABASE_URL or PGHOST, PGUSER, PGPASSWORD, PGDATABASE).")
        sys.exit(1)

    create_postgres_tables(pg_conn)

    tables_to_migrate = [
        "schemes",
        "admin_users",
        "users",
        "user_profiles",
        "empanelled_hospitals"
    ]

    with pg_conn.cursor() as cur:
        for table in tables_to_migrate:
            # Check SQLite table
            sq_rows = sqlite_conn.execute(f"SELECT * FROM {table}").fetchall()
            print(f"Found {len(sq_rows)} records in SQLite table '{table}'.")

            if not sq_rows:
                continue

            # Clear existing table data in Postgres to ensure clean synchronization
            cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")

            # Column names
            cols = sq_rows[0].keys()
            col_names_str = ", ".join(cols)
            placeholders = ", ".join(["%s"] * len(cols))

            insert_query = f"INSERT INTO {table} ({col_names_str}) VALUES ({placeholders})"

            data_tuples = []
            for r in sq_rows:
                row_vals = []
                for c in cols:
                    val = r[c]
                    row_vals.append(val)
                data_tuples.append(tuple(row_vals))

            cur.executemany(insert_query, data_tuples)
            print(f"  -> Migrated {len(data_tuples)} records into PostgreSQL '{table}'.")

            # Update PostgreSQL sequence to match max(id) so new inserts don't collide
            cur.execute(f"SELECT MAX(id) FROM {table}")
            max_id = cur.fetchone()[0]
            if max_id:
                cur.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), %s);", (max_id,))
                print(f"  -> Reset sequence for '{table}' to {max_id}.")

    pg_conn.commit()
    sqlite_conn.close()
    pg_conn.close()
    print("\nSUCCESS: All data successfully migrated from SQLite to PostgreSQL!")


if __name__ == "__main__":
    migrate_data()
