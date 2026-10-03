"""No real device imports. Fake time tests deadlines without sleeps."""

from types import SimpleNamespace

import pytest

from control_panel.server import create_app
from hardware.cart.control import DriveGate, Limits, SimDrive
from hardware.cart.odrive_adapter import ODriveAdapter


class Clock:
    now = 100.0

    def __call__(self):
        return self.now


def armed():
    clock = Clock()
    drive = SimDrive()
    gate = DriveGate(drive, clock=clock)
    epoch = gate.acquire("owner")
    permit = gate.heartbeat("owner", epoch)
    command = dict(epoch=epoch, permit=permit, seq=0, left=1, right=-1, deadman=True)
    return gate, drive, clock, command


def test_latest_pair_bounded_and_release_clears_pending():
    gate, drive, _, cmd = armed()
    for seq in range(1000):
        assert gate.command("owner", dict(cmd, seq=seq))
    gate.tick()
    assert drive.output == (0.3, -0.3)
    assert gate.pending is None
    assert gate.command("owner", dict(cmd, seq=1000))
    gate.release("owner")
    gate.tick()
    assert drive.output == (0, 0)
    assert not gate.command("owner", dict(cmd, seq=1001))


@pytest.mark.parametrize(
    "patch",
    [
        {"left": 10**1000},
        {"left": float("nan")},
        {"left": float("inf")},
        {"right": 1.01},
        {"left": "1"},
        {"left": True},
        {"seq": True},
        {"seq": -1},
        {"seq": 2**53},
        {"deadman": False},
        {"deadman": 1},
        {"epoch": "old"},
        {"permit": "old"},
        {"extra": 0},
    ],
)
def test_invalid_owner_command_stops_and_revokes(patch):
    gate, drive, _, cmd = armed()
    gate.command("owner", cmd)
    gate.tick()
    message = dict(cmd, seq=1)
    message.update(patch)
    assert not gate.command("owner", message)
    assert drive.output == (0, 0)
    assert gate.owner is None


@pytest.mark.parametrize("message", [None, [], "forward", {}, {"motor": "both", "value": 1}])
def test_malformed_and_legacy_protocol_rejected(message):
    gate, drive, _, _ = armed()
    assert not gate.command("owner", message)
    assert drive.output == (0, 0)
    assert gate.owner is None


def test_command_deadline_not_extended_by_heartbeat():
    gate, drive, clock, cmd = armed()
    gate.command("owner", cmd)
    gate.tick()
    clock.now += 0.2
    assert gate.heartbeat("owner", cmd["epoch"])
    clock.now += 0.051
    gate.tick()
    assert drive.output == (0, 0)
    assert gate.owner is None


def test_heartbeat_deadline_independent_of_commands():
    clock = Clock()
    gate = DriveGate(SimDrive(), clock=clock, limits=Limits(heartbeat_timeout=0.1))
    epoch = gate.acquire("a")
    permit = gate.heartbeat("a", epoch)
    clock.now += 0.11
    assert not gate.command(
        "a", dict(epoch=epoch, permit=permit, seq=1, left=1, right=1, deadman=True)
    )
    assert gate.owner is None


def test_stale_permit_even_with_fresh_command_deadline():
    clock = Clock()
    gate = DriveGate(SimDrive(), clock=clock, limits=Limits(command_timeout=1))
    epoch = gate.acquire("a")
    permit = gate.heartbeat("a", epoch)
    clock.now += 0.251
    assert not gate.command(
        "a", dict(epoch=epoch, permit=permit, seq=1, left=1, right=1, deadman=True)
    )


def test_replay_estop_reset_and_session_isolation():
    gate, drive, _, cmd = armed()
    assert gate.acquire("observer") is None
    gate.release("observer")
    assert gate.heartbeat("observer", cmd["epoch"]) is None
    assert not gate.command("observer", cmd)
    assert gate.command("owner", cmd)
    assert not gate.command("owner", cmd)  # repeated sequence stops
    assert gate.owner is None
    epoch = gate.acquire("owner")
    assert epoch != cmd["epoch"]
    gate.emergency_stop()
    gate.tick()
    assert gate.acquire("owner") is None
    assert gate.reset()
    assert drive.output == (0, 0)
    assert gate.owner is None
    assert not gate.command("owner", cmd)


def test_stop_attempts_every_subsystem_and_failure_latches():
    class BrokenDrive(SimDrive):
        def stop(self):
            raise IOError("unplugged")

    class Arm:
        calls = 0

        def emergency_stop(self):
            self.calls += 1

    arm = Arm()
    gate = DriveGate(BrokenDrive(), arms=[arm])
    assert arm.calls == 1
    assert gate.estopped
    assert not gate.reset()
    assert arm.calls == 2
    assert gate.status()["stop_errors"] == ["drive"]


def test_backend_write_error_latches_and_clears_pending():
    class BrokenDrive(SimDrive):
        def write(self, left, right):
            raise IOError("unplugged")

    gate, _, _, cmd = armed()
    gate.drive = BrokenDrive()
    gate.command("owner", cmd)
    gate.tick()
    assert gate.estopped and gate.pending is None
    assert gate.drive.output == (0, 0)


def test_arm_returned_error_is_visible():
    class Arm:
        def emergency_stop(self):
            return {"error": "timeout"}

    gate = DriveGate(SimDrive(), [Arm()])
    assert gate.estopped and gate.stop_errors == ["arm:0"]


@pytest.mark.parametrize("value", [0, -1, float("nan"), float("inf"), True])
def test_invalid_limits(value):
    with pytest.raises(ValueError):
        Limits(command_timeout=value)


def axis():
    return SimpleNamespace(
        config=SimpleNamespace(enable_watchdog=True, watchdog_timeout=0.3),
        error=0,
        controller=SimpleNamespace(input_vel=0),
        watchdog_feed=lambda: None,
    )


def test_mock_odrive_mapping_no_discovery_or_state_transition():
    left, right = axis(), axis()
    adapter = ODriveAdapter(left, right, turns_per_second=2)
    adapter.write(0.3, -0.2)
    assert (left.controller.input_vel, right.controller.input_vel) == (-0.6, -0.4)
    right.error = 1
    with pytest.raises(RuntimeError):
        adapter.write(0.1, 0.1)
    assert (left.controller.input_vel, right.controller.input_vel) == (0, 0)


def test_mock_odrive_stop_attempts_second_axis_when_first_fails():
    class Broken:
        @property
        def input_vel(self):
            return 0

        @input_vel.setter
        def input_vel(self, value):
            raise IOError("unplugged")

    left, right = axis(), axis()
    left.controller = Broken()
    right.controller.input_vel = 1
    with pytest.raises(RuntimeError):
        ODriveAdapter(left, right).stop()
    assert right.controller.input_vel == 0


def test_socketio_two_clients_disconnect_and_latch():
    clock = Clock()
    app, socket, gate = create_app(clock=clock)
    a, b = socket.test_client(app), socket.test_client(app)
    epoch = a.emit("acquire", None, callback=True)["epoch"]
    assert b.emit("acquire", None, callback=True)["epoch"] is None
    permit = a.emit("heartbeat", {"epoch": epoch}, callback=True)["permit"]
    cmd = dict(epoch=epoch, permit=permit, seq=1, left=1, right=1, deadman=True)
    assert a.emit("drive", cmd, callback=True)["accepted"]
    gate.tick()
    assert gate.drive.output == (0.3, 0.3)
    b.disconnect()
    assert gate.owner is not None
    a.disconnect()
    gate.tick()
    assert gate.drive.output == (0, 0)
    a = socket.test_client(app)
    a.emit("estop")
    assert gate.estopped
    assert a.emit("acquire", None, callback=True)["epoch"] is None
    a.emit("reset")
    assert not gate.estopped and gate.owner is None
    assert not a.emit("drive", cmd, callback=True)["accepted"]
    gate.close()
    a.disconnect()


def test_socketio_silence_requires_explicit_reacquire():
    clock = Clock()
    app, socket, gate = create_app(clock=clock)
    client = socket.test_client(app)
    epoch = client.emit("acquire", None, callback=True)["epoch"]
    clock.now += 0.251
    gate.tick()
    assert client.emit("heartbeat", {"epoch": epoch}, callback=True)["permit"] is None
    assert client.emit("acquire", None, callback=True)["epoch"] != epoch
    client.disconnect()


@pytest.mark.parametrize("timeout", [0, -1, 1, float("nan"), float("inf"), 10**1000])
def test_mock_watchdog_must_be_bounded(timeout):
    left, right = axis(), axis()
    left.config.watchdog_timeout = timeout
    with pytest.raises(RuntimeError):
        ODriveAdapter(left, right).write(0.1, 0.1)
    assert (left.controller.input_vel, right.controller.input_vel) == (0, 0)


def test_shutdown_discards_pending_and_does_not_import_hardware():
    import sys

    gate, drive, _, cmd = armed()
    gate.command("owner", cmd)
    gate.close()
    gate.tick()
    assert gate.estopped and drive.output == (0, 0)
    assert "odrive" not in sys.modules
    assert "serial" not in sys.modules
    assert "hardware.arm_interface.arm_controller" not in sys.modules


@pytest.mark.parametrize("payload", [(), (None,), ({"left": 1}, {"right": 1})])
def test_socketio_missing_or_extra_drive_arguments_stop(payload):
    app, socket, gate = create_app()
    client = socket.test_client(app)
    assert client.emit("acquire", callback=True)["epoch"]
    result = client.emit("drive", *payload, callback=True)
    assert not result["accepted"]
    assert gate.owner is None and gate.drive.output == (0, 0)
    client.disconnect()
