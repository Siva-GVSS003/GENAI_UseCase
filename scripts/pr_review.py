import os
import requests
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = os.getenv("PR_NUMBER")

# Get PR diff
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3.diff"
}

diff_url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
diff = requests.get(diff_url, headers=headers).text

prompt = f"""
You are a senior DevSecOps engineer.

Review the following pull request diff.
Focus on:
- Bugs
- Security issues
- Code quality
- Best practices

Provide actionable feedback.

Diff:
{diff}
"""

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": "You are a strict code reviewer."},
        {"role": "user", "content": prompt}
    ]
)

review = response.choices[0].message.content

# Post comment to PR
comment_url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
requests.post(
    comment_url,
    headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    },
    json={"body": review}
)
