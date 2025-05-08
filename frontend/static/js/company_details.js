//frontend/static/js/company_details.js
function fetchCompanyDetails(ticker) {
    $.ajax({
        url: `/api/company/${ticker}`,
        method: 'GET',
        success: function (data) {
            console.log("[DEBUG] fetchCompanyDetails - Received data:", data);
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
                fetchLatestFinancialData(companyId);
                displayTopNews(data.company_news, data.industry_news);
            } else {
                console.error('Error fetching company details:', error);
            $('#companyName').text('Error Loading Company Details');
            $('#graphsAndFinancials').hide();
            }
        },
        error: function (error) {
            console.error('Error fetching company details:', error);
            $('#companyName').text('Error Loading Company Details');
            $('#topNewsSection').text('Error Loading News Section');
            $('#graphsAndFinancials').hide();
        }
    });
}

function fetchLatestFinancialData(companyId) {
    $.ajax({
        url: `/api/company/${companyId}/financial_data`, // Your existing API endpoint for latest financial data
        method: 'GET',
        success: function (data) {
            console.log("[DEBUG] fetchLatestFinancialData - Data received:", data);
            displayLatestFinancialData(data.financial_data);
        },
        error: function (error) {
            console.error('Error fetching latest financial data:', error);
            $('#financialData').html('<p class="text-danger">Error loading financial data.</p>');
        }
    });
}

function displayLatestFinancialData(financialData) {
    const financialDataDiv = $('#financialData'); // The div where you want to display this data
    financialDataDiv.empty();
    if (financialData && Object.keys(financialData).length > 0) {
        for (const key in financialData) {
            if (financialData.hasOwnProperty(key)) {
                financialDataDiv.append(`<p><strong>${key.replace(/_/g, ' ').toUpperCase()}:</strong> ${financialData[key]}</p>`);
            }
        }
    } else {
        financialDataDiv.append('<p>No recent financial data available.</p>');
    }
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
    if (financialData && Object.keys(financialData).length > 0 && financialData.date) {
        let tableHTML = '<table class="financial-table">';
        tableHTML += `<tr><th colspan="2" class="data-date">Data as of: ${new Date(financialData.date).toLocaleDateString()}</th></tr>`;

        const leftColumnData = {
            "Previous Close": financialData.close,
            "Open": financialData.open,
            "Bid": financialData.bid || 'N/A',
            "Ask": financialData.ask || 'N/A',
            "Day's Range": `${financialData.low || 'N/A'} - ${financialData.high || 'N/A'}`,
            "52 Week Range": `${financialData['52_week_low'] || 'N/A'} - ${financialData['52_week_high'] || 'N/A'}`,
            "Volume": financialData.volume ? financialData.volume.toLocaleString() : 'N/A',
            "Avg. Volume": financialData.average_volume ? financialData.average_volume.toLocaleString() : 'N/A'
        };

        const rightColumnData = {
            "Market Cap (intraday)": financialData.market_cap ? formatMarketCap(financialData.market_cap) : 'N/A',
            "Beta (5Y Monthly)": financialData.beta || 'N/A',
            "PE Ratio (TTM)": financialData.pe_ratio || 'N/A',
            "EPS (TTM)": financialData.eps || 'N/A',
            "Earnings Date": financialData.earnings_date || 'N/A',
            "Forward Dividend & Yield": financialData.forward_dividend ? `${financialData.forward_dividend} (${financialData.dividend_yield || 'N/A'})` : 'N/A',
            "Ex-Dividend Date": financialData.ex_dividend_date || 'N/A',
            "1y Target Est": financialData.target_mean_price || 'N/A'
        };

        const leftKeys = Object.keys(leftColumnData);
        const rightKeys = Object.keys(rightColumnData);
        const numRows = Math.max(leftKeys.length, rightKeys.length);

        for (let i = 0; i < numRows; i++) {
            tableHTML += '<tr>';
            if (i < leftKeys.length) {
                const key = leftKeys[i];
                tableHTML += `<td>${key}</td><td>${leftColumnData[key]}</td>`;
            } else {
                tableHTML += '<td></td><td></td>'; // Empty cells for alignment
            }

            if (i < rightKeys.length) {
                const key = rightKeys[i];
                tableHTML += `<td>${key}</td><td>${rightColumnData[key]}</td>`;
            } else {
                tableHTML += '<td></td><td></td>'; // Empty cells for alignment
            }
            tableHTML += '</tr>';
        }

        tableHTML += '</table>';
        financialDataDiv.html(tableHTML);

    } else {
        financialDataDiv.append('<p>No recent financial data available.</p>');
    }
}
function displayTopNews(companyNews, industryNews) {
    const topNewsList = $('#topNewsList');
    topNewsList.empty();
    console.log("[DEBUG] displayTopNews - companyNews:", companyNews);   // Debug: Log companyNews
    console.log("[DEBUG] displayTopNews - industryNews:", industryNews);   // Debug: Log industryNews

    let newsHTML = '';

    // Helper function to generate news item HTML
    function generateNewsItemHTML(news) {
        return `
            <div class="col-12 col-md-4 news-item">
                <div class="card h-100">
                    <div class="card-body">
                        <h4 class="news-headline card-title">
                            <a href="${news.url}" target="_blank" class="stretched-link">${news.title}</a>
                        </h4>
                        <p class="news-origin card-subtitle mb-2 text-muted">${news.source ? news.source.name : 'Unknown Source'}</p>
                        <p class="news-summary card-text three-line-clamp">${news.description || 'No summary available.'}</p>
                        <p class="news-date card-text"><small class="text-muted">${news.publishedAt ? new Date(news.publishedAt).toLocaleDateString() : ''}</small></p>
                    </div>
                </div>
            </div>
        `;
    }

    // Display Company News (Horizontal Scroll)
    if (companyNews && companyNews.length > 0) {
        newsHTML += '<div class="row"><div class="col-12"><h4 class="news-category">Company News</h4></div></div>';
        newsHTML += '<div class="row flex-nowrap overflow-auto">'; // Use flex-nowrap for horizontal scroll
        companyNews.forEach(news => {
            newsHTML += generateNewsItemHTML(news);
        });
        newsHTML += '</div>';
    }

    // Display Industry News (Rows of 3)
    if (industryNews && industryNews.length > 0) {
        newsHTML += '<div class="row mt-4"><div class="col-12"><h4 class="news-category">Industry News</h4></div></div>';
        newsHTML += '<div class="row">';
        for (let i = 0; i < industryNews.length; i++) {
            newsHTML += generateNewsItemHTML(industryNews[i]);
            if ((i + 1) % 3 === 0) {
                newsHTML += '</div><div class="row">';
            }
        }
        if (industryNews.length % 3 !== 0) {
            newsHTML += '</div>';
        }
        newsHTML += '</div>'; // Close the last row.
    }

    if ((!companyNews || companyNews.length === 0) && (!industryNews || industryNews.length === 0)) {
        newsHTML = '<div class="col-12">No recent news available.</div>';
    }

    topNewsList.html(newsHTML); // Use .html() to render the generated HTML
}

function formatMarketCap(marketCap) {
    if (marketCap >= 1e12) {
        return (marketCap / 1e12).toFixed(3) + 'T';
    } else if (marketCap >= 1e9) {
        return (marketCap / 1e9).toFixed(3) + 'B';
    } else if (marketCap >= 1e6) {
        return (marketCap / 1e6).toFixed(3) + 'M';
    }
    return marketCap.toLocaleString();
}
