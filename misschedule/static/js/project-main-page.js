var popup = $($(".popup-task-wrapper")[0]);

$(".task:not(.task.new-task)").on("click", function() {
    
    $(".popup-task__title").text($(this).children(".task__title").text());
    
    $(".popup-task__description").text($(this).children(".task__description").text());
    if ($(this).children(".task__description").hasClass("no-description")) {
        $(".popup-task__description").addClass("no-description");
    } else {
        $(".popup-task__description").removeClass("no-description");
    }

    $(".popup-task__tag").text($(this).children(".task__tag").text());
    
    $(".popup-task__creator").text($(this).attr("data-creator-name"));
    $(".popup-task__creator").attr("href", "/" + $(this).attr("data-creator-username"));

    $(".popup-task__worker").text($(this).attr("data-worker-name"));
    $(".popup-task__worker").attr("href", "/" + $(this).attr("data-worker-username"));

    $(".popup-task__creation-date").text($(this).attr("data-creation-date-formatted"));
    $(".popup-task__deadline-date").text($(this).attr("data-deadline-date-formatted"));

    popup.children(".popup-task").attr("style", $(this).attr("style"));
    popup.addClass("active");
    $("body").addClass("scroll-locked");
});

$(".popup-task .close-btn").on("click", function() {
    popup.removeClass("active");
    $("body").removeClass("scroll-locked");
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