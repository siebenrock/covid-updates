import io
from datetime import date, timedelta

import pandas as pd
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

# Initiate app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['JSON_SORT_KEYS'] = False

last_updated = None
data = None

# For development
CORS(app)

# Info
@app.route("/", methods=["GET"])
def label():
    return jsonify({"Description": "Covid API for U.S.", "Example": "/query/california/alameda"}), 200

# Update dataset
@app.route("/update", methods=["GET"])
def update():

    error = {"status": False, "message": ""}

    # Request .csv file from Github
    def request_file(date):
        URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/"
        path = URL + date.strftime("%m-%d-%Y") + ".csv"
        global last_updated

        try:
            res = requests.get(path)
            print("Request status code:", res.status_code)
            last_updated = date
            error = {"status": False, "message": ""}
            return res, error
        except:
            error = {"status": True,
                     "message": "Error retrieving file from GitHub"}
            print(error["message"])
            return False, error

    res, error = request_file(date.today())

    # Return on error
    if error["status"]:
        return jsonify(error["message"]), 400

    # If today's data is not available yet, request data from yesterday
    if res.status_code == 404:
        res, error = request_file(date.today() - timedelta(days=1))

    # Create and clean df
    global data
    try:
        df = pd.read_csv(io.StringIO(res.content.decode('utf-8')))
        df.rename(columns={'Admin2': 'County', 'Province_State': 'State', 'Country_Region': 'Country',
                           'Last_Update': 'Update', 'Long_': 'Long', 'Combined_Key': 'Key'}, inplace=True)
        df.set_index('Key', inplace=True)
        df = df.drop(columns=["FIPS", "Lat", "Long"])
        for column in ["County", "State"]:
            df[column] = df[column].str.replace(' ', '-')
            df[column] = df[column].str.lower()
        data = df[df["Country"] == "US"]
        data.to_csv('data.csv')
    except:
        error = {"status": True, "message": "Error while handling df"}
        print(error["message"])
        return jsonify(error["message"]), 400

    return jsonify("Data updated {}".format(last_updated.strftime("%m-%d-%Y"))), 200

# Get date of last update
@app.route("/last_update", methods=["GET"])
def last_update():
    if last_updated:
        return jsonify(last_updated.strftime("%m-%d-%Y")), 200
    else:
        return jsonify("No data"), 400

# Get data for specific state and county
@app.route("/get", methods=["GET"])
def get():
    global data, last_updated

    # Check if data exists
    if data is None:
        return jsonify("No data"), 400
    df = data

    # State and county given
    if "state" in request.args and "county" in request.args:
        state = request.args.get("state").lower()
        county = request.args.get("county").lower()

        # Filter df by state and county
        query = df[(df["State"] == state) & (df["County"] == county)
                   ][["Confirmed", "Deaths", "Recovered", "Active"]]
        query_dict = query.to_dict(orient="records")[0]

    # State but no county given
    elif "state" in request.args and "county" not in request.args:
        state = request.args.get("state").lower()

        # Filter df by state
        query = df[(df["State"] == state)][[
            "Confirmed", "Deaths", "Recovered", "Active"]]
        query = query.sum()
        query_dict = query.to_dict()

    # No state and no county given
    elif "state" not in request.args and "county" not in request.args:
        query = df[["Confirmed", "Deaths", "Recovered", "Active"]]
        query = query.sum()
        query_dict = query.to_dict()

    # Include last update date
    if len(query_dict) != 0:
        query_dict.update({"Date": last_updated})

    return jsonify(query_dict), 200

# Get data for all states
@app.route("/states", methods=["GET"])
def get_states():
    global data, last_updated

    # Check if data exists
    if data is None:
        return jsonify("No data"), 400

    # Aggregate values by state
    df = data[["State", "Confirmed", "Deaths", "Recovered"]]
    df = df.groupby("State").sum()

    df_dict = {}
    for state in df.index:
        df_dict[state] = df.loc[state].to_dict()

    # Include last update date
    if len(df_dict) != 0:
        df_dict.update({"Date": last_updated})

    return jsonify(df_dict), 200


@app.route("/locate", methods=["GET"])
def locate():
    # Initial idea to locate user by IP address
    # ip_address = request.remote_addr
    ip_address = request.headers['X-Real-IP']
    URL = "http://api.ipstack.com/"
    params = {"access_key": "0fc82cef6483b1d8c902208cd7d08964"}

    try:
        res = requests.get(URL + ip_address, params=params)
        #{"ip": ip_address, "location": "SOME LOCATION"}
        if res.status_code == 200:
            if res.json()["country_code"] != "US":
                return jsonify({"error": "Must be in United States; please deactivate VPN", "ip": ip_address}), 400
            state = res.json()["region_name"]
            zip = res.json()["zip"]
            return jsonify({"state": state, "zip": zip, "ip": ip_address}), 200
        else:
            return jsonify("Error with code {}".format(res.status_code)), 400
    except:
        return jsonify("Error while retrieving location"), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4001, threaded=True, debug=True)
