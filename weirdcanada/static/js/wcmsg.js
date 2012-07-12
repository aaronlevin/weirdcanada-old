// Javascript to handle push messages
// Channel is stored in `wcmsg` cookie
// listen for `message` event.
// update a div with id `"pushing_message"`

var pusher = new Pusher('7dbbd42f2f88111a3ad5');
// need to pull channel from session cookie
var channel = pusher.subscribe($.cookie('wcmsg'));
var firstMessage = true;
   
channel.bind('message', function(data) {

    if(firstMessage) {
        // Create message div
        $('div#pushing_message').append('<div class="alert">'+data.payload+'</div>');
            firstMessage = false;
        }
        else {
            $('div#pushing_message div.alert').html(data.payload);
        }
});
