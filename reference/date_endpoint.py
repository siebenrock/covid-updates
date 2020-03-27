from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['JSON_SORT_KEYS'] = False

@app.route("/")
def index():
    return "Hello"


@app.route("/date/<ipDate>")
def get_data_from_date(ipDate):

    try:
        url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/"+ipDate+".csv"
        df = pd.read_csv(url)
    except:
        return jsonify({"error": "No data for that date currently exist."})
    data = df.loc[df["Country_Region"] == "US"]
    data = data.drop(columns=["FIPS", "Country_Region", "Last_Update", "Lat", "Long_", "Combined_Key"])
    data.rename(columns = {'Admin2':'County', 'Province_State':'State'}, inplace = True)
    data_dict = data.to_dict(orient='records')
    
    return jsonify(data_dict)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)