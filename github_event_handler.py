from logging import Logger
from typing import Dict

from github import Github, PullRequest, Repository, Commit
from pydantic import BaseModel

from reviewer import Reviewer


class GithubEventHandler(BaseModel):
    github: Github
    logger: Logger
    review_trigger: str
    reviewer: Reviewer

    class Config:
        arbitrary_types_allowed = True

    def handle_event(self, event: str, payload: Dict):
        self.logger.debug("Event")
        if event == 'issue_comment':
            self._handle_issue_comment_event(payload)

    def is_review_requested(self, payload: Dict) -> bool:
        comment_belongs_to_pull_request = 'issue' in payload and 'pull_request' in payload['issue']
        proper_comment = 'comment' in payload and "body" in payload['comment']
        if comment_belongs_to_pull_request and proper_comment:
            comment_text = payload['comment']['body']
            return self.review_trigger in comment_text
        return False

    def extract_pull_request_number(self, pull_request_url: str) -> int:
        return int(pull_request_url.split('/')[-1])

    def get_repository(self, payload: Dict) -> Repository:
        repo_name = payload['repository']['full_name']
        repo = self.github.get_repo(repo_name)
        return repo

    def get_pull_request(self, repository: Repository, payload: Dict) -> PullRequest:
        pull_request_url = payload['issue']['pull_request']['url']
        pull_request_number = self.extract_pull_request_number(pull_request_url)
        pull_request = repository.get_pull(pull_request_number)
        return pull_request

    def get_latest_commit(self, repository: Repository, pull_request: PullRequest) -> Commit:
        commit = repository.get_commit(pull_request.head.sha)
        return commit

    def add_lines_to_hunk(self, hunk: str) -> str:
        result = ""
        for line_number, line in enumerate(hunk):
            result += f"{line_number}: line\n"
        return result

    def _handle_issue_comment_event(self, payload):
        self.logger.debug("IssueComment")
        self.logger.debug("payload: {}".format(payload))

        if self.is_review_requested(payload):
            self.logger.debug("Review requested")
            repository = self.get_repository(payload)
            pull_request: PullRequest = self.get_pull_request(repository, payload)
            commit = self.get_latest_commit(repository, pull_request)
            files = pull_request.get_files()
            for file in files:
                hunk_with_line_numbers = self.add_lines_to_hunk(file.patch)
                reviews = self.reviewer.review_file_changes(hunk_with_line_numbers)
                for review in reviews:
                    try:
                        pull_request.create_review_comment(
                            body=review.comment,
                            commit_id=commit,
                            path=file.filename,
                            position=review.line_number
                        )
                        self.logger.debug(f"Posted review on {file.filename}")
                    except Exception as e:
                        self.logger.error(f"Error posting comment: {str(e)}")
