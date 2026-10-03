"""Local simulation server. There is deliberately no hardware backend option."""

import argparse
import json
import threading
from dataclasses import asdict

from flask import Flask, request
from flask_socketio import SocketIO, emit

from hardware.cart.control import DriveGate, Limits, SimDrive


def create_app(limits=None, clock=None):
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 4096
    socket = SocketIO(
        app,
        async_mode="threading",
        max_http_buffer_size=4096,
        cors_allowed_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    )
    options = {"limits": limits}
    if clock is not None:
        options["clock"] = clock
    gate = DriveGate(SimDrive(), **options)

    @app.get("/")
    def index():
        return {"name": "shop-lifter", "mode": "simulation", **gate.status()}

    @socket.on("connect")
    def connect():
        emit("state", {"mode": "simulation", **gate.status()})

    @socket.on("acquire")
    def acquire(message=None):
        return {"epoch": gate.acquire(getattr(request, "sid")), "state": gate.status()}

    @socket.on("heartbeat")
    def heartbeat(message=None):
        epoch = message.get("epoch") if isinstance(message, dict) else None
        return {"permit": gate.heartbeat(getattr(request, "sid"), epoch), "state": gate.status()}

    @socket.on("drive")
    def drive(message=None, *extra):
        if extra:
            message = None
        return {"accepted": gate.command(getattr(request, "sid"), message), "state": gate.status()}

    @socket.on("release")
    def release():
        gate.release(getattr(request, "sid"))
        return gate.status()

    @socket.on("disconnect")
    def disconnect(reason=None):
        gate.release(getattr(request, "sid"))

    @socket.on("estop")
    def estop():
        gate.emergency_stop()
        socket.emit("state", {"mode": "simulation", **gate.status()})
        return gate.status()

    @socket.on("reset")
    def reset():
        gate.reset()
        socket.emit("state", {"mode": "simulation", **gate.status()})
        return gate.status()

    return app, socket, gate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/cart-sim.json")
    parser.add_argument("--port", type=int, default=5050)
    args = parser.parse_args()
    with open(args.config, encoding="utf-8") as file:
        config = json.load(file)
    if set(config) != {"mode", "limits"} or config["mode"] != "simulation":
        parser.error("Only simulation configuration is supported")
    limits = Limits(**config["limits"])
    app, socket, gate = create_app(limits)
    stop = threading.Event()

    def worker():
        while not stop.wait(0.02):
            gate.tick()

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    print("SIMULATION ONLY", asdict(limits), flush=True)
    try:
        socket.run(
            app, host="127.0.0.1", port=args.port, use_reloader=False, allow_unsafe_werkzeug=True
        )
    finally:
        stop.set()
        thread.join(timeout=1)
        gate.close()


if __name__ == "__main__":
    main()
