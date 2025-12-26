import os
import requests
from openai import OpenAI

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
REPO = os.environ["GITHUB_REPOSITORY"]
PR_NUMBER = os.environ["PR_NUMBER"]

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Fetch PR files
files_url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/files"
response = requests.get(files_url, headers=headers)
response.raise_for_status()

findings = []

for file in response.json():
    patch = file.get("patch", "")
    filename = file.get("filename", "")

    if "PASSWORD" in patch or "SECRET" in patch:
        findings.append(f"Hardcoded secret detected in {filename}")

    if "eval(" in patch or "exec(" in patch:
        findings.append(f"Dangerous function usage (eval/exec) in {filename}")

if not findings:
    findings_text = "No obvious security issues detected."
else:
    findings_text = "\n".join(findings)

client = OpenAI(api_key=OPENAI_API_KEY)

ai_response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {
            "role": "system",
            "content": "You are an application security engineer."
        },
        {
            "role": "user",
            "content": f"""
Analyze the following security findings from a pull request.

Findings:
{findings_text}

For each issue:
- Explain why it is a security risk
- Provide a safe remediation recommendation
"""
        }
    ]
)

security_review = ai_response.choices[0].message.content.strip()

# Post comment
comment_url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
requests.post(
    comment_url,
    headers=headers,
    json={"body": f"## 🔐 AI SAST Security Review\n\n{security_review}"}
)

print("✅ AI SAST review completed")
