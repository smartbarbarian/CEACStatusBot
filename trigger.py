# Original Code Restore
# This is an example that indicates the original code to restore. Replace this comment
# with the actual original code from the earlier revision of trigger.py.


def notify_github_issue():
    import requests
    repo_owner = 'smartbarbarian'
    repo_name = 'CEACStatusBot'
    issue_title = 'Restored original code in trigger.py'
    issue_body = f'Original code restored successfully. Commit SHA: {original_sha}'
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/issues'
    headers = {'Authorization': f'token YOUR_GITHUB_TOKEN', 'Accept': 'application/vnd.github.v3+json'}
    response = requests.post(url, json={'title': issue_title, 'body': issue_body}, headers=headers)
    if response.status_code == 201:
        print('Issue created successfully.')
    else:
        print('Failed to create issue.')


# Call the function to notify GitHub issue
otify_github_issue()