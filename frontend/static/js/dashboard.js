const companySearchInput = document.getElementById('companySearch');
const refreshTableButton = document.getElementById('refreshTable');
const industryFilterDropdown = document.getElementById('industryFilter');
const pageSizeSelect = document.getElementById('pageSizeSelect');
const paginationContainer = document.getElementById('paginationContainer');
const tickerInput = document.getElementById('tickerInput');
const ingestionStatus = document.getElementById('ingestionStatus');
const currentPageInput = document.getElementById('currentPageInput');
const prevPageButton = document.getElementById('prevPage');
const nextPageButton = document.getElementById('nextPage');
const totalPagesDisplay = document.getElementById('totalPagesDisplay');
const dateFromInput = document.getElementById('dateFrom');
const dateToInput = document.getElementById('dateTo');
const applyFiltersButton = document.getElementById('applyFiltersButton');
const filtersToggle = document.getElementById('filtersToggle');
const filtersContainer = document.getElementById('filtersContainer');

let allFinancialData = [];
let filteredFinancialData = []; // To hold data after search and filters
let industries = new Set();
let currentPage = 1;
let rowsPerPage = parseInt(pageSizeSelect.value, 10);
let flatpickrFrom, flatpickrTo;

document.addEventListener('DOMContentLoaded', () => {
    flatpickrFrom = flatpickr(dateFromInput, { dateFormat: "Y-m-d" });
    flatpickrTo = flatpickr(dateToInput, { dateFormat: "Y-m-d" });
    $(industryFilterDropdown).select2({
        placeholder: "Select Industries"
    });

    filtersToggle.addEventListener('click', () => {
        if (filtersContainer.style.display === 'none' || filtersContainer.style.display === '') {
            filtersContainer.style.display = 'flex'; // Use flex for display
            filtersContainer.style.maxHeight = filtersContainer.scrollHeight + 'px';
        } else {
            filtersContainer.style.maxHeight = '0';
            setTimeout(() => {
                if (filtersContainer.style.maxHeight === '0px') {
                    filtersContainer.style.display = 'none';
                }
            }, 300);
        }
    });

    applyFiltersButton.addEventListener('click', applyFilters);
});

async function fetchAndStoreData() {
    console.log("fetchAndStoreData function called!");
    const ticker = tickerInput.value.toUpperCase();
    ingestionStatus.textContent = `Ingesting data for ${ticker}...`;

    if (ticker) {
        try {
            const response = await fetch(`/api/data/ingest/${ticker}`, {
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
        const response = await fetch('/api/data/dashboard/latest');
        const data = await response.json();
        console.log("Data received from backend:", data);
        allFinancialData = data;
        populateIndustryFilter(allFinancialData);
        applyFilters(); // Apply initial filters if any
    } catch (error) {
        latestDataDiv.textContent = `Error fetching all financial data: ${error.message}`;
    }
}

function populateIndustryFilter(data) {
    const industryCheckboxesContainer = document.getElementById('industryCheckboxes');
    industryCheckboxesContainer.innerHTML = ''; // Clear any existing checkboxes
    industries.clear();

    for (const item of data) {
        if (item.industry && !industries.has(item.industry)) {
            industries.add(item.industry);
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = item.industry;
            checkbox.id = `industry-${item.industry.replace(/\s+/g, '-')}`; // Create a unique ID

            const label = document.createElement('label');
            label.textContent = item.industry;
            label.setAttribute('for', checkbox.id);
            label.classList.add('form-check-label', 'mr-2'); // Add Bootstrap classes for styling

            const formCheck = document.createElement('div');
            formCheck.classList.add('form-check');
            formCheck.appendChild(checkbox);
            formCheck.appendChild(label);

            industryCheckboxesContainer.appendChild(formCheck);
        }
    }
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
        totalPagesDisplay.textContent = totalPages;
        currentPageInput.value = page;
        prevPageButton.disabled = page === 1;
        nextPageButton.disabled = page === totalPages;

        let paginationHtml = '';
        const maxVisiblePages = 5;
        const ellipsis = '<li class="page-item disabled"><span class="page-link">...</span></li>';

        if (totalPages > 1) {
            paginationHtml += `<li class="page-item ${page === 1 ? 'disabled' : ''}">
                                    <a class="page-link" href="#" aria-label="Previous" data-page="${page - 1}">
                                        <span aria-hidden="true">&laquo;</span>
                                        <span class="sr-only">Previous</span>
                                    </a>
                                </li>`;

            paginationHtml += `<li class="page-item ${page === 1 ? 'active' : ''}">
                                    <a class="page-link" href="#" data-page="1">1</a>
                                </li>`;

            if (totalPages <= maxVisiblePages) {
                for (let i = 2; i <= totalPages; i++) {
                    paginationHtml += `<li class="page-item ${page === i ? 'active' : ''}">
                                            <a class="page-link" href="#" data-page="${i}">${i}</a>
                                        </li>`;
                }
            } else {
                let startPage = Math.max(2, page - Math.floor(maxVisiblePages / 2));
                let endPage = Math.min(totalPages - 1, page + Math.floor((maxVisiblePages - 1) / 2));

                if (startPage > 2) {
                    paginationHtml += ellipsis;
                }

                for (let i = startPage; i <= endPage; i++) {
                    paginationHtml += `<li class="page-item ${page === i ? 'active' : ''}">
                                            <a class="page-link" href="#" data-page="${i}">${i}</a>
                                        </li>`;
                }

                if (endPage < totalPages - 1) {
                    paginationHtml += ellipsis;
                }

                if (totalPages > 1) {
                    paginationHtml += `<li class="page-item ${page === totalPages ? 'active' : ''}">
                                            <a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a>
                                        </li>`;
                }
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
        totalPagesDisplay.textContent = '1';
        currentPageInput.value = '1';
        prevPageButton.disabled = true;
        nextPageButton.disabled = true;
    }
}
filtersToggle.addEventListener('click', () => {
    if (filtersContainer.style.display === 'none' || filtersContainer.style.display === '') {
        filtersContainer.style.display = 'flex'; // Use flex for display
        filtersContainer.style.maxHeight = filtersContainer.scrollHeight + 'px';
    } else {
        filtersContainer.style.maxHeight = '0';
        setTimeout(() => {
            if (filtersContainer.style.maxHeight === '0px') {
                filtersContainer.style.display = 'none';
            }
        }, 300);
    }
});

function applyFilters() {
    console.log('applyFilters function called');
    let filteredData = [...allFinancialData];

    const searchTerm = companySearchInput.value;
    console.log('Search Term:', searchTerm);

    const selectedIndustries = Array.from(document.querySelectorAll('#industryCheckboxes input[type="checkbox"]:checked'))
        .map(checkbox => checkbox.value);
    console.log('Selected Industries:', selectedIndustries);

    const dateFrom = flatpickrFrom.selectedDates[0];
    const dateTo = flatpickrTo.selectedDates[0];
    console.log('Date From:', dateFrom, 'Date To:', dateTo);

    filteredData = filteredData.filter(item =>
        item.ticker_symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (item.company_name && item.company_name.toLowerCase().includes(searchTerm.toLowerCase()))
    );
    console.log('After Search Filter:', filteredData);

    // Industry filter
    if (selectedIndustries.length > 0) {
        console.log('Filtering by industries:', selectedIndustries);
        filteredData = filteredData.filter(item => selectedIndustries.includes(item.industry));
        console.log('After Industry Filter:', filteredData);
    }

    // Date range filter
    console.log('Date From (in applyFilters):', dateFrom);
    console.log('Date To (in applyFilters):', dateTo);
    if (dateFrom && dateTo) {
        filteredData = filteredData.filter(item => {
            const itemDate = new Date(item.date);
            return itemDate >= dateFrom && itemDate <= dateTo;
        });
        console.log('After Date Filter:', filteredData);
    } else if (dateFrom) {
        filteredData = filteredData.filter(item => new Date(item.date) >= dateFrom);
    } else if (dateTo) {
        filteredData = filteredData.filter(item => new Date(item.date) <= dateTo);
    }
    console.log('After Date Filter:', filteredData);

    filteredFinancialData = filteredData;
    currentPage = 1;
    displayData(filteredFinancialData, currentPage);
    console.log('filteredFinancialData before displayData:', filteredFinancialData);
}

companySearchInput.addEventListener('input', applyFilters);

pageSizeSelect.addEventListener('change', () => {
    rowsPerPage = parseInt(pageSizeSelect.value, 10);
    currentPage = 1;
    displayData(filteredFinancialData, currentPage);
});

paginationContainer.addEventListener('click', (event) => {
    const target = event.target;
    if (target.classList.contains('page-link') && !target.parentElement.classList.contains('disabled')) {
        event.preventDefault();
        const page = parseInt(target.dataset.page, 10);
        if (!isNaN(page)) {
            currentPage = page;
            displayData(filteredFinancialData, currentPage);
        }
    }
});

prevPageButton.addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        displayData(filteredFinancialData, currentPage);
    }
});

nextPageButton.addEventListener('click', () => {
    const totalPages = Math.ceil(filteredFinancialData.length / rowsPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        displayData(filteredFinancialData, currentPage);
    }
});

currentPageInput.addEventListener('change', () => {
    const pageNumber = parseInt(currentPageInput.value, 10);
    const totalPages = Math.ceil(filteredFinancialData.length / rowsPerPage);
    if (!isNaN(pageNumber) && pageNumber >= 1 && pageNumber <= totalPages) {
        currentPage = pageNumber;
        displayData(filteredFinancialData, currentPage);
    } else if (isNaN(pageNumber) || pageNumber < 1) {
        currentPageInput.value = 1;
        currentPage = 1;
        displayData(filteredFinancialData, currentPage);
    } else {
        currentPageInput.value = totalPages;
        currentPage = totalPages;
        displayData(filteredFinancialData, currentPage);
    }
});

refreshTableButton.addEventListener('click', () => {
    displayAllFinancialData();
});

displayAllFinancialData();