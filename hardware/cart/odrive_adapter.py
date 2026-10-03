"""Experimental mapping seam derived from shoppy PR #4, never used by the server.

Accepts an already-provisioned driver (mocks in tests). No discovery, calibration,
error clearing, reboot, closed-loop entry, or watchdog configuration. This class
alone is NOT a commissioned hardware backend.
"""

import math


class ODriveAdapter:
    def __init__(self, left_axis, right_axis, turns_per_second=1.0, left_sign=-1, right_sign=1):
        if left_axis is right_axis:
            raise ValueError("Axes must be distinct")
        if (
            type(turns_per_second) not in (int, float)
            or not math.isfinite(turns_per_second)
            or turns_per_second <= 0
        ):
            raise ValueError("Explicit positive finite velocity scale required")
        if left_sign not in (-1, 1) or right_sign not in (-1, 1):
            raise ValueError("Signs must be -1 or 1")
        self.axes = (left_axis, right_axis)
        self.scale = turns_per_second
        self.signs = (left_sign, right_sign)

    def write(self, left, right):
        if not all(type(v) in (int, float) and -1 <= v <= 1 for v in (left, right)):
            self.stop()
            raise ValueError("Expected normalized wheel velocities")
        try:
            for axis in self.axes:
                timeout = axis.config.watchdog_timeout
                if (
                    not axis.config.enable_watchdog
                    or type(timeout) not in (int, float)
                    or not 0 < timeout <= 0.5
                ):
                    raise RuntimeError("Independent watchdog must be commissioned")
                if axis.error:
                    raise RuntimeError("Axis is not healthy")
            for axis, value, sign in zip(self.axes, (left, right), self.signs):
                axis.controller.input_vel = value * self.scale * sign
            # Feed only after a fresh accepted pair, never from an idle loop.
            for axis in self.axes:
                axis.watchdog_feed()
        except Exception:
            self.stop()
            raise

    def stop(self):
        errors = []
        for axis in self.axes:
            try:
                axis.controller.input_vel = 0.0
            except Exception as exc:
                errors.append(exc)
        if errors:
            raise RuntimeError("Could not zero every drive axis") from errors[0]
