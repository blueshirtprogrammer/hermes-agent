/**
 * Dashboard View — Unified overview of agent health, usage, cron, and activity.
 *
 * This is the "mission control" view that shows:
 * - Health monitor status (gateway uptime, crash count, flap detection)
 * - Usage summary (tokens, costs, per-model breakdown)
 * - Cron job status (active, paused, recent failures)
 * - Recent activity stream (latest agent actions across all sessions)
 * - Plugin security status (permissions, approvals needed)
 */

import { useStore } from '@nanostores/react'
import { useQuery } from '@tanstack/react-query'
import { useEffect, useMemo, useState } from 'react'

import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useI18n } from '@/i18n'
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Cpu,
  CreditCard,
  GitBranch,
  Heart,
  MessageCircle,
  Package,
  Play,
  RefreshCw,
  Shield,
  ShieldAlert,
  Timer,
  TrendingUp,
  XCircle,
  Zap
} from '@/lib/icons'
import { cn } from '@/lib/utils'
import { notifyError } from '@/store/notifications'

import type { ReactNode } from 'react'

/* ─── Types ─── */

interface HealthData {
  state: string
  uptime_seconds: number
  restart_count: number
  crash_count: number
  flap_detected: boolean
  backoff_seconds: number
  last_healthy_at?: string
  last_check_at?: string
  last_crash?: {
    timestamp: string
    exit_code: number | null
    signal_name: string | null
    uptime_seconds: number
    reason: string
  }
  recent_crashes: Array<{
    timestamp: string
    exit_code: number | null
    signal_name: string | null
    uptime_seconds: number
    reason: string
  }>
  gateway_pid?: number
  gateway_running: boolean
}

interface UsageData {
  period: string
  total_input_tokens: number
  total_output_tokens: number
  total_tokens: number
  total_cost_usd: number
  model_breakdown: Record<string, {
    input_tokens: number
    output_tokens: number
    cost: number
    sessions: number
  }>
  sessions: Array<{
    id: string
    title: string
    model: string
    input_tokens: number
    output_tokens: number
    cost: number
    profile: string
    last_active: string
  }>
}

interface PluginPermission {
  name: string
  version: string
  description: string
  status: 'active' | 'needs_approval' | 'disabled'
  dangerous_permissions: string[]
  permissions: string[]
}

/* ─── Helpers ─── */

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${Math.round(seconds)}s`
  if (seconds < 3600) return `${Math.round(seconds / 60)}m`
  if (seconds < 86400) return `${Math.round(seconds / 3600)}h ${Math.round((seconds % 3600) / 60)}m`
  return `${Math.round(seconds / 86400)}d ${Math.round((seconds % 86400) / 3600)}h`
}

function formatTokens(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return n.toString()
}

function formatCost(n: number): string {
  if (n < 0.01) return '<$0.01'
  return `$${n.toFixed(2)}`
}

function formatIso(iso: string): string {
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}

function healthStateTone(state: string): 'good' | 'warn' | 'bad' | 'muted' {
  switch (state) {
    case 'healthy': return 'good'
    case 'degraded': return 'warn'
    case 'crash_loop': return 'bad'
    case 'starting': return 'muted'
    default: return 'muted'
  }
}

const TONE_BG: Record<string, string> = {
  good: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  warn: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  bad: 'bg-red-500/10 text-red-400 border-red-500/20',
  muted: 'bg-zinc-500/10 text-zinc-400 border-zinc-500/20',
}

const TONE_DOT: Record<string, string> = {
  good: 'bg-emerald-400',
  warn: 'bg-amber-400',
  bad: 'bg-red-400',
  muted: 'bg-zinc-400',
}

/* ─── Sub-components ─── */

function CardShell({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={cn(
      'rounded-xl border border-[--ui-stroke-tertiary] bg-[--ui-bg-secondary] p-4',
      className,
    )}>
      {children}
    </div>
  )
}

function CardLabel({ children, icon: Icon }: { children: ReactNode; icon?: ReactNode }) {
  return (
    <div className="flex items-center gap-1.5 text-xs font-medium text-[--ui-text-tertiary] uppercase tracking-wider mb-3">
      {Icon && <span className="size-3.5 opacity-60">{Icon}</span>}
      {children}
    </div>
  )
}

function StatValue({ value, label, tone }: { value: string; label: string; tone?: 'good' | 'warn' | 'bad' }) {
  return (
    <div className="flex flex-col">
      <span className={cn(
        'text-2xl font-semibold tabular-nums',
        tone === 'good' && 'text-emerald-400',
        tone === 'warn' && 'text-amber-400',
        tone === 'bad' && 'text-red-400',
        !tone && 'text-[--ui-text-primary]',
      )}>
        {value}
      </span>
      <span className="text-xs text-[--ui-text-tertiary] mt-0.5">{label}</span>
    </div>
  )
}

/* ─── Health Card ─── */

function HealthCard({ data, loading, onReset }: { data?: HealthData; loading: boolean; onReset: () => void }) {
  const { t } = useI18n()
  const tone = data ? healthStateTone(data.state) : 'muted'

  if (loading) {
    return (
      <CardShell>
        <CardLabel icon={<Heart className="size-3.5" />}>Health</CardLabel>
        <div className="space-y-3">
          <Skeleton className="h-8 w-24" />
          <Skeleton className="h-4 w-32" />
        </div>
      </CardShell>
    )
  }

  if (!data) {
    return (
      <CardShell>
        <CardLabel icon={<Heart className="size-3.5" />}>Health</CardLabel>
        <div className="text-sm text-[--ui-text-tertiary]">No health data available</div>
      </CardShell>
    )
  }

  return (
    <CardShell>
      <div className="flex items-start justify-between mb-3">
        <CardLabel icon={<Heart className="size-3.5" />}>Gateway Health</CardLabel>
        <div className={cn('flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium border', TONE_BG[tone])}>
          <span className={cn('size-1.5 rounded-full', TONE_DOT[tone])} />
          {data.state === 'healthy' ? 'Healthy' : data.state === 'crash_loop' ? 'Crash Loop' : data.state}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <StatValue value={formatDuration(data.uptime_seconds)} label="Uptime" tone={tone} />
        <StatValue value={data.restart_count.toString()} label="Restarts" tone={data.restart_count > 0 ? 'warn' : undefined} />
        <StatValue value={data.crash_count.toString()} label="Crashes" tone={data.crash_count > 0 ? 'bad' : undefined} />
      </div>

      {data.flap_detected && (
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs mb-3">
          <AlertTriangle className="size-3.5 shrink-0" />
          <span>Crash loop detected — auto-recovery paused. Manual intervention required.</span>
        </div>
      )}

      {data.last_crash && (
        <div className="text-xs text-[--ui-text-tertiary] space-y-1">
          <div className="flex items-center gap-1.5">
            <Clock className="size-3 opacity-50" />
            Last crash: {formatIso(data.last_crash.timestamp)}
          </div>
          <div className="truncate pl-4.5">{data.last_crash.reason}</div>
        </div>
      )}

      <div className="flex items-center gap-2 mt-3 pt-3 border-t border-[--ui-stroke-tertiary]">
        <Button variant="text" size="xs" onClick={onReset} className="text-[--ui-text-tertiary]">
          <RefreshCw className="size-3 mr-1" />
          Reset
        </Button>
        {data.gateway_running && (
          <span className="text-xs text-[--ui-text-tertiary] ml-auto">
            PID {data.gateway_pid}
          </span>
        )}
      </div>
    </CardShell>
  )
}

/* ─── Usage Card ─── */

function UsageCard({ data, loading }: { data?: UsageData; loading: boolean }) {
  const { t } = useI18n()

  const topModels = useMemo(() => {
    if (!data) return []
    return Object.entries(data.model_breakdown)
      .sort((a, b) => b[1].cost - a[1].cost)
      .slice(0, 4)
  }, [data])

  if (loading) {
    return (
      <CardShell>
        <CardLabel icon={<CreditCard className="size-3.5" />}>Usage</CardLabel>
        <div className="space-y-3">
          <Skeleton className="h-8 w-32" />
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </div>
        </div>
      </CardShell>
    )
  }

  if (!data) {
    return (
      <CardShell>
        <CardLabel icon={<CreditCard className="size-3.5" />}>Usage</CardLabel>
        <div className="text-sm text-[--ui-text-tertiary]">No usage data available</div>
      </CardShell>
    )
  }

  return (
    <CardShell>
      <div className="flex items-start justify-between mb-3">
        <CardLabel icon={<CreditCard className="size-3.5" />}>Usage (24h)</CardLabel>
        <span className="text-lg font-semibold text-[--ui-text-primary]">{formatCost(data.total_cost_usd)}</span>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <StatValue value={formatTokens(data.total_tokens)} label="Tokens" />
        <StatValue value={formatTokens(data.total_input_tokens)} label="Input" />
        <StatValue value={formatTokens(data.total_output_tokens)} label="Output" />
      </div>

      {topModels.length > 0 && (
        <div className="space-y-2">
          <div className="text-xs text-[--ui-text-tertiary] font-medium">Top Models</div>
          {topModels.map(([model, stats]) => (
            <div key={model} className="flex items-center justify-between text-xs">
              <span className="text-[--ui-text-secondary] truncate mr-2">{model}</span>
              <span className="text-[--ui-text-tertiary] tabular-nums shrink-0">
                {formatTokens(stats.input_tokens + stats.output_tokens)} · {formatCost(stats.cost)}
              </span>
            </div>
          ))}
        </div>
      )}
    </CardShell>
  )
}

/* ─── Cron Card ─── */

function CronCard({ jobs, loading }: { jobs?: any[]; loading: boolean }) {
  const { t } = useI18n()

  const activeJobs = jobs?.filter(j => j.enabled && j.state !== 'paused') || []
  const failedJobs = jobs?.filter(j => j.last_status === 'error') || []
  const pausedJobs = jobs?.filter(j => j.state === 'paused') || []

  if (loading) {
    return (
      <CardShell>
        <CardLabel icon={<Timer className="size-3.5" />}>Cron</CardLabel>
        <div className="space-y-3">
          <Skeleton className="h-8 w-20" />
          <Skeleton className="h-4 w-28" />
        </div>
      </CardShell>
    )
  }

  return (
    <CardShell>
      <div className="flex items-start justify-between mb-3">
        <CardLabel icon={<Timer className="size-3.5" />}>Cron Jobs</CardLabel>
        <span className="text-xs text-[--ui-text-tertiary]">{jobs?.length || 0} total</span>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <StatValue value={activeJobs.length.toString()} label="Active" tone="good" />
        <StatValue value={failedJobs.length.toString()} label="Failed" tone={failedJobs.length > 0 ? 'bad' : undefined} />
        <StatValue value={pausedJobs.length.toString()} label="Paused" />
      </div>

      {failedJobs.length > 0 && (
        <div className="space-y-2">
          <div className="text-xs text-[--ui-text-tertiary] font-medium">Recent Failures</div>
          {failedJobs.slice(0, 3).map(job => (
            <div key={job.id} className="flex items-center gap-2 text-xs">
              <XCircle className="size-3 text-red-400 shrink-0" />
              <span className="text-[--ui-text-secondary] truncate">{job.name}</span>
              <span className="text-[--ui-text-tertiary] ml-auto shrink-0">
                {job.last_run_at ? formatIso(job.last_run_at) : '—'}
              </span>
            </div>
          ))}
        </div>
      )}

      {jobs && jobs.length === 0 && (
        <div className="text-xs text-[--ui-text-tertiary]">
          No cron jobs configured. Create one to schedule automated tasks.
        </div>
      )}
    </CardShell>
  )
}

/* ─── Plugin Security Card ─── */

function PluginCard({ plugins, loading }: { plugins?: PluginPermission[]; loading: boolean }) {
  const needsApproval = plugins?.filter(p => p.status === 'needs_approval') || []
  const active = plugins?.filter(p => p.status === 'active') || []

  if (loading) {
    return (
      <CardShell>
        <CardLabel icon={<Shield className="size-3.5" />}>Plugins</CardLabel>
        <div className="space-y-3">
          <Skeleton className="h-8 w-20" />
          <Skeleton className="h-4 w-32" />
        </div>
      </CardShell>
    )
  }

  return (
    <CardShell>
      <div className="flex items-start justify-between mb-3">
        <CardLabel icon={<Shield className="size-3.5" />}>Plugin Security</CardLabel>
        <span className="text-xs text-[--ui-text-tertiary]">{plugins?.length || 0} installed</span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <StatValue value={active.length.toString()} label="Active" tone="good" />
        <StatValue value={needsApproval.length.toString()} label="Need Approval" tone={needsApproval.length > 0 ? 'warn' : undefined} />
      </div>

      {needsApproval.length > 0 && (
        <div className="space-y-2">
          <div className="text-xs text-[--ui-text-tertiary] font-medium">Needs Approval</div>
          {needsApproval.slice(0, 3).map(p => (
            <div key={p.name} className="flex items-center gap-2 text-xs">
              <ShieldAlert className="size-3 text-amber-400 shrink-0" />
              <span className="text-[--ui-text-secondary] truncate">{p.name}</span>
              <span className="text-[--ui-text-tertiary] ml-auto shrink-0">
                {p.dangerous_permissions.length} dangerous
              </span>
            </div>
          ))}
        </div>
      )}
    </CardShell>
  )
}

/* ─── Main Dashboard ─── */

export default function DashboardView() {
  const { t } = useI18n()
  const [refreshKey, setRefreshKey] = useState(0)

  // Health data
  const { data: healthData, isLoading: healthLoading } = useQuery({
    queryKey: ['dashboard-health', refreshKey],
    queryFn: async () => {
      const resp = await fetch('/api/health/detailed')
      if (!resp.ok) throw new Error('Health check failed')
      return resp.json() as Promise<HealthData>
    },
    refetchInterval: 30_000,
  })

  // Usage data
  const { data: usageData, isLoading: usageLoading } = useQuery({
    queryKey: ['dashboard-usage', refreshKey],
    queryFn: async () => {
      const resp = await fetch('/api/usage/summary')
      if (!resp.ok) throw new Error('Usage check failed')
      return resp.json() as Promise<UsageData>
    },
    refetchInterval: 60_000,
  })

  // Cron jobs
  const { data: cronJobs, isLoading: cronLoading } = useQuery({
    queryKey: ['dashboard-cron', refreshKey],
    queryFn: async () => {
      const { getCronJobs } = await import('@/hermes')
      return getCronJobs(true) // include disabled
    },
    refetchInterval: 30_000,
  })

  // Plugin permissions
  const { data: pluginData, isLoading: pluginLoading } = useQuery({
    queryKey: ['dashboard-plugins', refreshKey],
    queryFn: async () => {
      const resp = await fetch('/api/plugins/permissions')
      if (!resp.ok) throw new Error('Plugin check failed')
      return resp.json() as Promise<{ plugins: PluginPermission[] }>
    },
    refetchInterval: 60_000,
  })

  const handleResetHealth = async () => {
    try {
      await fetch('/api/health/reset', { method: 'POST' })
      setRefreshKey(k => k + 1)
    } catch (e) {
      notifyError('Failed to reset health monitor')
    }
  }

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-xl font-semibold text-[--ui-text-primary]">Dashboard</h1>
            <p className="text-sm text-[--ui-text-tertiary] mt-0.5">
              Gateway health, usage, cron jobs, and plugin security at a glance
            </p>
          </div>
          <Button variant="secondary" size="sm" onClick={() => setRefreshKey(k => k + 1)}>
            <RefreshCw className="size-3.5 mr-1.5" />
            Refresh
          </Button>
        </div>

        {/* Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <HealthCard data={healthData} loading={healthLoading} onReset={handleResetHealth} />
          <UsageCard data={usageData} loading={usageLoading} />
          <CronCard jobs={cronJobs} loading={cronLoading} />
          <PluginCard plugins={pluginData?.plugins} loading={pluginLoading} />
        </div>

        {/* Recent Activity */}
        <div className="mt-6">
          <CardShell>
            <CardLabel icon={<Activity className="size-3.5" />}>Recent Activity</CardLabel>
            {usageData?.sessions && usageData.sessions.length > 0 ? (
              <div className="space-y-2">
                {usageData.sessions.slice(0, 10).map(session => (
                  <div key={session.id} className="flex items-center gap-3 text-xs py-1.5 border-b border-[--ui-stroke-tertiary] last:border-0">
                    <MessageCircle className="size-3.5 text-[--ui-text-tertiary] shrink-0" />
                    <span className="text-[--ui-text-secondary] truncate flex-1">{session.title || 'Untitled'}</span>
                    <span className="text-[--ui-text-tertiary] shrink-0">{session.model}</span>
                    <span className="text-[--ui-text-tertiary] tabular-nums shrink-0">
                      {formatTokens(session.input_tokens + session.output_tokens)}
                    </span>
                    <span className="text-[--ui-text-tertiary] shrink-0">{session.profile}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-[--ui-text-tertiary]">No recent activity</div>
            )}
          </CardShell>
        </div>
      </div>
    </div>
  )
}
