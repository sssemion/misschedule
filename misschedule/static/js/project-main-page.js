// Всплывающее окно с детальной информацией
var popup = $($(".popup-task-wrapper.detail-info")[0]);
var clickedTask = null;

$(".task:not(.task.new-task)").on("click", function() {
    // При клике на какую-либо из задач, появляется всплывающее окно

    clickedTask = $(this);

    // Данные в всплывающем окне формируются на основе тех, что лежат в элементе самой задачи
    // и из атрибутов "data-"
    
    // Название
    $(".popup-task__title").text($(this).children(".task__title").text());
    
    // Описание
    $(".popup-task__description").text($(this).children(".task__description").text());
    if ($(this).children(".task__description").hasClass("no-description")) {
        $(".popup-task__description").addClass("no-description");
    } else {
        $(".popup-task__description").removeClass("no-description");
    }

    // Тег
    $(".popup-task__tag").text($(this).children(".task__tag").text());
    
    // Создатель
    $(".popup-task__creator").text($(this).attr("data-creator-name"));
    $(".popup-task__creator").attr("href", "/" + $(this).attr("data-creator-username"));

    // Ответственный
    $(".popup-task__worker").text($(this).attr("data-worker-name"));
    $(".popup-task__worker").attr("href", "/" + $(this).attr("data-worker-username"));

    // Дата создания
    $(".popup-task__creation-date").text($(this).attr("data-creation-date-formatted"));
    $(".popup-task__deadline-date").text($(this).attr("data-deadline-date-formatted"));

    // Подзадачи
    $(".popup-task__items").html($(this).children(".task__items").html());

    popup.children(".popup-task").attr("style", $(this).attr("style")); // Цвет фона
    popup.children(".popup-task").attr("data-id", $(this).attr("data-id")); // id
    popup.fadeIn(500);
    popup.addClass("active");
    $("body").addClass("scroll-locked");
});

$(".popup-task .close-btn").on("click", function() {
    popup.fadeOut(500, function() {    
        popup.removeClass("active");
        clickedTask = null;
        $("body").removeClass("scroll-locked");
    });
});

$(".popup-task__send-button").on("click", function() {
    var params = {
        task_id: popup.children(".popup-task").attr("data-id"),
        item_ids: []
    }
    $(".popup-task__items .item").each(function() {
        // Если пользователь отметил чекбокс, значит он выполнил задачу, 
        // и мы добавляем id подзадачи в список
        if (!$(this).children(".item__completed").prop("disabled") &&
            $(this).children(".item__completed").is(':checked')) {
            params.item_ids.push($(this).attr("data-id"));
        }
    });

    // И передаем его на сервер с помощью ajax
    $.ajax("/ajax/complete_item", {
        method: 'post',
        dataType: 'json',
        data: JSON.stringify(params),
        contentType: "application/json; charset=utf-8",
        success: function(data) {
            $(".popup-task__items .item").each(function() {
                if (!$(this).children(".item__completed").prop("disabled") &&
                        $(this).children(".item__completed").is(':checked')) {
                    // Для всех выполненных только что подзадач добавляем элементы "Кем выполнено"
                    // и "Когда выполнено" с информацией, полученной в ответе сервера. А также отключаем чекбокс,
                    // т.к. выполненную задачу нельзя развыполнить
                    $(this).children(".item__completed").prop("disabled", true);
                    $(this).children(".item__info").append('<span>Кем выполнено: </span><a class="popup-task__worker" href="/' + data.completed_by.username + '">' + 
                                   data.completed_by.first_name + ' ' + data.completed_by.last_name + '</a><br>');
                    $(this).children(".item__info").append('<span>Когда выполнено: </span><span>' + data.completion_date + '</span><br>');

                    // Изменяем ифнормацию и для элемента Задачи
                    var item = clickedTask.children(".task__items").children(".item[data-id=" + $(this).attr("data-id") + "]");
                    item.children(".item__completed").prop("disabled", true);
                    item.children(".item__completed").attr("checked", true);
                    item.children(".item__info").append('<span>Кем выполнено: </span><a class="popup-task__worker" href="/' + data.completed_by.username + '">' + 
                                                        data.completed_by.first_name + ' ' + data.completed_by.last_name + '</a><br>');
                    item.children(".item__info").append('<span>Когда выполнено: </span><span>' + data.completion_date + '</span><br>');
                }
            });
        }
    });
});


// Форма для создания задачи
var newTask = $(".popup-task-wrapper.new-task");

$(".task.new-task").on("click", function() {
    newTask.fadeIn(500);
    newTask.addClass("active");
    $("body").addClass("scroll-locked");
});

$(".task-form .close-btn").on("click", function() {
    newTask.fadeOut(500, function() {    
        newTask.removeClass("active");
        $("body").removeClass("scroll-locked");
    });
});