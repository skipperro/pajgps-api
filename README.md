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


## API Endpoint Coverage

### ✅ Supported

| Category          | Method | Endpoint                                            | Library method                          |
|-------------------|--------|-----------------------------------------------------|-----------------------------------------|
| **Login**         | `POST` | `/api/v1/login`                                     | `login()`                               |
| **Login**         | `POST` | `/api/v1/updatetoken`                               | `update_token()`                        |
| **Device**        | `GET`  | `/api/v1/device`                                    | `get_devices()`                         |
| **Device**        | `GET`  | `/api/v1/device/{DeviceID}`                         | `get_device()`                          |
| **Device**        | `PUT`  | `/api/v1/device/{DeviceID}`                         | `update_device()`                       |
| **Tracking Data** | `GET`  | `/api/v1/trackerdata/{DeviceID}/last_minutes`       | `get_tracking_data_last_minutes()`      |
| **Tracking Data** | `GET`  | `/api/v1/trackerdata/{DeviceID}/last_points`        | `get_tracking_data_last_points()`       |
| **Tracking Data** | `GET`  | `/api/v1/trackerdata/{DeviceID}/date_range`         | `get_tracking_data_date_range()`        |
| **Tracking Data** | `POST` | `/api/v1/trackerdata/getalllastpositions`           | `get_all_last_positions()`              |
| **Tracking Data** | `GET`  | `/api/v1/sensordata/last/{DeviceID}`                | `get_last_sensor_data()`                |
| **Notifications** | `GET`  | `/api/v1/notifications`                             | `get_notifications()`                   |
| **Notifications** | `GET`  | `/api/v1/notifications/{deviceID}`                  | `get_device_notifications()`            |
| **Notifications** | `GET`  | `/api/v1/customnotifications/{deviceID}`            | `get_custom_notifications()`            |
| **Notifications** | `PUT`  | `/api/v1/notifications/markReadByDevice/{deviceID}` | `mark_notifications_read_by_device()`   |
| **Notifications** | `PUT`  | `/api/v1/notifications/markReadByCustomer`          | `mark_notifications_read_by_customer()` |

### ❌ Not Yet Supported

| Category             | Method   | Endpoint                                                 | Description                         |
|----------------------|----------|----------------------------------------------------------|-------------------------------------|
| **Customer**         | `GET`    | `/api/v1/customer`                                       | Get customer data                   |
| **Customer**         | `GET`    | `/api/v1/customer/{CustomerID}`                          | Get customer data by ID             |
| **Customer**         | `PUT`    | `/api/v1/customer/{CustomerID}`                          | Update customer by ID               |
| **Dashboard**        | `POST`   | `/api/v1/customer/dashboard/dataDistance`                | Data and distance calculation       |
| **Dashboard**        | `POST`   | `/api/v1/customer/dashboard/downloadpdf`                 | Trip and rest PDF download          |
| **Dashboard**        | `POST`   | `/api/v1/customer/dashboard/triprest_data`               | Trip and rest data                  |
| **Geofence**         | `POST`   | `/api/v1/geofences`                                      | Get all geofences for given devices |
| **Geofence**         | `POST`   | `/api/v1/geofence/{DeviceID}`                            | Create geofence for a device        |
| **Geofence**         | `PUT`    | `/api/v1/geofence/{DeviceID}/{GeofenceID}`               | Update a geofence                   |
| **Geofence**         | `DELETE` | `/api/v1/geofence/{DeviceID}/{GeofenceID}`               | Delete a geofence                   |
| **Car Manufacturer** | `GET`    | `/api/v1/cars`                                           | Get all car manufacturers           |
| **Car Manufacturer** | `POST`   | `/api/v1/addcar`                                         | Add car manufacturer                |
| **Car Manufacturer** | `PUT`    | `/api/v1/cars/{carManufacturerID}`                       | Update car manufacturer             |
| **Car Manufacturer** | `DELETE` | `/api/v1/cars/{carManufacturerID}`                       | Delete car manufacturer             |
| **Car Model**        | `GET`    | `/api/v1/carmodels/{Make_ID}`                            | Get car models of a manufacturer    |
| **Car Model**        | `POST`   | `/api/v1/addcarmodel`                                    | Add car model                       |
| **Car Model**        | `PUT`    | `/api/v1/carmodels/{carModelID}`                         | Update car model                    |
| **Car Model**        | `DELETE` | `/api/v1/carmodels/{carModelID}`                         | Delete car model                    |
| **Car Device Data**  | `GET`    | `/api/v1/sdevice/car`                                    | Get car-device linked data          |
| **Car Device Data**  | `POST`   | `/api/v1/sdevice/car`                                    | Link car to device                  |
| **Car Device Data**  | `GET`    | `/api/v1/sdevice/car/{CarDevice_id}`                     | Get single car-device link          |
| **Car Device Data**  | `PUT`    | `/api/v1/sdevice/car/{CarDevice_id}`                     | Update car-device link              |
| **Car Device Data**  | `DELETE` | `/api/v1/sdevice/car/{CarDevice_id}`                     | Delete car-device link              |
| **Logbook Routes**   | `GET`    | `/api/v1/logbook/getAllRoutes/{DeviceID}`                | Get all routes of a device          |
| **Logbook Routes**   | `GET`    | `/api/v1/logbook/getAllRoutes/{DeviceID}/{CarDevice_id}` | Get routes with linked car          |
| **Logbook Routes**   | `GET`    | `/api/v1/logbook/generateSingleDeviceRoutes/{DeviceID}`  | Generate logbook routes             |
| **Logbook Routes**   | `GET`    | `/api/v1/logbook/generateSingleDeviceAddress/{DeviceID}` | Generate route addresses            |
| **Logbook Driver**   | `GET`    | `/api/v1/logbook/driver`                                 | Get drivers                         |
| **Logbook Driver**   | `POST`   | `/api/v1/logbook/driver`                                 | Create driver                       |
| **Logbook Driver**   | `PUT`    | `/api/v1/logbook/driver/{DriverID}`                      | Update driver                       |
| **Logbook Driver**   | `DELETE` | `/api/v1/logbook/driver/{DriverID}`                      | Delete driver                       |
| **Logbook Reason**   | `GET`    | `/api/v1/logbook/reason`                                 | Get reasons                         |
| **Logbook Reason**   | `POST`   | `/api/v1/logbook/reason`                                 | Create reason                       |
| **Logbook Reason**   | `PUT`    | `/api/v1/logbook/reason/{ReasonID}`                      | Update reason                       |
| **Logbook Reason**   | `DELETE` | `/api/v1/logbook/reason/{ReasonID}`                      | Delete reason                       |
| **Logbook Contact**  | `GET`    | `/api/v1/logbook/contact`                                | Get contacts                        |
| **Logbook Contact**  | `POST`   | `/api/logbook/contact`                                   | Create contact                      |
| **Logbook Contact**  | `PUT`    | `/api/v1/logbook/contact/{ContactID}`                    | Update contact                      |
| **Logbook Contact**  | `DELETE` | `/api/v1/logbook/contact/{ContactID}`                    | Delete contact                      |

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
