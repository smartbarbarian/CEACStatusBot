import json

import requests

from .handle import NotificationHandle


class GitHubIssueNotificationHandle(NotificationHandle):
    def __init__(self, token: str, repo: str) -> None:
        super().__init__()
        self.__token = token
        self.__repo = repo

    def send(self, result):
        title = f"[CEACStatusBot] {result.get('application_num_origin', 'unknown')}: {result.get('status', 'Unknown')}"
        body = f"```json\n{json.dumps(result, ensure_ascii=False, indent=2)}\n```"
        api_url = f"https://api.github.com/repos/{self.__repo}/issues"
        response = requests.post(
            api_url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.__token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            json={"title": title, "body": body},
            timeout=30,
        )
        if response.status_code in (200, 201):
            print("GitHub issue created successfully")
        else:
            print(f"Failed to create GitHub issue: {response.status_code}, {response.text}")
