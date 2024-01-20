from logging import Logger
from typing import Dict

from github import Github, PullRequest
from pydantic import BaseModel


class GithubEventHandler(BaseModel):
    github: Github
    logger: Logger

    def handle_event(self, event: str, payload: Dict):
        self.logger.debug("Event")
        if event == 'issue_comment':
            self._handle_issue_comment_event(payload)

    def is_review_requested(self, payload: Dict) -> bool:
        pass

    def get_pull_request(self, payload: Dict) -> PullRequest:
        repo_name = payload['repository']['full_name']
        pull_request_number = payload['pull_request']['number']
        repo = self.github.get_repo(repo_name)
        pull_request = repo.get_pull(pull_request_number)
        return pull_request

    def _handle_issue_comment_event(self, payload):
        self.logger.debug("IssueComment")
        self.logger.debug("payload: {}".format(payload))

        if self.is_review_requested(payload):
            self.logger.debug("Review requested")
            pull_request = self.get_pull_request(payload)
            files = pull_request.get_files()
            for file in files:
                self.logger.debug(f"File: {file.filename}, Changes: {file.patch}")
