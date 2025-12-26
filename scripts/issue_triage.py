import os
import json
import requests
from openai import OpenAI

# ---------- Config ----------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")
ISSUE_NUMBER = os.getenv("ISSUE_NUMBER")

client = OpenAI(api_key=OPENAI_API_KEY)

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# ---------- Fetch Issue ----------
issue_url = f"https://api.github.com/repos/{REPO}/issues/{ISSUE_NUMBER}"
issue_resp = requests.get(issue_url, headers=headers)
issue_resp.raise_for_status()

issue = issue_resp.json()
title = issue.get("title", "")
body = issue.get("body", "")

# ---------- Prompt ----------
prompt = f"""
You are a senior DevOps triage engineer.

Respond ONLY in valid JSON.
DO NOT add explanations.
DO NOT use markdown.
DO NOT add text outside JSON.

Required JSON schema:
{{
  "type": "bug | feature | security | question",
  "priority": "high | medium | low",
  "labels": ["label1", "label2"],
  "summary": "short summary"
}}

Issue title:
{title}

Issue body:
{body}
"""

# ---------- Call OpenAI ----------
response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": "You strictly output JSON only."},
        {"role": "user", "content": prompt}
    ],
    temperature=0
)

raw_response = response.choices[0].message.content.strip()

# ---------- Clean AI Output ----------
raw_response = raw_response.replace("```json", "").replace("```", "").strip()

# ---------- Parse JSON Safely ----------
try:
    result = json.loads(raw_response)
except json.JSONDecodeError:
    print("❌ JSON parsing failed")
    print("Raw AI response:")
    print(raw_response)

    # Fallback to avoid pipeline failure
    result = {
        "type": "unknown",
        "priority": "medium",
        "labels": ["needs-triage"],
        "summary": "AI could not confidently classify this issue."
    }

# ---------- Add Labels ----------
label_url = f"https://api.github.com/repos/{REPO}/issues/{ISSUE_NUMBER}/labels"
requests.post(
    label_url,
    headers=headers,
    json={"labels": result.get("labels", [])}
)

# ---------- Post Comment ----------
comment_body = f"""
### 🤖 AI Issue Triage

**Type:** {result.get("type")}
**Priority:** {result.get("priority")}

**Summary:**  
{result.get("summary")}
"""

comment_url = f"https://api.github.com/repos/{REPO}/issues/{ISSUE_NUMBER}/comments"
requests.post(
    comment_url,
    headers=headers,
    json={"body": comment_body}
)

print("✅ AI Issue Triage completed successfully")
