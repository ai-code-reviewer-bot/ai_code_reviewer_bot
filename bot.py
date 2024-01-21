import logging
import os

from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from github import Github

from auth import get_github_access_token
from github_event_handler import GithubEventHandler
from reviewer import TestReviewer

app_id = os.getenv('APP_ID')
installation_id = os.getenv('INSTALLATION_ID')
private_key_path = os.getenv('PRIVATE_KEY_PATH')


def create_github_bot() -> Flask:
    github_bot_app = Flask(__name__)
    limiter = Limiter(key_func=get_remote_address)
    logger = github_bot_app.logger

    github = Github(
        get_github_access_token(
            app_id=app_id, private_key_path=private_key_path, installation_id=installation_id
        )
    )
    github_event_handler = GithubEventHandler(
        github=github, logger=logger, review_trigger="@ai-code-reviewer-bot", reviewer=TestReviewer()
    )

    @github_bot_app.route('/webhook', methods=['POST'])
    @limiter.limit("10 per minute")
    def webhook():
        event = request.headers.get('X-GitHub-Event', None)
        github_event_handler.handle_event(event, request.json)
        return jsonify({'status': 'success'}), 200

    return github_bot_app


github_bot = create_github_bot()


if __name__ == '__main__':
    github_bot.logger.setLevel(logging.DEBUG)
    github_bot.run(host='0.0.0.0', port=5103, debug=True)
