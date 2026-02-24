const reporterCache = {};
let timeseriesData;
let dates;
let ccy_country_map;

async function loadTimeSeries() {
    const res= await fetch("/data/NEER_CHART_DAILY.json");
    timeseriesData = await res.json();
    timeseriesData = {
        "Date": timeseriesData.Date,
        "USD": timeseriesData.USD,
        "JPY": timeseriesData.JPY,
        "EUR": timeseriesData.EUR}
    dates = timeseriesData.Date;
}

function plotTimeSeries() {
    const currencies = Object.keys(timeseriesData).filter(k => k != "Date");
    const traces = currencies.map(c => ({
        x: dates,
        y: timeseriesData[c],
        mode: "lines",
        name: c,
    }));
    const layout = {
        title: "NEER trend",
        hovermode: "closest",
        xaxis: {
            type: "date",
            hoverformat: "%d %b %Y",
        }
    }
    Plotly.newPlot("timeseries", traces, layout);
}

async function loadReporter(reporter) {
    if(reporterCache[reporter]) return reporterCache[reporter]

    const res = await fetch(`/data/detail/${reporter}.json`);
    const data = await res.json();
    reporterCache[reporter] = data;
    return data;
}

function getDateIndex(date, datesArray) {
    return datesArray.indexOf(date);
}

function computeRangeValues(data, startIdx, endIdx) {
    const result = {};
    for (const partner in data.partner) {
        const arr = data.partner[partner];
        result[partner] = {}
        for(const key of Object.keys(arr)) {
            const endVal = arr[key][endIdx];
            const startVal = startIdx > 0 ? arr[key][startIdx] : 0;
            result[partner][key] = endVal - startVal
        }
        result[partner]["cum_weight"] /= endIdx - startIdx
    }
    return result;
}

function plotHeatmap(reporter, values) {
    const partners = Object.keys(values);
    const ret = partners.map(p => values[p]["cum_return"]);
    const weight = partners.map(p => values[p]["cum_weight"]);
    const contrib = partners.map(p => values[p]["cum_contribution"]);
    const group = Array(partners.length).fill("");
    // partners.map(() => "");
    // const group = partners.map(() => reporter + "NEER impact from partner currencies");

    const data = [{
        type: "treemap",
        // paper_bgcolor: "rgba(0,0,0,0)",
        // plot_bgcolor: "rgba(0,0,0,0)",
        labels: partners,
        parents: group,
        branchvalues: "total",
        pathbar: { visible: false },
        root: {
            visible: true,
            color: "rgba(0,0,0,0)",
        },
        // tiling: {packing: "squarify"},
        values: weight,
        // domain: { x: [0, 1], y: [0, 1] },
        marker: {
            colors: contrib,
            colorscale: [
                [0.0, "#8b0000"],
                [0.5, "#f0f0f0"],
                [1.0, "#006400"]
            ],
            cmin: -1.0,
            cmax: 1.0,
            cmid: 0.0,
            line: {width: 1}
        },
        textinfo: "label",
        // hoverlabel: {
        //     namelength: 0,
        // },
        hovertemplate:
            '<b>%{label}</b><br>' +
            'Weight: %{value:.2f}%<br>' +
            'Contribution: %{color:.2f}%<extra></extra>',
        // hoverinfo: "label+value",
        // textinfo: "label",
        // tiling: { pad: 2 }
    }]
    const layout = {
        margin: {t:0, l:0, r:0, b:0},
        // margin: {t:10, l:0, r:0, b:0},
        // clickmode: "none",
    };
    Plotly.react("heatmap", data, layout);
    // Plotly.newPlot("heatmap", data, layout);
    // Plotly.newPlot("heatmap", [{
    //     z: z,
    //     x: partners,
    //     y: [reporter],
    //     type: "heatmap",
    //     colorscale: "RdBu",
    //     reversescale: true,
    // }], {
    //     title: `Return vs ${reporter}`
    // });
}

async function plotMap(values) {
    if(!ccy_country_map) {
        const res = await fetch(`/data/detail/CCY_COUNTRY.json`);
        ccy_country_map = await res.json();
    }
    const partners = Object.keys(values);
    const country_code = partners.flatMap(p => ccy_country_map[p]);
    const z = Object.entries(values).flatMap(([ccy, val]) => {
        const countries = ccy_country_map[ccy] ?? [];
        const countryList = Array.isArray(countries) ? countries : [countries];
        return countryList.map(() => val);
    });
    Plotly.newPlot("map", [{
        type: "choropleth",
        locations: country_code,
        z: z,
        locationmode: "ISO-3",
        colorscale: "RdBu",
        reversescale: true,
    }], {
        geo: { projection: {type: "natural earth"}},
        title: "Return of each NEER",
    });
}
function shiftPastDate(yyyymmdd) {
    const yearStr = yyyymmdd.substring(0, 4);
    const year = parseInt(yearStr, 10) - 1;
    const mmdd = yyyymmdd.substring(4);
    return year.toString() + mmdd;
}
document.addEventListener("DOMContentLoaded", async() => {
    await loadTimeSeries();
    // line chart
    plotTimeSeries();
    
    // world map
    // default date
    const lastDate = timeseriesData["Date"][timeseriesData["Date"].length-1];
    const pastDate = shiftPastDate(lastDate);
    const startInput = document.getElementById("startDate");
    const endInput = document.getElementById("endDate");
    if (!startInput.value) startInput.value = pastDate;
    if (!endInput.value) endInput.value = lastDate;
    const triggerWorldMap = (event) => {

        const start = document.getElementById("startDate").value;
        const end = document.getElementById("endDate").value;
        // if(!start || !end) return;
        const startIdx = getDateIndex(start, dates);
        const endIdx = getDateIndex(end, dates);
        if(startIdx == -1 || endIdx == -1) return;
        if(endIdx > startIdx) {
            const result = {};
            for (const partner in timeseriesData) {
                if (partner === "Date") continue;
                const arr = timeseriesData[partner];
                result[partner] = {}
                const endVal = arr[endIdx];
                const startVal = startIdx > 0 ? arr[startIdx] : 0;
                result[partner] = endVal - startVal
            }
            plotMap(result);
        }
    }
    triggerWorldMap();
    startInput.addEventListener("change", triggerWorldMap);
    endInput.addEventListener("change", triggerWorldMap);

    // heatmap
    document.getElementById("timeseries").on("plotly_hover", async function(event) {
        const start = document.getElementById("startDate").value;
        const end = document.getElementById("endDate").value;
        if(!start || !end) return;
        const reporter = event.points[0].data.name;
        const reporterData = await loadReporter(reporter);
        const startIdx = getDateIndex(start, reporterData.Date);
        const endIdx = getDateIndex(end, reporterData.Date);
        if(startIdx == -1 || endIdx == -1) return;

        const values = endIdx > startIdx ? computeRangeValues(reporterData, startIdx, endIdx) : null;
        plotHeatmap(reporter, values);
    });
});
