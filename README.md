# 🏥 Hospital Management System — Setup Guide

## Files in This Project
```
hospital_app.py         ← Main GUI application (run this)
db_config.py            ← Database connection settings
hospital_db_schema.sql  ← MySQL database schema + seed data
README.md               ← This file
```

---

## Step 1 — Install Requirements

Make sure Python 3.8+ is installed, then install the MySQL connector:

```bash
pip install mysql-connector-python
```

---

## Step 2 — Set Up MySQL Database

1. Open **MySQL Workbench** or your MySQL terminal
2. Run the schema file:

```sql
SOURCE /path/to/hospital_db_schema.sql;
```

OR copy-paste the entire contents of `hospital_db_schema.sql` and execute it.

This will:
- Create the `hospital_db` database
- Create all 8 tables (wards, rooms, doctors, patients, appointments, medicines, prescriptions, bills)
- Insert sample/demo data

---

## Step 3 — Configure Database Password

Open `db_config.py` and update the database credentials if needed.

The application also supports environment variables:
- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`

If your MySQL username is not `root`, update `DB_USER` in `db_config.py` or set it as an environment variable.

If you get an access denied error, verify that `DB_PASSWORD` is correct for your MySQL user. When the app starts, it will show a login prompt if the stored credentials fail.

The app will automatically create the `hospital_db` database and tables if the database does not exist.

---

## Step 4 — Run the Application

```bash
python hospital_app.py
```

---

## Modules & Features

| Module        | Features                                              |
|---------------|-------------------------------------------------------|
| Dashboard     | Live stats: patients, doctors, appts, revenue, rooms  |
| Patients      | Add/Edit/Delete, search, blood group, status tracking |
| Doctors       | Add/Edit/Delete, specialization, schedule, fee        |
| Appointments  | Book, update status, cancel, doctor-patient linking   |
| Wards & Rooms | Manage ward types, add rooms, update room status      |
| Pharmacy      | Add medicines, track stock, low-stock alerts          |
| Billing       | Generate bills, calculate totals, payment tracking    |

---

## Database Tables

```
patients        — patient records
doctors         — doctor profiles
appointments    — patient-doctor appointments
wards           — hospital wards
rooms           — individual rooms inside wards
medicines       — pharmacy inventory
prescriptions   — prescribed medicines
bills           — patient billing records
```

---

## Troubleshooting

| Problem                        | Solution                                           |
|--------------------------------|----------------------------------------------------|
| "Cannot connect to database"   | Check DB_PASSWORD in db_config.py                  |
| "Module not found"             | Run: pip install mysql-connector-python            |
| Blank tables after launch      | Ensure hospital_db_schema.sql was run successfully |
| tkinter not found (Linux)      | Run: sudo apt-get install python3-tk               |

---

## Technologies Used
- **Python 3** — Application logic
- **Tkinter** — GUI framework (built into Python)
- **MySQL** — Relational database
- **mysql-connector-python** — Python-MySQL bridge
