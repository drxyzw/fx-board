const reporterCache = {};
let timeseriesData;
let dates;
let ccy_country_map;
let heatmap_reporter;

async function loadTimeSeries() {
    const res= await fetch("/data/NEER_CHART_DAILY.json");
    timeseriesData = await res.json();
    // timeseriesData = {
    //     "Date": timeseriesData.Date,
    //     "USD": timeseriesData.USD,
    //     "JPY": timeseriesData.JPY,
    //     "EUR": timeseriesData.EUR}
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
        result[partner]["weight"] /= endIdx - startIdx
    }
    return result;
}

function plotHeatmap(reporter, values) {
    const partners = Object.keys(values);
    const ret = partners.map(p => values[p]["return"]);
    const weight = partners.map(p => values[p]["weight"]);
    const contrib = partners.map(p => values[p]["contribution"]);
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
    const cmax = Math.max([Math.max(...z), Math.min(...z)]);
    Plotly.newPlot("map", [{
        type: "choropleth",
        locations: country_code,
        z: z,
        locationmode: "ISO-3",
        colorscale: [
            [0.0, "#006400"],
            [0.5, "#f0f0f0"],
            [1.0, "#8b0000"]
        ],
        cmin: -cmax,
        cmax: cmax,
        cmid: 0.0,
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
    
    // date range slider
    const slider1 = document.getElementById("slider-1");
    const slider2 = document.getElementById("slider-2");
    const maxIdx = dates.length - 1;
    slider1.min = 0;
    slider1.max = maxIdx;
    slider1.value = 0;
    slider2.min = 0;
    slider2.max = maxIdx;
    slider2.value = maxIdx;
    // default date
    // const lastDate = timeseriesData["Date"][timeseriesData["Date"].length-1];
    // const pastDate = shiftPastDate(lastDate);
    const startInput = document.getElementById("startDate");
    const endInput = document.getElementById("endDate");
    // if (!startInput.value) startInput.value = pastDate;
    // if (!endInput.value) endInput.value = lastDate;

    // world map
    const triggerWorldMap = (event) => {
        const val1 = parseInt(slider1.value);
        const val2 = parseInt(slider2.value);
        const startIdx = Math.min(val1, val2);
        const endIdx = Math.max(val1, val2);
        startInput.value = dates[startIdx];
        endInput.value = dates[endIdx];

        if(startIdx == -1 || endIdx == -1) return;
        const result = {};
        for (const partner in timeseriesData) {
            if (partner === "Date") continue;
            const arr = timeseriesData[partner];
            const endVal = arr[endIdx];
            const startVal = arr[startIdx];
            result[partner] = endVal - startVal;
        }
        plotMap(result);
    };

    triggerWorldMap();
    slider1.addEventListener("input", triggerWorldMap);
    slider2.addEventListener("input", triggerWorldMap);

    // heatmap
    async function triggerHeatmap(event) {
        const eventForType = event.event ?? event;
        const start = document.getElementById("startDate").value;
        const end = document.getElementById("endDate").value;
        if(!start || !end) return;
        if(eventForType.type == "mousemove") { // hovering a line chart
            heatmap_reporter = event.points[0].data.name;
        }
        if(heatmap_reporter) {
            const reporterData = await loadReporter(heatmap_reporter);
            const startIdx = getDateIndex(start, reporterData.Date);
            const endIdx = getDateIndex(end, reporterData.Date);
            if(startIdx == -1 || endIdx == -1) return;

            const values = endIdx > startIdx ? computeRangeValues(reporterData, startIdx, endIdx) : null;
            plotHeatmap(heatmap_reporter, values);
        }
    }
    document.getElementById("timeseries").on("plotly_hover", triggerHeatmap);
    slider1.addEventListener("input", triggerHeatmap);
    slider2.addEventListener("input", triggerHeatmap);
});
