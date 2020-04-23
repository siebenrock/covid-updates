from flask import Flask, request, jsonify, render_template
from uszipcode import SearchEngine
import MySQLdb
import requests
import json
from twilio import twiml

states = {
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AS': 'American Samoa',
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'District of Columbia',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'GU': 'Guam',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MP': 'Northern Mariana Islands',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NA': 'National',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NV': 'Nevada',
    'NY': 'New York',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'PR': 'Puerto Rico',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VI': 'Virgin Islands',
    'VT': 'Vermont',
    'WA': 'Washington',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming'
}

# Initiate app
app = Flask(__name__)

search = None
cursor = None
db = None


def get_db_connection():
    global cursor
    global db
    if not cursor:
        db = MySQLdb.connect("user-db-container", "root", "pass", "users")
        cursor = db.cursor()
    return cursor


def get_search():
    global search
    if not search:
        search = SearchEngine(simple_zipcode=True)
    return search

@app.route("/register", methods=['GET', 'POST'])
def register_user():
    global db
    cursor = get_db_connection()
    data = request

    if data.form:
        data = data.form
    else:
        data = data.get_json()

    try:
        name = data["first_name"]
        surname = data["last_name"]
        phone = data["phone"]
        zipcode = data["zipcode"]
        sql = f"INSERT INTO users (name, surname, phone, zipcode) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, [name, surname, phone, zipcode])
        db.commit()
        return render_template("index.html"), 200
    except:
        return "error: couldn't register user", 400

### update user
@app.route("/update", methods=['POST'])
def update_user():
    cursor = get_db_connection()
    data = request

    if data.form:
        data = data.form
    else:
        data = data.get_json()

    last_phone = data["last_phone"]
    if exists(last_phone):
        name = data["first_name"]
        surname = data["last_name"]
        new_phone = data["phone"]
        new_zipcode = data["zipcode"]
        sql = f"UPDATE users SET phone = %s, zipcode = %s WHERE phone = %s"
        cursor.execute(sql, [new_phone, new_zipcode, new_phone])
        db.commit()
        return render_template("index.html"), 200
    else:
        return "error: user doesn't exist", 400

## delete user for Ananya

# endpoint que llame al endpoint de county
@app.route("/send", methods=['POST'])
def send_data():
    search = get_search()
    cursor = get_db_connection()

    cursor.execute("SELECT name, surname, phone, zipcode from users")
    data = cursor.fetchall()
    list_users = {"users": list()}
    for row in data:
        response_msg = dict()
        response_msg["name"] = row[0]
        response_msg["surname"] = row[1]
        response_msg["phone"] = row[2]
        response_msg["zipcode"] = row[3]
        list_users["users"].append(response_msg)

        zipcode = search.by_zipcode(response_msg["zipcode"])
        zipcode = zipcode.to_dict()
        state = states[zipcode["state"]].lower()
        county = zipcode["county"].replace(" County", "").lower()
        url = "http://arielms.pythonanywhere.com/query/{state}/{county}".format(
            state=state, county=county)
        response = requests.get(url)
        response_dict = json.loads(response.text)
        # returns a list with 1 object
        # keys are Confirmed, Deaths, Recovered, Active, Date
        # print(response_dict)

        # TODO Add twilio request below

    return (''), 200

def exists(phone):
    try:
        print('gets here1')
        sql = "SELECT * FROM users WHERE phone = %s"
        cursor = get_db_connection()
        cursor.execute(sql, [phone])
        data = cursor.fetchall()
        data = data[0]
        name = data[0]
        surname = data[1]
        phone = data[2]
        zipcode = data[3]
        return True
    except:
        return False
