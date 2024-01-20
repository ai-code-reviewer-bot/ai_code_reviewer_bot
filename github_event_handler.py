from logging import Logger
from typing import Dict

from github import Github
from pydantic import BaseModel


class GithubEventHandler(BaseModel):
    github: Github
    logger: Logger

    def handle_event(self, event: str, payload: Dict):
        self.logger.debug("Event")
        if event == 'issue_comment':
            self._handle_issue_comment_event(payload)
        elif event == 'pull_request':
            self._handle_pull_request_event(payload)

    def _handle_issue_comment_event(self, payload):
        self.logger.debug("IssueComment")
        self.logger.debug("payload: {}".format(payload))

        if 'comment' in payload and '@ai-code-reviewer-bot' in payload['comment']['body']:
            self.logger.debug("Payload valid")
            repo_name = payload['repository']['full_name']
            issue_number = payload['issue']['number']
            repo = self.github.get_repo(repo_name)
            issue = repo.get_issue(number=issue_number)
            issue.create_comment("Did you call me?")

    def _handle_pull_request_event(self, payload):
        self.logger.debug("PullRequest")
        self.logger.debug("payload: {}".format(payload))

        if (payload['action'] in ['opened', 'synchronize'] and
                '@ai-code-reviewer-bot' in payload['pull_request']['body']):
            self.logger.debug("Payload valid")
            repo_name = payload['repository']['full_name']
            pr_number = payload['pull_request']['number']
            repo = self.github.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            files = pr.get_files()
            for file in files:
                print(f"File: {file.filename}, Changes: {file.patch}")
