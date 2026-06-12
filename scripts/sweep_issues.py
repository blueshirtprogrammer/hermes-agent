#!/usr/bin/env python3
"""
Comprehensive GitHub issue/PR sweep for NousResearch/hermes-agent.
Fetches ALL issues and PRs with full details, categorizes them,
and outputs a structured JSON report.
"""
import json, time, sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from collections import defaultdict

def get_token():
    with open(r"C:\Users\Link Team\Desktop\.github_token") as f:
        return f.read().strip()

def api_get(path, params=""):
    token = get_token()
    url = f"https://api.github.com{path}{params}"
    req = Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "hermes-alpha-owl-sweep/1.0"
    })
    try:
        with urlopen(req, timeout=30) as r:
            return json.load(r)
    except HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        return {"error": e.code, "body": body[:200]}

def paginate(path, params="&per_page=100", max_pages=50):
    """Fetch all pages of a paginated endpoint."""
    all_items = []
    page = 1
    while page <= max_pages:
        result = api_get(path, f"?page={page}{params}")
        if isinstance(result, dict) and "error" in result:
            print(f"  ERROR on {path} page {page}: {result}")
            break
        if not result:
            break
        all_items.extend(result)
        print(f"  {path} page {page}: {len(result)} items (total: {len(all_items)})")
        if len(result) < 100:
            break
        page += 1
        time.sleep(0.5)  # Rate limit friendly
    return all_items

def categorize_issue(issue):
    """Categorize an issue by area, severity, and type."""
    labels = [l["name"].lower() for l in issue.get("labels", [])]
    title = issue.get("title", "").lower()
    body = (issue.get("body") or "").lower()
    
    # Determine area
    area = "unknown"
    area_keywords = {
        "gateway": ["gateway", "telegram", "whatsapp", "discord", "slack", "messaging", "platform", "websocket", "poll"],
        "agent": ["agent", "loop", "context", "compression", "memory", "tool", "reasoning", "llm", "model", "inference", "prompt"],
        "desktop": ["desktop", "electron", "dashboard", "ui", "gui", "window", "tray", "menu", "dock", "installer"],
        "cron": ["cron", "schedule", "job", "periodic"],
        "config": ["config", "yaml", "env", "setting", "profile"],
        "auth": ["auth", "oauth", "token", "login", "credential", "secret", "password", "api key"],
        "security": ["security", "vulnerability", "exploit", "malicious", "sandbox", "permission", "xss", "ssrf", "injection"],
        "tools": ["browser", "terminal", "file", "search", "mcp", "execute"],
        "session": ["session", "conversation", "chat", "history", "state.db"],
        "plugins": ["plugin", "extension", "marketplace", "hook"],
    }
    for a, keywords in area_keywords.items():
        if any(k in title or k in body[:500] for k in keywords) or any(k in labels for k in [a]):
            area = a
            break
    
    # Determine severity
    severity = "P3"
    if any(l in labels for l in ["p0", "critical"]):
        severity = "P0"
    elif any(l in labels for l in ["p1", "high"]):
        severity = "P1"
    elif any(l in labels for l in ["p2", "medium"]):
        severity = "P2"
    
    # Determine type
    issue_type = "unknown"
    if any("bug" in l or "crash" in l or "broken" in l or "fix" in l for l in labels):
        issue_type = "bug"
    elif any("feature" in l or "enhancement" in l or "request" in l for l in labels):
        issue_type = "feature"
    elif any("security" in l or "vulnerability" in l for l in labels):
        issue_type = "security"
    elif any("docs" in l or "documentation" in l for l in labels):
        issue_type = "docs"
    
    return area, severity, issue_type

def main():
    print("=" * 60)
    print("HERMES AGENT FORK — COMPREHENSIVE ISSUE/PR SWEEP")
    print("=" * 60)
    
    # Check rate limit
    rl = api_get("/rate_limit")
    if "resources" in rl:
        core = rl["resources"]["core"]
        print(f"Rate limit: {core['remaining']}/{core['limit']}")
        if core["remaining"] < 500:
            print("WARNING: Low rate limit. Waiting for reset.")
            return
    
    # Fetch all open issues and PRs in one sweep from the /issues endpoint
    print("\n--- FETCHING ALL OPEN ISSUES & PRs ---")
    all_items = paginate("/repos/NousResearch/hermes-agent/issues", "&state=open&per_page=100")
    
    # Split into issues and PRs
    all_issues = []
    all_prs = []
    for item in all_items:
        if "pull_request" in item:
            all_prs.append(item)
        else:
            all_issues.append(item)
            
    print(f"Total open items: {len(all_items)}")
    print(f"Total open issues (pure): {len(all_issues)}")
    print(f"Total open PRs: {len(all_prs)}")
    
    # Categorize issues
    print("\n--- CATEGORIZING ISSUES ---")
    categorized = defaultdict(list)
    severity_count = defaultdict(int)
    type_count = defaultdict(int)
    area_count = defaultdict(int)
    
    for issue in all_issues:
        area, severity, issue_type = categorize_issue(issue)
        categorized[area].append({
            "number": issue["number"],
            "title": issue["title"][:100],
            "url": issue["html_url"],
            "labels": [l["name"] for l in issue.get("labels", [])],
            "severity": severity,
            "type": issue_type,
            "created_at": issue.get("created_at", ""),
            "updated_at": issue.get("updated_at", ""),
            "comments": issue.get("comments", 0),
        })
        severity_count[severity] += 1
        type_count[issue_type] += 1
        area_count[area] += 1
    
    # Categorize PRs
    print("\n--- CATEGORIZING PRs ---")
    pr_areas = defaultdict(int)
    for pr in all_prs:
        area, _, _ = categorize_issue(pr)
        pr_areas[area] += 1
    
    # Build report
    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "summary": {
            "total_open_issues": len(all_issues),
            "total_open_prs": len(all_prs),
            "severity_breakdown": dict(severity_count),
            "type_breakdown": dict(type_count),
            "area_breakdown_issues": dict(area_count),
            "area_breakdown_prs": dict(pr_areas),
        },
        "departments": {}
    }
    
    # Build department structure
    dept_mapping = {
        "gateway": "DEPT 1: GATEWAY & INFRASTRUCTURE",
        "auth": "DEPT 1: GATEWAY & INFRASTRUCTURE",
        "security": "DEPT 1: GATEWAY & INFRASTRUCTURE",
        "agent": "DEPT 2: AGENT & REASONING",
        "tools": "DEPT 2: AGENT & REASONING",
        "session": "DEPT 2: AGENT & REASONING",
        "memory": "DEPT 2: AGENT & REASONING",
        "desktop": "DEPT 3: DESKTOP APP",
        "plugins": "DEPT 3: DESKTOP APP",
        "cron": "DEPT 4: CRON & SCHEDULING",
        "config": "DEPT 5: CONFIG & PROFILES",
        "unknown": "DEPT 6: UNCATEGORIZED",
    }
    
    dept_issues = defaultdict(list)
    for area, issues in categorized.items():
        dept = dept_mapping.get(area, "DEPT 6: UNCATEGORIZED")
        dept_issues[dept].extend(issues)
    
    for dept, issues in sorted(dept_issues.items()):
        p0 = [i for i in issues if i["severity"] == "P0"]
        p1 = [i for i in issues if i["severity"] == "P1"]
        p2 = [i for i in issues if i["severity"] == "P2"]
        p3 = [i for i in issues if i["severity"] == "P3"]
        bugs = [i for i in issues if i["type"] == "bug"]
        features = [i for i in issues if i["type"] == "feature"]
        security = [i for i in issues if i["type"] == "security"]
        
        report["departments"][dept] = {
            "total_issues": len(issues),
            "p0_critical": len(p0),
            "p1_high": len(p1),
            "p2_medium": len(p2),
            "p3_low": len(p3),
            "bugs": len(bugs),
            "features": len(features),
            "security": len(security),
            "top_p0_issues": p0[:10],
            "top_p1_issues": p1[:10],
        }
    
    # Output
    output_path = r"C:\Users\Link Team\Desktop\hermes-agent-fork\.alpha-owl\full_sweep.json"
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{'=' * 60}")
    print("SWEEP COMPLETE")
    print(f"{'=' * 60}")
    print(f"\nSUMMARY:")
    print(f"  Total Open Issues: {report['summary']['total_open_issues']}")
    print(f"  Total Open PRs: {report['summary']['total_open_prs']}")
    print(f"\nSEVERITY BREAKDOWN:")
    for sev, count in sorted(report['summary']['severity_breakdown'].items()):
        print(f"  {sev}: {count}")
    print(f"\nTYPE BREAKDOWN:")
    for typ, count in sorted(report['summary']['type_breakdown'].items(), key=lambda x: -x[1]):
        print(f"  {typ}: {count}")
    print(f"\nDEPARTMENT BREAKDOWN:")
    for dept, data in sorted(report['departments'].items()):
        print(f"  {dept}: {data['total_issues']} issues (P0: {data['p0_critical']}, P1: {data['p1_high']}, Bugs: {data['bugs']}, Security: {data['security']})")
    
    # Rate limit check
    rl = api_get("/rate_limit")
    if "resources" in rl:
        core = rl["resources"]["core"]
        print(f"\nRemaining API calls: {core['remaining']}/{core['limit']}")
    
    print(f"\nFull report saved to: {output_path}")

if __name__ == "__main__":
    main()
