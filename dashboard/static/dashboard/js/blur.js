document.addEventListener("DOMContentLoaded", () => {
    const canvases = document.querySelectorAll(".blur-container canvas");

    function resizeCanvas(canvas) {
        const container = canvas.parentElement; // 부모 요소를 가져옴
        const containerWidth = container.offsetWidth;
        const containerHeight = container.offsetHeight;

        // 캔버스 크기 조정
        canvas.width = containerWidth;
        canvas.height = containerHeight;
    }

    function resizeAllCanvases() {
        canvases.forEach((canvas) => resizeCanvas(canvas));
    }

    // 초기 크기 설정
    resizeAllCanvases();

    // 화면 크기 변경 시 캔버스 크기 업데이트
    window.addEventListener("resize", resizeAllCanvases);
});
