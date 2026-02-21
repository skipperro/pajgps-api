from pajgps_api import PajGpsApi

def test_api_init():
    api = PajGpsApi("test@example.com", "password")
    assert api.email == "test@example.com"
    assert api.password == "password"
    assert api.base_url == "https://v2-api.paj-gps.de/api"
