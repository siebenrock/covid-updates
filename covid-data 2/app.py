import pandas as pd
from flask import Flask, jsonify, request
from datetime import datetime, date, timedelta
import os.path
import requests

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['JSON_SORT_KEYS'] = False


# Function to check if a file exists in url
def exists(path):
    r = requests.head(path)
    return r.status_code == requests.codes.ok

# Function to download a file fro url
def download(url, file_name):
    with open(file_name, "wb") as file:
        response = requests.get(url)
        file.write(response.content)


# Function to get the dataframe
def get_dataframe(lastestDate=datetime.today().strftime('%m-%d-%Y')):
    path = lastestDate+".csv"

    # check if file already exists
    if os.path.exists(path):
        df = pd.read_csv(path)
        return df
    
    # If file does not exists then download
    url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/"
    yesterday = date.today() - timedelta(days=1)
    newDate = yesterday.strftime('%m-%d-%Y')

    # If file for today exists download, else get yesterday date's file
    if(exists(url+lastestDate+".csv")):
        download(url+lastestDate+".csv", lastestDate+".csv")
        return get_dataframe()
    else:
        return get_dataframe(newDate)
    return pd.DataFrame()


# Main Endpoint
@app.route('/getData', methods=["GET"])
def getData():

    # Call Dataframe
    df_raw = get_dataframe()

    # Preprocessing 
    df = df_raw.drop(columns=["FIPS", "Lat", "Long_"])
    df.rename(columns={'Admin2': 'County', 'Province_State': 'State', 'Country_Region': 'Country',
                       'Last_Update': 'Update', 'Combined_Key': 'Key'}, inplace=True)
    df.set_index('Key', inplace=True)
    for column in ["County", "State"]:
        df[column] = df[column].str.replace(' ', '-')
        df[column] = df[column].str.lower()

     # Check for get Data
    if request.method == 'GET':

        # If user has provided both state and county
        if 'state' in request.args and 'county' in request.args:
            data = df.loc[(df["County"] == request.args.get('county').lower()) & (
                df["State"] == request.args.get('state').lower())]
            data_dict = data.to_dict(orient='records')
            print(data_dict)
            if not bool(data_dict):
                return jsonify({"status": False, "error": "No data found for specified county and state, please check your inputs."})
            return jsonify(data_dict)

        # If user has only provided state
        elif 'state' in request.args and 'county' not in request.args:
            data = df.loc[df["State"] == request.args.get('state').lower()]
            data_dict = data.to_dict(orient='records')
            if not bool(data_dict):
                return jsonify({"status": False, "error": "No data found for specified state, please check your input."})
            return jsonify(data_dict)

    # User has not provided any parameters, then return US Data.
    data = df[df["Country"] == "US"]
    data_dict = data.to_dict(orient='records')
    
    return jsonify(data_dict)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)
