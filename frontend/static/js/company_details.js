//frontend/static/js/company_details.js
function fetchCompanyDetails(ticker) {
    $.ajax({
        url: `/api/company/${ticker}`,
        method: 'GET',
        success: function (data) {
            if (data.company) {
                const company = data.company;
                console.log("[DEBUG] fetchCompanyDetails - Company data received:", company);
                companyId = company.id; // Store the company ID
                console.log("[DEBUG] fetchCompanyDetails - companyId set to:", companyId);
                $('#companyName').text(company.name + ' (' + company.ticker + ')');
                $('#companyExchange').text(company.exchange);
                $('#companyIndustry').text(company.industry);

                // Fetch initial graph data (e.g., weekly)
                console.log("[DEBUG] fetchCompanyDetails - Calling fetchGraphData with companyId:", companyId, "and timeframe: weekly");
                fetchGraphData(companyId, 'weekly');
                displayLatestFinancialData(data.financial_data && data.financial_data[0]);

            } else {
                console.error('Error fetching company details:', error);
            $('#companyName').text('Error Loading Company Details');
            $('#graphsAndFinancials').hide();
            }
        },
        error: function (error) {
            console.error('Error fetching company details:', error);
            $('#companyName').text('Error Loading Company Details');
            $('#graphsAndFinancials').hide();
        }
    });
}

$(document).ready(function () {
    console.log("jQuery is ready!");
    console.log("typeof window.$:", typeof window.$);
    console.log("typeof window.jQuery:", typeof window.jQuery);
    console.log("window.$.ajax:", window.$.ajax);
    console.log("window.jQuery.ajax:", window.jQuery.ajax);
    const companyTicker = getParameterByName('ticker');
    // let companyId; // REMOVE THIS LOCAL DECLARATION
    console.log("[DEBUG] $(document).ready - companyTicker:", companyTicker);
    if (companyTicker) {
        fetchCompanyDetails(companyTicker); // Moved inside $(document).ready()
    } else {
        $('#companyName').text('Company Not Found');
    }

});

function getParameterByName(name, url = window.location.href) {
    name = name.replace(/[\[\]]/g, '\\$&');
    var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, ' '));
}


$('#timeframeSelect').change(function () {
    const selectedTimeframe = $(this).val();
    console.log("[DEBUG] timeframeSelect.change - selectedTimeframe:", selectedTimeframe, "current companyId:", companyId);
    if (companyId) {
        fetchGraphData(companyId, selectedTimeframe);
    } else {
        console.warn("[DEBUG] timeframeSelect.change - companyId is undefined, cannot fetch graph data.");
    }
});

let charts = {};
let volumeCharts = {};

function fetchGraphData(companyId, timeframe) {
    console.log("[DEBUG] fetchGraphData - companyId:", companyId, "timeframe:", timeframe);
    $.ajax({
        url: `/api/graph/company/${companyId}/${timeframe}`,
        method: 'GET',
        success: function (data) {
            renderCharts(data, timeframe);
        },
        error: function (error) {
            console.error(`[ERROR] fetchGraphData - Error fetching ${timeframe} graph data:`, error);
            // Optionally display an error message in the UI
        }
    });
}

function renderCharts(data, timeframe) { // Ensure timeframe is received here
    console.log("[DEBUG] renderCharts - Received data for timeframe:", timeframe, "Data:", data);
    const labels = data.map(item => item.date);
    const closePrices = data.map(item => item.close);
    const volumes = data.map(item => item.volume);
    const stockCanvasId = timeframe + 'Chart';
    const stockCtx = document.getElementById(stockCanvasId).getContext('2d');

    if (charts[timeframe]) {
        charts[timeframe].destroy();
    }
    charts[timeframe] = new Chart(stockCtx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Close Price',
                data: closePrices,
                borderColor: 'blue',
                fill: false
            }]
        },
        options: {}
    });

    const volumeCanvasId = timeframe + 'VolumeChart'; // Make sure you have corresponding canvas IDs
    const volumeCtx = document.getElementById(volumeCanvasId) ? document.getElementById(volumeCanvasId).getContext('2d') : null;
    if (volumeCtx) {
        if (volumeCharts[timeframe]) {
            volumeCharts[timeframe].destroy();
        }
        volumeCharts[timeframe] = new Chart(volumeCtx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Volume',
                    data: volumes,
                    backgroundColor: 'green'
                }]
            },
            options: {}
        });
    }
}

function displayLatestFinancialData(financialData) {
    const financialDataDiv = $('#financialData');
    financialDataDiv.empty();
    if (financialData) {
        financialDataDiv.append(`<p><strong>Date:</strong> ${financialData.date}</p>`);
        financialDataDiv.append(`<p><strong>Open:</strong> ${financialData.open}</p>`);
        financialDataDiv.append(`<p><strong>Close:</strong> ${financialData.close}</p>`);
        // Add other relevant financial data points
    } else {
        financialDataDiv.append('<p>No recent financial data available.</p>');
    }
}