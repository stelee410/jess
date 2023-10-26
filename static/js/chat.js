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
function countdown(msg,callback){
    var countdown = document.createElement('div');
    countdown.style.fontSize = '80px';
    countdown.style.textAlign = 'center';
    countdown.style.marginTop = '100px';
    countdown.style.position = 'absolute';
    countdown.style.top = '0';
    countdown.style.width = '100%';
    document.body.appendChild(countdown);
    var timeLeft = 3;

    // Update the countdown timer every second
    var countdownInterval = setInterval(function() {
    // Update the countdown timer text
    countdown.innerHTML = timeLeft;

    // Decrement the time left
    timeLeft--;

    // Stop the countdown when the time reaches 0
    if (timeLeft < 0) {
        clearInterval(countdownInterval);
        countdown.innerHTML = msg;
        callback()
    }
    }, 1000);
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
    if ($("#chat-container").length>0){
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
function flash(message, alert_type) {
    var alert_class = 'alert-' + alert_type;
    var alert_html = '<div class="alert '+alert_class+' alert-dismissible fade show" role="alert">\
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>'+message+'\
                    </div>';
    $('#main').append(alert_html);
}
function showModal(title, body, actionName, actionFn,actionBtnStyle='primary'){
    $('#my-modal-label').html(title);
    $('#my-modal-body').html(body);
    $('#my-modal-action').text(actionName);
    $('#my-modal-action').click(actionFn);
    $('#my-modal-action').removeClass();
    $('#my-modal-action').addClass('btn btn-'+actionBtnStyle);
    $('#my-modal').modal('show');
}

function closeModal(){
    $('#my-modal').modal('hide');
}