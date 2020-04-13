from flask import Flask, request, jsonify
from uszipcode import SearchEngine
import requests
import json

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

users = [('5555555555', '94720'), ('5555555555', '94720')]

# Initiate app
app = Flask(__name__)

search = None

def get_search():
    global search
    if not search:
        search = SearchEngine(simple_zipcode=True)
    return search

@app.route("/register", methods = ["POST"])
def register_user():
    data = request.get_json()
    return jsonify(str(data["phone"]) + str(data["zipcode"]))

# endpoint que llame al endpoint de county
@app.route("/send")
def send_data():
    search = get_search()
    for user in users:
        user_zip_code = user[1]
        zipcode = search.by_zipcode(str(user_zip_code))
        zipcode = zipcode.to_dict()
        state = states[zipcode["state"]].lower()
        county = zipcode["county"].replace(" County", "").lower()
        url = "http://arielms.pythonanywhere.com/query/{state}/{county}".format(
            state = state, county = county)
        response = requests.get(url)
        print(json.loads(response.text))
    return (''), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, threaded=True, debug=True)
