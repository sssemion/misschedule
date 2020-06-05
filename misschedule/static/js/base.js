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

    $(".date-field").each(function() {
        formatDate($(this));
    });
});


// Функция для перевода даты из GMT в локальный часовой пояс
function formatDate(element) {
    // Парсим дату из ISO формата с добавлением Z в конце, т.к. дата в GMT
    var date = new Date(Date.parse(element.text() + "Z"));

    var s = date.toLocaleString();
    
    // Убираем ненужные секунды
    if (s.endsWith(":00")) {
        s = s.replace(/:00$/g, "");
    }
    s = s.replace(", ", " ");
    element.text(s);
}