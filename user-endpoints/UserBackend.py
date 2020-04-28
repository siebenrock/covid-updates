from flask import Flask, request, jsonify, render_template
from uszipcode import SearchEngine
import MySQLdb
import requests
import json
from twilio import twiml
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler

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


def sensor():
    """ Function for test purposes. """
    requests.get("https://covid-api.onrender.com/update")
    requests.post("http://localhost:5000/send")


sched = BackgroundScheduler(daemon=True)
# sched.add_job(sensor, 'interval', minutes=.25)
sched.add_job(sensor, 'cron', day_of_week='*', hour=9)
sched.start()

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

# Info
@app.route("/")
def label():
    return jsonify({"Description": "USER API"}), 200


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
        msg = "You have subscribed for COVID Updates."
        sendSMS(msg, phone)
        return (''), 200
    except:
        return "error: couldn't register user", 400

# update user
@app.route("/update", methods=['POST'])
def update_user():
    cursor = get_db_connection()
    data = request

    if data.form:
        data = data.form
    else:
        data = data.get_json()

    last_phone = str(data["last_phone"])

    if exists(last_phone):
        name = data["first_name"]
        surname = data["last_name"]
        new_phone = data["new_phone"]
        zipcode = data["zipcode"]
        # sql = "UPDATE users SET name = '{name}', surname = '{surname}', phone = '{phone}', zipcode = '{zipcode}' WHERE phone = {last_phone}".format(
        #     name=str(name), surname=str(surname), phone=str(new_phone), zipcode=str(zipcode), last_phone = str(last_phone))
        # cursor.execute(sql)
        sql = f"UPDATE users SET name = %s, surname = %s, phone = %s, zipcode = %s WHERE phone = %s"
        cursor.execute(sql, [name, surname, new_phone, zipcode, last_phone])
        db.commit()
        if new_phone != last_phone:
            msg_last = "You have updated your information. You will no longer be receiving COVID Updates at " + \
                str(last_phone) + \
                ". You will now recieve updates at " + str(new_phone)
            sendSMS(msg_last, last_phone)
            msg_new = "You have updated your information. You will now receive COVID Updates at " + \
                str(new_phone) + \
                ". You will no longer be receiving COVID Updates at " + \
                str(last_phone)
            sendSMS(msg_new, new_phone)
        else:
            msg = "You have updated your information."
            sendSMS(msg, new_phone)
        return (''), 200
    else:
        return "error: user doesn't exist", 400


@app.route("/unsubscribe", methods=['POST'])
def unsubscribe_user():
    global db
    cursor = get_db_connection()

    data = request

    if data.form:
        data = data.form
    else:
        data = data.get_json()

    phone = data["phone"]

    if exists(phone):
        sql = f"DELETE FROM users WHERE phone = %s"
        cursor.execute(sql, [phone])
        db.commit()
        msg = "You have unsubscribed from COVID Updates."
        sendSMS(msg, phone)
        return (''), 200
    else:
        return "error: user doesn't exist", 404

# endpoint que llame al endpoint de county
@app.route("/send", methods=['POST'])
def send_data():
    list_users = getUsers()
    for user in list_users["users"]:
        phone = str(user["phone"])
        zipcode = str(user["zipcode"])
        msg = getCovidData(zipcode)

        if msg != "error":
            resp = sendSMS(msg, phone)
            if resp == 'failed':
                print("failure, could not send to: " + phone + "\n")
            else:
                print("success, the following message was sent to: " + phone)
                print(msg + "\n")
        else:
            print("failure, could not identify zipcode: " + zipcode + "\n")

    return (''), 200


def exists(phone):
    try:
        sql = "SELECT * FROM users WHERE phone = '{phone}'".format(
            phone=str(phone))
        cursor = get_db_connection()
        cursor.execute(sql)
        data = cursor.fetchall()
        data = data[0]
        name = data[0]
        surname = data[1]
        phone = data[2]
        zipcode = data[3]
        return True
    except:
        return False


def getTwilioClient():
    account_sid = 'AC71c18c3fb2750f45f156ba3a884204b0'
    auth_token = 'dcf2070f53ebf5da9082aaa6941abad0'
    client = Client(account_sid, auth_token)
    return client


def sendSMS(msg, number):
    client = getTwilioClient()
    try:
        message = client.messages \
            .create(
                body=str(msg),
                messaging_service_sid='MG1e4b8901eff112fe61c2292994d6f5c9',
                to=str(number)
            )
        return 'sent'
    except:
        return 'failed'


def getUsers():
    search = SearchEngine(simple_zipcode=True)
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

    return list_users


def getCovidData(zipcode):
    try:
        search = SearchEngine(simple_zipcode=True)
        zipcode = search.by_zipcode(str(zipcode))
        zipcode = zipcode.to_dict()
        state = states[zipcode["state"]].lower()
        county = zipcode["county"].replace(" County", "").lower()
        url = "https://covid-api.onrender.com/get?state={state}&county={county}".format(
            state=state, county=county)
        response = requests.get(url)
        response_dict = json.loads(response.text)
        if str(response_dict['Recovered']) == '0':
            msg = "COVID UPDATE " + state.upper() + ", " + county.upper() + " COUNTY. DATE: " + str(response_dict['Date']) + "\n" \
                "There are " + str(response_dict['Confirmed']) + " confirmed cases.\n" + \
                "There are " + \
                str(response_dict['Deaths']) + " confirmed deaths."
        else:
            msg = "COVID UPDATE " + state.upper() + ", " + county.upper() + " COUNTY. DATE: " + str(response_dict['Date']) + "\n" \
                "There are " + str(response_dict['Confirmed']) + " confirmed cases.\n" + \
                "There are " + str(response_dict['Deaths']) + " confirmed deaths.\n" + \
                "There are " + \
                str(response_dict['Recovered']) + " confirmed recoveries."
        return msg
    except:
        return "error"
