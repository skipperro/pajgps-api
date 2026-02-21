#!/usr/bin/env bash
# Verifies that the pajgps-api package was uploaded to TestPyPI correctly.
#
# What it does:
#   1. Creates a temporary virtual environment (isolated from your project).
#   2. Installs pajgps-api from TestPyPI (with real PyPI as fallback for deps).
#   3. Verifies the installed version matches expectations.
#   4. Imports the package and checks that all public symbols are accessible.
#   5. Cleans up the temporary environment.
#
# Usage: ./verify_test_pypi.sh

set -euo pipefail

PACKAGE_NAME="pajgps-api"
IMPORT_NAME="pajgps_api"
EXPECTED_VERSION="0.2.1"

TMPDIR="$(mktemp -d)"
VENV_DIR="$TMPDIR/venv"

cleanup() {
    echo ""
    echo "=== Cleaning up temporary environment ==="
    rm -rf "$TMPDIR"
}
trap cleanup EXIT

echo "=== Creating isolated virtual environment in $VENV_DIR ==="
python -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo ""
echo "=== Installing $PACKAGE_NAME from TestPyPI ==="
pip install \
    --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    "$PACKAGE_NAME==$EXPECTED_VERSION"

echo ""
echo "=== Checking installed version ==="
INSTALLED_VERSION=$(python -c "import $IMPORT_NAME; print($IMPORT_NAME.__version__)")
if [ "$INSTALLED_VERSION" != "$EXPECTED_VERSION" ]; then
    echo "FAIL: Expected version $EXPECTED_VERSION but got $INSTALLED_VERSION"
    exit 1
fi
echo "OK: version $INSTALLED_VERSION"

echo ""
echo "=== Verifying public API imports ==="
python -c "
from $IMPORT_NAME import (
    PajGpsApi,
    PajGpsApiError,
    AuthenticationError,
    TokenRefreshError,
    RequestError,
    AlertType,
    ALERT_TYPE_SHOCK,
    ALERT_TYPE_BATTERY,
    ALERT_TYPE_RADIUS,
    ALERT_TYPE_SOS,
    ALERT_TYPE_SPEED,
    ALERT_TYPE_POWER_CUT_OFF,
    ALERT_TYPE_IGNITION,
    ALERT_TYPE_DROP,
    ALERT_TYPE_AREA_ENTER,
    ALERT_TYPE_AREA_LEAVE,
    ALERT_TYPE_VOLTAGE,
    ALERT_TYPE_TURN_OFF,
)
from ${IMPORT_NAME}.models import (
    Device,
    TrackPoint,
    SensorData,
    AuthResponse,
    Notification,
)

# Verify AlertType enum values
assert AlertType.SHOCK == 1
assert AlertType.SOS == 4
assert ALERT_TYPE_TURN_OFF == 22

# Verify models can be instantiated
d = Device(id=1, name='Test')
assert d.id == 1
assert d.name == 'Test'
assert d.to_dict()['id'] == 1

tp = TrackPoint(lat=50.0, lng=6.0, speed=30)
assert tp.lat == 50.0

sd = SensorData(volt=12400, did=1)
assert sd.volt == 12400

ar = AuthResponse(token='tok', refresh_token='ref', userID=1)
assert ar.token == 'tok'

n = Notification(
    id=1, iddevice=2, icon='i', bezeichnung='b', meldungtyp=1,
    dateunix=100, lat=1.0, lng=2.0, isread=0, radiusin=0,
    radiusout=0, zuendon=0, zuendoff=0, push=1, suppressed=0,
)
assert n.id == 1

# Verify exception hierarchy
assert issubclass(AuthenticationError, PajGpsApiError)
assert issubclass(TokenRefreshError, PajGpsApiError)
assert issubclass(RequestError, PajGpsApiError)

# Verify PajGpsApi can be instantiated (no network call)
api = PajGpsApi('user@example.com', 'pass')
assert api.email == 'user@example.com'
assert api.token is None

print('All imports and smoke tests passed.')
"

echo ""
echo "=== All checks passed! Package $PACKAGE_NAME $EXPECTED_VERSION is working correctly from TestPyPI. ==="

