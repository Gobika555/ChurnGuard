import sqlite3
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATABASE_DIR = os.path.join(
    BASE_DIR,
    "data"
)

DATABASE_PATH = os.path.join(
    DATABASE_DIR,
    "churnguard.db"
)


def get_db_connection():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def init_database():

    os.makedirs(
        DATABASE_DIR,
        exist_ok=True
    )

    connection = get_db_connection()

    cursor = connection.cursor()


    # USERS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


    # PREDICTIONS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            customer_id TEXT,
            prediction TEXT,
            probability REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id)
                REFERENCES users(id)
        )
    """)


    connection.commit()
    connection.close()


if __name__ == "__main__":

    init_database()

    print("=" * 60)
    print("CHURNGUARD DATABASE")
    print("=" * 60)

    print("\nDatabase initialized successfully!")

    print("\nDatabase location:")
    print(DATABASE_PATH)

    print("=" * 60)