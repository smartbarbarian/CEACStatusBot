import requests

# Other existing imports


def create_github_issue(visa_status):
    # Define your GitHub API endpoint and repository details
    repo_owner = 'smartbarbarian'
    repo_name = 'CEACStatusBot'
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/issues'

    # Prepare the issue data
    title = f'Visa Status Changed to {visa_status}'
    body = f'The visa status has been updated to: {visa_status}'
    issue_data = {'title': title, 'body': body}

    # GitHub token for authentication (ensure you keep this secret)
    headers = {'Authorization': 'token YOUR_GITHUB_TOKEN'}  # Replace with your GitHub token

    # Send the request to create the issue
    response = requests.post(url, json=issue_data, headers=headers)

    if response.status_code == 201:
        print('Issue created successfully.')
    else:
        print(f'Failed to create issue: {response.content}')


def send_notification(visa_status):
    # Original notification logic
    notificationManager.send()
    # Call the function to create a GitHub issue
    create_github_issue(visa_status)  # Ensure you pass the correct visa status variable

# Keep all original code below this comment

