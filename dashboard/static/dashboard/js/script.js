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
                    borderWidth: 2,
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
                    type: 'time', // 시간 축 사용
                    time: {
                        unit: 'hour', // 매시 단위로 레이블 설정
                        displayFormats: {
                            hour: 'MM/dd HH:mm', // 날짜와 시간 표시
                        },
                    },
                    title: {
                        display: true,
                        text: 'Time',
                    },
                    ticks: {
                        autoSkip: true, // 자동으로 레이블 간격 조정
                        maxRotation: 0, 
                        callback: function (value) {
                            const time = new Date(value);

                            // 날짜와 시간을 MM/DD HH:mm 포맷으로 변환
                            const month = String(time.getMonth() + 1).padStart(2, '0');
                            const day = String(time.getDate()).padStart(2, '0');
                            const hours = String(time.getHours()).padStart(2, '0');
                            const minutes = String(time.getMinutes()).padStart(2, '0');

                            if (minutes === '00') {
                                // 정각만 표시
                                return `${month}/${day} ${hours}:${minutes}`;
                            }
                            return null; // 정각이 아니면 표시하지 않음
                        },
                    },
                },
                y: {
                    title: {
                        display: true,
                        text: 'BTC Price',
                    },
                    ticks: {
                        callback: function (value) {
                            return value.toLocaleString() + '$';
                        },
                    },
                },
            },
        },
    });

    const featureCtx = document.getElementById('featureChart').getContext('2d');
    const featureChart = new Chart(featureCtx, {
        type: 'pie',
        data: {
            labels: [], // 피처 이름
            datasets: [
                {
                    data: [], // 중요도 값
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                    ],
                    borderWidth: 1,
                },
            ],
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Feature Importance',
                },
            },
        },
    });


    // Fetch Bitcoin Forecast Data
    function fetchBitcoinForecast() {
        fetch('/api/btc-forecasting/') 
            .then(response => response.json())
            .then(data => {
                bitcoinChart.data.labels = data.time;
                bitcoinChart.data.datasets[0].data = data.real_price;
                bitcoinChart.data.datasets[1].data = data.predicted_price.map(
                    price => price !== null ? price : NaN
                );
                bitcoinChart.update();
            })
            .catch(error => console.error('Error fetching Bitcoin forecast data:', error));
    }

    // Fetch Feature Importance Data
    function fetchFeatureImportance() {
        fetch('/api/feature-importance/') 
            .then(response => response.json())
            .then(data => {
                featureChart.data.labels = data.features.map(item => item.name);
                featureChart.data.datasets[0].data = data.features.map(item => item.importance);
                featureChart.update();
            })
            .catch(error => console.error('Error fetching feature importance data:', error));
    }

    // 초기 데이터 로드
    fetchBitcoinForecast();
    fetchFeatureImportance();

    // 1시간마다 데이터 갱신
    setInterval(fetchBitcoinForecast, 3600000);
    setInterval(fetchFeatureImportance, 3600000);
});
