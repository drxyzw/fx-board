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

function plotTimeSeries() {
    const currencies = Object.keys(timeseriesData).filter(k => k != "Date");
    const initial_ccies = CONFIG.initial_currencies;
    if(!ts_scale) ts_scale = Object.fromEntries(currencies.map((c) => [c, 1.0]));

    const traces = currencies.map((c, i) => ({
        x: dates,
        y: timeseriesData[c].map((v) => v * ts_scale[c]),
        name: c,
        mode: "lines",
        visible: initial_ccies.includes(c) ? true : "legendonly",
        line: {
            width: 1.2,
            color: `hsl(${(i * 137.5) % 360}, 70%, 60%)`, // HSL color scheme
        },
        hovertemplate: '<b>%{fullData.name}</b><br>' +
                        '%{x}<br>' +
                        '%{y}<br><extra></extra>',
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
            rangeslider: {
                visible: true,
            },
        },
        yaxis: {
            side: "right",
            gridcolor: "#1e293b",
            tickfont: { size: 11, color: "#94a3b8" },
            tickpadding: 15,
            automargin: false,
            autorange: true,
            fixedrange: false,
        },
        legend: {
            orientation: "v",
            x: 1.1,
            y: 1,
            font: { size: 10, color: "#94a3b8" },
            bgcolor: "rgba(0,0,0,0)",
        },
    };
    const config = {
        responsive: true,
    };
    Plotly.newPlot("timeseries", traces, layout, config);
    const chart = document.getElementById("timeseries")
    document.getElementById("startDate").value = chart._fullLayout.xaxis.range[0].substring(0, 10);
    document.getElementById("endDate").value = chart._fullLayout.xaxis.range[1].substring(0, 10);
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
    const customdata = partners.map((p, i) => [ret[i], contrib[i]]);
    const group = Array(partners.length).fill(null);
    const maxAbsContrib = Math.max(Math.abs(Math.max(contrib)), Math.abs(Math.min(contrib)));
    const texttemplates = partners.map((v, i) => {
        return i == 0 ? null :
            // '<span style="font-size: 40px;">' +
            '<b>%{label}</b><br>' +
            'Return: %{customdata[0]:.0%}<br>' +
            'Weight: %{value:.0%}<br>' +
            'Contribution: %{customdata[1]:.0%}'
            // 'Contribution: %{customdata[1]:.0%}</span>'
    });
    const hovertemplates = partners.map((v, i) => {
        return i == 0 ? null :
            '<b>%{label}</b><br>' +
            'Return: %{customdata[0]:.2%}<br>' +
            'Weight: %{value:.2%}<br>' +
            'Contribution: %{customdata[1]:.2%}<extra></extra>'
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
        customdata: customdata,
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
        // textinfo: "label",
        texttemplate: texttemplates,
        textfont: {
            size: 1,
        },
        insidetextfont: {
            size: 40,
        },
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
document.addEventListener("DOMContentLoaded", async() => {
    await loadTimeSeries();
    // line chart
    plotTimeSeries();
    
    // world map
    const ts_chart = document.getElementById("timeseries");
    const startInput = document.getElementById("startDate");
    const endInput = document.getElementById("endDate");
    const triggerWorldMap = (event) => {
        // obtain time range
        const startDate = ts_chart._fullLayout.xaxis.range[0];
        const endDate = ts_chart._fullLayout.xaxis.range[1];
        const startIdx = dates.indexOf(startDate);
        const endIdx = dates.indexOf(endDate);
        // get visible ccies in time series chart
        let visibleReporters = ts_chart.data.filter(t => t.visible == true).map(t => t.name);
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
    };

    triggerWorldMap();

    // heatmap
    async function triggerHeatmap(event) {
        const eventForType = event.event ?? event;
        const startDate = ts_chart._fullLayout.xaxis.range[0].substring(0, 10);
        const endDate = ts_chart._fullLayout.xaxis.range[1].substring(0, 10);
        if(!startDate || !endDate) return;
        if(eventForType.type == "mousemove") { // hovering a line chart
            heatmap_reporter = event.points[0].data.name;
        }
        if(heatmap_reporter) {
            const reporterData = await loadReporter(heatmap_reporter);
            const startIdx = getDateIndex(startDate, reporterData.Date);
            const endIdx = getDateIndex(endDate, reporterData.Date);
            if(startIdx == -1 || endIdx == -1) return;

            const values = endIdx > startIdx ? computeRangeValues(reporterData, startIdx, endIdx) : null;
            plotHeatmap(heatmap_reporter, values);
        }
    }
    ts_chart.on("plotly_hover", triggerHeatmap);
    ts_chart.on("plotly_relayout", triggerHeatmap);
    startInput.addEventListener("input", triggerHeatmap);
    endInput.addEventListener("input", triggerHeatmap);

    function changeTimeseriesRange() {
        const startDateLimit = new Date(ts_chart._fullLayout.xaxis.rangeslider.range[0]);
        const endDateLimit = new Date(ts_chart._fullLayout.xaxis.rangeslider.range[1]);
        if(typeof(startInput.value) == "string" && typeof(endInput.value) == "string") {
            const startDate = new Date(startInput.value);
            const endDate = new Date(endInput.value);
            if(startDateLimit <= startDate && startDate <= endDate && endDate <= endDateLimit) {
                Plotly.relayout(ts_chart, {"xaxis.range": [startInput.value, endInput.value]});
            }
        }
    }
    startInput.addEventListener("input", changeTimeseriesRange);
    endInput.addEventListener("input", changeTimeseriesRange);

    function changeTimeseriesRangeScale(eventData) {
        if(!eventData["xaxis.range"] && !eventData?.srcElement?.name && (eventData?.srcElement?.name != "scaleChoice")) return;
        // obtain time range
        const startDate = ts_chart._fullLayout.xaxis.range[0].substring(0, 10);
        const endDate = ts_chart._fullLayout.xaxis.range[1].substring(0, 10);
        startInput.value = startDate
        endInput.value = endDate
        const startIdx = dates.indexOf(startDate);
        const endIdx = dates.indexOf(endDate);
        if(document.getElementById("scaleStartDate").checked) {
            const traceIndices= [...ts_chart.data.keys()];
            const newTimeseiesData = ts_chart.data.map((v) => {
                const ccy = v.name;
                ts_scale[ccy] = 100 / timeseriesData[ccy][startIdx];
                return timeseriesData[ccy].map((r, i) =>
                        (startIdx <= i && i <= endIdx) ?
                        (r * ts_scale[ccy]) : null
                );
            });
            Plotly.restyle(ts_chart, {y: newTimeseiesData}, traceIndices);
        } else {
            const traceIndices= [...ts_chart.data.keys()];
            const newTimeseiesData = ts_chart.data.map((v) => {
                const ccy = v.name;
                ts_scale[ccy] = 1.0;
                return timeseriesData[ccy].map((r, i) =>
                        (startIdx <= i && i <= endIdx) ?
                        r : null
                );
            });
            Plotly.restyle(ts_chart, {y: newTimeseiesData}, traceIndices);
        }
    }
    ts_chart.on("plotly_relayout", changeTimeseriesRangeScale);
    document.getElementById("scaleDefault").addEventListener("change", changeTimeseriesRangeScale);
    document.getElementById("scaleStartDate").addEventListener("change", changeTimeseriesRangeScale);
});
