import json
import os
import subprocess
from datetime import UTC, datetime

from dotenv import load_dotenv

from CEACStatusBot import (
    EmailNotificationHandle,
    GitHubIssueNotificationHandle,
    NotificationManager,
    TelegramNotificationHandle,
)

FAILURE_RECORD_FILE = "failure_record.json"
STATUS_RECORD_FILE = "status_record.json"
DEFAULT_FAILURE_NOTIFY_AFTER_HOURS = 24

# --- Load .env if present, else fallback to system env ---
if os.path.exists(".env"):
    load_dotenv(dotenv_path=".env")  # loads into os.environ
else:
    print(".env not found, using system environment only")


def download_artifact():
    try:
        if not REPO:
            print("GITHUB_REPOSITORY not found, skip artifact download")
            return
        result = subprocess.run(
            ["gh", "api", f"repos/{REPO}/actions/artifacts"],
            capture_output=True,
            text=True,
        )
        artifacts = json.loads(result.stdout)
        artifact_exists = any(artifact["name"] == "status-artifact" for artifact in artifacts["artifacts"])

        if artifact_exists:
            subprocess.run(["gh", "run", "download", "--name", "status-artifact"], check=True)
        else:
            with open(STATUS_RECORD_FILE, "w", encoding="utf-8") as file:
                json.dump({"statuses": []}, file)
            with open(FAILURE_RECORD_FILE, "w", encoding="utf-8") as file:
                json.dump({}, file)
    except Exception as e:
        print(f"Error downloading artifact: {e}")
    finally:
        if not os.path.exists(STATUS_RECORD_FILE):
            with open(STATUS_RECORD_FILE, "w", encoding="utf-8") as file:
                json.dump({"statuses": []}, file)
        if not os.path.exists(FAILURE_RECORD_FILE):
            with open(FAILURE_RECORD_FILE, "w", encoding="utf-8") as file:
                json.dump({}, file)


def load_failure_state() -> dict:
    if not os.path.exists(FAILURE_RECORD_FILE):
        return {}
    with open(FAILURE_RECORD_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_failure_state(state: dict) -> None:
    with open(FAILURE_RECORD_FILE, "w", encoding="utf-8") as file:
        json.dump(state, file)


def clear_failure_state() -> None:
    with open(FAILURE_RECORD_FILE, "w", encoding="utf-8") as file:
        json.dump({}, file)


def handle_query_failure(error: Exception, handles: list, application_number: str) -> None:
    notify_after_hours = int(os.getenv("FAILURE_NOTIFY_AFTER_HOURS", DEFAULT_FAILURE_NOTIFY_AFTER_HOURS))
    notify_after_seconds = notify_after_hours * 3600
    now = datetime.now(UTC)

    state = load_failure_state()
    consecutive_failures = state.get("consecutive_failures", 0) + 1
    first_failure_at_str = state.get("first_failure_at")
    first_failure_at = datetime.fromisoformat(first_failure_at_str) if first_failure_at_str else now

    should_notify = False
    if (now - first_failure_at).total_seconds() >= notify_after_seconds:
        last_notified_at_str = state.get("last_notified_at")
        if last_notified_at_str:
            last_notified_at = datetime.fromisoformat(last_notified_at_str)
            should_notify = (now - last_notified_at).total_seconds() >= notify_after_seconds
        else:
            should_notify = True

    next_state = {
        "first_failure_at": first_failure_at.isoformat(),
        "last_failure_at": now.isoformat(),
        "consecutive_failures": consecutive_failures,
        "last_notified_at": state.get("last_notified_at"),
    }

    if should_notify:
        failure_result = {
            "success": False,
            "status": "Query Failed",
            "application_num_origin": application_number,
            "error": str(error),
            "consecutive_failures": consecutive_failures,
            "first_failure_at": first_failure_at.isoformat(),
            "last_failure_at": now.isoformat(),
        }
        for handle in handles:
            handle.send(failure_result)
        next_state["last_notified_at"] = now.isoformat()
    else:
        print(f"Query failed but notification suppressed. Consecutive failures: {consecutive_failures}.")

    save_failure_state(next_state)


# --- Read env vars with fallback ---
GH_TOKEN = os.getenv("GH_TOKEN")
if not GH_TOKEN:
    print("GH_TOKEN not found")
REPO = os.getenv("GITHUB_REPOSITORY")
if not REPO:
    REPO = os.getenv("REPO")
if not REPO:
    print("GITHUB_REPOSITORY/REPO not found")

if not os.path.exists(STATUS_RECORD_FILE) or not os.path.exists(FAILURE_RECORD_FILE):
    download_artifact()

try:
    LOCATION = os.environ["LOCATION"]
    NUMBER = os.environ["NUMBER"]
    PASSPORT_NUMBER = os.environ["PASSPORT_NUMBER"]
    SURNAME = os.environ["SURNAME"]
    notificationManager = NotificationManager(LOCATION, NUMBER, PASSPORT_NUMBER, SURNAME)
except KeyError as e:
    raise RuntimeError(f"Missing required env var: {e}") from e

notification_handles = []

# --- Optional: Email notifications ---
FROM = os.getenv("FROM")
TO = os.getenv("TO")
PASSWORD = os.getenv("PASSWORD")
SMTP = os.getenv("SMTP", "")

if FROM and TO and PASSWORD:
    emailNotificationHandle = EmailNotificationHandle(FROM, TO, PASSWORD, SMTP)
    notificationManager.addHandle(emailNotificationHandle)
    notification_handles.append(emailNotificationHandle)
else:
    print("Email notification config missing or incomplete")


# --- Optional: Telegram notifications ---
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")

if BOT_TOKEN and CHAT_ID:
    tgNotif = TelegramNotificationHandle(BOT_TOKEN, CHAT_ID)
    notificationManager.addHandle(tgNotif)
    notification_handles.append(tgNotif)
else:
    print("Telegram bot notification config missing or incomplete")

# --- Optional: GitHub issue notifications ---
if GH_TOKEN and REPO:
    ghNotif = GitHubIssueNotificationHandle(GH_TOKEN, REPO)
    notificationManager.addHandle(ghNotif)
    notification_handles.append(ghNotif)
else:
    print("GitHub issue notification config missing or incomplete")


# --- Send notifications ---
try:
    notificationManager.send()
    clear_failure_state()
except RuntimeError as error:
    handle_query_failure(error, notification_handles, NUMBER)
