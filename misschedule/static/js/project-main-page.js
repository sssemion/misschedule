// Всплывающее окно с детальной информацией
var popup = $($(".popup-task-wrapper.detail-info")[0]);
var clickedTask = null;

$(".task:not(.task.new-task)").on("click", click_on_task);

function click_on_task() {
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
    if ($(this).children(".task__tag")[0]) {
        $(".popup-task__tag").text($(this).children(".task__tag").text());
        $(".popup-task__tag").css("display", "inline-block");
    } else {
        $(".popup-task__tag").css("display", "none");
    }
    
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

    if ($(this).hasClass("planned")) {
        $(".popup-task__move-button").text("Начать");
        $(".popup-task__move-button").css("display", "block");
    } else if ($(this).hasClass("in-progress")) {
        $(".popup-task__move-button").text("Завершить");
        $(".popup-task__move-button").css("display", "block");
    } else if ($(this).hasClass("finished")) {
        $(".popup-task__move-button").css("display", "none");
    }

    popup.children(".popup-task").attr("style", $(this).attr("style")); // Цвет фона
    popup.children(".popup-task").attr("data-id", $(this).attr("data-id")); // id
    popup.fadeIn(500);
    popup.addClass("active");
    $("body").addClass("scroll-locked");
}

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
    };
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

$(".popup-task__move-button").on("click", function() {
    var params = {
        task_id: popup.children(".popup-task").attr("data-id")
    };
    if (clickedTask.hasClass("planned")) {
        params.condition = 1;
    } else if (clickedTask.hasClass("in-progress")) {
        params.condition = 2;
    }

    $.ajax("/ajax/set_task_condition", {
        method: 'post',
        dataType: 'json',
        data: JSON.stringify(params),
        contentType: "application/json; charset=utf-8",
        success: function(data) {
            if (data.success) {
                var taskHtml = clickedTask[0].outerHTML;
                console.log(taskHtml);
                console.log(data);
                clickedTask.remove();
                if (data.condition == 1) {
                    $(".tasks__column.in-progress").append(taskHtml);
                    clickedTask = $(".tasks__column.in-progress .task.planned");
                    clickedTask.removeClass("planned");
                    clickedTask.addClass("in-progress");
                } else if (data.condition == 2) {
                    $(".tasks__column.finished").append(taskHtml);
                    clickedTask = $(".tasks__column.finished .task.in-progress");
                    clickedTask.removeClass("in-progress");
                    clickedTask.addClass("finished");
                }
                clickedTask.on("click", click_on_task);
                $(".popup-task .close-btn").click();
            }
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


$(".chat.new-chat").on("click", function() {
    $(this).slideUp(500);
    $(".chat.new-chat-form").slideDown(500);
    $(".chat.new-chat-form").addClass("active");
})


$(".create-task-button").on("click", function() {
    var title = $(".input-chat-title").val();
    if (title === '') {
        return;
    }
    $(".input-chat-title").val("");

    params = {
        project_id: parseInt($(".project").attr("data-id")),
        title: title
    };

    $.ajax("/ajax/create_chat", {
        method: 'post',
        dataType: 'json',
        data: JSON.stringify(params),
        contentType: "application/json; charset=utf-8",
        success: function(data) {
            if (data["success"]) {
                var html = '<div class="chat">\
    <a class="chat-link" href="/chat/' + data["chat"]["id"] + '">' + data["chat"]["title"] + '</a>\
</div>';
                $(".chat-panel").append(html);
                $(".chat.new-chat-form").slideUp(500);
                $(".chat.new-chat-form").removeClass("active");
                $(".chat.new-chat").slideDown(500);
                $(".new-chat-error-message").css("display", "none");
                $(".new-chat-error-message").text("");
            } else {
                $(".new-chat-error-message").text("Такой чат уже существует");
                $(".new-chat-error-message").css("display", "block");
            }
        }
    })
});