from flask import Flask, request, jsonify
from threading import Lock
import sys

sys.path.append("Tracer")
from Tracer.TracerConsole import TracerConsole

sys.path.append("Advertiser")
if sys.platform == "linux":
    from Advertiser.AdvertiserBTSocket import AdvertiserBTSocket as Advertiser
elif sys.platform == "win32":
    from Advertiser.AdvertiserDummy import AdvertiserDummy as Advertiser
else:
    raise Exception("unsupported platform")

sys.path.append("MouldKing")
from MouldKing.MouldKing import MouldKing


app = Flask(__name__)
bluetooth_lock = Lock()

tracer = TracerConsole()

advertiser = Advertiser()
advertiser.SetTracer(tracer)

MouldKing.SetTracer(tracer)
MouldKing.SetAdvertiser(advertiser)

hubs = {
    0: MouldKing.Module6_0.Device0,
    1: MouldKing.Module6_0.Device1,
    2: MouldKing.Module6_0.Device2,
    3: MouldKing.Module4_0.Device0,
    4: MouldKing.Module4_0.Device1,
    5: MouldKing.Module4_0.Device2,
}


def get_hub(device_id: int):
    if device_id not in hubs:
        raise ValueError("device_id must be between 0 and 5")
    return hubs[device_id]


@app.route("/api/connect", methods=["POST"])
def connect():
    data = request.get_json(silent=True) or {}
    device_id = int(data.get("deviceId", 0))

    try:
        with bluetooth_lock:
            hub = get_hub(device_id)
            hub.Connect()

        return jsonify({
            "ok": True,
            "action": "connect",
            "deviceId": device_id,
        })

    except Exception as exc:
        return jsonify({
            "ok": False,
            "error": str(exc),
        }), 400


@app.route("/api/stop", methods=["POST"])
def stop():
    data = request.get_json(silent=True) or {}
    device_id = int(data.get("deviceId", 0))

    try:
        with bluetooth_lock:
            hub = get_hub(device_id)
            hub.Stop()

        return jsonify({
            "ok": True,
            "action": "stop",
            "deviceId": device_id,
        })

    except Exception as exc:
        return jsonify({
            "ok": False,
            "error": str(exc),
        }), 400


@app.route("/api/control", methods=["POST"])
def control():
    data = request.get_json(silent=True) or {}

    device_id = int(data.get("deviceId", 0))
    channel = data.get("channel", 0)
    power = float(data.get("power", 0))

    if isinstance(channel, str):
        channel = channel.upper()
        channel_map = {
            "A": 0,
            "B": 1,
            "C": 2,
            "D": 3,
            "E": 4,
            "F": 5,
        }
        channel = channel_map.get(channel, channel)

    channel = int(channel)

    if power < -1 or power > 1:
        return jsonify({
            "ok": False,
            "error": "power must be between -1 and 1",
        }), 400

    try:
        with bluetooth_lock:
            hub = get_hub(device_id)
            hub.SetChannel(channel, power)

        return jsonify({
            "ok": True,
            "action": "control",
            "deviceId": device_id,
            "channel": channel,
            "power": power,
        })

    except Exception as exc:
        return jsonify({
            "ok": False,
            "error": str(exc),
        }), 400


@app.route("/api/btstop", methods=["POST"])
def btstop():
    try:
        with bluetooth_lock:
            advertiser.AdvertisementStop()

        return jsonify({
            "ok": True,
            "action": "btstop",
        })

    except Exception as exc:
        return jsonify({
            "ok": False,
            "error": str(exc),
        }), 400


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "ok": True,
        "service": "mkconnect-flask",
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
