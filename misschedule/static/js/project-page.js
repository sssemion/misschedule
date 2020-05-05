$(document).ready(function() {
    $("#projects__select").on('change', projectsSelectChanged);
    $("#tasks__select").on('change', tasksSelectChanged);
});

// PROJECTS
var projects = $(".project:not(.new-project)");
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