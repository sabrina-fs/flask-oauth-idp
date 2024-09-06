import jwt
import os
from dotenv import load_dotenv
from time import time
from secrets import token_hex
from uuid import uuid4

load_dotenv()
key = os.getenv("HS256_KEY")


class AuthorizationCode:
    """Handles the authorization code."""

    def __init__(self):
        self.value = None
        self.client_id = None
        self.email = None
        self.iat = None
        self.exp = None

    def generate(self, client_id, email, exp):
        """Generates a new authorization code or access token, valid for a specific client and user combination."""
        self.client_id = client_id
        self.value = f"{token_hex(32)}"
        self.email = email
        self.iat = int(time())
        self.exp = exp

    def validate(self, client_id, value):
        """Validates if a request's token is legitimate, issued for the requesting client, and not expired."""
        if (client_id != self.client_id) or (value != self.value) or (int(time()) > self.iat + self.exp):
            return False
        else:
            return True


def generate_jwt(audience, subject):
    now = time()
    duration = 3600
    expiration = now + duration
    payload = {"aud": audience, "exp": expiration, "iat": now, "sub": subject, "jti": str(uuid4())}
    encoded_token = jwt.encode(payload, key, algorithm="HS256")
    return {"value": encoded_token, "duration": duration}


def verify_jwt(encoded_token):
    decoded_token = jwt.decode(encoded_token, key, algorithms="HS256", options={"verify_aud": False})
    return decoded_token
