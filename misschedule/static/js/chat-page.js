$(document).ready(function() {
    scorllChatToBottom();
    setInterval(checkForNewMessages, 5000);
    $(".text-message").focus();
});

var pollingPaused = false;

function scorllChatToBottom(){
    var chatResult = $('.messages');
    chatResult.scrollTop(chatResult.prop('scrollHeight'));
}

$(".text-message").keyup(function(e) {
    if (e.keyCode == 13 && !e.shiftKey) {
        $(this).val($(this).val().slice(0, -1));
        $(".send-button").click();
    }
});

$(".send-button").on("click", function() {
    var messageText = $(".text-message").val();
    if (messageText === '') {
        return;
    }
    $(".text-message").val("");

    params = {
        chat_id: parseInt($(".chat-name").attr("data-id")),
        message: messageText
    };

    pollingPaused = true;
    checkForNewMessages(true, function() {
        $.ajax("/ajax/send_message", {
            method: 'post',
            dataType: 'json',
            data: JSON.stringify(params),
            contentType: "application/json; charset=utf-8",
            success: function(data) {
                if(data.success) {
                    addMessage(data["id"], messageText, data["date"], data["user"]);
                }
            },
            complete: function() {
                pollingPaused = false;
            }
        })
    });
    
});


$(".user.add-user").on("click", function() {
    $(this).slideUp(500);
    $(".user.add-user-form").slideDown(500);
    $(".user.add-user-form").addClass("active");
})

// Раскрывающийся список пользователей для маленьких экранов
$(".users-column__heading .expand-button").on("click", function() {
    var usersColumn = $(".users-column");
    if (usersColumn.hasClass("expanned")) {
        $(".users-column .user-list").slideUp(500, clearStyleDisplay);
    } else {
        $(".users-column .user-list").slideDown(500);
    }
    usersColumn.toggleClass("expanned");
});

function checkForNewMessages(force=false, callback=function(){}) {
    if (pollingPaused && !force) {
        return;
    }
    var params = {
        chat_id: parseInt($(".chat-name").attr("data-id")),
        last_message_id: parseInt($(".message:last-child").attr("data-id"))
    };
    $.ajax("/ajax/check_for_new_messages", {
        method: 'post',
        dataType: 'json',
        data: JSON.stringify(params),
        contentType: "application/json; charset=utf-8",
        success: function(data) {
            if (data.length > 0) {
                for (var i = 0; i < data.length; i++) {
                    addMessage(data.messages[i].message.id, data.messages[i].message.message,
                        data.messages[i].message.date, data.messages[i].user);
                }
            }
            callback();
        }
    })
}

function addMessage(id, message, date, user) {
    var html = '<div class="message" data-id="' + id + '">\
    <div>\
        <h3 class="message__addresser">' + user["first_name"] + ' ' + user["last_name"] + '</h3>\
        <p class="message__date date-field">' + date + '</p>\
    </div>\
    <p class="message__text">' + message + '</p>\
</div>';
    $(".messages").append(html);
    formatDate($(".messages .message:last-child .date-field"));
    scorllChatToBottom();
}