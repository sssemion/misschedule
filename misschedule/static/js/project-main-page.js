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