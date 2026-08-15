from database.db import get_connection, init_db


PATIENTS = [
    ("P001", "Alex Morgan", 45, "Hypertension"),
    ("P002", "Sarah Williams", 61, "Type 2 Diabetes"),
    ("P003", "David Brown", 37, "Asthma"),
]


def seed_patients():

    # Make sure database tables exist
    init_db()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.executemany(
        """
        INSERT OR IGNORE INTO patients (
            id,
            name,
            age,
            condition
        )
        VALUES (?, ?, ?, ?)
        """,
        PATIENTS,
    )

    connection.commit()
    connection.close()


if __name__ == "__main__":

    seed_patients()

    print("✓ Patients seeded")