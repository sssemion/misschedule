$(document).ready(function() {

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

    $("#projects__select").on('change', function() {
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
        };
    });
});