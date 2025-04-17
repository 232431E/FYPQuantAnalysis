// frontend/static/js/company_details.js

async function loadCompanyInfo() {
    const ticker = window.location.pathname.split('/').pop(); // Get ticker from the URL (e.g., /company/AAPL)
    if (ticker) {
        try {
            const response = await fetch(`/api/company/${ticker}`);
            if (response.ok) {
                const data = await response.json();
                document.getElementById('companyName').textContent = `${data.company.name} (${data.company.ticker})`;
                document.getElementById('companyExchange').textContent = data.company.exchange;
                document.getElementById('companyIndustry').textContent = data.company.industry;

                // Update Key Financial Data
                if (data.financial_data && data.financial_data.length > 0) {
                    const latest = data.financial_data[data.financial_data.length - 1];
                    document.getElementById('revenue').textContent = latest.revenue ? latest.revenue.toFixed(2) : 'N/A';
                    document.getElementById('eps').textContent = latest.eps ? latest.eps.toFixed(2) : 'N/A';
                    // Update more financial metrics as needed
                }

                // Update Trend Predictions
                if (data.trend_predictions) {
                    document.getElementById('revenueTrend').textContent = data.trend_predictions.revenue_growth || 'N/A';
                    document.getElementById('epsTrend').textContent = data.trend_predictions.profit_margin || 'N/A'; // Adjust key based on your prediction output
                }

                // Update News Analysis
                if (data.latest_news_analysis) {
                    document.getElementById('newsBrief').textContent = data.latest_news_analysis.brief || 'Loading...';
                    const sentimentSpan = document.getElementById('newsSentiment');
                    sentimentSpan.textContent = data.latest_news_analysis.sentiment || 'N/A';
                    sentimentSpan.className = `sentiment-${(data.latest_news_analysis.sentiment || '').toLowerCase()}`;
                }

                // Update Top News
                const topNewsList = document.getElementById('topNewsList');
                topNewsList.innerHTML = '';
                if (data.top_news && data.top_news.length > 0) {
                    data.top_news.forEach(newsItem => {
                        const li = document.createElement('li');
                        li.className = 'news-item';
                        li.textContent = newsItem;
                        topNewsList.appendChild(li);
                    });
                } else {
                    topNewsList.innerHTML = '<li>No top news available.</li>';
                }

                // Update Similar Companies
                const similarCompaniesDiv = document.getElementById('similarCompaniesList');
                similarCompaniesDiv.innerHTML = '';
                if (data.similar_companies && data.similar_companies.length > 0) {
                    data.similar_companies.forEach(company => {
                        const link = document.createElement('a');
                        link.href = `/company/${company}`; // Assuming you want to link to their page
                        link.className = 'similar-company-link';
                        link.textContent = company;
                        similarCompaniesDiv.appendChild(link);
                    });
                } else {
                    similarCompaniesDiv.innerHTML = 'No similar companies found.';
                }

                // TODO: Implement graph rendering using a charting library with data.financial_data
                console.log("Financial Data for Graphs:", data.financial_data);

            } else {
                const errorData = await response.json();
                document.querySelector('.content').innerHTML = `<div class="alert alert-danger" role="alert">Error loading company data: ${errorData.error || response.statusText}</div>`;
            }
        } catch (error) {
            document.querySelector('.content').innerHTML = `<div class="alert alert-danger" role="alert">An unexpected error occurred: ${error}</div>`;
        }
    } else {
        document.querySelector('.content').innerHTML = `<div class="alert alert-warning" role="alert">No company ticker provided in the URL.</div>`;
    }
}

window.onload = loadCompanyInfo;