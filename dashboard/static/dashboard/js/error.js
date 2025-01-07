document.addEventListener("DOMContentLoaded", () => {
    const errorCtx = document.getElementById('errorChart').getContext('2d');
    const errorChart = new Chart(errorCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Prediction Error',
                    data: [],
                    borderColor: '#f03738',
                    borderWidth: 2,
                    pointRadius: 3,
                    pointHoverRadius: 6,
                    fill: false,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                tooltip: {
                    enabled: true,
                },
            },
            scales: {
                x: {
                    title: { display: true, text: 'Date' },
                    ticks: {
                        callback: function (value, index, ticks) {
                            const date = new Date(this.getLabels()[index]);
                            const month = date.getMonth() + 1;
                            const day = date.getDate();
                            return `${month}/${day}`; // MM/DD 형식으로 출력
                        },
                    },
                },
                y: {
                    title: { display: true, text: 'Error' },
                    ticks: {
                        stepSize: 100, // 레이블 간격 설정
                        callback: function (value) {
                            return Math.round(value); // 소수점 제거
                        },
                    },
                    grid: {
                        color: (context) => (context.tick.value === 0 ? '#000' : '#ccc'), // 0 기준선 강조
                        lineWidth: (context) => (context.tick.value === 0 ? 2 : 1), // 0 기준선 두께
                    },
                },
            },
        },
    });

    function fetchErrorData() {
        fetch('/api/error-data/')
            .then(response => response.json())
            .then(data => {
                errorChart.data.labels = data.map(item => item.date);
                errorChart.data.datasets[0].data = data.map(item => item.error);

                // 가장 큰 절대값 계산
                const maxAbsError = Math.ceil(
                    Math.max(...data.map(item => Math.abs(item.error))) / 100
                ) * 100;

                // y축 범위 설정
                errorChart.options.scales.y.suggestedMin = -maxAbsError;
                errorChart.options.scales.y.suggestedMax = maxAbsError;

                errorChart.update();
            })
            .catch(error => console.error('Error fetching error data:', error));
    }

    fetchErrorData();
});
