document.addEventListener("DOMContentLoaded", () => {
    // Sentiment pie 그래프 생성 함수
    function createPieChart(canvasId, labels, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: ['#FF6384', '#36A2EB', '#9C9C9C'],
                }],
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    // 제목 비활성화
                    title: {
                        display: false,
                    },
                    datalabels: {
                        color: '#fff', // 텍스트 색상
                        formatter: (value) => value, // 값을 그대로 표시
                        font: {
                            weight: 'bold',
                            size: 28,
                        },
                    },
                },
            },
            plugins: [ChartDataLabels], // 데이터 레이블 플러그인 추가
        });
    }

    // 레이블 매핑 함수
    function mapLabels(labels) {
        return labels.map(label => {
            if (label === 'positive') return '긍정';
            if (label === 'negative') return '부정';
            if (label === 'neutral') return '중립';
            return label; // 매핑되지 않은 레이블은 그대로 유지
        });
    }

    // API를 호출하여 데이터 가져오기
    function fetchSentimentData(classId, canvasId) {
        fetch(`/api/sentiment/${classId}/`)
            .then(response => response.json())
            .then(data => {
                const mappedLabels = mapLabels(data.labels);
                createPieChart(canvasId, mappedLabels, data.counts);
            })
            .catch(error => console.error('Error fetching sentiment data:', error));
    }

    // News Sentiments Chart
    fetchSentimentData('news', 'newsChart');

    // Reddit Sentiments Chart
    fetchSentimentData('reddit', 'redditChart');
});
