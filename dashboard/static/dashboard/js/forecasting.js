document.addEventListener("DOMContentLoaded", () => {
    // 날짜 입력 필드 요소 가져오기
    const startDateInput = document.getElementById('startDate'); // 시작 날짜 입력 필드
    const endDateInput = document.getElementById('endDate');     // 종료 날짜 입력 필드

    // 날짜 입력 필드가 없을 경우 오류 출력 후 중단
    if (!startDateInput || !endDateInput) {
        console.error("Date input elements are missing in the HTML.");
        return;
    }

    // 차트 컨텍스트 가져오기
    const btcCtx = document.getElementById('bitcoinChart').getContext('2d');

    // Chart.js 차트 생성
    const bitcoinChart = new Chart(btcCtx, {
        type: 'line', // 라인 차트
        data: {
            labels: [], // x축 레이블 (시간 데이터)
            datasets: [
                {
                    label: 'Real Price',    // 실제 비트코인 가격
                    data: [],               // 데이터 값
                    borderColor: '#0971ff', // 선 색상
                    borderWidth: 1,         // 선 두께
                    pointRadius: 1,         // 데이터 점 크기
                    pointHoverRadius: 5,    // 데이터 점 hover 크기
                    fill: false,            // 차트 아래 채우기 비활성화
                },
                {
                    label: 'Predicted Price', // 예측된 비트코인 가격
                    data: [],                 // 데이터 값
                    borderColor: '#f79a57',   // 선 색상
                    borderWidth: 2,           // 선 두께
                    pointRadius: 1,           // 데이터 점 크기
                    pointHoverRadius: 5,      // 데이터 점 hover 크기
                    fill: false,              // 차트 아래 채우기 비활성화
                    spanGaps: true,           // 결측값 무시하고 선 연결
                },
            ],
        },
        options: {
            responsive: true,             // 반응형 차트
            maintainAspectRatio: false,   // 고정 비율 비활성화
            plugins: {
                tooltip: {                // 툴팁 설정
                    enabled: true,        // 툴팁 활성화
                    mode: 'nearest',      // 툴팁이 가장 가까운 데이터에 반응
                    intersect: false,     // 교차점 없이 데이터에만 반응
                    callbacks: {
                        title: (tooltipItems) => {
                            const date = new Date(tooltipItems[0].parsed.x);
                            return `Date: ${date.toLocaleString()}`; // 툴팁 제목: 날짜
                        },
                        label: (tooltipItem) => {
                            const datasetLabel = tooltipItem.dataset.label || ''; // 데이터셋 레이블
                            const value = tooltipItem.raw || 0;                   // 데이터 값
                            return `${datasetLabel}: $${value.toLocaleString()}`; // 툴팁 내용
                        },
                    },
                },
            },
            scales: {
                x: {
                    type: 'time',                  // x축을 시간으로 설정
                    time: {
                        unit: 'hour',             // 시간 단위
                        displayFormats: {
                            hour: 'MMM D HH:mm',  // x축 레이블 표시 형식
                        },
                    },
                    title: {
                        display: true,            // x축 제목 표시
                        text: 'Date & Time',      // x축 제목
                    },
                    ticks: {
                        autoSkip: true,           // 레이블 자동 생략
                        maxTicksLimit: 9,         // 최대 레이블 수 제한
                        callback: function (value) {
                            const date = new Date(value);
                            return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:00`; // 레이블 포맷
                        },
                    },
                },
                y: {
                    title: {
                        display: true,            // y축 제목 표시
                        text: 'BTC Price',        // y축 제목
                    },
                    ticks: {
                        callback: (value) => value.toLocaleString() + '$', // y축 값에 $ 추가
                    },
                },
            },
        },
    });

    // 비트코인 예측 데이터를 가져와 차트 업데이트
    function fetchBitcoinForecast(startDate, endDate) {
        fetch(`/api/btc-forecasting/?start_date=${startDate}&end_date=${endDate}`)
            .then(response => response.json())
            .then(data => {
                // API로부터 받은 데이터로 차트 업데이트
                bitcoinChart.data.labels = data.time; // x축 레이블 설정
                bitcoinChart.data.datasets[0].data = data.real_price; // 실제 가격 데이터
                bitcoinChart.data.datasets[1].data = data.predicted_price.map(price => {
                    return price || null; // 결측값(null) 유지
                });
                bitcoinChart.update(); // 차트 업데이트

                // 기본 시작/종료 날짜가 제공되면 입력 필드 초기화
                if (data.default_start_date && data.default_end_date) {
                    startDateInput.value = data.default_start_date;
                    endDateInput.value = data.default_end_date;
                }
            })
            .catch(error => console.error('Error fetching Bitcoin forecast data:', error));
    }

    // 기본 날짜 범위를 설정하고 데이터 가져오기
    function initializeDefaultDateRange() {
        fetchBitcoinForecast(null, null); // 기본 날짜를 백엔드에서 받아옴
    }

    // 시작 날짜 변경 시 차트 업데이트
    startDateInput.addEventListener("change", () => {
        fetchBitcoinForecast(startDateInput.value, endDateInput.value);
    });

    // 종료 날짜 변경 시 차트 업데이트
    endDateInput.addEventListener("change", () => {
        fetchBitcoinForecast(startDateInput.value, endDateInput.value);
    });

    initializeDefaultDateRange(); 
});
