import time

import jwt
import requests


def create_jwt(app_id, private_key_path):
    """
    Create a JWT (JSON Web Token) using the given app ID and private key file.
    """
    # Read the private key file
    with open(private_key_path, 'r') as file:
        private_key = file.read()

    # Generate the JWT
    payload = {
        'iat': int(time.time()),  # Issued at time
        'exp': int(time.time()) + (10 * 60),  # Expiration time (10 minutes)
        'iss': app_id  # Issuer (GitHub App ID)
    }

    token = jwt.encode(payload, private_key, algorithm='RS256')
    return token


def get_installation_access_token(jwt_token, installation_id):
    """
    Obtain an installation access token for the GitHub App using the JWT.
    """
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    url = f'https://api.github.com/app/installations/{installation_id}/access_tokens'
    response = requests.post(url, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()['token']


def get_github_access_token(app_id, private_key_path, installation_id):
    jwt_token = create_jwt(app_id, private_key_path)
    access_token = get_installation_access_token(jwt_token, installation_id)
    return access_token
