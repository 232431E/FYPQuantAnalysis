//frontend/static/js/company_details.js
let companyId = null; 
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
                if (companyId) {
                    updateLLMReport(companyId);
                } else {
                    console.error("[ERROR] Company ID not found. Cannot fetch LLM report.");
                }
                console.log("[DEBUG - Frontend] fetchCompanyDetails - Company details, graph, financials, news, sentiment, and report initiated.");
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

// fetchSentimentAnalysis might not be relevant as replaced with updateLLMReport
function fetchSentimentAnalysis(companyId) {
    console.log(`[DEBUG - Frontend] fetchSentimentAnalysis called for companyId: ${companyId}`);
    $.ajax({
        url: `/api/llm/sentiment/${companyId}`, // This endpoint is returning {"report": { ... }} as per your logs
        method: 'GET',
        success: function (data) {
            console.log("[DEBUG] fetchSentimentAnalysis - Received data:", data);

            // FIX HERE: Access data.report first, then its nested properties
            if (data && data.report) { // Check if 'report' key exists
                const sentiment = data.report; // Assign the 'report' object to 'sentiment' for consistency
                console.log("[DEBUG - Frontend] fetchSentimentAnalysis - Sentiment Data:", sentiment);

                // Update News Summary Section
                // Assuming you have an element with ID 'newsSummarySection'
                $('#newsSummarySection').html(`
                    <p><strong>Overall News Summary:</strong> ${sentiment.overall_news_summary || 'News summary unavailable.'}</p>
                `);

                // Update the brief sentiment display (e.g., "Mixed")
                $('#newsSentiment').text(sentiment.brief_overall_sentiment || 'Sentiment analysis unavailable.')
                    .removeClass('sentiment-positive sentiment-negative sentiment-neutral')
                    .addClass(getSentimentClass(sentiment.brief_overall_sentiment));

                // Update the sentiment details section
                $('#sentimentDetails').html(`
                    <p><strong>Market Outlook:</strong> ${sentiment.market_outlook || 'Market outlook unavailable.'}</p>
                    <p><strong>Detailed Explanation:</strong> ${sentiment.detailed_explanation || 'Detailed explanation unavailable.'}</p>
                `);
                console.log("[DEBUG - Frontend] fetchSentimentAnalysis - Sentiment displayed.");
            } else {
                console.warn("[DEBUG - Frontend] fetchSentimentAnalysis - Sentiment data is missing or empty or incorrect structure.");
                $('#newsSummarySection').html('<p>News summary unavailable.</p>');
                $('#newsSentiment').text('Sentiment analysis unavailable.');
                $('#sentimentDetails').html('<p>Sentiment details unavailable.</p>');
            }
        },
        error: function (error) {
            console.error("[ERROR - Frontend] fetchSentimentAnalysis - Error:", error);
            $('#newsSummarySection').html('<p>Error loading news summary.</p>');
            $('#newsSentiment').text('Error loading sentiment analysis.');
            $('#sentimentDetails').html('<p>Error loading sentiment details.</p>');
        }
    });
}

function getSentimentClass(sentiment) {
    if (sentiment && typeof sentiment === 'string') {
        const lowerSentiment = sentiment.toLowerCase();
        if (lowerSentiment.includes('positive') || lowerSentiment.includes('optimistic')) {
            return 'sentiment-positive';
        } else if (lowerSentiment.includes('negative') || lowerSentiment.includes('bearish')) { // Added 'bearish'
            return 'sentiment-negative';
        } else if (lowerSentiment.includes('neutral') || lowerSentiment.includes('mixed') || lowerSentiment.includes('cautious')) {
            return 'sentiment-neutral';
        }
    }
    return ''; // Default or unknown sentiment
}

function updateLLMReport(companyId) {
    console.log(`[DEBUG - Frontend] updateLLMReport called for companyId: ${companyId}`);
    $.ajax({
        url: `/api/llm/sentiment/${companyId}`, 
        method: 'GET',
        dataType: 'json', 
        success: function (data) {
            console.log("[DEBUG - Frontend] updateLLMReport - Received raw data from backend:", data);
            const report = data.report; // Access the nested 'report' object
            console.log("[DEBUG - Frontend] updateLLMReport - Parsed report data (after accessing 'report' key):", report);
            if (report && report.overall_news_summary && report.brief_overall_sentiment && 
                report.reasons_for_sentiment && report.market_outlook && 
                report.detailed_explanation && report.key_offerings !== undefined && // Check for existence for key_offerings
                report.financial_dates !== undefined) { // Check for existence for financial_dates
                $('#newsBrief').html(`<p><strong>Overall News Summary:</strong> ${report.overall_news_summary}</p>`);
                console.log("[DEBUG - Frontend] News Summary updated.");
                $('#briefOverallSentimentText').html(report.brief_overall_sentiment) // Use .html() as it might contain HTML for score explanation
                    .removeClass('sentiment-positive sentiment-negative sentiment-neutral') 
                    .addClass(getSentimentClass(report.brief_overall_sentiment)); 
                console.log("[DEBUG - Frontend] Brief Overall Sentiment updated.");
                $('#reasonsForSentimentContent').html(`<div>${report.reasons_for_sentiment}</div>`);
                console.log("[DEBUG - Frontend] Reasons for Sentiment updated.");
                $('#marketOutlookContent').html(`<strong>Market Outlook:</strong> ${report.market_outlook}`) // Use .html()
                    .removeClass('sentiment-positive sentiment-negative sentiment-neutral') 
                    .addClass(getSentimentClass(report.market_outlook));
                console.log("[DEBUG - Frontend] Market Outlook updated.");
                $('#detailedExplanationContent').html(`<div>${report.detailed_explanation}</div>`);
                console.log("[DEBUG - Frontend] Detailed Explanation (Market Outlook) updated.");
                const keyOfferingsList = $('#keyOfferingsList');
                keyOfferingsList.empty(); 
                if (Array.isArray(report.key_offerings) && report.key_offerings.length > 0) {
                    report.key_offerings.forEach(item => {
                        keyOfferingsList.append(`<li>${item}</li>`);
                    });
                } else {
                    keyOfferingsList.append(`<li>No key products/services/subsidiaries identified.</li>`);
                }
                console.log("[DEBUG - Frontend] Key Offerings updated.");
                const financialDatesList = $('#financialDatesList');
                financialDatesList.empty(); // Clear previous content
                if (Array.isArray(report.financial_dates) && report.financial_dates.length > 0) {
                    $('#financialDatesContent').html('<p>Here are some key financial events and their potential impact:</p>'); // Add introductory text
                    report.financial_dates.forEach(event => {
                        financialDatesList.append(`
                            <li>
                                <strong>Date:</strong> ${event.date || 'N/A'}<br>
                                <strong>Event:</strong> ${event.event || 'N/A'}<br>
                                <strong>Impact:</strong> ${event.impact || 'No impact explanation.'}
                            </li>
                        `);
                    });
                } else {
                    $('#financialDatesContent').html('<p>No significant upcoming or recent financial events identified.</p>');
                }
                console.log("[DEBUG - Frontend] Financial Dates updated.");

                console.log("[DEBUG - Frontend] All sentiment report fields updated successfully.");

            } else {
                console.warn("[DEBUG - Frontend] updateLLMReport - Essential report data is missing or incomplete. Data received:", data, "Parsed report object:", report);
                $('#newsBrief').html('<p>News summary unavailable.</p>');
                $('#briefOverallSentimentText').html('Sentiment analysis unavailable.');
                $('#reasonsForSentimentContent').html('<p>Reasons for sentiment unavailable.</p>');
                $('#marketOutlookContent').html('<p>Market outlook unavailable.</p>');
                $('#detailedExplanationContent').html('<p>Detailed explanation for market outlook unavailable.</p>');
                $('#keyOfferingsList').html('<li>Key offerings unavailable.</li>');
                $('#financialDatesContent').html('<p>Financial event details unavailable.</p>');
                $('#financialDatesList').empty(); // Ensure list is empty too
            }
        },
        error: function (xhr, status, error) {
            console.error("[ERROR - Frontend] updateLLMReport - AJAX Error:", status, error, xhr);
            $('#newsBrief').html('<p>Error loading news summary.</p>');
            $('#briefOverallSentimentText').html('Error loading sentiment analysis.');
            $('#reasonsForSentimentContent').html('<p>Error loading reasons for sentiment.</p>');
            $('#marketOutlookContent').html('<p>Error loading market outlook.</p>');
            $('#detailedExplanationContent').html('<p>Error loading detailed explanation for market outlook.</p>');
            $('#keyOfferingsList').html('<li>Error loading key offerings.</li>');
            $('#financialDatesContent').html('<p>Error loading financial event details.</p>');
            $('#financialDatesList').empty(); // Ensure list is empty too
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
function formatMarketCap(marketCap) {
    if (marketCap >= 1e12) {
        return (marketCap / 1e12).toFixed(3) + 'T';
    } else if (marketCap >= 1e9) {
        return (marketCap / 1e9).toFixed(3) + 'B';
    } else if (marketCap >= 1e6) {
        return (marketCap / 1e6).toFixed(3) + 'M';
    } else if (marketCap !== null && marketCap !== undefined) {
        return marketCap.toLocaleString();
    }
    return 'N/A';
}

function formatNumber(number) {
    if (number >= 1e9) {
        return (number / 1e9).toFixed(2) + 'B';
    } else if (number >= 1e6) {
        return (number / 1e6).toFixed(2) + 'M';
    } else if (number >= 1e3) {
        return (number / 1e3).toFixed(2) + 'K';
    } else if (number !== null && number !== undefined) {
        return number.toLocaleString();
    }
    return 'N/A';
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
            //"Bid": financialData.bid || 'N/A',
            //"Ask": financialData.ask || 'N/A',
            "High": financialData.high || 'N/A',
            "Low": financialData.low || 'N/A',
            "Day's Range": `${financialData.low || 'N/A'} - ${financialData.high || 'N/A'}`,
            "52 Week Range": `${financialData.fifty_two_week_low || 'N/A'} - ${financialData.fifty_two_week_high || 'N/A'}`,
            "Revenue": financialData.revenue ? formatNumber(financialData.revenue) : 'N/A', // Added Revenue
            "Cash Flow": financialData.cash_flow ? formatNumber(financialData.cash_flow) : 'N/A', // Added Cash Flow
            "Volume": financialData.volume ? financialData.volume.toLocaleString() : 'N/A',
            "Avg. Volume": financialData.average_volume ? financialData.average_volume.toLocaleString() : 'N/A'
        };

        const rightColumnData = {
            "Market Cap (intraday)": financialData.market_cap ? formatMarketCap(financialData.market_cap) : 'N/A',
            "Beta (5Y Monthly)": financialData.beta || 'N/A',
            "PE Ratio (TTM)": financialData.pe_ratio !== null && financialData.pe_ratio !== undefined ? parseFloat(financialData.pe_ratio).toFixed(4) : 'N/A', // Add PE Ratio
            "EPS (TTM)": financialData.eps || 'N/A',
            "ROI": financialData.roi ? (financialData.roi * 100).toFixed(2) + '%' : 'N/A', // Display as percentage
            "Debt to Equity": financialData.debt_to_equity || 'N/A',
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
        // Ensure news.url is a string and not null/undefined
        const newsUrl = news.url ? news.url : '#'; 
        // Ensure news.source is an object before accessing .name
        const sourceName = news.source && news.source.name ? news.source.name : 'Unknown Source';
        // Format date safely
        const publishedDate = news.publishedAt ? new Date(news.publishedAt).toLocaleDateString() : '';
        return `
            <div class="col-12 col-md-4 news-item">
                <div class="card h-100">
                    <div class="card-body">
                        <h4 class="news-headline card-title">
                            <a href="${newsUrl}" target="_blank" class="stretched-link">${news.title}</a>
                        </h4>
                        <p class="news-origin card-subtitle mb-2 text-muted">${sourceName}</p>
                        <p class="news-summary card-text three-line-clamp">${news.description || 'No summary available.'}</p>
                        <p class="news-date card-text"><small class="text-muted">${publishedDate}</small></p>
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
    } else {
        newsHTML += '<div class="row"><div class="col-12"><h4 class="news-category">Company News</h4><p>No recent news available for this company.</p></div></div>';
    }
    // Display Industry News (Rows of 3)
    const companyIndustryElement = $('#companyIndustry'); // Assuming this ID holds the industry name
    const currentIndustryName = companyIndustryElement.length > 0 ? companyIndustryElement.text() : 'the specified industry';
    newsHTML += '<div class="row mt-4"><div class="col-12"><h4 class="news-category">Industry News</h4></div></div>';
    if (industryNews && industryNews.length > 0) {
        newsHTML += '<div class="row">';
        for (let i = 0; i < industryNews.length; i++) {
            newsHTML += generateNewsItemHTML(industryNews[i]);
            if ((i + 1) % 3 === 0) {
                newsHTML += '</div><div class="row">';
            }
        }
        // Close the last row div if it wasn't closed by the loop
        if (industryNews.length % 3 !== 0) {
            newsHTML += '</div>';
        }
    } else {
        newsHTML += `<div class="row"><div class="col-12"><p>No recent news available for ${currentIndustryName}.</p></div></div>`;
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
