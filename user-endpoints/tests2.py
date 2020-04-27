import requests
import json

### testing register of user
def test_register_user():
    r = requests.post('http://3.12.83.161:5000/register',
    json={"first_name": "Danny", "last_name": "Halawi", "phone": "+16507400429", "zipcode": "94701"})
    assert r.status_code == 200

def test_register_user_2():
    r = requests.post('http://3.12.83.161:5000/register',
    json={"first_name": "Abbas", "last_name": "MJ", "phone": "+15103458520", "zipcode": "94702"})
    assert r.status_code == 200

## testing register of another user
def test_register_user_again():
    r = requests.post('http://3.12.83.161:5000/register',
    json={"first_name": "Tammy", "last_name": "Halawi", "phone": "+16507669601", "zipcode": "94404"})
    assert r.status_code == 200

## testing update of user
def test_update_user():
    r = requests.post('http://3.12.83.161:5000/update',
    json={"first_name": "Danny", "last_name": "Halawi", "last_phone": "+16507400429", "new_phone": "+16507669640", "zipcode": "94701"})
    assert r.status_code == 200

## test unsubscribe user
def test_unsubscribe_user():
    r = requests.post('http://3.12.83.161:5000/unsubscribe',
    json={"phone": "+16507669601"})
    assert r.status_code == 200

## test send
def test_send():
    r = requests.post('http://3.12.83.161:5000/send')
    assert r.status_code == 200
