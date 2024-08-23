from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sql_server import fetch_user, fetch_client, update_user_hash, update_client_hash

argon2id = PasswordHasher()


def authenticate_user(email, password):
    """Validates user credentials against the database."""
    try:
        db_hash = fetch_user(email, fields=["password_hash"])
        argon2id.verify(db_hash, password)
    except (TypeError, VerifyMismatchError):
        return False
    else:
        if argon2id.check_needs_rehash(db_hash):
            new_hash = argon2id.hash(password)
            update_user_hash(email, new_hash)
        return True


def authenticate_client(client_id, client_secret):
    """Validates client credentials against the database."""
    db_hash = fetch_client(client_id, fields=["secret_hash"])

    try:
        argon2id.verify(db_hash, client_secret)
    except (TypeError, VerifyMismatchError):
        return False
    else:
        if argon2id.check_needs_rehash(db_hash):
            new_hash = argon2id.hash(client_secret)
            update_client_hash(client_id, new_hash)
        return True


def validate_client(req):
    """Validates a request's client parameters against the database."""
    try:
        (db_client_id, db_client_secret, db_redirect_uri) = fetch_client(
            req["client_id"], fields=["id", "secret_hash", "redirect_uri"])
        if not authenticate_client(req["client_id"], req["client_secret"]) or (req["redirect_uri"] != db_redirect_uri):
            return False
        else:
            return True
    except TypeError:
        return False
