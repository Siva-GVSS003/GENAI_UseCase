import os
import requests
from openai import OpenAI

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

REPO = os.environ["GITHUB_REPOSITORY"]
PR_NUMBER = os.environ["PR_NUMBER"]

# Fetch PR files
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

files_url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/files"
files_response = requests.get(files_url, headers=headers)
files_response.raise_for_status()

diff_text = ""
for file in files_response.json():
    if file.get("patch"):
        diff_text += f"\nFile: {file['filename']}\n{file['patch']}\n"

client = OpenAI(api_key=OPENAI_API_KEY)

ai_response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {
            "role": "system",
            "content": "You are a senior software architect reviewing a pull request."
        },
        {
            "role": "user",
            "content": f"""
Review the following pull request diff.
Provide:
- Code quality feedback
- Possible bugs
- Best practice improvements
- DevOps or security suggestions

PR Diff:
{diff_text}
"""
        }
    ]
)

review_comment = ai_response.choices[0].message.content

# Post comment to PR
comment_url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
requests.post(
    comment_url,
    headers=headers,
    json={"body": f"## 🤖 AI PR Review\n\n{review_comment}"}
)

print("✅ AI PR Review completed")
