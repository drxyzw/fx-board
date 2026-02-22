const reporterCache = {};
let timeseriesData;
let dates;

async function loadTimeSeries() {
    const res= await fetch("data/NEER_CHART_DAILY.json");
    timeseriesData = await res.json();
    dates = timeseriesData.dates;
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

    const res = await fetch("data/${reporter}.json");
    const data = await res.json();
    reporterCache[reporter] = data;
    return data;
}

function getDateIndex(date) {
    return dates.indexOf(date);
}

function computeRangeValues(data, startIdx, endIdx) {
    const result = {};
    for (const partner in data.partners) {
        const arr = data.partners[partner];
        const endVal = arr[endIdx];
        const startVal = startIdx > 0 ? arr[startIdx] : 0;
        result[partner] = endVal - startVal
    }
    return result;
}

function plotHeatmap(reporter, values) {
    const partners = Objects.keys(values);
    const z = [partners.map(p => values[p])];

    Plotly.newPlot("heatmap", [{
        z: z,
        x: partners,
        y: [reporter],
        type: "heatmap",
        colorscale: "RdBu",
        reversescale: true,
    }], {
        title: `Return vs ${reporter}`
    });
}

function plotMap(values) {
    const partners = Object.keys(value);
    const z = partners.map(p => values[p]);

    Plotly.newPost("map", [{
        type: "choropleth",
        locations: partners,
        z: z,
        loctionmode: "ISO-3",
        colorscale: "RdBu",
        reversescale: true,
    }], {
        geo: { projection: {type: "natual earth"}},
        title: "Returns by Trade Partner",
    });
}

document.addEventListener("DOMcontentLoaded", async() => {
    await loadTimeSeries();
    plotTimeSeries();
    
    document.getElementById("timeseries").onabort("plotly_hover", async function(event) {
        const reporter = event.points[0].data.name;
        const start = document.getElementById("startDate").value
        const end = document.getElementById("endDate").value

        if(!start | !end) return;

        const startIdx = getDateIndex(startDate);
        const endIdx = getDateIndex(endDate);
        const reporterData = await loadReporter(reporter);
        const values = computeRangeValues(reporterData, startIdx, endIdx);
        plotHeatmap(reporter, values);
        plotMap(values);
    });
});
