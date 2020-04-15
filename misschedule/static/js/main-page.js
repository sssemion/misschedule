$(document).ready(function() {
    $(".next").on("click", function() {
        plusSlide();
    });
    
    $(".prev").on("click", function() {
        minusSlide();
    });
    
    $(".slider-dots__item").on("click", function() {
        currentSlide($(".slider-dots__item").index($(this)) + 1);
    });
})
// slider
var slideIndex = 1;
showSlides(slideIndex);

function plusSlide() {
    showSlides(slideIndex += 1);
}

function minusSlide() {
    showSlides(slideIndex -= 1);  
}

function currentSlide(n) {
    showSlides(slideIndex = n);
}

/* Основная функция слайдера */
function showSlides(n) {
    var i;
    var slides = document.getElementsByClassName("slide");
    var dots = document.getElementsByClassName("slider-dots__item");
    var descriprionItems = document.getElementsByClassName("slide-description");
    if (n > slides.length) {
      slideIndex = 1;
    }
    if (n < 1) {
        slideIndex = slides.length;
    }
    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    for (i = 0; i < dots.length; i++) {
        dots[i].className = dots[i].className.replace(" active", "");
    }
    for (i = 0; i < descriprionItems.length; i++) {
        descriprionItems[i].style.display = "none";
    }
    slides[slideIndex - 1].style.display = "block";
    dots[slideIndex - 1].className += " active";
    descriprionItems[slideIndex - 1].style.display = "block";
}
