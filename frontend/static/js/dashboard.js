const companySearchInput = document.getElementById('companySearch');
const refreshTableButton = document.getElementById('refreshTable');
const industryFilterDropdown = document.getElementById('industryFilter');
const pageSizeSelect = document.getElementById('pageSizeSelect');
const paginationContainer = document.getElementById('paginationContainer');
const tickerInput = document.getElementById('tickerInput');
const ingestionStatus = document.getElementById('ingestionStatus');

let allFinancialData = [];
let industries = new Set();
let currentPage = 1;
let rowsPerPage = parseInt(pageSizeSelect.value, 10);

async function fetchAndStoreData() {
    console.log("fetchAndStoreData function called!");
    const ticker = tickerInput.value.toUpperCase();
    ingestionStatus.textContent = `Ingesting data for ${ticker}...`;

    if (ticker) {
        try {
            const response = await fetch(`/api/ingest/${ticker}`, {
                method: 'POST',
            });
            const result = await response.json();

            if (response.ok) {
                ingestionStatus.textContent = result.message || `Data ingestion successful for ${ticker}`;
                displayAllFinancialData();
            } else {
                ingestionStatus.textContent = result.error || `Failed to ingest data for ${ticker}`;
            }
        } catch (error) {
            ingestionStatus.textContent = `Error: ${error.message}`;
        }
    } else {
        ingestionStatus.textContent = 'Please enter a ticker symbol.';
    }
}

async function displayAllFinancialData() {
    const latestDataDiv = document.getElementById('latestDataDisplay');
    latestDataDiv.textContent = 'Fetching all financial data...';
    try {
        const response = await fetch('/api/dashboard/latest');
        const data = await response.json();
        allFinancialData = data;
        currentPage = 1;
        displayData(allFinancialData, currentPage);
        populateIndustryFilter(allFinancialData);
    } catch (error) {
        latestDataDiv.textContent = `Error fetching all financial data: ${error.message}`;
    }
}

function populateIndustryFilter(data) {
    industries.clear();
    industryFilterDropdown.innerHTML = '<option value="">All Industries</option>';
    for (const item of data) {
        industries.add(item.industry);
    }
    industries.forEach(industry => {
        if (industry) {
            const option = document.createElement('option');
            option.value = industry;
            option.textContent = industry;
            industryFilterDropdown.appendChild(option);
        }
    });
}

function displayData(data, page) {
    const latestDataDiv = document.getElementById('latestDataDisplay');
    const paginationWrapper = document.querySelector('.pagination');
    if (data && data.length > 0) {
        data.sort((a, b) => new Date(b.date) - new Date(a.date));

        const startIndex = (page - 1) * rowsPerPage;
        const endIndex = startIndex + rowsPerPage;
        const pagedData = data.slice(startIndex, endIndex);

        let html = '<table class="table table-striped">';
        html += '<thead><tr><th>Company</th><th>Date</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Volume</th></tr></thead><tbody>';
        for (const item of pagedData) {
            html += `<tr><td><a href="/company/${item.ticker_symbol}">${item.ticker_symbol}</a></td>`;
            html += `<td>${new Date(item.date).toLocaleDateString()}</td>`;
            html += `<td>${item.open}</td>`;
            html += `<td>${item.high}</td>`;
            html += `<td>${item.low}</td>`;
            html += `<td>${item.close}</td>`;
            html += `<td>${item.volume}</td></tr>`;
        }
        html += '</tbody></table>';
        latestDataDiv.innerHTML = html;

        const totalPages = Math.ceil(data.length / rowsPerPage);
        let paginationHtml = '';
        if (totalPages > 1) {
            paginationHtml += `<li class="page-item ${page === 1 ? 'disabled' : ''}">
                                    <a class="page-link" href="#" aria-label="Previous" data-page="${page - 1}">
                                        <span aria-hidden="true">&laquo;</span>
                                        <span class="sr-only">Previous</span>
                                    </a>
                                </li>`;
            for (let i = 1; i <= totalPages; i++) {
                paginationHtml += `<li class="page-item ${page === i ? 'active' : ''}">
                                        <a class="page-link" href="#" data-page="${i}">${i}</a>
                                    </li>`;
            }
            paginationHtml += `<li class="page-item ${page === totalPages ? 'disabled' : ''}">
                                    <a class="page-link" href="#" aria-label="Next" data-page="${page + 1}">
                                        <span aria-hidden="true">&raquo;</span>
                                        <span class="sr-only">Next</span>
                                    </a>
                                </li>`;
        }
        paginationWrapper.innerHTML = paginationHtml;
    } else {
        latestDataDiv.textContent = 'No financial data available.';
        paginationWrapper.innerHTML = '';
    }
}

companySearchInput.addEventListener('input', () => {
    const searchTerm = companySearchInput.value.toLowerCase();
    const filteredData = allFinancialData.filter(item =>
        item.ticker_symbol.toLowerCase().includes(searchTerm) ||
        (item.company_name && item.company_name.toLowerCase().includes(searchTerm))
    );
    currentPage = 1;
    displayData(filteredData, currentPage);
});

refreshTableButton.addEventListener('click', () => {
    displayAllFinancialData();
});

industryFilterDropdown.addEventListener('change', () => {
    const selectedIndustry = industryFilterDropdown.value;
    if (selectedIndustry) {
        const filteredData = allFinancialData.filter(item => item.industry === selectedIndustry);
        currentPage = 1;
        displayData(filteredData, currentPage);
    } else {
        currentPage = 1;
        displayData(allFinancialData, currentPage);
    }
});

pageSizeSelect.addEventListener('change', () => {
    rowsPerPage = parseInt(pageSizeSelect.value, 10);
    currentPage = 1;
    displayData(allFinancialData, currentPage);
});

paginationContainer.addEventListener('click', (event) => {
    const target = event.target;
    if (target.classList.contains('page-link') && !target.parentElement.classList.contains('disabled')) {
        event.preventDefault();
        const page = parseInt(target.dataset.page, 10);
        if (!isNaN(page)) {
            currentPage = page;
            displayData(allFinancialData, currentPage);
        }
    }
});

displayAllFinancialData();
