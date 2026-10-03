# One robot, one repository: shop-lifter

The physical cart has a brushless-DC/ODrive mobile base below robotic arms.
`shop-lifter` is the canonical name and repository. This draft consolidates source
and a runnable **simulation control path**. It does not commission the robot.

## Current-source review (2026-10-03 UTC)

Fetched both repositories, all advertised branches, and shoppy PR #4 before editing.
There were no open shop-lifter PRs. shoppy #4 was the only open shoppy PR.

| Source | Reviewed revision | Decision |
| --- | --- | --- |
| shop-lifter main | `c72bbd77902d514f3e5077bdb9a9f084392cb1c7` | Base; arm controllers, leader/follower, multi-follower feedback, camera code and research unchanged |
| shop-lifter devin/1741028069-add-prompt-to-readme | `c6b5636433df8b4c31253e1c33c300c9a9be1998` | Already reachable from main |
| shop-lifter devin/1741031367-add-research-folder | `c81692c3fb982251ba7c3a726dfaa01e7ed8ef40` | Unmerged PDF/link corrections; unrelated to drive consolidation; defer |
| shop-lifter devin/1741794432-uvc-compatibility | `bdfb0062b9a5a0b2773b39170f65ab28e85cff6e` | Unmerged UVC camera implementation; leave for separate firmware review |
| shoppy development (default) | `f67c7c319c8c2c2fcfedebcd0a4cc7c58251a363` | Preserve history and tank-control UI concepts |
| shoppy feature/connectivity-safety | `34ffabf2e4a41465012ac416f82c7bfcfcfb0746` | Already reachable from development |
| shoppy test-branch | `17fa9588db218d2d5fb3ffe76f86cd949a2bfa77` | Preserve history; integrate explicit reconnect concept |
| [shoppy PR #4](https://github.com/jhacksman/shoppy/pull/4) | `0bd1653bffcdd279baa1919bf32c636af770ebc0` | Preserve history and complete source snapshot; rework worker/watchdog concepts |

No applicable AGENTS.md or .agents/skills were present in these checkouts or task
ancestors. Read the existing CLAUDE.md project guide; its multi-cart roadmap is
historical context, not a reason to expand this single-cart task. Read-only local
Codex memory lookup found no shop-lifter/shoppy entries.

## History and attribution

The first integration commit has shop-lifter main, shoppy PR #4 and shoppy
`test-branch` as parents. Their original commits, authors and ancestry remain
reachable; PR #4 contains development history too. `legacy/shoppy/` is a byte-for-byte
snapshot of PR #4, including original docs, Raspberry Pi script, UART helper,
requirements and frontend lockfile. It is archival source, **not a supported startup
path**. In particular, do not run its app or deployment script: it can discover
ODrive, enter closed-loop control, clear errors and reboot a controller.

Original shoppy work by Enzo Marrama (`EggRollForce`), Jon (`jhacksman`), and other
contributors remains attributed in Git history. The active React/Chakra panel is
derived from that work. No new license is asserted over either repository.
The shoppy repository and its PR remain untouched. This draft does not merge either
upstream default branch or any upstream PR.

## Layout and dependencies

- `hardware/cart/control.py`: normalized wheel-pair interface, simulation output,
  ownership/deadman/heartbeat gate, bounded latest-value slot, stop fan-out.
- `hardware/cart/odrive_adapter.py`: experimental injected-axis mapping seam;
  tested only with mocks. No hardware discovery or configuration.
- `control_panel/server.py`: Flask-SocketIO local simulation server, no arm imports.
- `control_panel/frontend/`: retained React 18 / Chakra 2 / CRA 5 stack and lockfile;
  touch sliders, keyboard tank control, gamepad sticks, reconnect, explicit stop.
- Existing `hardware/arm_interface/`, follower readers and sensor firmware remain
  independent and unchanged. Their examples may actuate hardware; they are not
  simulation startup instructions and are excluded from these tests.

The small control-panel requirements are separate from the existing ML/perception
requirements. Simulation requires neither ODrive, serial, Torch nor camera SDKs.
The inherited CRA toolchain emits deprecation/outdated browser-data warnings;
modernizing it is deferred, and this development server must not be exposed publicly.
The legacy requirements are provenance, not the consolidated runtime lockfile.

## Start locally, with no hardware

From the shop-lifter repository root, using Python 3.9+ and Node 22:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r control_panel/requirements.txt
python -m control_panel.server --config config/cart-sim.json
```

In another terminal:

```sh
cd control_panel/frontend
npm ci
HOST=127.0.0.1 BROWSER=none npm start
```

Open http://localhost:3000. Backend is http://127.0.0.1:5050 (avoids macOS port
5000 conflicts). `REACT_APP_CONTROL_URL` can change the frontend endpoint; server
origins are deliberately limited to localhost/127.0.0.1 on port 3000. No service
installation, autostart, deployment or hardware option exists in this workflow.
The backend rejects non-simulation configs. Ctrl-C stops the process; its finalizer
revokes ownership and zeros simulated output. Abrupt process death requires an
independent hardware watchdog in any future physical implementation.

Select an input mode. Touch: set sliders and hold the hold-to-drive button.
Keyboard: hold Space and F/V (left) or J/N (right). Gamepad: release then hold left
shoulder/button 4 and use vertical axes 1 and 3. Mode changes, blur, hidden page,
gamepad loss and release stop locally and notify the server. Lost messages fall
back to server deadlines. Reconnect does not re-arm. Reset does not move anything;
release and hold again after a stop/rejection. The output display is simulated
normalized velocity, not measured wheel speed, electrical power or torque.

## Interface and stop semantics

`Drive.write(left, right)` accepts a normalized complete wheel-velocity pair;
`Drive.stop()` requests zero from both sides. `SimDrive` only stores the pair.
An optional `ArmStop.emergency_stop()` interface matches the existing arm controller
method. Gate stops attempt the drive and every injected arm even if one fails;
exceptions/error responses latch and are reported as stop errors. The server injects
**no arms**. Direct arm scripts and ESP-NOW broadcasts bypass this gate; this UI
therefore cannot claim to stop those paths. Their motion/position APIs are preserved,
not automatically exposed over the drive network protocol.

Socket.IO events (versioned here as the initial consolidated contract):

1. `acquire` returns a random ownership `epoch`; only one SID can own drive.
2. `heartbeat {epoch}` returns a short-lived random `permit`. The client has at
   most one request in flight and does not enqueue offline control events.
3. `drive {epoch, permit, seq, left, right, deadman}` sends both wheels atomically.
   `seq` is a strictly increasing integer below 2^53; wheels are finite numbers in
   [-1, 1]; `deadman` must be boolean true. Unknown/missing fields are rejected.
4. `release` or owner disconnect zeros and revokes. Observer disconnect does not
   affect another owner's drive. Non-owners cannot feed the owner's heartbeat.
5. `estop` latches a software stop for the process lifetime (not persisted across restart). `reset` requests zero again and clears only if
   stops succeed; it never acquires drive. Any local simulation client can stop or
   reset. Authentication/operator authorization must precede network/hardware use.

Default independent deadlines: heartbeat 500 ms, accepted command 250 ms, permit
250 ms, with a 20 ms worker poll. Heartbeats cannot keep an old command alive.
Server-issued permits bound delayed network commands without trusting client clocks;
sequence and epoch reject replay/reconnect traffic. These are software scheduling
bounds, not hard real-time guarantees. Invalid owner messages, expired deadlines,
and release revoke authority and discard pending output. Non-owner messages are
rejected without disrupting the owner. Driver write failure latches the stop.

The single latest-value slot replaces PR #4's FIFO (10 entries plus blocking stop
puts). Stop takes priority by clearing the slot under the same lock as writes.
No queued drive may replay after stop. Stop requests **zero velocity**, not power
isolation, brake engagement, torque disable, a guaranteed stopping distance, or an
IEC-rated emergency stop. No gradual-stop routine invents nonzero motion.

The injected ODrive seam preserves PR #4's axis/sign idea: caller supplies left axis
(historically axis1, sign -1) and right (historically axis0, sign +1), plus turns/sec
scale. It rejects non-finite commands and requires each supplied axis to report an
enabled positive watchdog <=500 ms and no axis error. It feeds watchdogs only after
a fresh wheel pair. It never enters closed loop or clears/reboots faults. Firmware
API compatibility, controller-wide errors, actual watchdog state and blocking I/O
need physical backend work; this seam is not sufficient to enable the robot.

## Migration and review decisions

Conceptually integrated: one name/repo; browser drive modes; reconnect status;
Flask-SocketIO transport; independent control gate/worker; watchdog-aware mapping;
shared stop interface and repeatable simulation tests. Original arm/camera behavior
and all source attribution are preserved.

Deliberately replaced: global client heartbeat, individual wheel messages, unconditional
Start at 0.5, gradual stop that could command motion, blocking/stale FIFO, and automatic
ODrive discovery, closed-loop entry, fault clear/reboot. Old `control_command`, `ping`
and `pong` clients must migrate; they cannot drive the new server.

Before a separate hardware PR, Jon must choose/confirm:

- ODrive board/firmware, serial identity, axis wiring/signs, wheel dimensions/gear
  ratio and commissioned speed/acceleration/current limits. Normalized 0.3 here is
  a simulation cap, not a physically safe speed claim.
- Physical emergency-stop circuit, braking/power isolation and verified watchdog
  behavior under process death, blocked I/O, cable loss and partial-axis failure.
- Whether arms may move while driving; safe arm poses, collision/workspace limits,
  bounded arm stop calls and authority over direct/ESP-NOW leader/follower streams.
- Hardware operator authentication/network exposure and explicit enable procedure.
- Separate acceptance of UVC firmware branch and research-link corrections.

No hardware connection, motor/arm motion, firmware build/flash, desktop UI inspection,
service activation or physical safety validation was performed. Simulation/mocks do
not prove physical safety.

## Reproduce validation

```sh
pip install -r control_panel/requirements-dev.txt
python -m pytest -q
ruff check hardware/cart control_panel/server.py tests/test_cart_control.py
ruff format --check hardware/cart control_panel/server.py tests/test_cart_control.py
mypy --ignore-missing-imports --check-untyped-defs hardware/cart control_panel/server.py
cd control_panel/frontend
CI=true npm test -- --watchAll=false --runInBand
CI=true npm run build
```

Tests use fake time, in-process Flask-SocketIO clients and injected fake axes/arms;
pytest collection is restricted to `tests/` so the legacy live WebSocket script is
never collected. No new test imports ODrive, serial or arm transport modules.

### Results recorded for this draft

- 46 Python unit/integration/mock tests passed (Python 3.9.6).
- 6 frontend tests passed; production build compiled successfully (Node 22.14.0).
- Scoped Ruff lint/format and mypy with checked untyped bodies passed.
- Live localhost Socket.IO client/server smoke passed: acquisition, wheel pair,
  independent timeout without further commands, latched stop and reset. The test
  server was shut down afterward.
- Imported PR #4 tree hash equals the `legacy/shoppy` tree hash; development, PR #4
  and reconnect branch heads are ancestors of the integration branch.
- Physical hardware, firmware, full legacy ML stack and visual/manual desktop
  interaction were not tested. The desktop remained locked and untouched.
