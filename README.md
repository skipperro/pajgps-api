# pajgps-api

A Python library for communicating with the PAJ GPS API.

## Installation

```bash
pip install pajgps-api
```

## Usage

```python
from pajgps_api import PajGpsApi

# Initialize the API
api = PajGpsApi(email="your_email@example.com", password="your_password")

# Log in
try:
    api.login()
    print(f"Logged in successfully! User ID: {api.user_id}")
except Exception as e:
    print(f"Login failed: {e}")

# Subsequent requests will automatically use the token and refresh it if needed.

# Reading Devices
devices = api.get_devices()
for device in devices:
    print(f"ID: {device.id}, Name: {device.name}, IMEI: {device.imei}")

# Current Positions for all devices
device_ids = [device.id for device in devices]
if device_ids:
    last_positions = api.get_all_last_positions(device_ids)
    for pos in last_positions:
        print(f"Device {pos.iddevice}: Lat {pos.lat}, Lng {pos.lng}, Speed {pos.speed}")

# Voltage Sensor (for the first device)
if devices:
    sensor_data = api.get_last_sensor_data(devices[0].id)
    if hasattr(sensor_data, "volt"):
        print(f"Voltage: {sensor_data.volt} mV")
```


## Timeouts and Retries

By default, every HTTP request made by `PajGpsApi` uses incremental timeouts and automatic retries:
- Attempts: 3
- Timeouts per attempt: 5s, 10s, 15s (each attempt adds the base timeout)
- Retries on: network timeouts/connection errors and HTTP status codes 500, 502, 503, 504, 429
- Not retried: 4xx client errors like 404
- 401 handling: for authenticated endpoints, a token refresh is attempted once automatically, then the request is retried within the same attempt.

You can configure these via the constructor:

```python
from pajgps_api import PajGpsApi

api = PajGpsApi(
    email="your_email@example.com",
    password="your_password",
    timeout=5,       # base timeout (seconds) for the first attempt
    max_retries=3,   # total number of attempts
)
```
