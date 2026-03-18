import requests
import json

# Function to notify about visa status change

def notify_github_issue(visa_status):
    url = 'https://api.github.com/repos/smartbarbarian/CEACStatusBot/issues'
    headers = {'Authorization': 'token YOUR_GITHUB_TOKEN','Accept': 'application/vnd.github.v3+json'}
    issue_data = {
        'title': 'Visa Status Changed',
        'body': f'The visa status has changed to: {visa_status}',
        'labels': ['visa', 'notification']
    }

    response = requests.post(url, headers=headers, data=json.dumps(issue_data))

    if response.status_code == 201:
        print('Notification sent successfully.')
    else:
        print('Failed to send notification:', response.content)

# Example usage
visa_status = 'Approved'  # This should be dynamically set based on your application logic
notify_github_issue(visa_status)