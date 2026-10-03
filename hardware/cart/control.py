"""Transport-independent, single-owner drive gate. No hardware imports or discovery."""

import math
import secrets
import threading
import time
from dataclasses import dataclass
from typing import List, Optional, Protocol, Tuple


class Drive(Protocol):
    def write(self, left: float, right: float) -> None: ...
    def stop(self) -> None: ...


class ArmStop(Protocol):
    """Compatible with ArmController.emergency_stop; injected explicitly."""

    def emergency_stop(self): ...


@dataclass(frozen=True)
class Limits:
    heartbeat_timeout: float = 0.5
    command_timeout: float = 0.25
    permit_timeout: float = 0.25
    max_output: float = 0.3

    def __post_init__(self):
        for value in vars(self).values():
            if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                raise ValueError("Limits must be positive finite numbers")
        if self.max_output > 1:
            raise ValueError("max_output must be <= 1")


class SimDrive:
    def __init__(self):
        self.output = (0.0, 0.0)

    def write(self, left, right):
        self.output = (left, right)

    def stop(self):
        self.output = (0.0, 0.0)


class DriveGate:
    """One latest-value slot; stop clears it and revokes the ownership epoch.

    All state and output calls share a lock: a pre-stop write cannot run after stop.
    Drivers must have bounded calls; an independent hardware watchdog is required
    for any future physical integration. Python cannot stop a stalled USB call.
    """

    def __init__(self, drive: Drive, arms=(), limits=None, clock=time.monotonic):
        self.drive, self.arms = drive, tuple(arms)
        self.limits, self.clock = limits or Limits(), clock
        self.lock = threading.RLock()
        self.owner: Optional[str] = None
        self.epoch: Optional[str] = None
        self.permit: Optional[str] = None
        self.pending: Optional[Tuple[float, float]] = None
        self.seq = -1
        self.heartbeat_at = self.command_at = self.permit_at = 0.0
        self.estopped = False
        self.reason = "startup"
        self.output = (0.0, 0.0)
        self.stop_errors: List[str] = []
        self._stop("startup")

    def _stop(self, reason, latch=False):
        self.owner = self.epoch = self.permit = self.pending = None
        self.output = (0.0, 0.0)
        self.reason = reason
        self.estopped = self.estopped or latch
        self.stop_errors = []
        for name, action in [("drive", self.drive.stop)] + [
            (f"arm:{i}", arm.emergency_stop) for i, arm in enumerate(self.arms)
        ]:
            try:
                result = action()
                if isinstance(result, dict) and (
                    "error" in result or result.get("status") == "error"
                ):
                    raise RuntimeError("backend reported stop failure")
            except Exception:
                self.stop_errors.append(name)
                self.estopped = True

    def status(self):
        with self.lock:
            return {
                "estopped": self.estopped,
                "reason": self.reason,
                "occupied": self.owner is not None,
                "output": self.output,
                "stop_errors": list(self.stop_errors),
            }

    def acquire(self, sid):
        with self.lock:
            self._expire()
            if self.estopped or self.owner is not None:
                return None
            self.owner, self.epoch = sid, secrets.token_hex(16)
            self.seq = -1
            self.heartbeat_at = self.command_at = self.clock()
            self.reason = "armed"
            return self.epoch

    def _expire(self):
        now = self.clock()
        if self.owner is not None and (
            now - self.heartbeat_at >= self.limits.heartbeat_timeout
            or now - self.command_at >= self.limits.command_timeout
        ):
            self._stop("timeout")

    def heartbeat(self, sid, epoch):
        with self.lock:
            self._expire()
            if sid != self.owner or epoch != self.epoch or self.owner is None:
                return None
            self.heartbeat_at = self.clock()
            self.permit_at = self.heartbeat_at
            self.permit = secrets.token_hex(16)
            return self.permit

    def command(self, sid, message):
        with self.lock:
            self._expire()
            if self.owner is None or sid != self.owner:
                return False
            valid = isinstance(message, dict) and set(message) == {
                "epoch",
                "permit",
                "seq",
                "left",
                "right",
                "deadman",
            }
            if valid:
                valid = (
                    message["epoch"] == self.epoch
                    and self.permit is not None
                    and message["permit"] == self.permit
                    and self.clock() - self.permit_at < self.limits.permit_timeout
                    and type(message["seq"]) is int
                    and self.seq < message["seq"] < 2**53
                    and message["deadman"] is True
                    and all(
                        type(message[k]) in (int, float) and -1 <= message[k] <= 1
                        for k in ("left", "right")
                    )
                )
            if not valid:
                self._stop("invalid_or_released_command")
                return False
            self.seq = message["seq"]
            self.command_at = self.clock()
            self.pending = tuple(message[k] * self.limits.max_output for k in ("left", "right"))
            return True

    def tick(self):
        with self.lock:
            self._expire()
            if self.pending is not None:
                value, self.pending = self.pending, None
                try:
                    self.drive.write(*value)
                    self.output = value
                except Exception:
                    self._stop("drive_error", latch=True)

    def release(self, sid):
        with self.lock:
            if sid == self.owner and self.owner is not None:
                self._stop("released_or_disconnected")

    def emergency_stop(self):
        with self.lock:
            self._stop("software_estop", latch=True)

    def reset(self):
        with self.lock:
            self._stop("reset")
            # A failed stop must never be cleared by reset.
            if not self.stop_errors:
                self.estopped = False
            return not self.estopped

    def close(self):
        with self.lock:
            self._stop("shutdown", latch=True)
