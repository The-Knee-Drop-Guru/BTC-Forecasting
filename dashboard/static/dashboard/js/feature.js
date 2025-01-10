document.addEventListener("DOMContentLoaded", () => {
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
                        <span class="feature-importance">${feature.importance.toFixed(1)}%
                    `;
                    featureRanking.appendChild(listItem);
                });
            })
            .catch(error => console.error('Error fetching feature importance data:', error));
    }

    fetchFeatureImportance();
});
