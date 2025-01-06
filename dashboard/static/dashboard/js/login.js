document.addEventListener("DOMContentLoaded", function () {
    const popup = document.getElementById("popup-messages");
    if (popup) {
        setTimeout(() => {
            popup.style.opacity = "0";
            setTimeout(() => popup.remove(), 500); // 팝업 완전히 삭제
        }, 3000); // 3초 후 자동 제거
    }
});