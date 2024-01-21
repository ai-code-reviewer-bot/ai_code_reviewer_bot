import argparse
import logging

from flask import Flask, request, jsonify
from flask_limiter import Limiter, RateLimitExceeded
from github import Github

from github_event_handler import GithubEventHandler
from pydantic import BaseModel

from auth import get_github_access_token
from reviewer import FakeReviewer


class GithubBotApp(BaseModel):
    flask_app: Flask
    github_handler: GithubEventHandler
    port: int
    debug_mode: bool
    limiter: Limiter

    class Config:
        arbitrary_types_allowed = True

    def register_webhook(self):
        self.flask_app.add_url_rule('/webhook', view_func=self.webhook, methods=['POST'])

    def webhook(self):
        try:
            self.limiter.check()
        except RateLimitExceeded:
            return jsonify({'error': 'rate limit exceeded'}), 429
        event = request.headers.get('X-GitHub-Event', None)
        self.github_handler.handle_event(event, request.json)
        return jsonify({'status': 'success'}), 200

    def run(self):
        self.flask_app.run(host='0.0.0.0', port=self.port, debug=self.debug_mode)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--app_id', help='Github App ID')
    parser.add_argument('--installation_id', help='Github Installation ID')
    parser.add_argument('--private_key_path', help='Path to Github Private Key')
    parser.add_argument('--port', type=int, help='Port for the app')
    parser.add_argument('--debug_mode', type=bool, help='Debug flag')
    parser.add_argument('--rate_limit_per_minute', type=int, default=10, help='Rate limit')

    args = parser.parse_args()

    flask_app = Flask(__name__)
    limiter = Limiter(
        default_limits=[f"{args.rate_limit_per_minute} per minute"],
        key_func=lambda: "shared"
    )
    logger = flask_app.logger
    logger.setLevel(logging.DEBUG if args.debug_mode else logging.INFO)
    github = Github(
        get_github_access_token(
            app_id=args.app_id,
            private_key_path=args.private_key_path,
            installation_id=args.installation_id
        )
    )
    github_event_handler = GithubEventHandler(
        github=github,
        logger=logger,
        review_trigger="@ai-code-reviewer-bot",
        reviewer=FakeReviewer()
    )

    github_bot_app = GithubBotApp(
        flask_app=flask_app,
        github_handler=github_event_handler,
        port=args.port,
        debug_mode=args.debug_mode,
        limiter=limiter
    )
    github_bot_app.register_webhook()
    logger.debug("Staring bot.")
    github_bot_app.run()
