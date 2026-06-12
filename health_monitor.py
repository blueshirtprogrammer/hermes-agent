"""
Hermes Agent Health Monitor — Auto-recovery and alerting system.

Monitors gateway health, detects crash loops, and auto-recovers.
Features:
- Process watchdog: detects zombie/crashed gateway processes
- SIGTERM flap detection: identifies rapid restart loops
- Auto-recovery: restarts gateway with exponential backoff
- Health metrics: uptime, restart count, last crash reason
- Alerting: delivers alerts via configured channels on persistent failures
- Dashboard integration: exposes health status via /api/health/detailed

This module is designed to be self-contained and moatable.
"""

from __future__ import annotations

import json
import logging
import os
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class HealthState(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRASH_LOOP = "crash_loop"
    UNREACHABLE = "unreachable"
    STARTING = "starting"
    STOPPED = "stopped"


@dataclass
class CrashRecord:
    timestamp: str
    exit_code: Optional[int]
    signal_name: Optional[str]
    uptime_seconds: float
    reason: str


@dataclass
class HealthMetrics:
    state: str = HealthState.STOPPED.value
    uptime_seconds: float = 0.0
    restart_count: int = 0
    crash_count: int = 0
    last_crash: Optional[CrashRecord] = None
    last_healthy_at: Optional[str] = None
    last_check_at: Optional[str] = None
    flap_detected: bool = False
    backoff_seconds: float = 0.0
    pid: Optional[int] = None
    version: str = ""
    platform: str = ""


@dataclass
class HealthConfig:
    """Configuration for the health monitor."""
    # How often to check gateway health (seconds)
    check_interval: float = 30.0
    # How many crashes in the flap window before declaring a crash loop
    flap_threshold: int = 3
    # Window in seconds for flap detection
    flap_window: float = 300.0
    # Initial backoff for auto-restart (seconds)
    restart_backoff_initial: float = 5.0
    # Maximum backoff for auto-restart (seconds)
    restart_backoff_max: float = 300.0
    # Backoff multiplier after each failed restart
    restart_backoff_multiplier: float = 2.0
    # Maximum consecutive restart attempts before giving up
    max_restart_attempts: int = 10
    # Whether to auto-restart the gateway on crash
    auto_restart: bool = True
    # Whether to send alerts on persistent failures
    alert_on_failure: bool = True
    # Minimum uptime (seconds) to consider the gateway "healthy"
    min_healthy_uptime: float = 60.0
    # Health check timeout (seconds)
    health_check_timeout: float = 10.0


class HealthMonitor:
    """
    Monitors gateway health and manages auto-recovery.
    
    Usage:
        monitor = HealthMonitor(config=HealthConfig())
        monitor.start()
        # ... later ...
        metrics = monitor.get_metrics()
        monitor.stop()
    """

    def __init__(
        self,
        config: Optional[HealthConfig] = None,
        gateway_start_fn: Optional[Callable[[], subprocess.Popen]] = None,
        gateway_stop_fn: Optional[Callable[[], None]] = None,
        alert_fn: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        state_dir: Optional[Path] = None,
    ):
        self.config = config or HealthConfig()
        self._gateway_start_fn = gateway_start_fn
        self._gateway_stop_fn = gateway_stop_fn
        self._alert_fn = alert_fn
        self._state_dir = state_dir or (Path.home() / ".hermes" / "health")
        self._state_dir.mkdir(parents=True, exist_ok=True)
        self._state_file = self._state_dir / "health_state.json"
        self._crashes_file = self._state_dir / "crash_history.jsonl"

        self._metrics = HealthMetrics()
        self._crashes: List[CrashRecord] = []
        self._gateway_process: Optional[subprocess.Popen] = None
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._restart_attempts = 0
        self._current_backoff = self.config.restart_backoff_initial
        self._started_at: Optional[float] = None

    def start(self) -> None:
        """Start the health monitor."""
        self._stop_event.clear()
        self._load_state()
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="health-monitor",
        )
        self._monitor_thread.start()
        logger.info("Health monitor started (interval=%.1fs)", self.config.check_interval)

    def stop(self) -> None:
        """Stop the health monitor."""
        self._stop_event.set()
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=10)
        self._save_state()
        logger.info("Health monitor stopped")

    def get_metrics(self) -> Dict[str, Any]:
        """Get current health metrics."""
        with self._lock:
            metrics = asdict(self._metrics)
            metrics["recent_crashes"] = [asdict(c) for c in self._crashes[-5:]]
            return metrics

    def register_gateway_process(self, process: subprocess.Popen) -> None:
        """Register a gateway process to monitor."""
        with self._lock:
            self._gateway_process = process
            self._metrics.pid = process.pid
            self._metrics.state = HealthState.STARTING.value
            self._started_at = time.time()

    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while not self._stop_event.is_set():
            try:
                self._check_health()
            except Exception as e:
                logger.error("Health check error: %s", e)
            self._stop_event.wait(self.config.check_interval)

    def _check_health(self) -> None:
        """Perform a health check."""
        now = time.time()
        with self._lock:
            self._metrics.last_check_at = datetime.now(timezone.utc).isoformat()

            if self._gateway_process is None:
                self._metrics.state = HealthState.STOPPED.value
                return

            # Check if process is still running
            return_code = self._gateway_process.poll()

            if return_code is None:
                # Process is running
                if self._started_at:
                    self._metrics.uptime_seconds = now - self._started_at

                # Check if it's been healthy long enough
                if self._metrics.uptime_seconds >= self.config.min_healthy_uptime:
                    if self._metrics.state != HealthState.HEALTHY.value:
                        logger.info("Gateway is healthy (uptime=%.1fs)", self._metrics.uptime_seconds)
                        self._metrics.state = HealthState.HEALTHY.value
                        self._metrics.last_healthy_at = datetime.now(timezone.utc).isoformat()
                        self._restart_attempts = 0
                        self._current_backoff = self.config.restart_backoff_initial
                        self._metrics.flap_detected = False
            else:
                # Process exited
                uptime = self._metrics.uptime_seconds
                signal_name = self._signal_name(return_code)
                reason = f"Process exited with code {return_code}"
                if signal_name:
                    reason = f"Process killed by signal {signal_name} ({return_code})"

                crash = CrashRecord(
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    exit_code=return_code,
                    signal_name=signal_name,
                    uptime_seconds=uptime,
                    reason=reason,
                )
                self._record_crash(crash)
                self._metrics.last_crash = asdict(crash)
                self._metrics.crash_count += 1

                # Check for crash loop
                if self._is_flap_detected():
                    self._metrics.state = HealthState.CRASH_LOOP.value
                    self._metrics.flap_detected = True
                    logger.error("Crash loop detected! %d crashes in %.0fs",
                                 len(self._recent_crashes()), self.config.flap_window)
                    if self.config.alert_on_failure:
                        self._send_alert("Crash loop detected", self.get_metrics())
                else:
                    self._metrics.state = HealthState.DEGRADED.value

                # Auto-restart
                if self.config.auto_restart and not self._metrics.flap_detected:
                    self._attempt_restart()

            self._save_state()

    def _record_crash(self, crash: CrashRecord) -> None:
        """Record a crash event."""
        self._crashes.append(crash)
        # Keep only recent crashes
        cutoff = time.time() - self.config.flap_window * 2
        self._crashes = [
            c for c in self._crashes
            if datetime.fromisoformat(c.timestamp).timestamp() > cutoff
        ]
        # Append to crash history file
        try:
            with open(self._crashes_file, "a") as f:
                f.write(json.dumps(asdict(crash)) + "\n")
        except Exception:
            pass

    def _recent_crashes(self) -> List[CrashRecord]:
        """Get crashes within the flap detection window."""
        cutoff = time.time() - self.config.flap_window
        return [
            c for c in self._crashes
            if datetime.fromisoformat(c.timestamp).timestamp() > cutoff
        ]

    def _is_flap_detected(self) -> bool:
        """Check if we're in a crash loop."""
        return len(self._recent_crashes()) >= self.config.flap_threshold

    def _attempt_restart(self) -> None:
        """Attempt to restart the gateway with exponential backoff."""
        if self._restart_attempts >= self.config.max_restart_attempts:
            logger.error("Max restart attempts (%d) reached — giving up",
                         self.config.max_restart_attempts)
            self._metrics.state = HealthState.CRASH_LOOP.value
            if self.config.alert_on_failure:
                self._send_alert("Max restart attempts reached", self.get_metrics())
            return

        self._restart_attempts += 1
        self._metrics.restart_count += 1
        self._metrics.backoff_seconds = self._current_backoff

        logger.info("Attempting gateway restart #%d (backoff=%.1fs)",
                     self._restart_attempts, self._current_backoff)

        # Wait for backoff
        if self._current_backoff > 0:
            self._stop_event.wait(self._current_backoff)

        if self._stop_event.is_set():
            return

        # Stop existing process
        if self._gateway_stop_fn:
            try:
                self._gateway_stop_fn()
            except Exception as e:
                logger.warning("Error stopping gateway: %s", e)

        # Start new process
        if self._gateway_start_fn:
            try:
                self._gateway_process = self._gateway_start_fn()
                self._metrics.pid = self._gateway_process.pid
                self._metrics.state = HealthState.STARTING.value
                self._started_at = time.time()
                logger.info("Gateway restarted (pid=%d)", self._gateway_process.pid)
            except Exception as e:
                logger.error("Failed to restart gateway: %s", e)

        # Increase backoff
        self._current_backoff = min(
            self._current_backoff * self.config.restart_backoff_multiplier,
            self.config.restart_backoff_max,
        )

    def _send_alert(self, message: str, metrics: Dict[str, Any]) -> None:
        """Send an alert about a persistent failure."""
        if self._alert_fn:
            try:
                self._alert_fn(message, metrics)
            except Exception as e:
                logger.error("Alert delivery failed: %s", e)

    @staticmethod
    def _signal_name(return_code: int) -> Optional[str]:
        """Get signal name from negative return code."""
        if return_code < 0:
            try:
                return signal.Signals(-return_code).name
            except (ValueError, AttributeError):
                return None
        # Common exit codes that indicate signals
        sig_map = {137: "SIGKILL", "143": "SIGTERM", "139": "SIGSEGV", "134": "SIGABRT"}
        return sig_map.get(str(return_code))

    def _save_state(self) -> None:
        """Persist health state to disk."""
        try:
            state = {
                "metrics": asdict(self._metrics),
                "restart_attempts": self._restart_attempts,
                "current_backoff": self._current_backoff,
                "saved_at": datetime.now(timezone.utc).isoformat(),
            }
            self._state_file.write_text(json.dumps(state, indent=2))
        except Exception:
            pass

    def _load_state(self) -> None:
        """Load health state from disk."""
        try:
            if self._state_file.exists():
                state = json.loads(self._state_file.read_text())
                self._restart_attempts = state.get("restart_attempts", 0)
                self._current_backoff = state.get("current_backoff", self.config.restart_backoff_initial)
        except Exception:
            pass
