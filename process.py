import json, os, re, requests

TOKEN = os.environ["GITHUB_TOKEN"]
REPO = os.environ["GITHUB_REPOSITORY"]           # owner/repo
OWNER, REPO_NAME = REPO.split("/")

# Load state
with open("tasks.json", "r+") as f:
    data = json.load(f)

# Fetch open issues labeled "worker-result"
headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
issues_url = f"https://api.github.com/repos/{REPO}/issues?labels=worker-result&state=open"
resp = requests.get(issues_url, headers=headers)
issues = resp.json()

for issue in issues:
    body = issue.get("body", "")
    # Extract JSON proof from body
    match = re.search(r'```json\s*(\{.*?\})\s*```', body, re.DOTALL)
    if match:
        proof = json.loads(match.group(1))
        task_id = proof.get("taskId")
        # Mark task as completed
        data["pending"] = [t for t in data.get("pending", []) if t.get("id") != task_id]
        if "completed" not in data:
            data["completed"] = []
        data["completed"].append(proof)
        # Award points (simple: +10 per task)
        submitter = issue.get("user", {}).get("login", "anonymous")
        data["points"][submitter] = data["points"].get(submitter, 0) + 10

        # Close the issue
        close_url = f"https://api.github.com/repos/{REPO}/issues/{issue['number']}"
        requests.patch(close_url, json={"state": "closed"}, headers=headers)

# Write back state
with open("tasks.json", "w") as f:
    json.dump(data, f, indent=2)
