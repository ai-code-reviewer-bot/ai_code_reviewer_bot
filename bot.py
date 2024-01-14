import os
import jwt
import time
import requests
from flask import Flask, request, jsonify
from github import Github

app = Flask(__name__)


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


@app.route('/webhook', methods=['POST'])
def webhook():
    print("webhook triggered")
    if request.method == 'POST':
        print("webhook post triggered")
        payload = request.json
        if payload['action'] == 'created' and 'comment' in payload:
            print("webhook post comment created triggered")
            comment_text = payload['comment']['body']
            print("comment_text ", comment_text)
            if '@ai-code-reviewer-bot' in comment_text:
                print("webhook post comment created mention triggered")
                repo_name = payload['repository']['full_name']
                issue_number = payload['issue']['number']
                repo = g.get_repo(repo_name)
                issue = repo.get_issue(number=issue_number)
                issue.create_comment("Did you call me?")
        return jsonify({'status': 'success'}), 200


if __name__ == '__main__':
    # Retrieve GitHub App credentials from environment variables
    app_id = os.environ["GITHUB_APP_ID"]  # Your GitHub App ID
    installation_id = os.environ["GITHUB_INSTALLATION_ID"]  # Installation ID for your GitHub App
    private_key_path = os.environ["GITHUB_PRIVATE_KEY_PATH"]  # Path to your private key file

    # Generate a JWT and use it to get an installation access token
    jwt_token = create_jwt(app_id, private_key_path)
    access_token = get_installation_access_token(jwt_token, installation_id)

    # Initialize the GitHub client with the access token
    g = Github(access_token)

    print("running")
    app.run(host='0.0.0.0', port=5000)
