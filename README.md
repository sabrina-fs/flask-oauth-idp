# Flask OAuth Identity Provider

An example OAuth identity provider built on the Flask framework for Python.
Created primarily as a tool for testing VTEX ID's integrations with custom identity providers.

## Disclaimer

This tool was written for learning and testing purposes. It is not advised for use as-is in production environments.

## Setup

### Running locally

1. In the application's directory, create a virtual environment: `python3 -m venv .venv`
2. Activate it: `source .venv/bin/activate`
3. Install project requirements: `pip install -r requirements.txt`
4. The directory must contain a file named `.env` from which the application will obtain a secret key used to sign access tokens. A template is provided, as `.env.example`.  
You may replace the value of the `HS256_KEY` variable there with a value of your choice, then rename to file to just `.env`.  
5. Run the application: `flask --app app.py --debug run`

Consider using a cryptographically secure generator to create a 32+ bytes secret key. The `secrets` module from Python's standard library can help with that:
```python
from secrets import token_hex
key = token_hex(32)
```

When running the provider locally in this manner, no redirects will be performed, to facilitate testing and simulations. Instead, the authorization code will be returned to you in a JSON response.

### Protocol endpoints

The endpoints for each OAuth step are exposed at the following routes:
- Get authorization code: `/oauth/auth`;
- Get access token: `/oauth/get-access-token`;
- Get user information: `/oauth/get-user-info`.

### Integration parameters

On top of the endpoints, you will likely need additional information when setting up an integration between a client and the identity provider.

#### Key/field names

Clients may require you to specify the exact names expected used by the identity provider for certain fields during setup. Below is a mapping of the field names used in this project:
- Client ID: `client_id`
- Client secret: `client_secret`
- Authorization code: `code`
- Access token: `access_token`
- User ID: `user_id`
- User email: `user_email`
- User name: `user_name`

#### Access token request

You may need to specify the Content-Type the client should use when requesting access tokens from the provider. The one used in this project is `application/json`. 

#### Get user information request

Finally, a client may need you to specify how it should format the access token when requesting user information. This application expects it as a Bearer token; that is, a request header in the format: `Authorization: Bearer <token-here>`

#### Integrating with VTEX ID

Should you utilize this tool to test VTEX's OAuth integration, their specifications for custom providers, along with instructions for setting the integration up in the VTEX Admin, can found at:
- [Live link](https://developers.vtex.com/docs/guides/login-integration-guide-webstore-oauth2)
- [Web archive](https://web.archive.org/web/20240000000000*/https://developers.vtex.com/docs/guides/login-integration-guide-webstore-oauth2)

> The information covered in this section should cover everything needed to set up the integration through the Admin. Also note that the field names specified in the "Key/field names for integrations" section match the defaults suggested by the setup UI at the time of writing. 

### Identity provider

The application exposes three endpoints corresponding to each step in the OAuth flow, as per the VTEX documentations above.

The provider operates on a SQLite database containing two tables: `clients` and `users`, that store all required data.
An example database is provided with a default client and user already set up accordingly.

Client secrets and user passwords are hashed with argon2id, using the default parameters from [argon2-cffi](https://argon2-cffi.readthedocs.io/en/stable/), and re-hashed if different parameters are identified.  

Access tokens are JWTs with the HS256 algorithm. The signing key is assumed to be set in the `HS256_KEY` environment variable.

#### Database: clients table

The `clients` table contains the following columns, with `id` being its primary key:
- `id`: Client ID that uniquely identifies each client known to the IdP;
- `secret_hash`: hash of the Client Secret used to authenticate the client;
- `redirect_uri`: the client's authorized redirect URI to where the IdP will send the OAuth authorization code;
- `name`: client's friendly name.

These are the parameters set for the default client included in the example database:
- Client ID: "vid_example_7595436f49ed650b";
- Client secret: "d3966558b58a636c557c8d62e943c0fd"; 
- Redirect URI: "https://vtexid.vtex.com.br/VtexIdAuthSiteKnockout/ReceiveAuthorizationCode.ashx";
- Name: "VTEX ID Example".

> Note that, for use with VTEX ID, the Redirect URI is required to always have this value, as per its documented specifications.

#### Database: users table

The `users` table contains the following columns, with `email` being its primary key:
- `id`: random unique identifier tied to the user;
- `email`: user's email address;
- `password_hash`: hash of the user's password;
- `name`: user's name.

These are the parameters set for the default user included in the example database:
- Email: "test@example.com"
- Password: "Welcome-To-Flask-OAuth-01"