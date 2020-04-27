let URL = window.location.href.includes("index.html") ? "http://0.0.0.0:4001" : "http://0.0.0.0:4001";

google.charts.load('current', {
  'packages': ['geochart']
});
google.charts.setOnLoadCallback(drawRegionsMap);

// Get data for all states
async function get_states_data() {
  try {
    let path = "/states";
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
async function drawRegionsMap() {

  // Get data and transform
  const data_raw = await get_states_data();


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
        "\nDeath cases: " + format_case_number(data_raw[key]["Deaths"]) +
        "\nRecovered cases: " + format_case_number(data_raw[key]["Recovered"]);
      data.addRow(["US-" + states_to_abbr(key), value, tooltip]);
    }
  });

  console.log(data)

  const options = {
    region: 'US',
    displayMode: 'regions',
    resolution: 'provinces',
    width: 670,
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
        bold: true,
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