#!/usr/bin/env python3
"""
GitHub API client for Hermes Agent fork.
Usage: python3 github_api.py <endpoint> [method] [json_body]
Example: python3 github_api.py repos/NousResearch/hermes-agent/issues?state=open&per_page=10
"""
import json, sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError

def get_token():
    with open(r"C:\Users\Link Team\Desktop\.github_token") as f:
        return f.read().strip()

def api(method, path, body=None):
    token = get_token()
    url = f"https://api.github.com{path}"
    data = json.dumps(body).encode() if body else None
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=30) as r:
            return json.load(r)
    except HTTPError as e:
        return {"error": e.code, "message": e.read().decode()[:500]}

if __name__ == "__main__":
    method = sys.argv[1] if len(sys.argv) > 1 else "GET"
    path = sys.argv[2] if len(sys.argv) > 2 else "rate_limit"
    if not path.startswith("/"):
        path = "/" + path
    body = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
    result = api(method, path, body)
    print(json.dumps(result, indent=2))
