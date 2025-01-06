document.addEventListener("DOMContentLoaded", () => {
    // Bitcoin Forecast Chart 초기화
    const btcCtx = document.getElementById('bitcoinChart').getContext('2d');
    const bitcoinChart = new Chart(btcCtx, {
        type: 'line',
        data: {
            labels: [], // 시간 축 데이터
            datasets: [
                {
                    label: 'Real Price',
                    data: [],
                    borderColor: '#0971ff',
                    borderWidth: 1,
                    pointRadius: 1,
                    pointHoverRadius: 5,
                    fill: false,
                },
                {
                    label: 'Predicted Price',
                    data: [],
                    borderColor: '#f03738',
                    borderDash: [5, 5],
                    borderWidth: 2,
                    pointRadius: 1,
                    pointHoverRadius: 5,
                    fill: false,
                },
            ],
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'day', // 매일 단위
                        displayFormats: { day: 'MM/dd' }, // 날짜 형식
                    },
                    title: { display: true, text: 'Time' },
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

    // 날짜 선택 초기화
    const startDateInput = document.getElementById('startDate');
    const filterButton = document.getElementById('filterButton');
    const availableDates = [
        "2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04",
        "2025-01-05", "2025-01-06", "2025-01-07", "2025-01-08"
    ];

    // 날짜 비활성화
    function disableUnavailableDates() {
        startDateInput.min = availableDates[0];
        startDateInput.max = availableDates[availableDates.length - 1];

        startDateInput.addEventListener('input', () => {
            if (!availableDates.includes(startDateInput.value)) {
                startDateInput.setCustomValidity('Selected date is unavailable.');
            } else {
                startDateInput.setCustomValidity('');
            }
        });
    }

    // Bitcoin Forecast 데이터 로드
    function fetchBitcoinForecast(startDate, endDate) {
        fetch(`/api/btc-forecasting?start_date=${startDate}&end_date=${endDate}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error fetching data: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (!data.time || !data.real_price || !data.predicted_price) {
                    throw new Error("Invalid data format from API.");
                }

                bitcoinChart.data.labels = data.time;
                bitcoinChart.data.datasets[0].data = data.real_price;
                bitcoinChart.data.datasets[1].data = data.predicted_price.map(price => price || NaN);
                bitcoinChart.update();
            })
            .catch(error => console.error('Error fetching Bitcoin forecast data:', error));
    }

    // Feature Importance 데이터 로드 및 순위 리스트 생성
    function fetchFeatureImportance() {
        fetch('/api/feature-importance/')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error fetching data: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (!data.features) {
                    throw new Error("Invalid data format from API.");
                }

                // 피처 데이터를 중요도 기준으로 내림차순 정렬
                const sortedFeatures = data.features.sort((a, b) => b.importance - a.importance);

                // 순위 리스트 업데이트
                const featureRanking = document.getElementById('featureRanking');
                featureRanking.innerHTML = ''; // 기존 리스트 초기화
                sortedFeatures.forEach((feature, index) => {
                    const listItem = document.createElement('li');
                    listItem.setAttribute('data-rank', index + 1); // 순위 추가
                    listItem.innerHTML = `
                        <span class="feature-name">${feature.name}</span>
                        <span class="feature-importance">${feature.importance.toFixed(2)}</span>
                    `;
                    featureRanking.appendChild(listItem);
                });
            })
            .catch(error => console.error('Error fetching feature importance data:', error));
    }

    // 필터 버튼 클릭 이벤트
    filterButton.addEventListener('click', () => {
        const selectedStartDate = startDateInput.value;

        if (!selectedStartDate) {
            alert('Please select a valid start date.');
            return;
        }

        const startDate = new Date(selectedStartDate);
        const endDate = new Date(startDate);
        endDate.setDate(startDate.getDate() + 6);

        const start = startDate.toISOString().split('T')[0];
        const end = endDate.toISOString().split('T')[0];

        // 날짜 범위가 유효한지 확인
        const isStartValid = availableDates.includes(start);
        const isEndValid = availableDates.includes(end);

        if (!isStartValid || !isEndValid) {
            alert('Selected date range includes unavailable dates.');
            return;
        }

        console.log(`Fetching data from ${start} to ${end}`);
        fetchBitcoinForecast(start, end);
    });

    // 초기화
    disableUnavailableDates();
    const initialStart = availableDates[0];
    const initialEnd = availableDates[6];
    fetchBitcoinForecast(initialStart, initialEnd);
    fetchFeatureImportance();
});
