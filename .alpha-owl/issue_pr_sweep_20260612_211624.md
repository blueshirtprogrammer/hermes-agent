# Hermes Agent Issue/PR Sweep
Generated: 2026-06-12T11:16:24.291048+00:00

## Counts
- open_issue_items_total: 3000
- open_issues: 852
- open_issue_pr_refs: 2148
- open_prs: 2000
- bugs: 811
- features: 748
- desktop_issues: 782
- security_issues: 521
- desktop_pr_search: 300
- desktop_issue_search: 500

## Top issue areas
- gateway: 280
- desktop: 265
- agent: 215
- config: 22
- tools: 17
- unknown: 14
- session: 12
- profile: 8
- cron: 8
- memory: 7
- auth: 1
- model: 1
- terminal: 1
- provider: 1

## Top priority issues
- score 296 #33365 [gateway] (security, bug, desktop, feature) WhatsApp gateway crashes (exit 1) on first poll after using existing bridge — https://github.com/NousResearch/hermes-agent/issues/33365
- score 292 #43083 [agent] (security, bug, desktop) Passwords get replaced by *** but model reads back its own conversation history and fails on second tool call. — https://github.com/NousResearch/hermes-agent/issues/43083
- score 288 #29092 [gateway] (security, bug, desktop, feature) [Bug]: Two profile gateway services enter SIGTERM flap loop — `--replace` + PID file cross-profile mis-routing — https://github.com/NousResearch/hermes-agent/issues/29092
- score 288 #31486 [gateway] (security, bug, desktop, feature) [Bug]: TUI freezes — stdin handler unresponsive while agent continues in background — https://github.com/NousResearch/hermes-agent/issues/31486
- score 286 #33913 [desktop] (security, bug, desktop, feature) double-.hermes path mismatch, the HOME env var leak, and the fallback-notification UX problem — https://github.com/NousResearch/hermes-agent/issues/33913
- score 284 #42524 [gateway] (security, bug, desktop, feature) macOS 26: gateway start/restart refreshes LaunchAgent but launchctl exits 5 and falls back to detached process — https://github.com/NousResearch/hermes-agent/issues/42524
- score 284 #44710 [gateway] (security, bug, desktop, feature) [Bug]: Auth token refresh uses non-existent api.nousresearch.com instead of portal.nousresearch.com — https://github.com/NousResearch/hermes-agent/issues/44710
- score 284 #27564 [gateway] (security, bug, desktop, feature) Gateway unconditionally interrupts running agent during clarify, discarding user answer — https://github.com/NousResearch/hermes-agent/issues/27564
- score 284 #42126 [gateway] (security, bug, desktop, feature) [Bug]: systemd `gateway run` exits 1 right after platforms connect (crash-loop) — regression after auto-update; runs fine standalone — https://github.com/NousResearch/hermes-agent/issues/42126
- score 282 #44727 [gateway] (security, bug, desktop, feature) [Security] Hermes gateway quick commands bypass admin-only slash command restrictions — https://github.com/NousResearch/hermes-agent/issues/44727
- score 282 #44585 [gateway] (security, bug, desktop, feature) [Bug]: Cron can inherit temporary paid provider state and continue billing during pause/stop containment — https://github.com/NousResearch/hermes-agent/issues/44585
- score 282 #16700 [agent] (security, bug, desktop, feature) security.redact_secrets redacts values before passing to tools, breaking Bitwarden CLI workflows — https://github.com/NousResearch/hermes-agent/issues/16700
- score 282 #42909 [gateway] (security, bug, desktop, feature) Telegram gateway connects and polls successfully but incoming DMs produce zero log output and no response (WSL2, v0.16.0, PTB 22.6) — https://github.com/NousResearch/hermes-agent/issues/42909
- score 282 #42203 [tools] (security, bug, desktop) macOS: background processes (terminal background=true) silently fail — _find_shell returns bash whose login shell (-l) swallows commands — https://github.com/NousResearch/hermes-agent/issues/42203
- score 280 #44731 [agent] (security, bug, desktop, feature) [Security] Hermes browser private-network policy bypass via eval-triggered main-frame navigation — https://github.com/NousResearch/hermes-agent/issues/44731
- score 280 #43719 [agent] (security, bug, desktop, feature) Security: Malicious third-party plugins targeting Hermes dashboards (jellyfinuser/gitea.com) — https://github.com/NousResearch/hermes-agent/issues/43719
- score 280 #43025 [gateway] (security, bug, desktop, feature) Security: redact_secrets config not preventing API key exposure in terminal output — https://github.com/NousResearch/hermes-agent/issues/43025
- score 280 #42197 [desktop] (security, bug, desktop, feature) [Bug]: Cron job fails with `'PluginManager' object has no attribute '_middleware'` — https://github.com/NousResearch/hermes-agent/issues/42197
- score 273 #22714 [gateway] (security, bug, desktop, feature) Matrix gateway: no in-band channel to drive per-message LLM orchestration in a downstream dispatcher — https://github.com/NousResearch/hermes-agent/issues/22714
- score 261 #27566 [agent] (security, bug, desktop, feature) Context compression triggers every turn due to rough token estimate inflating last_prompt_tokens — https://github.com/NousResearch/hermes-agent/issues/27566
- score 259 #43899 [gateway] (security, bug, desktop, feature) [Bug]: Cron jobs fail with 'Model parameter is required' when model is not explicitly set on the job — https://github.com/NousResearch/hermes-agent/issues/43899
- score 259 #42875 [agent] (security, bug, desktop, feature) memory(action=add) drift guard rejects valid writes after external disk changes — internal base never syncs from disk after startup — https://github.com/NousResearch/hermes-agent/issues/42875
- score 257 #43842 [gateway] (security, bug, desktop, feature) macOS: plist refresh bootout from inside the gateway kills the CLI before bootstrap — agent-initiated self-update leaves service unloaded — https://github.com/NousResearch/hermes-agent/issues/43842
- score 257 #43466 [gateway] (security, bug, desktop, feature) delegate_task: _strip_blocked_tools doesn't strip 'messaging'/'cronjob', so children inherit send_message and cronjob despite DELEGATE_BLOCKED_TOOLS — https://github.com/NousResearch/hermes-agent/issues/43466
- score 257 #43066 [gateway] (security, bug, desktop) Context compaction loses assistant messages and merges user follow-ups — https://github.com/NousResearch/hermes-agent/issues/43066

## Top priority PRs
- score 180 PR #44859 [agent] (desktop) fix(backup): exclude Git for Windows installation from hermes backup — https://github.com/NousResearch/hermes-agent/pull/44859
- score 180 PR #44858 [tools] (desktop) fix(tools): share execute_code RPC dispatch policy — https://github.com/NousResearch/hermes-agent/pull/44858
- score 180 PR #44829 [gateway] (desktop) feat(telegram): Bot API 10.1 rich messages (opt-in) — https://github.com/NousResearch/hermes-agent/pull/44829
- score 180 PR #44816 [agent] (desktop) fix(curator): verify reference files exist on disk after consolidation — https://github.com/NousResearch/hermes-agent/pull/44816
- score 180 PR #44818 [cron] (desktop) fix(kanban): respawn guard no longer false-positives on bare 'auth' word — https://github.com/NousResearch/hermes-agent/pull/44818
- score 180 PR #44753 [agent] (desktop) fix(tools): report environment failures instead of 'File not found' in read_file/search — https://github.com/NousResearch/hermes-agent/pull/44753
- score 180 PR #44805 [gateway] (desktop) fix(hindsight): re-read on-disk config when recreating the embedded client — https://github.com/NousResearch/hermes-agent/pull/44805
- score 180 PR #44594 [gateway] (desktop) feat(feishu): CardKit v1 streaming card support — https://github.com/NousResearch/hermes-agent/pull/44594
- score 180 PR #44835 [agent] (desktop) fix(state): surface failed WAL checkpoints instead of silently swallowing them — https://github.com/NousResearch/hermes-agent/pull/44835
- score 180 PR #44851 [agent] (desktop) feat(llm-guard): protect tool calls — https://github.com/NousResearch/hermes-agent/pull/44851
- score 180 PR #44856 [agent] (desktop) fix(agent): keep pool entries when terminal-OAuth quarantine save fails — https://github.com/NousResearch/hermes-agent/pull/44856
- score 180 PR #44853 [agent] (desktop) fix(credential-pool): keep OAuth refresh chain alive during exhaustion cooldown — https://github.com/NousResearch/hermes-agent/pull/44853
- score 180 PR #43624 [desktop] (desktop) fix(desktop): re-enable streaming autoscroll with user-scroll respect — https://github.com/NousResearch/hermes-agent/pull/43624
- score 180 PR #41164 [gateway] (desktop) feat: Feishu Card JSON 2.0 final response rendering for Markdown replies — https://github.com/NousResearch/hermes-agent/pull/41164
- score 180 PR #44850 [gateway] (desktop) fix(gateway): reset stream delivery state on cached turns — https://github.com/NousResearch/hermes-agent/pull/44850
- score 180 PR #44849 [agent] (desktop) fix(tools): skip read_file dedup for execute_code sandbox calls — https://github.com/NousResearch/hermes-agent/pull/44849
- score 180 PR #44102 [desktop] (desktop) fix(tui-gateway): re-arm WS orphan reap while a detached session is mid-turn — https://github.com/NousResearch/hermes-agent/pull/44102
- score 180 PR #44847 [agent] (desktop) fix(tools): bypass read dedup in execute_code — https://github.com/NousResearch/hermes-agent/pull/44847
- score 180 PR #44825 [agent] (desktop) feat(dashboard): add sessions:overview-top plugin slot — https://github.com/NousResearch/hermes-agent/pull/44825
- score 180 PR #44824 [agent] (desktop) feat(plugins): full-fidelity request_tools passthrough on pre_api_request — https://github.com/NousResearch/hermes-agent/pull/44824
- score 180 PR #44823 [gateway] (desktop) fix(prompt-size): resolve per-platform toolsets for accurate diagnostics — https://github.com/NousResearch/hermes-agent/pull/44823
- score 180 PR #44820 [tools] (desktop) fix(dashboard): correct approvals.mode dropdown options — https://github.com/NousResearch/hermes-agent/pull/44820
- score 180 PR #44833 [gateway] (desktop) feat(web): Perplexity-style grounded citations + live summary streaming box — https://github.com/NousResearch/hermes-agent/pull/44833
- score 180 PR #44834 [agent] (desktop) fix(state): log WAL checkpoint failures instead of silently swallowing — https://github.com/NousResearch/hermes-agent/pull/44834
- score 180 PR #44840 [gateway] (desktop) fix(discord): prevent operator lockout when all username allowlist entries fail to resolve — https://github.com/NousResearch/hermes-agent/pull/44840