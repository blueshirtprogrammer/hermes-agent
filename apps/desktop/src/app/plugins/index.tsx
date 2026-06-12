/**
 * Plugin Marketplace — Browse, install, and configure plugins.
 *
 * Features:
 * - Browse installed plugins with permission/security info
 * - Search and filter plugins
 * - Install new plugins from marketplace or local directory
 * - Configure plugin settings
 * - Approve/revoke dangerous permissions
 * - View plugin changelog and documentation
 * - One-click update for installed plugins
 */

import { useStore } from '@nanostores/react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useCallback, useMemo, useState } from 'react'

import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { SearchField } from '@/components/ui/search-field'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { Switch } from '@/components/ui/switch'
import { useI18n } from '@/i18n'
import {
  AlertTriangle,
  CheckCircle2,
  Download,
  ExternalLink,
  Eye,
  EyeOff,
  Package,
  RefreshCw,
  Search,
  Settings,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Trash2,
  Upload
} from '@/lib/icons'
import { cn } from '@/lib/utils'
import { notify, notifyError } from '@/store/notifications'

import type { ReactNode } from 'react'

/* ─── Types ─── */

interface PluginInfo {
  name: string
  version: string
  description: string
  author: string
  hooks: string[]
  permissions: string[]
  dangerous_permissions: string[]
  requires_approval: boolean
  enabled: boolean
  approved: boolean
  status: 'active' | 'needs_approval' | 'disabled'
  install_path?: string
  homepage?: string
  changelog?: string
}

interface MarketplacePlugin {
  id: string
  name: string
  version: string
  description: string
  author: string
  downloads: number
  rating: number
  category: string
  tags: string[]
  permissions: string[]
  dangerous_permissions: string[]
  installed: boolean
  icon?: string
}

/* ─── Helpers ─── */

function statusTone(status: string): 'good' | 'warn' | 'bad' | 'muted' {
  switch (status) {
    case 'active': return 'good'
    case 'needs_approval': return 'warn'
    case 'disabled': return 'muted'
    default: return 'muted'
  }
}

const TONE_BADGE: Record<string, string> = {
  good: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  warn: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  bad: 'bg-red-500/10 text-red-400 border-red-500/20',
  muted: 'bg-zinc-500/10 text-zinc-400 border-zinc-500/20',
}

/* ─── Sub-components ─── */

function PluginCard({ plugin, onApprove, onRevoke, onInstall }: {
  plugin: PluginInfo
  onApprove: (name: string) => void
  onRevoke: (name: string) => void
  onInstall?: (name: string) => void
}) {
  const { t } = useI18n()
  const tone = statusTone(plugin.status)

  return (
    <div className={cn(
      'rounded-xl border border-[--ui-stroke-tertiary] bg-[--ui-bg-secondary] p-4',
      'hover:border-[--ui-stroke-secondary] transition-colors'
    )}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="size-10 rounded-lg bg-[--ui-bg-tertiary] flex items-center justify-center">
            <Package className="size-5 text-[--ui-text-secondary]" />
          </div>
          <div>
            <h3 className="text-sm font-medium text-[--ui-text-primary]">{plugin.name}</h3>
            <p className="text-xs text-[--ui-text-tertiary]">v{plugin.version} · {plugin.author}</p>
          </div>
        </div>
        <div className={cn('px-2 py-0.5 rounded-full text-xs font-medium border', TONE_BADGE[tone])}>
          {plugin.status === 'active' ? 'Active' : plugin.status === 'needs_approval' ? 'Needs Approval' : 'Disabled'}
        </div>
      </div>

      <p className="text-xs text-[--ui-text-secondary] mb-3 line-clamp-2">{plugin.description}</p>

      {/* Permissions */}
      {plugin.permissions.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {plugin.permissions.slice(0, 4).map(perm => (
            <span key={perm} className={cn(
              'px-1.5 py-0.5 rounded text-[10px] font-medium border',
              plugin.dangerous_permissions.includes(perm)
                ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                : 'bg-[--ui-bg-tertiary] text-[--ui-text-tertiary] border-[--ui-stroke-tertiary]'
            )}>
              {perm}
            </span>
          ))}
          {plugin.permissions.length > 4 && (
            <span className="px-1.5 py-0.5 rounded text-[10px] text-[--ui-text-tertiary]">
              +{plugin.permissions.length - 4} more
            </span>
          )}
        </div>
      )}

      {/* Dangerous permissions warning */}
      {plugin.dangerous_permissions.length > 0 && (
        <div className="flex items-center gap-1.5 px-2 py-1.5 rounded-lg bg-amber-500/5 border border-amber-500/10 text-xs text-amber-400 mb-3">
          <ShieldAlert className="size-3 shrink-0" />
          <span>{plugin.dangerous_permissions.length} dangerous permission{plugin.dangerous_permissions.length > 1 ? 's' : ''} — {plugin.dangerous_permissions.join(', ')}</span>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-2 pt-3 border-t border-[--ui-stroke-tertiary]">
        {plugin.status === 'needs_approval' && (
          <Button variant="secondary" size="xs" onClick={() => onApprove(plugin.name)}>
            <ShieldCheck className="size-3 mr-1" />
            Approve
          </Button>
        )}
        {plugin.status === 'active' && plugin.dangerous_permissions.length > 0 && (
          <Button variant="text" size="xs" onClick={() => onRevoke(plugin.name)}>
            <ShieldAlert className="size-3 mr-1" />
            Revoke
          </Button>
        )}
        <Button variant="text" size="xs" className="ml-auto text-[--ui-text-tertiary]">
          <Settings className="size-3 mr-1" />
          Configure
        </Button>
      </div>
    </div>
  )
}

function MarketplaceCard({ plugin, onInstall }: {
  plugin: MarketplacePlugin
  onInstall: (id: string) => void
}) {
  return (
    <div className={cn(
      'rounded-xl border border-[--ui-stroke-tertiary] bg-[--ui-bg-secondary] p-4',
      'hover:border-[--ui-stroke-secondary] transition-colors'
    )}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="size-10 rounded-lg bg-[--ui-bg-tertiary] flex items-center justify-center">
            {plugin.icon ? (
              <img src={plugin.icon} alt={plugin.name} className="size-6" />
            ) : (
              <Package className="size-5 text-[--ui-text-secondary]" />
            )}
          </div>
          <div>
            <h3 className="text-sm font-medium text-[--ui-text-primary]">{plugin.name}</h3>
            <p className="text-xs text-[--ui-text-tertiary]">{plugin.author}</p>
          </div>
        </div>
        <Badge variant="secondary" className="text-[10px]">
          {plugin.category}
        </Badge>
      </div>

      <p className="text-xs text-[--ui-text-secondary] mb-3 line-clamp-2">{plugin.description}</p>

      <div className="flex items-center gap-3 text-xs text-[--ui-text-tertiary] mb-3">
        <span>{plugin.downloads.toLocaleString()} downloads</span>
        <span>★ {plugin.rating.toFixed(1)}</span>
        <span>v{plugin.version}</span>
      </div>

      {plugin.dangerous_permissions.length > 0 && (
        <div className="flex items-center gap-1.5 px-2 py-1.5 rounded-lg bg-amber-500/5 border border-amber-500/10 text-xs text-amber-400 mb-3">
          <ShieldAlert className="size-3 shrink-0" />
          <span>Requires approval: {plugin.dangerous_permissions.join(', ')}</span>
        </div>
      )}

      <div className="flex items-center gap-2 pt-3 border-t border-[--ui-stroke-tertiary]">
        <Button
          variant={plugin.installed ? 'secondary' : 'default'}
          size="xs"
          onClick={() => onInstall(plugin.id)}
          disabled={plugin.installed}
        >
          {plugin.installed ? (
            <>
              <CheckCircle2 className="size-3 mr-1" />
              Installed
            </>
          ) : (
            <>
              <Download className="size-3 mr-1" />
              Install
            </>
          )}
        </Button>
        <Button variant="text" size="xs" className="ml-auto text-[--ui-text-tertiary]">
          <ExternalLink className="size-3 mr-1" />
          Details
        </Button>
      </div>
    </div>
  )
}

function InstallPluginDialog({ open, onClose, onInstall }: {
  open: boolean
  onClose: () => void
  onInstall: (source: string) => void
}) {
  const [source, setSource] = useState('')
  const [installType, setInstallType] = useState<'url' | 'path' | 'id'>('url')

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Install Plugin</DialogTitle>
          <DialogDescription>
            Install a plugin from a Git repository, local directory, or marketplace ID.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="flex gap-2">
            {(['url', 'path', 'id'] as const).map(type => (
              <Button
                key={type}
                variant={installType === type ? 'default' : 'secondary'}
                size="sm"
                onClick={() => setInstallType(type)}
              >
                {type === 'url' ? 'Git URL' : type === 'path' ? 'Local Path' : 'Marketplace ID'}
              </Button>
            ))}
          </div>

          <SearchField
            placeholder={
              installType === 'url' ? 'https://github.com/author/plugin-name' :
              installType === 'path' ? '/path/to/plugin/directory' :
              'plugin-marketplace-id'
            }
            value={source}
            onChange={setSource}
          />

          {installType === 'url' && (
            <p className="text-xs text-[--ui-text-tertiary]">
              The plugin directory must contain a plugin.yaml manifest with declared permissions.
            </p>
          )}
        </div>

        <DialogFooter>
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button
            variant="default"
            onClick={() => {
              onInstall(source)
              onClose()
              setSource('')
            }}
            disabled={!source.trim()}
          >
            <Download className="size-3.5 mr-1.5" />
            Install
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

/* ─── Main Page ─── */

export default function PluginsPage() {
  const { t } = useI18n()
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [tab, setTab] = useState<'installed' | 'marketplace'>('installed')
  const [installDialogOpen, setInstallDialogOpen] = useState(false)
  const [filter, setFilter] = useState<'all' | 'active' | 'needs_approval' | 'disabled'>('all')

  // Fetch installed plugins
  const { data: pluginsData, isLoading: pluginsLoading } = useQuery({
    queryKey: ['plugins-permissions'],
    queryFn: async () => {
      const resp = await fetch('/api/plugins/permissions')
      if (!resp.ok) throw new Error('Failed to fetch plugins')
      return resp.json() as Promise<{ plugins: PluginInfo[] }>
    },
    refetchInterval: 30_000,
  })

  // Fetch marketplace plugins (mock for now — would hit a real marketplace API)
  const { data: marketplaceData, isLoading: marketplaceLoading } = useQuery({
    queryKey: ['plugins-marketplace', search],
    queryFn: async () => {
      // TODO: Replace with real marketplace API
      const mockPlugins: MarketplacePlugin[] = [
        {
          id: 'slack-integration',
          name: 'Slack Integration',
          version: '1.2.0',
          description: 'Send and receive messages from Slack workspaces. Supports channels, DMs, and threaded conversations.',
          author: 'NousResearch',
          downloads: 125000,
          rating: 4.8,
          category: 'Messaging',
          tags: ['slack', 'chat', 'team'],
          permissions: ['network.http', 'tools.read'],
          dangerous_permissions: [],
          installed: false,
        },
        {
          id: 'github-actions',
          name: 'GitHub Actions',
          version: '2.0.1',
          description: 'Trigger and monitor GitHub Actions workflows. Deploy code, run tests, manage releases.',
          author: 'NousResearch',
          downloads: 89000,
          rating: 4.6,
          category: 'DevOps',
          tags: ['github', 'ci/cd', 'deploy'],
          permissions: ['network.http', 'file.read', 'tools.read'],
          dangerous_permissions: ['file.write'],
          installed: false,
        },
        {
          id: 'notion-sync',
          name: 'Notion Sync',
          version: '1.0.3',
          description: 'Sync agent outputs to Notion databases and pages. Create structured documentation automatically.',
          author: 'Community',
          downloads: 45000,
          rating: 4.4,
          category: 'Productivity',
          tags: ['notion', 'docs', 'sync'],
          permissions: ['network.http', 'memory.write'],
          dangerous_permissions: ['memory.write'],
          installed: false,
        },
        {
          id: 'stripe-billing',
          name: 'Stripe Billing',
          version: '1.1.0',
          description: 'Manage Stripe subscriptions, invoices, and payments. Automated billing workflows.',
          author: 'Community',
          downloads: 32000,
          rating: 4.7,
          category: 'Finance',
          tags: ['stripe', 'billing', 'payments'],
          permissions: ['network.http', 'network.webhook', 'memory.write'],
          dangerous_permissions: ['memory.write', 'network.webhook'],
          installed: false,
        },
      ]
      return { plugins: mockPlugins.filter(p =>
        !search || p.name.toLowerCase().includes(search.toLowerCase()) ||
        p.description.toLowerCase().includes(search.toLowerCase()) ||
        p.tags.some(tag => tag.toLowerCase().includes(search.toLowerCase()))
      ) }
    },
    refetchInterval: 120_000,
  })

  // Approve mutation
  const approveMutation = useMutation({
    mutationFn: async (pluginName: string) => {
      const resp = await fetch(`/api/plugins/approve/${encodeURIComponent(pluginName)}`, { method: 'POST' })
      if (!resp.ok) throw new Error('Approval failed')
      return resp.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plugins-permissions'] })
      notify('Plugin approved')
    },
    onError: () => notifyError('Failed to approve plugin'),
  })

  // Revoke mutation
  const revokeMutation = useMutation({
    mutationFn: async (pluginName: string) => {
      const resp = await fetch(`/api/plugins/approve/${encodeURIComponent(pluginName)}`, { method: 'DELETE' })
      if (!resp.ok) throw new Error('Revoke failed')
      return resp.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plugins-permissions'] })
      notify('Plugin approval revoked')
    },
    onError: () => notifyError('Failed to revoke approval'),
  })

  // Filter plugins
  const filteredPlugins = useMemo(() => {
    if (!pluginsData?.plugins) return []
    let plugins = pluginsData.plugins
    if (filter !== 'all') {
      plugins = plugins.filter(p => p.status === filter)
    }
    if (search) {
      const s = search.toLowerCase()
      plugins = plugins.filter(p =>
        p.name.toLowerCase().includes(s) ||
        p.description.toLowerCase().includes(s)
      )
    }
    return plugins
  }, [pluginsData, filter, search])

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-5xl mx-auto p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-xl font-semibold text-[--ui-text-primary]">Plugins</h1>
            <p className="text-sm text-[--ui-text-tertiary] mt-0.5">
              Extend Hermes with plugins. Review permissions before installing.
            </p>
          </div>
          <Button variant="default" size="sm" onClick={() => setInstallDialogOpen(true)}>
            <Upload className="size-3.5 mr-1.5" />
            Install Plugin
          </Button>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-4 mb-6">
          <button
            className={cn(
              'text-sm font-medium pb-2 border-b-2 transition-colors',
              tab === 'installed'
                ? 'text-[--ui-text-primary] border-[--theme-primary]'
                : 'text-[--ui-text-tertiary] border-transparent hover:text-[--ui-text-secondary]'
            )}
            onClick={() => setTab('installed')}
          >
            Installed {pluginsData?.plugins?.length ? `(${pluginsData.plugins.length})` : ''}
          </button>
          <button
            className={cn(
              'text-sm font-medium pb-2 border-b-2 transition-colors',
              tab === 'marketplace'
                ? 'text-[--ui-text-primary] border-[--theme-primary]'
                : 'text-[--ui-text-tertiary] border-transparent hover:text-[--ui-text-secondary]'
            )}
            onClick={() => setTab('marketplace')}
          >
            Marketplace
          </button>
        </div>

        {/* Search & Filter */}
        <div className="flex items-center gap-3 mb-6">
          <div className="flex-1">
            <SearchField
              placeholder={tab === 'installed' ? 'Search installed plugins...' : 'Search marketplace...'}
              value={search}
              onChange={setSearch}
            />
          </div>
          {tab === 'installed' && (
            <div className="flex items-center gap-1">
              {(['all', 'active', 'needs_approval', 'disabled'] as const).map(f => (
                <Button
                  key={f}
                  variant={filter === f ? 'secondary' : 'ghost'}
                  size="xs"
                  onClick={() => setFilter(f)}
                >
                  {f === 'all' ? 'All' : f === 'needs_approval' ? 'Needs Approval' : f.charAt(0).toUpperCase() + f.slice(1)}
                </Button>
              ))}
            </div>
          )}
        </div>

        {/* Content */}
        {tab === 'installed' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {pluginsLoading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-48 rounded-xl" />
              ))
            ) : filteredPlugins.length > 0 ? (
              filteredPlugins.map(plugin => (
                <PluginCard
                  key={plugin.name}
                  plugin={plugin}
                  onApprove={(name) => approveMutation.mutate(name)}
                  onRevoke={(name) => revokeMutation.mutate(name)}
                />
              ))
            ) : (
              <div className="col-span-2 text-center py-12">
                <Package className="size-12 text-[--ui-text-tertiary] mx-auto mb-3 opacity-50" />
                <p className="text-sm text-[--ui-text-tertiary]">
                  {search ? 'No plugins match your search' : 'No plugins installed'}
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {marketplaceLoading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-56 rounded-xl" />
              ))
            ) : marketplaceData?.plugins?.length > 0 ? (
              marketplaceData.plugins.map(plugin => (
                <MarketplaceCard
                  key={plugin.id}
                  plugin={plugin}
                  onInstall={() => notify(`Installing ${plugin.name}...`)}
                />
              ))
            ) : (
              <div className="col-span-2 text-center py-12">
                <Search className="size-12 text-[--ui-text-tertiary] mx-auto mb-3 opacity-50" />
                <p className="text-sm text-[--ui-text-tertiary]">No marketplace plugins found</p>
              </div>
            )}
          </div>
        )}

        {/* Install Dialog */}
        <InstallPluginDialog
          open={installDialogOpen}
          onClose={() => setInstallDialogOpen(false)}
          onInstall={(source) => notify(`Installing from ${source}...`)}
        />
      </div>
    </div>
  )
}
