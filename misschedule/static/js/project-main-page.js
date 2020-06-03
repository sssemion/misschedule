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

    if ($(this).attr("data-can-you-edit") === '0') {
        $(".popup-task__add-item-button").css("display", "none");
    } else {
        $(".popup-task__add-item-button").css("display", "block");
    }
    
    popup.children(".popup-task").attr("style", $(this).attr("style")); // Цвет фона
    popup.children(".popup-task").attr("data-id", $(this).attr("data-id")); // id
    popup.fadeIn(500);
    popup.addClass("active");
    $("body").addClass("scroll-locked");

    // Проверяем, не вылезает ли окно за границы экрана
    checkTaskHeight();
}

$(".popup-task .close-btn").on("click", function() {
    popup.fadeOut(500, function() {
        popup.removeClass("active");
        clickedTask = null;
        $("body").removeClass("scroll-locked");
    });
});

$(".popup-task__send-button").on("click", function() {
    var taskId = popup.children(".popup-task").attr("data-id");
    var params = {
        task_id: taskId,
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

    // Собираем данные о новых TaskItem-ах
    var params = {
        items: []
    };

    $(".popup-task__add-item-form").each(function() {
        var titleObj = $(this).children(".input-outer").children(".add-item-title");
        var descriptionObj = $(this).children(".input-outer").children(".add-item-description");
        if (titleObj.val() === '') {
            titleObj.addClass("is-invalid");
            $(this).children(".error-msg").text("Заголовок не может быть пустым");
            $(this).children(".error-msg").addClass("active");
        } else {
            titleObj.removeClass("is-invalid");
            $(this).children(".error-msg").removeClass("active");
        }
        params["items"].push({
            task_id: taskId,
            title: titleObj.val(),
            description: descriptionObj.val()
        });
    });
    
    $.ajax("/ajax/create_task_items", {
        method: 'post',
        dataType: 'json',
        data: JSON.stringify(params),
        contentType: "application/json; charset=utf-8",
        success: function(data) {
            var offset = 0;
            for (var i = 0; i < data["items"].length; i++) {
                if (data["items"][i]["success"]) {
                    $(".popup-task__add-item-form:nth-child(" + (i + 1 - offset) + ")").remove();
                    offset++;
                    var itemHtml = '<div class="item" data-id="' + data["items"][i]["taskItem"]["id"] + '">\
    <input class="item__completed" type="checkbox" title="Не выполнено">\
    <div class="item__info">\
        <h4 class="item__title">' + data["items"][i]["taskItem"]["title"] + '</h4>\
        ';
                    if (data["items"][i]["taskItem"]["description"] !== "") {
                        itemHtml += '<p class="item__description">' + data["items"][i]["taskItem"]["description"] + '</p>'
                    } else {
                        itemHtml += '<p class="item__description">Нет описания</p>'
                    }
                    itemHtml += '\
    </div>\
</div>'
                    $(".popup-task__items").append(itemHtml);
                    $(".task[data-id=" + taskId + "] .task__items").append(itemHtml);
                    $(".popup-task__items .item[data-id=" + data["items"][i]["taskItem"]["id"] + "]");
                } else {
                    if (data["items"][i]["message"].indexOf("Task item with title ") == 0) {
                        $(".popup-task__add-item-form:nth-child(" + (i + 1 - offset) + ") > .add-item-title").addClass("is-invalid");
                        $(".popup-task__add-item-form:nth-child(" + (i + 1 - offset) + ") > .error-msg").text("Заголовок не может быть пустым");
                        $(".popup-task__add-item-form:nth-child(" + (i + 1 - offset) + ") > .error-msg").addClass("active");
                    }
                }
            }
        }
    })
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
                clickedTask.remove();
                if (data.condition == 1) {
                    $(".task-list.in-progress").append(taskHtml);
                    clickedTask = $(".tasks__column.in-progress .task.planned");
                    setDeadlineTimer($(".tasks__column.in-progress .task.planned .time-to-deadline"));
                    clickedTask.removeClass("planned");
                    clickedTask.addClass("in-progress");
                } else if (data.condition == 2) {
                    $(".task-list.finished").append(taskHtml);
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


// Создание чата
$(".chat.new-chat:not(.disabled)").on("click", function() {
    $(this).slideUp(500);
    $(".chat.new-chat-form").slideDown(500);
    $(".chat.new-chat-form").addClass("active");
})

$(".create-chat-button").on("click", function() {
    var title = $(".input-chat-title").val();
    if (title === '') {
        return;
    }
    $(".input-chat-title").val("");

    var params = {
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
                $(".chat-panel .chat-list").append(html);
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


// Добавление пользователей в проект
$(".user.add-user:not(.disabled)").on("click", function() {
    $(this).slideUp(500);
    $(".user.add-user-form").slideDown(500);
    $(".user.add-user-form").addClass("active");
});

$(".search-user-button").on("click", function() {
    var username = $(".input-username").val();
    if (username === ''){
        $(".add-user-error-message").text("Введите хотя бы 1 символ");
        $(".add-user-error-message").css("display", "block");
        return;
    } else {
        $(".add-user-error-message").text("");
        $(".add-user-error-message").css("display", "none");
    }

    $(".input-username").val("");
    
    $.ajax("/ajax/search_users", {
        method: 'post',
        dataType: 'json',
        data: JSON.stringify({username: username, project_id: parseInt($(".project").attr("data-id"))}),
        contentType: "application/json; charset=utf-8",
        success: function(data) {
            if (data["success"]) {
                var foundNum = data["found"];
                $(".found-number").text(foundNum);
                $(".select-outer").slideUp(500);
                $(".select-outer").removeClass("active");
                $(".users-select").empty();
                for (var i = 0; i < foundNum; i++) {
                    $(".users-select").append('<option value="' + data["users"][i]["id"] + '">' 
                        + data["users"][i]["first_name"] + ' ' + data["users"][i]["last_name"] + ' @'
                        + data["users"][i]["username"] + '</option>');
                }
                $(".found-users").slideDown(500);
                $(".found-users").addClass("active");
                if (foundNum > 0) {
                    $(".select-outer").slideDown(500);
                    $(".select-outer").addClass("active");
                }
            }
        }
    });
});


$(".add-user-button").on("click", function() {
    var users = $(".users-select").val();
    if (users.length == 0) {
        return;
    }
    
    $.ajax("/ajax/add_users_to_project", {
        method: 'post',
        dataType: 'json',
        data: JSON.stringify({users: users, project_id: parseInt($(".project").attr("data-id"))}),
        contentType: "application/json; charset=utf-8",
        success: function(data) {
            console.log(data);
            if (data["success"]) {
                for (var i = 0; i < data["users"].length; i++) {
                    $(".users-panel .user-list").append('<div class="user">\
    <h3 class="user__name">' + data["users"][i]["first_name"] + ' '
            + data["users"][i]["last_name"] + '</h3>\
    <a class="user__username" href="/users/' + data["users"][i]["username"] + '">@'
            + data["users"][i]["username"] + '</a>\
    <p class="user__email">Email: <a class="email-link" href="mailto:'
            + data["users"][i]["username"] + '">' + data["users"][i]["username"] + '</a></p>\
</div>');
                }
                $(".select-outer").removeClass("active");
                $(".user.add-user").slideDown(500);
                $(".user.add-user-form").slideUp(500);
                $(".user.add-user-form").removeClass("active");
            }
        }
    });
});

// Создание TaskItem-ов
const addItemForm = '<div class="popup-task__add-item-form">\
    <div class="input-outer">\
        <label for="add-item-title">Заголовок</label>\
        <input type="text" class="input-str add-item-title" id="add-item-title">\
    </div>\
    <p class="error-msg"></p>\
    <div class="input-outer">\
        <label for="add-item-description">Описание</label>\
        <input type="text" class="input-str add-item-description" id="add-item-description">\
    </div>\
    <span class="remove-form">&#10060;</span>\
</div>'

$(".popup-task__add-item-button").on("click", function() {
    $(".popup-task__add-item-form-container").append(addItemForm);
    $(".popup-task__add-item-form .remove-form").on("click", removeItemOnClick);
    checkTaskHeight();
});

function removeItemOnClick() {
    $(this).parent(".popup-task__add-item-form").remove();
    checkTaskHeight();
};

// Чтобы всплывающая задача не вылезала за границы экрана
function checkTaskHeight() {
    if ($(".popup-task").height() > $(".popup-task-wrapper.detail-info").height() * 0.8) {
        $(".popup-task-wrapper").css("justify-content", "flex-start");
    } else {
        $(".popup-task-wrapper").css("justify-content", "center");
    }
}

// Раскрывающийся список пользователей для маленьких экранов
$(".users-panel__heading .expand-button").on("click", function() {
    var usersPanel = $(".users-panel");
    if (usersPanel.hasClass("expanned")) {
        $(".users-panel .user-list").slideUp(500, clearStyleDisplay);
    } else {
        $(".users-panel .user-list").slideDown(500);
    }
    usersPanel.toggleClass("expanned");
});

// Раскрывающийся список чатов для маленьких экранов
$(".chat-panel__heading .expand-button").on("click", function() {
    var chatPanel = $(".chat-panel");
    if (chatPanel.hasClass("expanned")) {
        $(".chat-list").slideUp(500, clearStyleDisplay);
    } else {
        $(".chat-list").slideDown(500);
    }
    chatPanel.toggleClass("expanned");
});

function clearStyleDisplay() {
    console.log($(this));
    $(this).attr("style", $(this).attr("style").replace(/display:\s.+;/g, ""));
}