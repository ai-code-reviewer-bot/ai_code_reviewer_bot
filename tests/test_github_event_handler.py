import json
import unittest
from logging import Logger
from pathlib import Path
from unittest.mock import MagicMock

from github import Github

from github_event_handler import GithubEventHandler


class TestGithubEventHandler(unittest.TestCase):
    def setUp(self):
        data_path = Path(__file__).parent / 'data' / 'pull_request_comment_payload.json'
        with open(data_path, 'r') as json_file:
            self.payload = json.load(json_file)

        github_magic_mock = MagicMock()
        github_magic_mock.__class__ = Github
        self.github_event_handler = GithubEventHandler(
            github=github_magic_mock,
            logger=Logger("test"),
            review_trigger="@ai-code-reviewer-bot"
        )

    def test_is_review_requested(self):
        self.assertFalse(
            self.github_event_handler.is_review_requested(
                self.payload
            )
        )
        self.payload["comment"]["body"] = "@ai-code-reviewer-bot pls, review"
        self.assertTrue(
            self.github_event_handler.is_review_requested(
                self.payload
            )
        )

    def test_get_pull_request(self):
        self.github_event_handler.get_pull_request(self.payload)
