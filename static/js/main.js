document.addEventListener("DOMContentLoaded", () => {
  const phraseElement = document.querySelector(".animated-phrases");
  if (phraseElement) {
    const phrases = phraseElement.dataset.phrases.split(",");
    let currentIndex = 0;

    const updatePhrase = () => {
      phraseElement.textContent = phrases[currentIndex];
      currentIndex = (currentIndex + 1) % phrases.length;
    };

    updatePhrase();
    setInterval(updatePhrase, 3400);
  }

  const carousel = document.querySelector(".project-carousel");
  if (carousel) {
    const track = carousel.querySelector(".project-grid");
    const cards = Array.from(track.querySelectorAll(".project-card"));
    const prevButton = carousel.querySelector(".carousel-prev");
    const nextButton = carousel.querySelector(".carousel-next");
    const visibleCount = 3;
    let currentIndex = 0;

    const refreshCarousel = () => {
      const total = cards.length;
      const maxIndex = Math.max(0, total - visibleCount);
      currentIndex = Math.min(currentIndex, maxIndex);
      const cardWidth = cards[0]?.offsetWidth ?? 0;
      const gap = 24;
      const offset = currentIndex * (cardWidth + gap);
      track.style.transform = `translateX(-${offset}px)`;

      if (prevButton) prevButton.disabled = currentIndex <= 0;
      if (nextButton) nextButton.disabled = currentIndex >= maxIndex;
      if (total <= visibleCount) {
        if (prevButton) prevButton.style.display = "none";
        if (nextButton) nextButton.style.display = "none";
      }
    };

    if (prevButton) {
      prevButton.addEventListener("click", () => {
        currentIndex = Math.max(0, currentIndex - 1);
        refreshCarousel();
      });
    }

    if (nextButton) {
      nextButton.addEventListener("click", () => {
        currentIndex = Math.min(cards.length - visibleCount, currentIndex + 1);
        refreshCarousel();
      });
    }

    let autoRotateTimer = null;
    const startAutoRotate = () => {
      if (cards.length <= visibleCount || autoRotateTimer) return;
      autoRotateTimer = setInterval(() => {
        const total = cards.length;
        const maxIndex = Math.max(0, total - visibleCount);
        if (currentIndex >= maxIndex) {
          currentIndex = 0;
        } else {
          currentIndex += 1;
        }
        refreshCarousel();
      }, 3200);
    };

    const stopAutoRotate = () => {
      if (autoRotateTimer) {
        clearInterval(autoRotateTimer);
        autoRotateTimer = null;
      }
    };

    refreshCarousel();
    startAutoRotate();
    window.addEventListener("resize", refreshCarousel);
    carousel.addEventListener("mouseenter", stopAutoRotate);
    carousel.addEventListener("mouseleave", startAutoRotate);
  }
});
