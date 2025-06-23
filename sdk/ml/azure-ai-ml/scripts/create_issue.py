import os
import requests

GITHUB_API = "https://api.github.com"
REPO = "Azure/azure-sdk-for-python"
TOKEN = os.getenv("GITHUB_TOKEN")


def issue_exists(title):
    url = f"{GITHUB_API}/search/issues"
    headers = {"Authorization": f"token {TOKEN}"}
    params = {"q": f"{title} repo:{REPO}"}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    return data.get("total_count", 0) > 0


def create_issue(title, body, labels):
    url = f"{GITHUB_API}/repos/{REPO}/issues"
    headers = {"Authorization": f"token {TOKEN}"}
    payload = {"title": title, "body": body, "labels": labels}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print(f"Issue created: {title}")
    else:
        print(f"Failed to create issue: {title} - {response.text}")


with open("updates.txt", "r") as f:
    for line in f:
        dep, version = line.strip().split()
        title = f"Major version update available for {dep}"
        body = f"A major version update is available for `{dep}`. Latest version: {version}."
        labels = ["dependency", "major-update"]
        if not issue_exists(title):
            create_issue(title, body, labels)
        else:
            print(f"Issue already exists: {title}")
