import os
import requests
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")
ISSUE_NUMBER = os.getenv("ISSUE_NUMBER")

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Fetch issue details
issue_url = f"https://api.github.com/repos/{REPO}/issues/{ISSUE_NUMBER}"
issue = requests.get(issue_url, headers=headers).json()

title = issue.get("title", "")
body = issue.get("body", "")

prompt = f"""
You are a senior DevOps triage engineer.

Analyze the GitHub issue below and respond in JSON with:
- type (bug / feature / security / question)
- priority (high / medium / low)
- labels (array)
- summary (1–2 lines)

Issue title:
{title}

Issue body:
{body}
"""

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": "You classify GitHub issues strictly."},
        {"role": "user", "content": prompt}
    ]
)

import json
result = json.loads(response.choices[0].message.content)

# Add labels
label_url = f"https://api.github.com/repos/{REPO}/issues/{ISSUE_NUMBER}/labels"
requests.post(label_url, headers=headers, json={"labels": result["labels"]})

# Post AI summary comment
comment_url = f"https://api.github.com/repos/{REPO}/issues/{ISSUE_NUMBER}/comments"
requests.post(
    comment_url,
    headers=headers,
    json={
        "body": f"""
### 🤖 AI Issue Triage

**Type:** {result['type']}
**Priority:** {result['priority']}

**Summary:**  
{result['summary']}
"""
    }
)
