import { CONFIG } from "./config"

const reporterCache = {};
let timeseriesData;
let ts_scale;
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

function alignSliderWithChart() {
    const gd = document.getElementById('timeseries');
    const wrapper = document.querySelector('.slider-align-wrapper');
    
    // 1. Get the internal plotting rectangle (the actual grid area)
    const plotArea = gd.querySelector('.nse-grid') || gd.querySelector('.xy') || gd.querySelector('.gridlayer');
    
    if (!gd || !plotArea || !wrapper) return;

    const plotRect = plotArea.getBoundingClientRect();
    const wrapperRect = wrapper.parentElement.getBoundingClientRect();

    // 2. Calculate offsets relative to the common parent (the container)
    // We want the slider track to start EXACTLY where the grid starts
    const leftPadding = plotRect.left - wrapperRect.left;
    
    // And end EXACTLY where the grid ends
    const rightPadding = wrapperRect.right - plotRect.right;

    // 3. Apply to CSS variables
    wrapper.style.setProperty('--chart-margin-left', `${leftPadding}px`);
    wrapper.style.setProperty('--chart-margin-right', `${rightPadding}px`);
}

function plotTimeSeries() {
    const currencies = Object.keys(timeseriesData).filter(k => k != "Date");
    const initial_ccies = CONFIG.initial_currencies;
    if(!ts_scale) ts_scale = Array(currencies.length).fill(1.0);

    const traces = currencies.map((c, i) => ({
        x: dates,
        y: timeseriesData[c].map((v) => v * ts_scale[i]),
        // y: timeseriesData[c],
        name: c,
        mode: "lines",
        visible: initial_ccies.includes(c) ? true : "legendonly",
        line: {
            width: 1.2,
            color: `hsl(${(i * 137.5) % 360}, 70%, 60%)`, // HSL color scheme
        },
    }));

    const layout = {
        template: "plotly_dark",
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        title: {
            text: "NEER trend",
            font: { color: "#3a86ff", size: 16 },
        },
        hovermode: "closest",
        margin: { l: 50, r: 180, t: 40, b: 40 },
        xaxis: {
            type: "date",
            gridcolor: "#1e293b",
            tickfont: { size: 11, color: "#94a3b8" },
            hoverformat: "%d %b %Y",
            automargin: false,
        },
        yaxis: {
            side: "right",
            gridcolor: "#1e293b",
            tickfont: { size: 11, color: "#94a3b8" },
            tickpadding: 15,
            automargin: false,
        },
        legend: {
            orientation: "v",
            x: 1.1,
            y: 1,
            font: { size: 10, color: "#94a3b8" },
            bgcolor: "rgba(0,0,0,0)",
        }
    };
    const config = {
        responsive: true,
    };
    Plotly.newPlot("timeseries", traces, layout, config).then(() => {
        alignSliderWithChart();
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
        result[partner]["weight"] = result[partner]["cum_weight"] / (endIdx - startIdx)
    }
    return result;
}

function plotHeatmap(reporter, values) {
    const partners = Object.keys(values);
    const ret = partners.map(p => values[p]["return"]);
    const weight = partners.map(p => values[p]["weight"]);
    const contrib = partners.map(p => values[p]["contribution"]);
    const group = Array(partners.length).fill("");
    const maxAbsContrib = Math.max(Math.abs(Math.max(contrib)), Math.abs(Math.min(contrib)));
    const hovertemplates = partners.map((v, i) => {
        return i == 0 ? "" :
            '<b>%{label}</b><br>' +
            'Weight: %{value:.2%}<br>' +
            'Contribution: %{color:.2%}<extra></extra>'
    });
    const data = [{
        type: "treemap",
        labels: partners,
        parents: group,
        branchvalues: "total",
        pathbar: { visible: false },
        root: {
            visible: true,
            color: "rgba(0,0,0,0)",
        },
        values: weight,
        marker: {
            colors: contrib,
            colorscale: [
                [0.0, "#8b0000"],
                [0.5, "#f0f0f0"],
                [1.0, "#006400"]
            ],
            cmin: -maxAbsContrib,
            cmax: 1.0,
            cmid: maxAbsContrib,
            line: {width: 1}
        },
        textinfo: "label",
        // hoverlabel: {
        //     namelength: 0,
        // },
        hovertemplate: hovertemplates,
    }];
    const layout = {
        template: "plotly_dark",
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        margin: {t: 50, l: 10, r: 10, b:10 },
        title: {
            text: `Composition of ${reporter} NEER change vs partner`,
            font: { color: "#3a86ff", size: 16 },
        },
    };
    const config = {
        responsive: true,
    };
    Plotly.react("heatmap", data, layout, config);
}

async function plotMap(values) {
    if(!ccy_country_map) {
        const res = await fetch(`/data/detail/CCY_COUNTRY.json`);
        ccy_country_map = await res.json();
    }
    const reporters = Object.keys(values);
    const country_code = reporters.flatMap(p => ccy_country_map[p]);
    const z = Object.entries(values).flatMap(([ccy, val]) => {
        const countries = ccy_country_map[ccy] ?? [];
        const countryList = Array.isArray(countries) ? countries : [countries];
        return countryList.map(() => val);
    });
    const country2GroupArray = Object.entries(ccy_country_map).filter(([key, value]) => Array.isArray(value))
        .flatMap(([key, values]) => values.map(value=>[value, key]));
    const country2Group = Object.fromEntries(country2GroupArray);
    const country_code_tooltip = country_code.map((c) => country2Group[c] ?? c)
    const zmax = Math.max(Math.abs(Math.max(...z)), Math.abs(Math.min(...z)));
    const traces = [{
        type: "choropleth",
        locations: country_code,
        z: z,
        locationmode: "ISO-3",
        colorscale: [
            [0, "#8b0000"],
            [0.5, "#f0f0f0"],
            [1, "#006400"]
        ],
        zmin: -zmax,
        zmax: zmax,
        zmid: 0.0,
        cauto: false,
        customdata: country_code_tooltip,
        hovertemplate:
            '<b>%{customdata}</b><br>' +
            '%{z:.2%}<br>' +
            '<extra></extra>',
        // Colorbar at bottom
        colorbar: {
            orientation: "h",
            x: 0.5,
            y: -0.15,
            xanchor: "center",
            yanchor: "top",
            tickformat: ".1%",
            tickfont: { color: "#94a3b8" },
        }
    }];
    const layout = {
        template: "plotly_dark",
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        geo: {
            projection: {type: "natural earth"},
            bgcolor: "rgba(0,0,0,0)",
            lakecolor: "#0b0e14",
            showlake: true,
            landcolor: "#1e293b",
            subunitcolor: "#334155",
        },
        title: {
            text: "NEER OF REPORTER CURRENCY",
            font: { color: "#3a86ff", size: 16 },
        },
        margin: {t: 50, l: 10, r: 10, b:10 },
   };
    const config = {
        responsive: true,
    };
    Plotly.newPlot("map", traces, layout, config);
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
        // obtain time range
        const val1 = parseInt(slider1.value);
        const val2 = parseInt(slider2.value);
        const startIdx = Math.min(val1, val2);
        const endIdx = Math.max(val1, val2);
        startInput.value = dates[startIdx];
        endInput.value = dates[endIdx];
        // get visible ccies in time series chart
        const ts_chart = document.getElementById("timeseries")
        let visibleReporters = null;
        if(ts_chart) {
            visibleReporters = ts_chart.data.filter(t => t.visible == true).map(t => t.name);
        }
        if(startIdx == -1 || endIdx == -1) return;
        const result = {};
        for (const reporter in timeseriesData) {
            if (reporter === "Date" || !(visibleReporters.includes(reporter))) continue;
            const arr = timeseriesData[reporter];
            const endVal = arr[endIdx];
            const startVal = arr[startIdx];
            if(startVal && startVal != 0.0)
                result[reporter] = Math.log(endVal / startVal);
        }
        plotMap(result);

        // track highlight
        const track = document.querySelector(".slider-track");
        const total = slider1.max;
        const startPct = (startIdx / total) * 100;
        const endPct = (endIdx / total) * 100;
        // paint dim/active color
        track.style.background = `linear-gradient(to right,
            #1e293b 0%,
            #1e293b ${startPct}%,
            #3a86ff ${startPct}%,
            #3a86ff ${endPct}%,
            #1e293b ${endPct}%,
            #1e293b 100%
            )`;
    };

    triggerWorldMap();
    slider1.addEventListener("input", triggerWorldMap);
    slider2.addEventListener("input", triggerWorldMap);
    document.getElementById("timeseries").on("plotly_restyle", triggerWorldMap);

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

    function changeTimeseriesRange() {
        // obtain time range
        const val1 = parseInt(slider1.value);
        const val2 = parseInt(slider2.value);
        const startIdx = Math.min(val1, val2);
        const endIdx = Math.max(val1, val2);
        const startDateTS = dates[startIdx];
        const endDateTS = dates[endIdx];
        const ts = document.getElementById("timeseries");
        const update = {
            "xaxis.range": [startDateTS, endDateTS]
        };
        Plotly.relayout(ts, update);
    }
    slider1.addEventListener("input", changeTimeseriesRange);
    slider2.addEventListener("input", changeTimeseriesRange);

});
