import requests
import json

### testing register of user
def test_register_user():
    r = requests.post('http://localhost:5000/register',
    json={"first_name": "Danny", "last_name": "Halawi", "phone": "650-766-9640", "zipcode": "94404"})
    assert r.status_code == 200

## testing register of another user
def test_register_user_again():
    r = requests.post('http://localhost:5000/register',
    json={"first_name": "Tammy", "last_name": "Halawi", "phone": "650-766-9601", "zipcode": "94404"})
    assert r.status_code == 200

## testing update of user
def test_update_user():
    r = requests.put('http://localhost:5000/update/650-766-9640',
    json={"first_name": "Danny", "last_name": "Halawi", "phone": "650-766-9640", "zipcode": "94701"})
    assert r.status_code == 200
