import os
import requests
from datetime import datetime

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
REPO_OWNER = 'smartbarbarian'
REPO_NAME = 'CEACStatusBot'

EMAIL_API_URL = 'https://api.emailservice.com/send'
TELEGRAM_API_URL = 'https://api.telegram.org/bot{}/sendMessage'
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

# Function to send email notifications

def send_email_notification(subject, message):
    requests.post(EMAIL_API_URL, json={'subject': subject, 'message': message})

# Function to send Telegram notifications

def send_telegram_notification(message):
    requests.post(TELEGRAM_API_URL.format(TELEGRAM_BOT_TOKEN), json={'chat_id': TELEGRAM_CHAT_ID, 'text': message})

# Function to create a GitHub issue notification

def create_github_issue(title, body):
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues'
    headers = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    issue = {'title': title, 'body': body}
    requests.post(url, headers=headers, json=issue)

# Function to check visa status

def check_visa_status(current_status):
    # Assume previous_status is fetched from a stored state (e.g., database)
    previous_status = get_previous_status() # Assumed function to fetch previous status

    if current_status != previous_status:
        # Notify about the status change
        email_subject = 'Visa Status Update'
        email_message = f'Your visa status has changed to: {current_status}'
        send_email_notification(email_subject, email_message)
        send_telegram_notification(email_message)

        # Create GitHub issue on status change
        issue_title = f'Visa Status Changed to: {current_status}'
        issue_body = f'The visa status for the application has changed from {previous_status} to {current_status}.'
        create_github_issue(issue_title, issue_body)
        save_status(current_status) # Assumed function to save current status

# Main execution block
if __name__ == '__main__':
    # Example usage, current_status would come from actual status check
    current_status = fetch_current_status() # Assumed function to check current status
    check_visa_status(current_status)