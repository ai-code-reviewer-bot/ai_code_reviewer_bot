from logging import Logger
from typing import Dict

from github import Github, PullRequest
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

    def get_pull_request(self, payload: Dict) -> PullRequest:
        repo_name = payload['repository']['full_name']
        pull_request_url = payload['issue']['pull_request']['url']
        pull_request_number = self.extract_pull_request_number(pull_request_url)
        repo = self.github.get_repo(repo_name)
        pull_request = repo.get_pull(pull_request_number)
        return pull_request

    def _handle_issue_comment_event(self, payload):
        self.logger.debug("IssueComment")
        self.logger.debug("payload: {}".format(payload))

        if self.is_review_requested(payload):
            self.logger.debug("Review requested")
            repo_name = payload['repository']['full_name']
            repo = self.github.get_repo(repo_name)
            pull_request: PullRequest = self.get_pull_request(payload)
            commit = repo.get_commit(pull_request.head.sha)
            files = pull_request.get_files()
            for file in files:
                reviews = self.reviewer.review_file_changes(file.patch)
                for review in reviews:
                    review_line = review.line_number
                    review_text = review.comment
                    try:
                        pull_request.create_review_comment(
                            body=review_text,
                            commit=commit,
                            path=file.filename,
                        )
                        self.logger.debug(f"Posted review on {file.filename} at line {review_line}: {review_text}")
                    except Exception as e:
                        self.logger.error(f"Error posting comment: {str(e)}")
