import json
import unittest
from logging import Logger
from pathlib import Path

from github import Github

from github_event_handler import GithubEventHandler
from reviewer import FakeReviewer


class TestGithubEventHandler(unittest.TestCase):
    def setUp(self):
        data_path = Path(__file__).parent / 'data' / 'pull_request_comment_payload.json'
        with open(data_path, 'r') as json_file:
            self.payload = json.load(json_file)

        github = Github()
        self.github_event_handler = GithubEventHandler(
            github=github,
            logger=Logger("test"),
            review_trigger="@ai-code-reviewer-bot",
            reviewer=FakeReviewer()
        )

    def test_is_review_requested(self):
        self.assertTrue(
            self.github_event_handler.is_review_requested(
                self.payload
            )
        )
        self.payload["comment"]["body"] = "just random comment"
        self.assertFalse(
            self.github_event_handler.is_review_requested(
                self.payload
            )
        )

    def test_get_pull_request(self):
        repository = self.github_event_handler.get_repository(self.payload)
        pull_request = self.github_event_handler.get_pull_request(repository, self.payload)
        self.assertEqual(pull_request.number, 1)
