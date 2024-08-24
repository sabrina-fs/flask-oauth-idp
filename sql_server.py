import sqlite3
from pathlib import Path

db_path = Path(__file__).parent.resolve() / "database.db"
conn = sqlite3.connect(db_path, check_same_thread=False)

def fetch_client(client_id, fields):
    """Queries the database for client data."""
    columns = ", ".join(fields)
    with conn:
        result = conn.execute(f"SELECT {columns} FROM clients WHERE id = ?;", [client_id]).fetchall()

    if columns == "secret_hash":  # Hash must be extracted from the results tuple before operations.
        return validate(result)[0]
    else:
        return validate(result)


def fetch_user(email, fields):
    """Queries the database for user data."""
    columns = ", ".join(fields)
    with conn:
        result = conn.execute(f"SELECT {columns} FROM users WHERE email = ?;", [email]).fetchall()

    if columns == "password_hash":  # Hash must be extracted from the results tuple before operations.
        return validate(result)[0]
    else:
        return validate(result)


def update_user_hash(email, new_hash):
    """Updates a password's hash if the hashing parameters have been updated since the last write."""
    with conn:
        conn.execute("UPDATE users SET password_hash = ? WHERE email = ?;", [new_hash, email])


def update_client_hash(client_id, new_hash):
    """Updates a client secret's hash if the hashing parameters have been updated since the last write."""
    with conn:
        conn.execute("UPDATE clients SET secret_hash = ? WHERE id = ?;", [new_hash, client_id])


def validate(result):
    """Verifies database consistency status by checking the uniqueness of primary keys in query results."""
    if len(result) > 1:
        raise sqlite3.IntegrityError("Error: database is in inconsistent state.")
    elif len(result) == 0:
        return None
    else:
        return result[0]
