import os
import requests
from openai import OpenAI

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("REPO")
PR_NUMBER = os.getenv("PR_NUMBER")

client = OpenAI(api_key=OPENAI_API_KEY)

# GitHub API headers
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Fetch PR diff
diff_url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
pr_response = requests.get(diff_url, headers=headers)
pr_response.raise_for_status()

diff = pr_response.json().get("diff_url")
diff_content = requests.get(diff, headers=headers).text

# AI Prompt
prompt = f"""
You are a senior DevSecOps engineer.

Review the following pull request diff.
Provide:
1. Code quality issues
2. Security vulnerabilities (SAST)
3. Best practice improvements
4. Risk level (Low / Medium / High)

PR Diff:
{diff_content}
"""

# Call OpenAI
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are an expert DevSecOps code reviewer."},
        {"role": "user", "content": prompt}
    ],
)

review_comment = response.choices[0].message.content

# Post comment to PR
comment_url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
comment_payload = {"body": f"## 🤖 AI PR Review & SAST\n\n{review_comment}"}

comment_response = requests.post(comment_url, headers=headers, json=comment_payload)
comment_response.raise_for_status()

print("✅ AI PR Review completed successfully")
