import uuid
import random
import numpy as np
import pandas as pd
from datetime import date, timedelta
import io
import requests
import json
from flask import Flask, redirect, url_for, request, jsonify
app = Flask(__name__)

daily_data = None


def get_daily_data(url="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/"):
    global daily_data

    query_date = date.today()
    request = requests.get(url + query_date.strftime("%m-%d-%Y") + ".csv")

    df = pd.read_csv(io.StringIO(request.content.decode('utf-8')))
    df.rename(columns={'Admin2': 'County', 'Province_State': 'State', 'Country_Region': 'Country',
                       'Last_Update': 'Update', 'Long_': 'Long', 'Combined_Key': 'Key'}, inplace=True)
    df.set_index('Key', inplace=True)
    df.index = df.index.str.lower()
    data = df.loc[df["Country"] == "US"]

    daily_data = data.to_dict(orient='index')
    # print(daily_data)
    # print(json.dumps(data_dict, indent=2))
    return

@app.route('/county/<county_name>', methods=['GET'])
def get_by_county(county_name):
    get_daily_data()
    county_name = county_name.lower()
    resp = [value for key, value in daily_data.items()
            if county_name in key.lower()]
    return jsonify(resp), 200

# if __name__ == "__main__":
#     get_daily_data()
#     get_by_county("Adair")
