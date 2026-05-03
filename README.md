# mkconnect-python

...a bit of code to connect to MouldKing Bluetooth Hubs in Python.

This fork additionally provides a small Flask API wrapper, so MouldKing hubs can be controlled over HTTP instead of only through the interactive Python console.

# MouldKing Hubs

## MouldKing 6.0 Hub

The MouldKing 6.0 Hub has two modes:

* RC-Mode to be controlled with a MouldKing remote control
* Bluetooth-Mode to be controlled with an app or this project

You can control a maximum of three MK6.0 Hubs at the same time with Bluetooth.

> Currently this project can send only one advertising telegram at the same time, so only one hub can be controlled continuously. Other hubs may go into timeout mode until the next telegram with their device address is sent.

## MouldKing 4.0 Hub

This project also exposes entries for MouldKing 4.0 hubs through the Flask API.

# Setting the address of the Hub

To switch the hub's device address to the next one, press the button on the hub.

Example:

If the script or API controls `deviceId=2` and nothing happens, short-press the button on the hub until the matching device address is selected.

For MK6.0 hubs:

* `deviceId=0` - one LED flash
* `deviceId=1` - two LED flashes
* `deviceId=2` - three LED flashes

# Installation
Clone the repository and install the Python dependencies.
```
bash
git clone <your-repository-url>
cd mkconnect-python
pip install flask gunicorn
```
On Linux/Raspberry Pi, Bluetooth advertising usually requires elevated permissions.

Depending on your setup, you may need to run the server with `sudo`.

# Flask API usage

This fork provides a Flask application in `app.py`.

Start the API server with Gunicorn:
```
bash
sudo gunicorn --bind 0.0.0.0:5000 app:app
```
By default, the server listens on:
```
text
http://0.0.0.0:5000
```
From another device in the same network, use the IP address or hostname of the machine running the Flask app, for example:
```
text
http://raspberrypi.local:5000
```
or:
```
text
http://192.168.178.50:5000
```
For local development, the Flask development server can also be started directly:
```
bash
sudo python app.py
```

# Flask API usage

This fork provides a Flask application in `app.py`.

Start the API server with:
```
bash
sudo python app.py
```
By default, the server listens on:
```
text
http://0.0.0.0:5000
```
From another device in the same network, use the IP address of the machine running the Flask app, for example:
```
text
http://192.168.178.50:5000
```
## Device IDs

The API currently maps the following `deviceId` values:

| deviceId | Hub |
|---:|---|
| `0` | MouldKing 6.0 Device 0 |
| `1` | MouldKing 6.0 Device 1 |
| `2` | MouldKing 6.0 Device 2 |
| `3` | MouldKing 4.0 Device 0 |
| `4` | MouldKing 4.0 Device 1 |
| `5` | MouldKing 4.0 Device 2 |

## Channels

Channels can be passed either as numbers or letters.

| Channel letter | Channel number |
|---|---:|
| `A` | `0` |
| `B` | `1` |
| `C` | `2` |
| `D` | `3` |
| `E` | `4` |
| `F` | `5` |

## Power values

Power must be between `-1` and `1`.

Examples:

| Value | Meaning |
|---:|---|
| `1` | full speed forward |
| `0.5` | half speed forward |
| `0` | stop channel |
| `-0.5` | half speed backward |
| `-1` | full speed backward |

# API Endpoints

## Health check
```
http
GET /api/health
```
Example:
```
bash
curl http://localhost:5000/api/health
```
Response:
```
json
{
  "ok": true,
  "service": "mkconnect-flask"
}
```
## Connect hub

Switch a hub into Bluetooth mode.
```
http
POST /api/connect
```
Example:
```
bash
curl -X POST http://localhost:5000/api/connect \
  -H "Content-Type: application/json" \
  -d '{"deviceId": 0}'
```
Response:
```
json
{
  "ok": true,
  "action": "connect",
  "deviceId": 0
}
```
## Control channel

Control a single channel of a hub.
```
http
POST /api/control
```
Example using channel number:
```
bash
curl -X POST http://localhost:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"deviceId": 0, "channel": 0, "power": 1}'
```
Example using channel letter:
```
bash
curl -X POST http://localhost:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"deviceId": 0, "channel": "B", "power": -0.5}'
```
Response:
```
json
{
  "ok": true,
  "action": "control",
  "deviceId": 0,
  "channel": 1,
  "power": -0.5
}
```
## Stop hub

Set all channels of a device to zero.
```
http
POST /api/stop
```
Example:
```
bash
curl -X POST http://localhost:5000/api/stop \
  -H "Content-Type: application/json" \
  -d '{"deviceId": 0}'
```
Response:
```
json
{
  "ok": true,
  "action": "stop",
  "deviceId": 0
}
```
## Stop Bluetooth advertising

Stop Bluetooth advertising manually.
```
http
POST /api/btstop
```
Example:
```
bash
curl -X POST http://localhost:5000/api/btstop
```
Response:
```
json
{
  "ok": true,
  "action": "btstop"
}
```
# Error responses

If something goes wrong, the API returns a JSON response like this:
```
json
{
  "ok": false,
  "error": "device_id must be between 0 and 5"
}
```
The HTTP status code is usually `400`.

Common causes:

* invalid `deviceId`
* invalid `power` value
* Bluetooth permissions are missing
* unsupported operating system
* hub is not in the expected Bluetooth/device mode

# Console usage

The original interactive console usage is still available.

Start the script `consoletest.py` on your Raspberry Pi:
```
bash
sudo python -i consoletest.py
```
## mkbtstop() - stop bluetooth advertising
```
python
mkbtstop()
```
## mkconnect() - switch hubs into bluetooth mode

If you power on the hubs, they will listen to telegrams for the first device by default.

Call:
```
python
mkconnect()
```
By short-pressing the button on MK6.0 hubs you can choose the hub ID:

* `hubId=0` - one LED flash
* `hubId=1` - two LED flashes
* `hubId=2` - three LED flashes

## mkcontrol(deviceId, channel, powerAndDirection)

Example:
```
python
mkcontrol(0, 0, 1)
```
This controls the first device, channel A, with full speed forward.

Another example:
```
python
mkcontrol(0, "B", -1)
```
This controls channel B with full speed backward.

## mkstop(deviceId)

Set all channels of a device to zero.
```
python
mkstop(0)
```
# Notes

On Raspberry Pi/Linux, this project uses Bluetooth advertising to send control telegrams.

On Windows, the Flask app uses the dummy advertiser implementation.

Unsupported platforms will raise an exception during startup.

# Old stuff

There is a test script `consoletest.py` where, on Raspberry Pi, `hcitool` is used to advertise telegrams over Bluetooth.

Maybe you have to use `sudo`:
```
bash
sudo python -i consoletest.py
```
Available commands:
```
text
mkconnect(hubId)
mkstop(hubId)
mkcontrol(deviceId, channel, powerAndDirection)
```
Examples:
```
python
mkconnect(0)
mkconnect(1)
mkcontrol(0, 0, 0.5)
mkcontrol(0, "B", -1)
```
The minus sign indicates reverse motor direction.