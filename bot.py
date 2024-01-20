import argparse
from typing import Any

from flask import Flask, request, jsonify
from github import Github

from github_event_handler import GithubEventHandler
from pydantic import BaseModel

from auth import get_github_access_token

app = Flask(__name__)


class GithubBotApp(BaseModel):
    github_handler: GithubEventHandler
    port: int
    debug_mode: bool

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.app = Flask(__name__)
        self.app.add_url_rule('/webhook', view_func=self.webhook, methods=['POST'])

    def webhook(self):
        if request.method == 'POST':
            payload = request.json
            event = request.headers.get('X-GitHub-Event', None)
            self.github_handler.handle_event(event, payload)
            return jsonify({'status': 'success'}), 200

    def run(self):
        self.app.run(host='0.0.0.0', port=5103)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--app_id', help='Github App ID')
    parser.add_argument('--installation_id', help='Github Installation ID')
    parser.add_argument('--private_key_path', help='Path to Github Private Key')
    parser.add_argument('--port', type=int, help='Port for the app')
    parser.add_argument('--debug', type=bool, help='Debug flag')

    args = parser.parse_args()

    GithubBotApp(
        github_handler=GithubEventHandler(
            github=Github(
                get_github_access_token(
                    app_id=args.app_id,
                    private_key_path=args.private_key_path,
                    installation_id=args.installation_id
                )
            )
        ),
        port=args.port,
        debug_mode=args.debug_mode
    ).run()
