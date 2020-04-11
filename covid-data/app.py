from flask import Flask, request, jsonify
import pandas as pd
from datetime import date, timedelta
import io
import requests

# Initiate app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['JSON_SORT_KEYS'] = False

last_updated = None
data = None

@app.route("/")
def label():
    return jsonify({"Description": "Covid API for U.S.", "Example": "/query/california/alameda"})

@app.route("/update")
def update_data():

    error = {"status": False, "message": ""}

    # Request .csv file from Github
    def request_file(date):
        URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/"
        global last_updated

        try:
            res = requests.get(URL + date.strftime("%m-%d-%Y") + ".csv")
            print("Request status code:", res.status_code)
            last_updated = date
            error = {"status": False, "message": ""}
            return res, error
        except:
            error = {"status": True, "message": "Error retrieving file from GitHub"}
            print(error["message"])
            return False, error

    res, error = request_file(date.today())
    print("Date", date.today())

    # Return on error
    if error["status"]:
        return error["message"]

    # If today's data is not available yet, request data from yesterday
    if res.status_code == 404:
        res, error = request_file(date.today() - timedelta(days = 1))

    # Create and clean df
    global data
    try:
        df = pd.read_csv(io.StringIO(res.content.decode('utf-8')))
        df.rename(columns={'Admin2': 'County', 'Province_State': 'State', 'Country_Region': 'Country',
                           'Last_Update': 'Update', 'Long_': 'Long', 'Combined_Key': 'Key'}, inplace=True)
        df.set_index('Key', inplace=True)
        for column in ["County", "State"]:
            df[column] = df[column].str.replace(' ','-')
            df[column] = df[column].str.lower()
        data = df[df["Country"] == "US"]
        data.to_csv('data.csv')
    except:
        error = {"status": True, "message": "Error while handling df"}
        print(error["message"])
        return jsonify(error["message"])

    return jsonify("Data updated {}".format(last_updated.strftime("%m-%d-%Y")))

@app.route("/last_update")
def last_update():
    return jsonify(last_updated.strftime("%m-%d-%Y") if last_updated else "No data")

@app.route("/query/<state>/<county>")
def query(state, county):
    global data, last_updated
    state = state.lower()
    county = county.lower()

    # Check if data exists
    if data is None:
        return "No data"

    # Filter df by state and county
    df = data
    query = df[(df["State"] == state) & (df["County"] == county)][["Confirmed", "Deaths", "Recovered", "Active"]]
    query_dict = query.to_dict(orient = "records")
    if len(query_dict) != 0:
        query_dict[0].update({"Date": last_updated})

    return jsonify(query_dict)

@app.route("/locate")
def locate():
    # ip_address = request.remote_addr
    ip_address = request.headers['X-Real-IP']
    URL = "http://api.ipstack.com/"
    params = {"access_key": "0fc82cef6483b1d8c902208cd7d08964"}

    try:
        res = requests.get(URL + ip_address, params = params)
        #{"ip": ip_address, "location": "SOME LOCATION"}
        if res.status_code == 200:
            if res.json()["country_code"] != "US":
                return jsonify({"error": "Must be in United States; please deactivate VPN", "ip": ip_address})
            state = res.json()["region_name"]
            zip = res.json()["zip"]
            return jsonify({"state": state, "zip": zip, "ip": ip_address})
        else:
            return jsonify("Error with code {}".format(res.status_code))
    except:
        return jsonify("Error while retrieving location")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)
