import os
import json
import requests
from openai import OpenAI

# GitHub environment
repo = os.environ["GITHUB_REPOSITORY"]   # owner/repo
token = os.environ["GITHUB_TOKEN"]
event_path = os.environ["GITHUB_EVENT_PATH"]

# Read PR number from event payload
with open(event_path, "r") as f:
    event = json.load(f)

pr_number = event["pull_request"]["number"]

# GitHub API
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json"
}

# Fetch PR details
pr_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
pr_response = requests.get(pr_url, headers=headers)
pr_response.raise_for_status()

pr_data = pr_response.json()

# Combine PR title + body for AI review
pr_text = f"""
Title: {pr_data['title']}

Description:
{pr_data.get('body', '')}
"""

# OpenAI client
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

ai_response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": "You are a senior DevSecOps reviewer."},
        {"role": "user", "content": f"Review this PR and identify risks:\n{pr_text}"}
    ]
)

review_comment = ai_response.choices[0].message.content

# Post comment to PR
comment_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
requests.post(
    comment_url,
    headers=headers,
    json={"body": review_comment}
)

print("✅ AI PR Review completed successfully")
