document.addEventListener("DOMContentLoaded", () => {
    // Sentiment pie 그래프 생성 함수
    function createPieChart(canvasId, labels, data, title) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'],
                }],
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: title,
                    },
                },
            },
        });
    }

    // API를 호출하여 데이터 가져오기
    function fetchSentimentData(classId, canvasId, title) {
        fetch(`/api/sentiment/${classId}/`)
            .then(response => response.json())
            .then(data => {
                createPieChart(canvasId, data.labels, data.counts, title);
            })
            .catch(error => console.error('Error fetching sentiment data:', error));
    }

    // News Sentiments Chart
    fetchSentimentData('news', 'newsChart', 'News Sentiments');

    // Reddit Sentiments Chart
    fetchSentimentData('reddit', 'redditChart', 'Reddit Sentiments');
});
