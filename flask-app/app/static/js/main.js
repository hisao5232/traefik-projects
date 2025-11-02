// ページロード時に順番にフェードイン
document.addEventListener("DOMContentLoaded", () => {
    const fadeEls = document.querySelectorAll(".fade-in");
    fadeEls.forEach((el, i) => {
      setTimeout(() => {
        el.classList.add("show");
      }, i * 200); // 少しずつずらして出す
    });
  });
  