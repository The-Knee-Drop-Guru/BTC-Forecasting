// Bitcoin Forecast Chart
document.addEventListener("DOMContentLoaded", () => {
    const ctx = document.getElementById('bitcoinChart').getContext('2d');

    // Chart 초기화
    const bitcoinChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], // 시간 축 데이터
            datasets: [
                {
                    label: 'Real Price',
                    data: [], // 실제 가격
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    fill: false,
                },
                {
                    label: 'Predicted Price',
                    data: [], // 예측 가격
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderDash: [5, 5], // 점선 스타일
                    borderWidth: 2,
                    fill: false,
                },
            ],
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Time',
                    },
                },
                y: {
                    title: {
                        display: true,
                        text: 'Price',
                    },
                    min: 90000, // 세로축 최소값
                    max: 100000, // 세로축 최대값
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString(); // 숫자 콤마 형식
                        },
                    },
                },
            },
        },
    });

    // Fetch data from the API
    function fetchData() {
        fetch('forecast/') // Django API 엔드포인트
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // 데이터가 올바른지 확인
                if (data.time && data.real_price && data.predicted_price) {
                    bitcoinChart.data.labels = data.time; // 시간 데이터를 x축에 추가
                    bitcoinChart.data.datasets[0].data = data.real_price; // 실제 가격 데이터
                    bitcoinChart.data.datasets[1].data = data.predicted_price.map(
                        price => price !== null ? price : NaN // null 값을 NaN으로 처리
                    ); // 예측 가격 데이터
                    bitcoinChart.update(); // 그래프 업데이트
                } else {
                    console.error("Invalid data structure:", data);
                }
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    }

    // 10분마다 데이터 갱신
    setInterval(fetchData, 600000); // 600,000ms = 10분
    fetchData(); // 초기 데이터 로드
});
