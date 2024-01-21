import os
import argparse
import logging

from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from github import Github

from github_event_handler import GithubEventHandler
from auth import get_github_access_token
from reviewer import TestReviewer


def create_github_bot() -> Flask:
    parser = argparse.ArgumentParser()
    parser.add_argument('--app_id', default=os.getenv('APP_ID'), help='Github App ID')
    parser.add_argument('--installation_id', default=os.getenv('INSTALLATION_ID'), help='Github Installation ID')
    parser.add_argument('--private_key_path', default=os.getenv('PRIVATE_KEY_PATH'), help='Path to Github Private Key')

    args = parser.parse_args()

    github_bot_app = Flask(__name__)
    limiter = Limiter(key_func=get_remote_address)
    logger = app.logger

    github = Github(
        get_github_access_token(
            app_id=args.app_id, private_key_path=args.private_key_path, installation_id=args.installation_id
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
