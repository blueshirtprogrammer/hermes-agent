# HERMES AGENT FORK — PROJECT TRACKER
## Real Data from Full Sweep (2026-06-13)

---

## 📊 ACTUAL NUMBERS (Authenticated API Sweep)

| Category | Count |
|----------|-------|
| **Open Issues** | 1,499 |
| **Open PRs** | 3,501 |
| **P1 (High Priority)** | 56 |
| **P2 (Medium)** | 473 |
| **P3 (Low)** | 970 |
| **Bugs** | 971 |
| **Features** | 447 |
| **Security** | 37 |
| **Docs** | 11 |

---

## 🏢 DEPARTMENT STRUCTURE

### DEPT 1: GATEWAY & INFRASTRUCTURE
**Owner:** Gateway Lead  
**Scope:** Gateway core, messaging platforms, auth, security

| Metric | Count |
|--------|-------|
| Total Issues | 476 |
| P1 | 31 |
| P2 | 193 |
| P3 | 252 |
| Bugs | 335 |
| Features | 114 |
| Security | 16 |
| PRs | 1,251 |

**Teams:**
- Platform Connectors (Telegram, WhatsApp, Discord, Matrix)
- Service Management (systemd, launchd, Windows service)
- Auth & Security (OAuth, token refresh, permission system)
- Gateway Core (SIGTERM flap, crash loops, message routing)

### DEPT 2: AGENT & REASONING
**Owner:** Agent Lead  
**Scope:** Agent loop, tools, memory, context, compression

| Metric | Count |
|--------|-------|
| Total Issues | 700 |
| P1 | 21 |
| P2 | 211 |
| P3 | 468 |
| Bugs | 427 |
| Features | 240 |
| Security | 11 |
| PRs | 1,384 |

**Teams:**
- Agent Loop (context, compression, tool execution)
- Memory System (drift guard, sync, persistence)
- Tools (terminal, browser, MCP, file operations)
- Delegate System (context corruption, security)

### DEPT 3: DESKTOP APP
**Owner:** Desktop Lead  
**Scope:** Electron app, UI/UX, dashboard, plugin system

| Metric | Count |
|--------|-------|
| Total Issues | 265 |
| P1 | 4 |
| P2 | 54 |
| P3 | 207 |
| Bugs | 176 |
| Features | 75 |
| Security | 8 |
| PRs | 523 |

**Teams:**
- Desktop Core (path issues, installers, updates)
- UI/UX (command palette, dashboard, activity stream)
- Plugin System (marketplace, permissions, sandbox)
- Integration (desktop-backend communication)

### DEPT 4: CRON & SCHEDULING
**Owner:** Cron Lead  
**Scope:** Job scheduling, retries, monitoring, webhooks

| Metric | Count |
|--------|-------|
| Total Issues | 6 |
| P1 | 0 |
| P2 | 2 |
| P3 | 4 |
| Bugs | 2 |
| Features | 4 |
| Security | 0 |
| PRs | 26 |

### DEPT 5: CONFIG & PROFILES
**Owner:** Config Lead  
**Scope:** Configuration system, profile management, env vars

| Metric | Count |
|--------|-------|
| Total Issues | 34 |
| P1 | 0 |
| P2 | 11 |
| P3 | 23 |
| Bugs | 21 |
| Features | 10 |
| Security | 2 |
| PRs | 104 |

---

## 🎯 TOP 56 P1 ISSUES BY PRIORITY

### HIGHEST PRIORITY (Security + Data Loss)

**SECURITY (Must Fix Today):**
1. ~~#44727~~ - Quick commands bypass admin restrictions ✅ **FIXED + PUSHED**
2. ~~#44731~~ - Browser private-network policy bypass via eval ✅ **FIXED + PUSHED**
3. ~~#43025~~ - redact_secrets not preventing API key exposure ✅ **FIXED + PUSHED**
4. #43719 - Malicious third-party plugins targeting dashboards [SKIP - plugin permissions system already in place]
5. ~~#43899~~ - Cron model resolution fix ✅ **ALREADY FIXED**

**DATA LOSS (Must Fix Today):**
6. ~~#44837~~ - Session DB drops assistant after compaction ✅ **FIXED + PUSHED**
7. ~~#43066~~ - Context compaction truncating mid-turn ✅ **FIXED + PUSHED**
8. ~~#42449~~ - delegate_task context corruption (shared singleton) ✅ **FIXED + PUSHED**
9. ~~#44327~~ - Cached-agent cursor reset [already fixed in #44837 layer 1]
10. ~~#43211~~ - Stale stream silently retries on same provider instead of fallback ✅ **FIXED + PUSHED**
11. ~~#44585~~ - Cron inherits paid provider state during pause/stop ✅ **FIXED + PUSHED**

### HIGH PRIORITY (Functionality)

11. ~~#44037~~ - fd-recycle corruption in memory_store.db ✅ **FIXED + PUSHED**
12. ~~#43842~~ - macOS plist refresh kills CLI before bootstrap ✅ **FIXED + PUSHED**
13. ~~#43083~~ - Secret redaction breaks second tool call ✅ **FIXED + PUSHED**
14. #42909 - Telegram DMs produce zero log output [WSL2/PTB polling compat]
15. ~~#42524~~ - macOS 26 launchctl exit 5 fallback ✅ **FIXED + PUSHED**
16. ~~#44679~~ - Matrix gateway treats DM as group ✅ **FIXED + PUSHED**
17. #42875 - memory drift guard rejects valid writes after external disk changes
18. ~~#42874~~ - memory refuses legitimate appends (drift guard over-reach) ✅ **FIXED + PUSHED**
19. #42810 - OpenAI compatible endpoint fails on Python 3.11 [httpx/httpcore compat — NOT a Hermes bug; Python 3.14 works]
20. ~~#44710~~ - Auth token refresh uses wrong domain ✅ **ALREADY CORRECT** (portal.nousresearch.com already in codebase)
21. ~~#43014~~ - cron deliver=origin fails to resolve delivery target ✅ **FIXED + PUSHED**

---

## 🚀 EXECUTION PLAN

### PHASE 1: SECURITY & DATA LOSS (Week 1)
Fix all security issues + data loss bugs.

| # | Issue | Dept | Team | Status |
|---|-------|------|------|--------|
| 1 | #44727 Quick commands bypass | Gateway | Auth | TODO |
| 2 | #44731 Browser policy bypass | Agent | Tools | TODO |
| 3 | #43025 API key exposure | Gateway | Auth | TODO |
| 4 | #43719 Malicious plugins | Agent | Security | TODO |
| 5 | #43466 delegate_task | Agent | Security | ✅ DONE |
| 6 | #44837 Session DB flush | Gateway | Core | TODO |
| 7 | #43066 Context compaction | Agent | Loop | TODO |
| 8 | #42449 delegate context | Agent | Delegate | TODO |
| 9 | #44585 Cron billing | Agent | Cron | ✅ DONE |
| 10 | #43899 Cron model | Cron | Core | ✅ DONE |

### PHASE 2: PLATFORM STABILITY (Week 2)
Fix all platform connectivity issues.

| # | Issue | Dept | Platform |
|---|-------|------|----------|
| 11 | #44037 fd-recycle corruption | Gateway | Memory |
| 12 | #43842 macOS plist | Gateway | macOS |
| 13 | #42909 Telegram DM | Gateway | Telegram |
| 14 | #42524 launchctl exit 5 | Gateway | macOS |
| 15 | #44679 Matrix DM | Gateway | Matrix |
| 16 | #44710 Auth domain | Desktop | Auth |

### PHASE 3: TOOL CHAIN (Week 3)
Fix all tool-related issues.

| # | Issue | Dept | Tool |
|---|-------|------|------|
| 17 | #42875 memory drift | Agent | Memory |
| 18 | #42874 memory appends | Agent | Memory |
| 19 | #42810 OpenAI endpoint | Agent | API |
| 20 | #43014 cron deliver | Cron | Cron |
| 21 | #39714 venv path | Desktop | CLI |
| 22 | #39455 nix lockfile | Desktop | Nix |
| 23 | #38026 sync_back | Agent | File Sync |

---

## 🤖 AGENT TEAM STRUCTURE

```
OWL ALPHA (Project Manager)
│
├── DEPT 1: Gateway Lead
│   ├── Platform Team (3 agents)
│   │   ├── Telegram Specialist
│   │   ├── WhatsApp Specialist
│   │   └── Matrix Specialist
│   ├── Service Team (2 agents)
│   │   ├── systemd Specialist
│   │   └── macOS Specialist
│   └── Auth Team (2 agents)
│       ├── OAuth Specialist
│       └── Security Specialist
│
├── DEPT 2: Agent Lead
│   ├── Loop Team (2 agents)
│   │   ├── Context Specialist
│   │   └── Compression Specialist
│   ├── Memory Team (2 agents)
│   │   ├── Persistence Specialist
│   │   └── Sync Specialist
│   ├── Tools Team (3 agents)
│   │   ├── Terminal Specialist
│   │   ├── Browser Specialist
│   │   └── MCP Specialist
│   └── Delegate Team (2 agents)
│       ├── Context Isolation Specialist
│       └── Security Specialist
│
├── DEPT 3: Desktop Lead
│   ├── Core Team (2 agents)
│   │   ├── Installer Specialist
│   │   └── Path Specialist
│   ├── UI/UX Team (3 agents)
│   │   ├── Dashboard Specialist
│   │   ├── Command Palette Specialist
│   │   └── Activity Stream Specialist
│   └── Plugin Team (2 agents)
│       ├── Marketplace Specialist
│       └── Sandbox Specialist
│
├── DEPT 4: Cron Lead
│   └── Cron Team (2 agents)
│       ├── Scheduler Specialist
│       └── Retry Specialist
│
├── DEPT 5: Config Lead
│   └── Config Team (2 agents)
│       ├── Profile Specialist
│       └── Environment Specialist
│
├── QA TEAM (4 agents)
│   ├── Security QA (reviews all security fixes)
│   ├── Integration QA (tests cross-dept changes)
│   ├── Performance QA (benchmarks before/after)
│   └── Regression QA (runs full test suite)
│
└── INTEGRATION TEAM (2 agents)
    ├── Merge Agent (creates and merges PRs)
    └── Release Agent (tags releases, updates changelog)
```

---

## 📈 METRICS TRACKING

Daily standup reports:
- Issues resolved per day
- PRs created and merged
- Test pass rate
- Security issues remaining
- P1 issues remaining
- Time to resolution

---

## 🔧 WORKFLOW

1. **PM Agent** reads this tracker, assigns work to department leads
2. **Department Leads** spawn specialist agents per issue
3. **Specialists** fix issues, write tests, create PRs
4. **QA Agents** review each PR
5. **Integration Agent** merges approved PRs
6. **Daily report** generated and displayed in Dashboard view
