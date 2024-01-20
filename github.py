from pydantic import BaseModel


class GithubEventHandler(BaseModel):
    github: Github

    def handle_event(self, event, payload):

        if event == 'issue_comment':
            print("issue comment triggered")
            self.handle_issue_comment_event(payload)

        if event == 'pull_request':
            self.handle_pull_request_event(payload)

    def handle_issue_comment_event(self, payload):
        if 'comment' in payload and '@ai-code-reviewer-bot' in payload['comment']['body']:
            repo_name = payload['repository']['full_name']
            issue_number = payload['issue']['number']
            repo = self.github.get_repo(repo_name)
            issue = repo.get_issue(number=issue_number)
            issue.create_comment("Did you call me?")

    def handle_pull_request_event(self, payload):
        if payload['action'] in ['opened', 'synchronize'] and '@ai-code-reviewer-bot' in payload['pull_request'][
            'body']:
            repo_name = payload['repository']['full_name']
            pr_number = payload['pull_request']['number']
            repo = self.github.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            files = pr.get_files()
            for file in files:
                print(f"File: {file.filename}, Changes: {file.patch}")
