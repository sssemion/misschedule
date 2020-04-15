$(document).ready(function() {
    if ($(window).scrollTop() > 0) {
        $(".header").addClass("scrolled");
    }

    $(".burger").on("click", function() {
        $(".burger").toggleClass("active");
        $(".header__nav").toggleClass("active");
        $(".login-buttons").toggleClass("active");
        $(".header").toggleClass("active");
    })

    $(window).scroll(function(){
        if ($(window).scrollTop() > 0) {
            $(".header").addClass("scrolled");
        } else {
            $(".header").removeClass("scrolled");
        }
    });
});