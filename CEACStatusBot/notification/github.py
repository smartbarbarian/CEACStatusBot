import json
import os
import subprocess

import requests

from .handle import NotificationHandle


class GitHubIssueNotificationHandle(NotificationHandle):
    def __init__(self, token: str, repository: str) -> None:
        super().__init__()
        self.__api = f"https://api.github.com/repos/{repository}/issues"
        self.__headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def send(self, result):
        title = f"[CEACStatusBot] {result.get('application_num_origin', 'UNKNOWN')} : {result.get('status', 'UNKNOWN')}"
        body = "```json\n" + json.dumps(result, ensure_ascii=False, indent=2) + "\n```"
        resp = requests.post(self.__api, headers=self.__headers, json={"title": title, "body": body}, timeout=30)
        if not resp.ok:
            raise RuntimeError(f"Create GitHub issue failed: {resp.status_code} {resp.text}")


def infer_repository_from_git() -> str:
    repo_from_env = os.getenv("GITHUB_REPOSITORY", "")
    if repo_from_env:
        return repo_from_env

    try:
        remote_url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"], text=True).strip()
    except Exception:
        return ""

    if remote_url.endswith(".git"):
        remote_url = remote_url[:-4]
    if remote_url.startswith("git@github.com:"):
        return remote_url.replace("git@github.com:", "", 1)
    if "github.com/" in remote_url:
        return remote_url.split("github.com/", 1)[1]
    return ""
