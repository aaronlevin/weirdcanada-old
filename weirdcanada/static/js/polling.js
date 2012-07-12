var prev_data = null; // remember previous data fetched

function display_data(data) {

	if (data && (data != prev_data)) {
		setTimeout(function() {$('div#polling_message').html(data.payload);	},500);
		prev_data = data;
	}
}

function poll_and_update() {
	// Load data from /ajax/polldata
	
	var url = '/ajax/polldata';
	$.ajax({ url: url,
			success: function(data) {
				if(data.updated == true) {
					display_data(data);
				}
			},
			dataType: "json",
			//complete: poll_and_update,
			timeout: 30000
	});

	return true;
}

