# SwasthyaSetu AI — Healthcare Benefits Portal

A smart Flask-based healthcare benefits portal and recommendation system for discovering Indian government healthcare schemes, assessing personalized eligibility, preparing document checklists, finding empanelled hospitals, organizing medical records, tracking applications, and managing schemes through a dedicated Admin Panel.

---

## Features

- **Progressive Beneficiary Workflow**:
  - `1. My Profile`: Personal, demographic, household, socioeconomic, and occupation data.
  - `2. Scheme Finder`: Care needs assessment (specialties, treatments, surgeries).
  - `3. Recommendations`: Match status breakdown (*Potential Match*, *More Information Needed*, *Eligibility Not Yet Verified*) with targeted follow-up questions.
  - `4. Documents`: Dynamic checklist with status tracking, guidelines, and direct download links.
  - `5. Empanelled Hospitals`: Network hospital directory with verified clinical specialties, location, and helpline details.
- **Dedicated Admin Control Panel (`/admin`)**:
  - View, search, and filter 315+ government healthcare schemes.
  - Add new government schemes with full criteria (description, who benefits, eligibility rules, required documents, covered treatments, match tags, age/income thresholds, state limits).
  - Edit and update existing schemes with immediate real-time reflection across the beneficiary workflow.
  - Toggle active/inactive status and delete schemes.
  - Scheme author attribution (`Added By: Administrator`).
- **Dual Database Architecture (PostgreSQL & SQLite)**:
  - **PostgreSQL**: Enterprise-grade relational database for production with full ACID compliance, foreign keys, and indexing.
  - **SQLite (`swasthyasetu.db`)**: Local standalone fallback ensuring zero configuration setup out-of-the-box.
  - Automatic data migration utility (`migrate_to_postgres.py`) to migrate all 315 schemes, admin users, user profiles, and empanelled hospitals into PostgreSQL.
- **Native In-Portal Multilingual Engine**: Seamless instant translation across English, Hindi (हिन्दी), and Marathi (मराठी) without browser popups or external translation notifications.

---

## Database Architecture & PostgreSQL Setup

### Database Tables Overview

| Table | Description |
|---|---|
| `schemes` | Stores 315+ central and state healthcare schemes with eligibility rules, documents, and match tags. |
| `admin_users` | Administrator accounts for managing schemes and portal settings. |
| `users` | Citizen / patient accounts with hashed passwords (`scrypt`) and basic contact details. |
| `user_profiles` | Comprehensive demographic, socioeconomic, and medical need profiles with auto-calculated completion percentage. |
| `empanelled_hospitals` | Empanelled network hospitals with specialties, contact details, geo-coordinates, and distance metrics. |

### PostgreSQL Configuration

1. **Install Dependencies**:
   ```powershell
   py -3 -m pip install -r requirements.txt
   ```

2. **Configure Environment Variables (`.env`)**:
   Copy `.env.example` to `.env` in the root folder:
   ```ini
   # Option 1: Full Connection URL
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/swasthyasetu

   # Option 2: Individual Parameters
   PGHOST=localhost
   PGPORT=5432
   PGDATABASE=swasthyasetu
   PGUSER=postgres
   PGPASSWORD=YOUR_PASSWORD

   # Database Engine Selection
   DB_TYPE=postgres
   ```

3. **Migrate Existing SQLite Data to PostgreSQL**:
   Run the migration script to create all tables, indexes, and migrate all 315 schemes and records:
   ```powershell
   py -3 migrate_to_postgres.py
   ```

---

## Admin Credentials

- **URL**: `http://127.0.0.1:5000/admin/login`
- **Email / Username**: `admin@123` or `admin@swasthyasetu.gov.in`
- **Password**: `admin@123`

---

## Running the Application

1. **Start the Flask Server**:
   ```powershell
   py -3 app.py
   ```

2. **Access the Portal**:
   - Beneficiary Portal: `http://127.0.0.1:5000/`
   - Admin Panel: `http://127.0.0.1:5000/admin`
   - Empanelled Hospitals: `http://127.0.0.1:5000/hospitals`
   - AI Healthcare Assistant: `http://127.0.0.1:5000/assistant`

---

## Automated Test Suite

Run the full automated test suite (40 comprehensive unit and integration tests):
```powershell
py -3 test_app.py
```
