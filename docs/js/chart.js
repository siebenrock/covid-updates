// let URL = window.location.href.includes("index.html") ? "http://0.0.0.0:4001" : "https://covid-api.onrender.com";
let URL = "https://covid-api.onrender.com"

google.charts.load('current', {
  'packages': ['geochart']
});
google.charts.setOnLoadCallback(draw_map);

set_total()

// Get data for all states
async function get_states() {
  try {
    let path = "/states";
    const res = await axios.get(URL + path);
    return res.data;
  } catch (e) {
    console.error(e);
  }
}

// Get totals
async function get_total() {
  try {
    let path = "/total";
    const res = await axios.get(URL + path);
    return res.data;
  } catch (e) {
    console.error(e);
  }
}

// Convert states to abbreviation
function states_to_abbr(input) {
  for (state = 0; state < states.length; state++) {
    if (states[state][0] == input) {
      return (states[state][1]);
    }
  }
}

function format_case_number(number) {
  return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".")
}

// Draw map with states
async function draw_map() {

  // Get data and transform
  const data_raw = await get_states();

  // Setup Google data table
  var data = new google.visualization.DataTable();
  data.addColumn('string', 'State');
  data.addColumn('number', 'Value');
  data.addColumn({
    type: 'string',
    role: 'tooltip'
  });

  // Add data to data table
  Object.keys(data_raw).map(function(key) {
    if (states_drop.indexOf(key) === -1) {
      let value = data_raw[key]["Confirmed"];
      let state_name = key.replace("-", " ")
        .split(" ").map((str) => str.charAt(0).toUpperCase() + str.substring(1)).join(" ");
      let tooltip = state_name + "\nConfirmed cases: " + format_case_number(value) +
        "\nDeaths: " + format_case_number(data_raw[key]["Deaths"])
      if (data_raw[key]["Recovered"] !== 0) {
        tooltip += "\nRecovered cases: " + format_case_number(data_raw[key]["Recovered"]);
      };
      "\nRecovered cases: " + format_case_number(data_raw[key]["Recovered"]);
      data.addRow(["US-" + states_to_abbr(key), value, tooltip]);
    }
  });

  console.log(data)

  const options = {
    region: 'US',
    displayMode: 'regions',
    resolution: 'provinces',
    width: $(window).width() > 550 ? 670 : 380,
    backgroundColor: {
      fill: '#191a24',
    },
    datalessRegionColor: '#191a24',
    colorAxis: {
      colors: ['#430708', '#AF0C1B', '#C20A1B', '#EB0015'],
      minValue: 0,
    },
    tooltip: {
      textStyle: {
        color: 'black',
        fontSize: 14,
        bold: false,
      },
      showColorCode: true,
    },
    legend: {
      textStyle: {
        color: 'white',
        fontSize: 14,
      }
    }
  };

  let chart = new google.visualization.GeoChart(document.getElementById("chart-map"));

  chart.draw(data, options);
}

// Set total numbers
async function set_total() {

  // Get data
  const total = await get_total();

  // Set numbers
  $("#confirmed").html(format_case_number(total["Confirmed"]));
  $("#deaths").html(format_case_number(total["Deaths"]));
  $("#recovered").html(format_case_number(total["Recovered"]));
  $("#last-update").html("Last update: " + total["Date"].slice(0, 17));

}