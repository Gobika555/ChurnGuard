from database import get_db_connection


# ============================================================
# USER FUNCTIONS
# ============================================================

def create_user(username, email, password):
    """
    Create a new user in the database.
    """

    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
            """,
            (username, email, password)
        )

        connection.commit()

        user_id = cursor.lastrowid

        return user_id

    except Exception:

        connection.rollback()

        return None

    finally:

        connection.close()


# ============================================================
# FIND USER BY EMAIL
# ============================================================

def get_user_by_email(email):
    """
    Retrieve a user using their email.
    """

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        """,
        (email,)
    )

    user = cursor.fetchone()

    connection.close()

    return user


# ============================================================
# FIND USER BY ID
# ============================================================

def get_user_by_id(user_id):
    """
    Retrieve a user using their ID.
    """

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    connection.close()

    return user


# ============================================================
# SAVE PREDICTION
# ============================================================

def save_prediction(
    user_id,
    customer_id,
    prediction,
    probability
):
    """
    Save a prediction to prediction history.
    """

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO predictions
        (
            user_id,
            customer_id,
            prediction,
            probability
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            customer_id,
            prediction,
            probability
        )
    )

    connection.commit()

    connection.close()


# ============================================================
# GET USER PREDICTION HISTORY
# ============================================================

def get_user_predictions(user_id):
    """
    Return all predictions belonging to a user.
    """

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            customer_id,
            prediction,
            probability,
            created_at
        FROM predictions
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (user_id,)
    )

    predictions = cursor.fetchall()

    connection.close()

    return predictions