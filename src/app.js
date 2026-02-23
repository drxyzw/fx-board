const reporterCache = {};
let timeseriesData;
let dates;

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

    Plotly.newPlot("timeseries", traces, {
        title: "NEER trend",
        hovermode: "closest",
    });
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
    const group = Array(ret.length).fill("");

    const data = [{
        type: "treemap",
        labels: partners,
        parents: group,
        values: weight,
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
        hovertemplate:
            "<b>%{label}</b><br>" +
            "Weight: %{value.2%}<br>" +
            "Contribution: %{color.2f}%<extra></extra>"
    }]
    const layout = {
        margin: {t:10, l:0, r:0, b:0},
    };
    Plotly.newPlot("heatmap", data, layout);
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

function plotMap(values) {
    const partners = Object.keys(values);
    const z = partners.map(p => values[p]);

    Plotly.newPlot("map", [{
        type: "choropleth",
        locations: partners,
        z: z,
        locationmode: "ISO-3",
        colorscale: "RdBu",
        reversescale: true,
    }], {
        geo: { projection: {type: "natural earth"}},
        title: "Returns by Trade Partner",
    });
}

document.addEventListener("DOMContentLoaded", async() => {
    await loadTimeSeries();
    plotTimeSeries();
    
    document.getElementById("timeseries").on("plotly_hover", async function(event) {
        const reporter = event.points[0].data.name;
        const start = document.getElementById("startDate").value
        const end = document.getElementById("endDate").value
        if(!start | !end) return;

        const reporterData = await loadReporter(reporter);
        const startIdx = getDateIndex(start, reporterData.Date);
        const endIdx = getDateIndex(end, reporterData.Date);
        if(startIdx == -1 | endIdx == -1) return;

        const values = endIdx > startIdx ? computeRangeValues(reporterData, startIdx, endIdx) : None;
        plotHeatmap(reporter, values);
        plotMap(values);
    });
});
