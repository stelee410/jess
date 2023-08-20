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