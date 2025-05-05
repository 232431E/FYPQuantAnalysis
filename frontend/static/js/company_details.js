function fetchCompanyDetails(ticker) {
    $.ajax({
        url: `/api/company/${ticker}`,
        method: 'GET',
        success: function (data) {
            if (data.company) {
                const company = data.company;
                companyId = company.id; // Store the company ID
                $('#companyName').text(company.name + ' (' + company.ticker + ')');
                $('#companyExchange').text(company.exchange);
                $('#companyIndustry').text(company.industry);

                // Fetch initial graph data (e.g., weekly)
                fetchGraphData(companyId, 'weekly');
                displayLatestFinancialData(data.financial_data && data.financial_data[0]);

            } else {
                $('#companyName').text('Company Not Found');
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
    let companyId;
    console.log(companyTicker);
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
    if (companyId) {
        fetchGraphData(companyId, selectedTimeframe);
    }
});

let stockChart;
let volumeChart;

function fetchGraphData(companyId, timeframe) {
    $.ajax({
        url: `/api/graph/company/${companyId}/${timeframe}`,
        method: 'GET',
        success: function (data) {
            renderCharts(data);
        },
        error: function (error) {
            console.error('Error fetching graph data:', error);
            // Optionally display an error message in the UI
        }
    });
}

function renderCharts(data) {
    const labels = data.map(item => item.date);
    const closePrices = data.map(item => item.close);
    const volumes = data.map(item => item.volume);

    if (stockChart) {
        stockChart.destroy();
    }
    const stockCtx = document.getElementById('stockChart').getContext('2d');
    stockChart = new Chart(stockCtx, {
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

    if (volumeChart) {
        volumeChart.destroy();
    }
    const volumeCtx = document.getElementById('volumeChart').getContext('2d');
    volumeChart = new Chart(volumeCtx, {
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