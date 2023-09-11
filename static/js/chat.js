function addEmoji(emoji) {
     // Get the emoji element
     var emoji = $('<div class="emoji" style="display:none">' + emoji + '</div>');
     $('body').append(emoji);

     emoji.fadeIn(1000);

     // Zoom in and out the emoji repeatedly
     var interval = setInterval(function() {
         emoji.addClass('zoom-in').removeClass('zoom-out');
         setTimeout(function() {
             emoji.addClass('zoom-out').removeClass('zoom-in');
         }, 500);
     }, 1000);

     // Stop the animation after 10 seconds
     setTimeout(function() {
         clearInterval(interval);
         emoji.remove();
     }, 5000);
}

function showLove(){
    addEmoji('&#x2764;')
}
function submitMsg(){
    if($("#msgForm textarea").val().trim()!==""){
        $("#msgForm").submit();
        $('#msgForm').html('<p class=text-black>等待对方响应...</p>');
    }
}
var resizeId;
function doneResizing(){
    $('#chatbox').width($(window).width()*0.8);
    $('#chatbox').height($(window).height()*0.8);
    if (("#chat-container").length){
        $("#chat-container")[0].scrollTop = $("#chat-container")[0].scrollHeight;
        $("#content").focus()
    }
}
$(document).ready(function(){
    $('#action_menu_btn').click(function(){
        $('.action_menu').toggle();
    });
    doneResizing();
    $(window).resize(function(){
        clearTimeout(resizeId);
        resizeId = setTimeout(doneResizing, 500);
      });
});
