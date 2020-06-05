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
    // Парсим дату из ISO формата сначала в UTC формат, 
    // а затем в формат локального часового пояса

    var a = element.text().split(/[^0-9]/);
    if (a.length < 6) {
        a.push("0");
    }
    
    var date = new Date(Date.UTC(a[0], a[1] - 1, a[2], a[3], a[4], a[5]));
    
    var s = date.toLocaleString();
    
    // Убираем ненужные секунды
    if (s.endsWith(":00")) {
        s = s.replace(/:00$/g, "");
    }
    s = s.replace(", ", " ");
    element.text(s);
}

function clearStyleDisplay() {
    $(this).attr("style", $(this).attr("style").replace(/display:\s.+;/g, ""));
}