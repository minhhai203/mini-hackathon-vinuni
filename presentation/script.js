const slides = Array.from(document.querySelectorAll(".slide"));
const prevButton = document.querySelector("#prev");
const nextButton = document.querySelector("#next");
const counter = document.querySelector("#counter");
const imageSlots = Array.from(document.querySelectorAll(".image-slot img"));

let current = 0;

function showSlide(index) {
  current = (index + slides.length) % slides.length;
  slides.forEach((slide, slideIndex) => {
    slide.classList.toggle("active", slideIndex === current);
  });
  counter.textContent = `${current + 1} / ${slides.length}`;
}

prevButton.addEventListener("click", () => showSlide(current - 1));
nextButton.addEventListener("click", () => showSlide(current + 1));

document.addEventListener("keydown", (event) => {
  if (event.key === "ArrowRight" || event.key === " ") {
    event.preventDefault();
    showSlide(current + 1);
  }

  if (event.key === "ArrowLeft") {
    event.preventDefault();
    showSlide(current - 1);
  }
});

showSlide(0);

imageSlots.forEach((image) => {
  image.addEventListener("error", () => {
    image.style.display = "none";
    image.closest(".image-slot")?.classList.add("missing-image");
  });
});
