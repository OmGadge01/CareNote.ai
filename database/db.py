import sqlite3
from pathlib import Path
from datetime import datetime


# ------------------------------------------------------------
# Database location
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "carenote.db"


# ------------------------------------------------------------
# Connection
# ------------------------------------------------------------

def get_connection():

    connection = sqlite3.connect(
        DB_PATH,
        check_same_thread=False,
    )

    connection.row_factory = sqlite3.Row

    return connection


# ------------------------------------------------------------
# Initialize database
# ------------------------------------------------------------

def init_db():

    connection = get_connection()

    cursor = connection.cursor()

    # Patients
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            condition TEXT
        )
        """
    )

    # Encounters
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS encounters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            visit_type TEXT,
            raw_note TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(patient_id)
                REFERENCES patients(id)
        )
        """
    )

    # Clinical documents
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clinical_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            encounter_id INTEGER NOT NULL,
            documentation TEXT NOT NULL,
            approved INTEGER DEFAULT 0,
            approved_by TEXT,
            approved_at TEXT,
            FOREIGN KEY(encounter_id)
                REFERENCES encounters(id)
        )
        """
    )

    # Follow-up tasks
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS followup_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            encounter_id INTEGER NOT NULL,
            task TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL,
            FOREIGN KEY(encounter_id)
                REFERENCES encounters(id)
        )
        """
    )

    connection.commit()

    connection.close()


# ------------------------------------------------------------
# Create encounter
# ------------------------------------------------------------

def create_encounter(
    patient_id: str,
    visit_type: str,
    raw_note: str,
):

    connection = get_connection()

    cursor = connection.cursor()

    created_at = datetime.now().isoformat()

    cursor.execute(
        """
        INSERT INTO encounters (
            patient_id,
            visit_type,
            raw_note,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            patient_id,
            visit_type,
            raw_note,
            created_at,
        ),
    )

    encounter_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return encounter_id


# ------------------------------------------------------------
# Save documentation
# ------------------------------------------------------------

def save_documentation(
    encounter_id: int,
    documentation: str,
    approved_by: str,
):

    connection = get_connection()

    cursor = connection.cursor()

    approved_at = datetime.now().isoformat()

    cursor.execute(
        """
        INSERT INTO clinical_documents (
            encounter_id,
            documentation,
            approved,
            approved_by,
            approved_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            encounter_id,
            documentation,
            1,
            approved_by,
            approved_at,
        ),
    )

    connection.commit()

    connection.close()


# ------------------------------------------------------------
# Save follow-up task
# ------------------------------------------------------------

def save_followup_task(
    encounter_id: int,
    task: str,
):

    if not task:
        return

    connection = get_connection()

    cursor = connection.cursor()

    created_at = datetime.now().isoformat()

    cursor.execute(
        """
        INSERT INTO followup_tasks (
            encounter_id,
            task,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            encounter_id,
            task,
            "pending",
            created_at,
        ),
    )

    connection.commit()

    connection.close()