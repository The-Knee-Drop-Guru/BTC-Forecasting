// 페이지 로드 시 시뮬레이션 상태 확인
document.addEventListener('DOMContentLoaded', function () {
    checkSimulationStatus(); // 초기 시뮬레이션 상태 확인
});

document.getElementById('simulation-form').addEventListener('submit', function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    const url = document.getElementById('simulation-form').dataset.url;
    // 사용자 트레이딩 설정 저장
    fetch(url, {
        method: 'POST', // 반드시 POST로 설정
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
        },
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert(data.message);

                // 시뮬레이션 상태 업데이트 시작
                checkSimulationStatus();
            } else {
                alert(`오류 발생: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('오류 발생:', error);
        });
});

// 거래 기록을 주기적으로 갱신하는 함수
function fetchTransactionLogs() {
    const logsContainer = document.getElementById('transaction-logs');
    const url = logsContainer.dataset.url; // data-url 속성에서 URL 가져오기

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const logsContainer = document.getElementById('transaction-logs');
                logsContainer.innerHTML = ''; // 기존 내용을 지움
                data.transactions.forEach(log => {
                    const logRow = `
                        <tr>
                            <td>${log.timestamp}</td>
                            <td>${log.transaction_type}</td>
                            <td>${log.quantity}</td>
                            <td>${log.price}</td>
                            <td>${log.amount}</td>
                            <td>${log.fee}</td>
                            <td>${log.balance}</td>
                            <td>${log.asset}</td>
                        </tr>`;
                    logsContainer.innerHTML += logRow;
                });
            } else {
                console.error(`거래 기록 오류: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('거래 기록 가져오기 오류:', error);
        });
}

// 시뮬레이션 상태를 주기적으로 확인
function checkSimulationStatus() {
    const statusElement = document.getElementById('simulation-status');
    const url = statusElement.dataset.url;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            // 기존 클래스 제거
            statusElement.classList.remove('status-idle', 'status-running', 'status-completed');

            // 상태별 처리
            if (data.status === 'running') {
                statusElement.textContent = '시뮬레이션 진행 중...';
                statusElement.classList.add('status-running'); // Running 상태 클래스 추가
                setTimeout(checkSimulationStatus, 60000); // 1분 후 다시 상태 확인
            } else if (data.status === 'completed') {
                statusElement.textContent = '시뮬레이션 완료!';
                statusElement.classList.add('status-completed'); // Completed 상태 클래스 추가
            } else {
                statusElement.textContent = `시작값 미설정: ${data.message}`;
                statusElement.classList.add('status-idle'); // Idle 상태 클래스 추가
            }
        })
        .catch(error => {
            console.error('시뮬레이션 상태 확인 오류:', error);
        });
}