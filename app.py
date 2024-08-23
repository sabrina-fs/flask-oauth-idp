from flask import Flask, request, render_template, redirect
from flask_talisman import Talisman
from talisman_settings import talisman_settings
from token_utils import AuthorizationCode, generate_jwt, verify_jwt
from sql_server import fetch_user, fetch_client
from validations import authenticate_user, validate_client
from werkzeug.exceptions import BadRequest

app = Flask(__name__)
authorization_code = AuthorizationCode()
if not app.debug:
    Talisman(app, **talisman_settings)


@app.get('/oauth/auth')
def get_login():
    """Gets the provider's login page."""
    return render_template('login.html'), 200


@app.post('/oauth/auth')
def get_authorization_code():
    """Performs login and returns an authorization code to the client's redirect URI."""
    try:
        client_params = (client_id, redirect_uri) = request.args.get("client_id"), request.args.get("redirect_uri")
        state = request.args.get("state")
        email, password = request.form["email"], request.form["password"]
    except BadRequest:
        return "Bad request.", 400

    if None in client_params or client_params != fetch_client(client_id, fields=["id", "redirect_uri"]):
        return "Invalid client.", 403
    if not authenticate_user(email, password):
        return "Invalid credentials.", 403

    authorization_code.generate(client_id, email, exp=60)

    if app.debug:
        code_response = {"code": authorization_code.value, "state": state, "redirect_uri": redirect_uri}
        return code_response, 200
    else:
        return redirect(f"{redirect_uri}?code={authorization_code.value}&state={state}")


@app.post("/oauth/get-access-token")
def get_access_token():
    """Exchanges authorization code for access token."""
    req = request.get_json()

    if not validate_client(req):
        return "Invalid client.", 403
    if not authorization_code.validate(req["client_id"], req["code"]):
        return "Invalid authorization code.", 403

    authorization_code.exp = 0
    access_token = generate_jwt(audience=req["client_id"], subject=authorization_code.email)
    token_response = {"access_token": access_token["value"], "expires_in": access_token["duration"]}
    return token_response, 200


@app.get("/oauth/get-user-info")
def get_user_info():
    """Exchanges access token for user info."""
    authorization_header = request.headers.get("Authorization", "")
    req_token = authorization_header.replace("Bearer ", "")

    try:
        access_token = verify_jwt(req_token)
    except:
        return "Invalid access token.", 403
    else:
        user_id, user_email, user_name = (fetch_user(access_token["sub"], fields=["id", "email", "name"]))
        user_info = {"user_id": user_id, "user_email": user_email, "user_name": user_name}
        return user_info, 200
