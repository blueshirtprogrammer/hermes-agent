# HERMES AGENT FORK — PROJECT TRACKER
## Comprehensive Issue/PR Sweep & Roadmap
Generated: 2026-06-13

---

## 📊 BIG PICTURE

| Category | Count | % of Total |
|----------|-------|------------|
| Open Issues | 852 | 28% |
| Open PRs | 2000 | 67% |
| Total Items | 3000 | 100% |
| Bugs | 811 | 27% |
| Features | 748 | 25% |
| Desktop-related | 782 | 26% |
| Security | 521 | 17% |

---

## 🎯 DEPARTMENT STRUCTURE (Dogfooding Teams Integration)

We'll organize the work into **departments**, each with **teams**, each with **agents**:

### DEPT 1: GATEWAY & INFRASTRUCTURE (280 issues, 710 PRs)
**Mission:** Gateway stability, crash recovery, platform connections

| Team | Issues | PRs | Priority |
|------|--------|-----|----------|
| Gateway Core | ~120 | ~300 | P0 — Crashes take down everything |
| Platform Connectors | ~80 | ~200 | P1 — WhatsApp, Telegram, Discord |
| systemd/macOS Launch | ~40 | ~100 | P1 — Service management |
| Auth & Security | ~40 | ~110 | P0 — Token refresh, permissions |

### DEPT 2: AGENT & REASONING (215 issues, 586 PRs)
**Mission:** Agent loop, context, memory, tool execution

| Team | Issues | PRs | Priority |
|------|--------|-----|----------|
| Agent Loop | ~80 | ~200 | P0 — Compression, crashes |
| Memory System | ~40 | ~80 | P1 — Drift guard, sync |
| Tool Execution | ~50 | ~150 | P1 — Terminal, browser, MCP |
| Context Engine | ~45 | ~156 | P0 — Message loss |

### DEPT 3: DESKTOP APP (265 issues, 354 PRs)
**Mission:** Electron app, UI/UX, dashboard

| Team | Issues | PRs | Priority |
|------|--------|-----|----------|
| Desktop Core | ~100 | ~150 | P0 — Path issues, install |
| Dashboard/Health | ~50 | ~80 | P1 — NEW: We built this |
| Plugin System | ~65 | ~74 | P0 — Security sandbox |
| UI/UX Polish | ~50 | ~50 | P2 — Visual refinements |

### DEPT 4: CRON & SCHEDULING (8 issues, 24 PRs)
**Mission:** Reliable job execution, retries, monitoring

| Team | Issues | PRs | Priority |
|------|--------|-----|----------|
| Cron Core | 5 | 15 | P0 — Model resolution, billing |
| Cron Retries | 3 | 9 | P1 — NEW: We built this |

### DEPT 5: CONFIG & PROFILES (30 issues, 79 PRs)
**Mission:** Configuration system, profiles, settings

| Team | Issues | PRs | Priority |
|------|--------|-----|----------|
| Config System | 20 | 50 | P1 — Path mismatches |
| Profiles | 10 | 29 | P1 — Multi-profile |

---

## 🔥 TOP 30 ISSUES BY SEVERITY (Already Extracted)

**ALREADY FIXED (in our fork):**
- ✅ #43466 — Delegate subagent toolset stripping
- ✅ #43899 — Cron model parameter resolution
- ✅ #44585 — Cron retry with exponential backoff

**P0 — CRITICAL (Gateway crashes, security):**
1. #33365 — WhatsApp gateway crashes on first poll after existing bridge
2. #43083 — Secret redaction breaks second tool call
3. #29092 — Two-profile SIGTERM flap loop
4. #31486 — TUI freezes, stdin unresponsive
5. #33913 — Double-.hermes path mismatch in Docker
6. #44710 — Auth token refresh uses wrong domain
7. #27564 — Gateway unconditionally interrupts during clarify
8. #42126 — systemd gateway exits 1 after platforms connect
9. #44727 — Quick commands bypass admin restrictions [SECURITY]
10. #43719 — Malicious third-party plugins [SECURITY]

**P1 — HIGH (Platform, desktop, config):**
11. #42524 — macOS 26 launchctl exit 5
12. #42909 — Telegram DMs produce zero log output
13. #42203 — macOS background processes silently fail
14. #44731 — Browser private-network policy bypass [SECURITY]
15. #43025 — API key exposure in terminal output [SECURITY]
16. #16700 — redact_secrets breaks Bitwarden CLI
17. #43842 — macOS plist refresh bootout
18. #42875 — Memory drift guard rejects valid writes
19. #43066 — Context compression loses assistant messages
20. #42197 — Cron jobs fail with 'Model parameter is required'

**P2 — MEDIUM (Features, improvements):**
21-30. Various feature requests and improvements

---

## 📋 ROADMAP — ONE SWEEP EXECUTION PLAN

### PHASE 1: STABILIZE (Week 1) — "Stop the Bleeding"
**Goal:** All P0 crashes and security issues fixed

| # | Issue | Department | Team | Effort | Status |
|---|-------|------------|------|--------|--------|
| 1 | #44727 Quick commands bypass admin | Gateway | Security | 2h | TODO |
| 2 | #43719 Malicious plugins | Desktop | Plugin Security | 4h | IN PROGRESS |
| 3 | #33365 WhatsApp crash | Gateway | Platforms | 4h | TODO |
| 4 | #29092 SIGTERM flap loop | Gateway | Core | 3h | TODO |
| 5 | #31486 TUI freeze | Gateway | Core | 4h | TODO |
| 6 | #44710 Auth token refresh URL | Gateway | Auth | 1h | TODO |
| 7 | #27564 Clarify interrupt | Gateway | Core | 3h | TODO |
| 8 | #42126 systemd crash-loop | Gateway | Core | 3h | TODO |
| 9 | #43083 Secret redaction bug | Agent | Loop | 2h | TODO |
| 10 | #33913 Docker path mismatch | Desktop | Core | 2h | TODO |

### PHASE 2: SECURE (Week 2) — "Lock It Down"
**Goal:** All security issues fixed, plugin system hardened

| # | Issue | Department | Team | Effort | Status |
|---|-------|------------|------|--------|--------|
| 11 | #44731 Browser policy bypass | Agent | Tools | 3h | TODO |
| 12 | #43025 API key exposure | Gateway | Security | 2h | TODO |
| 13 | #16700 redact_secrets + Bitwarden | Agent | Config | 2h | TODO |
| 14 | #44710 Auth token refresh | Gateway | Auth | 1h | TODO |

### PHASE 3: POLISH (Week 3) — "Make It Sing"
**Goal:** Desktop app features, UI/UX, developer experience

| # | Issue | Department | Team | Effort | Status |
|---|-------|------------|------|--------|--------|
| 15 | Dashboard view | Desktop | Dashboard | 8h | DONE |
| 16 | Plugin Marketplace UI | Desktop | Plugins | 8h | DONE |
| 17 | Health Monitor | Infra | Monitoring | 6h | DONE |
| 18 | Cron retry system | Cron | Core | 4h | DONE |
| 19 | Usage/Cost API | Infra | API | 3h | DONE |

---

## 🤖 DOGFOODING: HOW WE'LL USE OUR OWN TEAMS INTEGRATION

### The OWL Alpha Workflow:
1. **Project Manager Agent** — Reads this tracker, assigns work
2. **Department Leads** — One per department, reviews priorities
3. **Team Agents** — Each team has agents that:
   - Fetch issue details from GitHub
   - Read relevant code
   - Implement fixes
   - Write tests
   - Create PRs
4. **QA Agent** — Reviews each PR, runs tests
5. **Integration Agent** — Merges approved PRs

### Running the Sweep:
```bash
# Each department lead spawns their teams
hermes task --agent "Dept1-Gateway-Lead" --prompt "
  You are the Gateway Department Lead.
  Read PROJECT_TRACKER.md Phase 1 issues.
  For each issue:
    1. Fetch full issue details
    2. Identify root cause
    3. Spawn a team agent to fix it
    4. Review the fix
    5. Create PR to fork
  Report progress to Project Manager.
"
```

---

## 📈 METRICS TO TRACK

- Issues resolved per day
- PRs merged
- Test pass rate
- Time to resolution per department
- Security issues remaining
- Crash-related issues remaining

---

## 🚀 NEXT ACTIONS

1. **Start Phase 1** — Fix P0 crash and security issues
2. **Set up agent teams** — Use delegate_task to spawn department leads
3. **Monitor progress** — Dashboard view shows health of the fork itself
4. **Iterate** — Daily standup agent reviews what was done, plans next
