$(".time-to-deadline").each(function() {
    var element = $(this);
    var seconds = parseInt(element.attr("data-seconds"));
    var total = parseInt(element.attr("data-duration"));
    var intervalId = setInterval(function() {
        seconds--;
        element.text(getTimeRemainingString(seconds));
        if (seconds < total / 10)
        element.addClass("close-to-passing")
        if (seconds < 0) {
            element.text("дедлайн прошел");
            element.attr("data-seconds", "-1");
            try {
                sort_tasks_by_time();
                if ($("#tasks__select")[0].value == "closer-to-deadline")
                    for (var i = 0; i < tasks.length; i++)
                        $(tasks[tasks_time_order[i]]).css("order", i + 1);
            } catch (e) {}
            clearInterval(intervalId);
        }
    }, 1000);
});

function getTimeRemainingString(seconds){
    var minutes = Math.floor((seconds/60)) % 60;
    var hours = Math.floor((seconds/(60*60))) % 24;
    var days = Math.floor(seconds/(60*60*24));

    var ans = "";
    if (days > 0) 
        ans += days + "д ";
    if (hours > 0) {
        if (hours < 10)
            ans += 0
        ans += hours + ":";
    }
    if (minutes < 10)
        ans += 0;
    ans += minutes + ":";
    if (seconds % 60 < 10)
        ans += 0;
    ans += seconds % 60;
    return ans;
}