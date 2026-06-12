"""
Plugin Permission System — Declarative permissions for Hermes plugins.

Plugins declare what they need in plugin.yaml:
  permissions:
    - file.read          # Read files from HERMES_HOME and workdir
    - file.write         # Write files to workdir
    - file.system        # Read/write any file on the system
    - network.http       # Make HTTP requests
    - network.webhook    # Deliver to webhook URLs
    - tools.read         # Access tool results
    - tools.delegate     # Use delegation tools
    - skills.load        # Load and execute skills
    - memory.read        # Read MEMORY.md / USER.md
    - memory.write       # Write to MEMORY.md / USER.md
    - cron.read          # Read cron job state
    - cron.manage        # Create/update/delete cron jobs

Permissions are checked at runtime before the plugin hook fires.
Plugins without explicit permissions get a safe default set.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Optional, Set

logger = logging.getLogger(__name__)


class Permission(str, Enum):
    """Available plugin permissions."""
    FILE_READ = "file.read"
    FILE_WRITE = "file.write"
    FILE_SYSTEM = "file.system"
    NETWORK_HTTP = "network.http"
    NETWORK_WEBHOOK = "network.webhook"
    TOOLS_READ = "tools.read"
    TOOLS_DELEGATE = "tools.delegate"
    SKILLS_LOAD = "skills.load"
    MEMORY_READ = "memory.read"
    MEMORY_WRITE = "memory.write"
    CRON_READ = "cron.read"
    CRON_MANAGE = "cron.manage"


# Safe defaults: what plugins get if they don't declare permissions
DEFAULT_PERMISSIONS: FrozenSet[Permission] = frozenset({
    Permission.FILE_READ,
    Permission.MEMORY_READ,
    Permission.TOOLS_READ,
})

# Dangerous permissions that require explicit user approval in config
DANGEROUS_PERMISSIONS: FrozenSet[Permission] = frozenset({
    Permission.FILE_SYSTEM,
    Permission.FILE_WRITE,
    Permission.TOOLS_DELEGATE,
    Permission.CRON_MANAGE,
    Permission.MEMORY_WRITE,
})

# All valid permissions
ALL_PERMISSIONS: FrozenSet[Permission] = frozenset(Permission)


@dataclass
class PluginManifest:
    """Parsed plugin manifest with permission declarations."""
    name: str
    version: str = "0.0.0"
    description: str = ""
    author: str = ""
    hooks: List[str] = field(default_factory=list)
    permissions: FrozenSet[Permission] = field(default_factory=lambda: DEFAULT_PERMISSIONS)
    dangerous_permissions: FrozenSet[Permission] = field(default_factory=frozenset)
    requires_approval: bool = False


def parse_manifest(manifest: Dict[str, Any], plugin_dir: Optional[Path] = None) -> PluginManifest:
    """Parse a plugin manifest dict into a PluginManifest."""
    name = manifest.get("name", "unknown")
    raw_perms = manifest.get("permissions", [])

    if not raw_perms:
        # No permissions declared — use safe defaults
        return PluginManifest(
            name=name,
            version=str(manifest.get("version", "0.0.0")),
            description=str(manifest.get("description", "")),
            author=str(manifest.get("author", "")),
            hooks=_parse_hooks(manifest.get("hooks", [])),
            permissions=DEFAULT_PERMISSIONS,
            dangerous_permissions=frozenset(),
            requires_approval=bool(DANGEROUS_PERMISSIONS & DEFAULT_PERMISSIONS),
        )

    perms: Set[Permission] = set()
    dangerous: Set[Permission] = set()

    for raw in raw_perms:
        raw_str = str(raw).strip().lower()
        try:
            perm = Permission(raw_str)
            perms.add(perm)
            if perm in DANGEROUS_PERMISSIONS:
                dangerous.add(perm)
        except ValueError:
            logger.warning("Plugin '%s': unknown permission '%s' — ignoring", name, raw_str)

    return PluginManifest(
        name=name,
        version=str(manifest.get("version", "0.0.0")),
        description=str(manifest.get("description", "")),
        author=str(manifest.get("author", "")),
        hooks=_parse_hooks(manifest.get("hooks", [])),
        permissions=frozenset(perms) if perms else DEFAULT_PERMISSIONS,
        dangerous_permissions=frozenset(dangerous),
        requires_approval=bool(dangerous),
    )


def _parse_hooks(raw_hooks: Any) -> List[str]:
    """Parse hooks from manifest."""
    if isinstance(raw_hooks, list):
        return [str(h).strip() for h in raw_hooks if str(h).strip()]
    return []


def check_permission(manifest: PluginManifest, permission: Permission, config: Dict[str, Any]) -> bool:
    """Check if a plugin has a specific permission.

    Checks:
    1. Plugin manifest declares the permission
    2. Plugin is in the enabled list (config.yaml plugins.enabled)
    3. For dangerous permissions, plugin is in the approved list
       (config.yaml plugins.approved)
    """
    # Check manifest
    if permission not in manifest.permissions:
        return False

    # Check enabled
    plugins_cfg = config.get("plugins", {})
    enabled = plugins_cfg.get("enabled", [])
    if enabled and manifest.name not in enabled:
        return False

    # Check dangerous permissions require approval
    if permission in DANGEROUS_PERMISSIONS:
        approved = plugins_cfg.get("approved", [])
        if manifest.name not in approved:
            logger.warning(
                "Plugin '%s' has dangerous permission '%s' but is not in plugins.approved — denied",
                manifest.name, permission.value,
            )
            return False

    return True


def get_plugin_permissions_report(config: Dict[str, Any], plugins_dir: Path) -> List[Dict[str, Any]]:
    """Generate a permissions report for all installed plugins.

    Used by the dashboard to show plugin security status.
    """
    import yaml

    report = []
    if not plugins_dir.is_dir():
        return report

    enabled = set(config.get("plugins", {}).get("enabled", []))
    approved = set(config.get("plugins", {}).get("approved", []))

    for child in sorted(plugins_dir.iterdir()):
        if not child.is_dir():
            continue
        manifest_file = child / "plugin.yaml"
        if not manifest_file.exists():
            manifest_file = child / "plugin.yml"
        if not manifest_file.exists():
            continue

        try:
            with open(manifest_file, encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
        except Exception:
            continue

        manifest = parse_manifest(raw, child)
        is_enabled = manifest.name in enabled or (not enabled and not manifest.requires_approval)
        is_approved = manifest.name in approved

        report.append({
            "name": manifest.name,
            "version": manifest.version,
            "description": manifest.description,
            "author": manifest.author,
            "hooks": manifest.hooks,
            "permissions": [p.value for p in sorted(manifest.permissions, key=lambda x: x.value)],
            "dangerous_permissions": [p.value for p in sorted(manifest.dangerous_permissions, key=lambda x: x.value)],
            "requires_approval": manifest.requires_approval,
            "enabled": is_enabled,
            "approved": is_approved,
            "status": "active" if (is_enabled and (not manifest.requires_approval or is_approved))
                       else "needs_approval" if (is_enabled and manifest.requires_approval and not is_approved)
                       else "disabled",
        })

    return report
