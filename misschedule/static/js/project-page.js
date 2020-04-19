$(document).ready(function() {
    $("#projects__select").on('change', projectsSelectChanged);
    $("#tasks__select").on('change', tasksSelectChanged);
});

// PROJECTS
var projects = $(".project");
var projects_order = [];
for (var i = 0; i < projects.length; i++)
    projects_order.push(i);
projects_order.sort(function(a, b) {
    a = projects[a];
    b = projects[b];
    if (a['firstElementChild']['textContent'] > b['firstElementChild']['textContent'])
        return 1;
    else if (a['firstElementChild']['textContent'] == b['firstElementChild']['textContent'])
        return 0;
    else 
        return -1;
});

// TASKS
var tasks = $(".task");
var tasks_alph_order = [];
var tasks_time_order = [];
for (var i = 0; i < tasks.length; i++) {
    tasks_alph_order.push(i);
    tasks_time_order.push(i);
}
tasks_alph_order.sort(function(a, b) {
    a = tasks[a];
    b = tasks[b];
    if (a['firstElementChild']['textContent'] > b['firstElementChild']['textContent'])
        return 1;
    else if (a['firstElementChild']['textContent'] == b['firstElementChild']['textContent'])
        return 0;
    else 
        return -1;
});

function sort_tasks_by_time() {
    tasks_time_order.sort(function(a, b) {
        a = parseInt($(tasks[a]).children(".task__deadline").children(".time-to-deadline").attr("data-seconds"));
        b = parseInt($(tasks[b]).children(".task__deadline").children(".time-to-deadline").attr("data-seconds"));
        if (a < 0)
            return 1;
        if (b < 0)
            return -1;
        if (a > b)
            return 1;
        else if (a == b)
            return 0;
        else 
            return -1;
    });
}
sort_tasks_by_time();

function projectsSelectChanged() {
    var value = this.value;
    switch (value) {
        case "date-older":
            for (var i = 0; i < projects.length; i++)
                $(projects[i]).css("order", i + 1);
            break;
        case "date-newer":
            for (var i = 0; i < projects.length; i++)
                $(projects[i]).css("order", projects.length - i);
            break;
        case "alphabet-normal":
            for (var i = 0; i < projects.length; i++) {
                $(projects[projects_order[i]]).css("order", i);
            }
            break;
        case "alphabet-reversed":
            for (var i = 0; i < projects.length; i++)
                $(projects[projects_order[i]]).css("order", projects.length - i);
            break;
    }
}

function tasksSelectChanged() {
    var value = this.value;
    switch (value) {
        case "date-older":
            for (var i = 0; i < tasks.length; i++)
                $(tasks[i]).css("order", i + 1);
            break;
        case "date-newer":
            for (var i = 0; i < tasks.length; i++)
                $(tasks[i]).css("order", tasks.length - i);
            break;
        case "closer-to-deadline":
            for (var i = 0; i < tasks.length; i++)
                $(tasks[tasks_time_order[i]]).css("order", i + 1);
            break;
        case "alphabet-normal":
            for (var i = 0; i < tasks.length; i++) {
                $(tasks[tasks_alph_order[i]]).css("order", i + 1);
            }
            break;
        case "alphabet-reversed":
            for (var i = 0; i < tasks.length; i++)
                $(tasks[tasks_alph_order[i]]).css("order", tasks.length - i);
            break;
    }
}

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
            sort_tasks_by_time();
            if ($("#tasks__select")[0].value == "closer-to-deadline")
                for (var i = 0; i < tasks.length; i++)
                    $(tasks[tasks_time_order[i]]).css("order", i + 1);
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