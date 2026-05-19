# db_config.py - MySQL version
import os
from pathlib import Path

import mysql.connector
from mysql.connector import Error

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Abdul123")      # Your correct password
DB_NAME = os.getenv("DB_NAME", "hospital_db")
SCHEMA_FILE = Path(__file__).with_name("hospital_db_schema.sql")


def get_connection(use_db=True):
    """Create and return a MySQL database connection."""
    try:
        conn_args = {
            "host": DB_HOST,
            "port": DB_PORT,
            "user": DB_USER,
            "password": DB_PASSWORD,
        }
        if use_db:
            conn_args["database"] = DB_NAME
        conn = mysql.connector.connect(**conn_args)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def initialize_database():
    """Ensure the database exists and the schema is loaded."""
    conn = get_connection(use_db=True)
    if conn is not None:
        conn.close()
        return True, None

    conn = get_connection(use_db=False)
    if conn is None:
        return False, "Database connection failed: check credentials and MySQL server"

    try:
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET utf8mb4")
        conn.commit()
        conn.close()
    except Error as e:
        conn.close()
        return False, str(e)

    if not SCHEMA_FILE.exists():
        return False, f"Schema file not found: {SCHEMA_FILE}"

    conn = get_connection(use_db=True)
    if conn is None:
        return False, "Failed to connect after creating database"

    try:
        cursor = conn.cursor()
        sql = SCHEMA_FILE.read_text(encoding="utf-8")
        for result in cursor.execute(sql, multi=True):
            pass
        conn.commit()
        conn.close()
        return True, None
    except Error as e:
        conn.close()
        return False, str(e)


def execute_query(query, params=None, fetch=False):
    conn = get_connection()
    if conn is None:
        return False, "Database connection failed"

    cursor = conn.cursor(dictionary=True) if fetch else conn.cursor()
    try:
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
            conn.close()
            return True, result
        else:
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            return True, last_id if last_id else True
    except Error as e:
        conn.close()
        return False, str(e)