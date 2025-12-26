import os
import json
import requests
from openai import OpenAI
import subprocess

# ---------- Config ----------
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
PR_NUMBER = os.environ["PR_NUMBER"]
REPO = os.environ["GITHUB_REPOSITORY"]

client = OpenAI(api_key=OPENAI_API_KEY)

# ---------- Run Bandit (Python SAST) ----------
print("🔍 Running Bandit security scan...")
subprocess.run(["bandit", "-r", "./", "-f", "json", "-o", "bandit_report.json"], check=True)

with open("bandit_report.json", "r") as f:
    bandit_data = json.load(f)

issues = bandit_data.get("results", [])

if not issues:
    ai_summary = "No security issues detected by Bandit."
else:
    # ---------- Prepare prompt for AI ----------
    issues_text = json.dumps(issues, indent=2)
    prompt = f"""
You are a senior security engineer.
Analyze the following SAST (Bandit) security findings.
Provide:
- Clear explanation of each issue
- Severity ranking (low, medium, high)
- Recommended fixes
- Summary at the end

SAST Findings:
{issues_text}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a helpful security expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    ai_summary = response.choices[0].message.content

# ---------- Post comment to PR ----------
comment_url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"

comment_body = f"## 🤖 AI SAST Review\n\n{ai_summary}"

res = requests.post(
    comment_url,
    headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    },
    json={"body": comment_body}
)

if res.status_code == 201:
    print("✅ AI SAST Review posted successfully")
else:
    print("❌ Failed to post AI SAST Review")
    print(res.text)
