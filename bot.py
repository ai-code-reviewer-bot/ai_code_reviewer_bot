import os
from flask import Flask, request, jsonify
from github import Github

from auth import create_jwt, get_installation_access_token

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    print("webhook triggered")
    if request.method == 'POST':
        payload = request.json
        event = request.headers.get('X-GitHub-Event', None)

        if event == 'issue_comment':
            print("issue comment triggered")
            handle_issue_comment_event(payload)

        return jsonify({'status': 'success'}), 200


def handle_issue_comment_event(payload):
    print(payload)
    if payload['action'] == 'created' and 'comment' in payload:
        print("payload good")
        comment_text = payload['comment']['body']
        if '@ai-code-reviewer-bot' in comment_text:
            print("bot tagged")
            repo_name = payload['repository']['full_name']
            issue_number = payload['issue']['number']
            repo = g.get_repo(repo_name)
            issue = repo.get_issue(number=issue_number)
            issue.create_comment("Did you call me?")


def handle_pull_request_event(payload):
    print(payload)
    if payload['action'] == 'opened' or payload['action'] == 'synchronize':
        print("payload good")
        comment_body = payload['pull_request']['body']
        if '@ai-code-reviewer-bot' in comment_body:
            print("bot tagged in pull request")
            repo_name = payload['repository']['full_name']
            pr_number = payload['pull_request']['number']
            repo = g.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            files = pr.get_files()

            for file in files:
                print(f"File: {file.filename}, Changes: {file.patch}")


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
    app.run(host='0.0.0.0', port=5103)
