import json, os, re, requests

TOKEN = os.environ["GITHUB_TOKEN"]
REPO = os.environ["GITHUB_REPOSITORY"]
OWNER, REPO_NAME = REPO.split("/")

with open("tasks.json") as f:
    data = json.load(f)

headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
issues_url = f"https://api.github.com/repos/{REPO}/issues?labels=worker-result&state=open"
resp = requests.get(issues_url, headers=headers)
issues = resp.json()

for issue in issues:
    body = issue.get("body", "")
    match = re.search(r'```json\s*(\{.*?\})\s*```', body, re.DOTALL)
    if match:
        proof = json.loads(match.group(1))
        task_id = proof.get("taskId")
        data["pending"] = [t for t in data.get("pending", []) if t.get("id") != task_id]
        if "completed" not in data:
            data["completed"] = []
        data["completed"].append(proof)
        submitter = issue.get("user", {}).get("login", "anonymous")
        data["points"][submitter] = data["points"].get(submitter, 0) + 5
        requests.patch(issues_url.replace("?labels=worker-result&state=open", f"/{issue['number']}"),
                       json={"state": "closed"}, headers=headers)

with open("tasks.json", "w") as f:
    json.dump(data, f, indent=2)
