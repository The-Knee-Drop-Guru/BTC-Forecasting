document.addEventListener("DOMContentLoaded", () => {
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');

    const btcCtx = document.getElementById('bitcoinChart').getContext('2d');
    const bitcoinChart = new Chart(btcCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Real Price',
                    data: [],
                    borderColor: '#0971ff',
                    borderWidth: 1,
                    pointRadius: 1,
                    pointHoverRadius: 6,
                    fill: false,
                },
                {
                    label: 'Predicted Price',
                    data: [],
                    borderColor: '#f03738',
                    borderDash: [5, 5],
                    borderWidth: 2,
                    pointRadius: 2,
                    pointHoverRadius: 6,
                    fill: false,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    enabled: true,
                    mode: 'nearest',
                    intersect: false,
                    callbacks: {
                        title: (tooltipItems) => {
                            const date = new Date(tooltipItems[0].parsed.x);
                            return `Date: ${date.toLocaleString()}`;
                        },
                        label: (tooltipItem) => {
                            const datasetLabel = tooltipItem.dataset.label || '';
                            const value = tooltipItem.raw || 0;
                            return `${datasetLabel}: $${value.toLocaleString()}`;
                        },
                    },
                },
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'hour',
                        displayFormats: {
                            hour: 'MMM D HH:mm',
                        },
                    },
                    title: {
                        display: true,
                        text: 'Date & Time',
                    },
                    ticks: {
                        autoSkip: true,
                        maxTicksLimit: 9,
                        callback: function (value) {
                            const date = new Date(value);
                            return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:00`;
                        },
                    },
                },
                y: {
                    title: { display: true, text: 'BTC Price' },
                    ticks: {
                        callback: (value) => value.toLocaleString() + '$',
                    },
                },
            },
        },
    });

    function fetchBitcoinForecast(startDate, endDate) {
        if (!startDate || !endDate) return;

        fetch(`/api/btc-forecasting/?start_date=${startDate}&end_date=${endDate}`)
            .then(response => response.json())
            .then(data => {
                console.log('API 데이터:', data); // 데이터 확인
                bitcoinChart.data.labels = data.time;
                bitcoinChart.data.datasets[0].data = data.real_price;
                bitcoinChart.data.datasets[1].data = data.predicted_price.map(price => price || NaN);
                bitcoinChart.update();
            })
            .catch(error => console.error('Error fetching Bitcoin forecast data:', error));
    }

    function initializeDefaultDateRange() {
        const today = new Date();
        const endDate = today.toISOString().split('T')[0];
        const startDate = new Date(today);
        startDate.setDate(startDate.getDate() - 6);
        const startDateFormatted = startDate.toISOString().split('T')[0];

        startDateInput.value = startDateFormatted;
        endDateInput.value = endDate;

        fetchBitcoinForecast(startDateFormatted, endDate);
    }

    startDateInput.addEventListener("change", () => {
        fetchBitcoinForecast(startDateInput.value, endDateInput.value);
    });

    endDateInput.addEventListener("change", () => {
        fetchBitcoinForecast(startDateInput.value, endDateInput.value);
    });

    initializeDefaultDateRange();
});
