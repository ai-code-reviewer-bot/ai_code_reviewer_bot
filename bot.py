import os
from typing import Any

from flask import Flask, request, jsonify
from github import GithubEventHandler
from pydantic import BaseModel

from auth import create_jwt, get_installation_access_token

app = Flask(__name__)


class App(BaseModel):
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
    app_id = os.environ["GITHUB_APP_ID"]
    installation_id = os.environ["GITHUB_INSTALLATION_ID"]
    private_key_path = os.environ["GITHUB_PRIVATE_KEY_PATH"]
    port = int(os.environ["PORT"])
    debug_mode = bool(int(os.environ["DEBUG"]))

    jwt_token = create_jwt(app_id, private_key_path)
    access_token = get_installation_access_token(jwt_token, installation_id)

    App().run()
