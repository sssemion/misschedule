$(document).ready(scorllChatToBottom);

function scorllChatToBottom(){
    var chatResult = $('.messages');
    chatResult.scrollTop(chatResult.prop('scrollHeight'));
}

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
    
    $.ajax("/ajax/send_message", {
        method: 'post',
        dataType: 'json',
        data: JSON.stringify(params),
        contentType: "application/json; charset=utf-8",
        success: function(data) {
            if(data.success) {
                var html = '<div class="message">\
    <div>\
        <h3 class="message__addresser">' + data["user"]["first_name"] + ' ' + data["user"]["last_name"] + '</h3>\
        <p class="message__date">' + data["date"] + '</p>\
    </div>\
    <p class="message__text">' + messageText + '</p>\
</div>';
                $(".messages").append(html);
                scorllChatToBottom();
            }
        }
    })
});


$(".user.add-user").on("click", function() {
    $(this).slideUp(500);
    $(".user.add-user-form").slideDown(500);
    $(".user.add-user-form").addClass("active");
})