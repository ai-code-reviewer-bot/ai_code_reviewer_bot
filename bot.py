import os

from flask import Flask, request, jsonify
from github import Github

app = Flask(__name__)

# Replace with your GitHub App's credentials
github_token = os.environ["GITHUB_APP_TOKEN"]
g = Github(github_token)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        payload = request.json
        # Check if the event is a pull request or issue comment
        if payload['action'] == 'created' and 'comment' in payload:
            comment_text = payload['comment']['body']
            # Check if the bot is mentioned in the comment
            if '@ai-code-reviewer-bot' in comment_text:
                # Respond to the mention
                repo_name = payload['repository']['full_name']
                issue_number = payload['issue']['number']
                repo = g.get_repo(repo_name)
                issue = repo.get_issue(number=issue_number)
                issue.create_comment("Did you call me?")
        return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
