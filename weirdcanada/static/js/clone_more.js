function node_iterator() {

    //task:function,node:HTML Node
    this.iterate = function iterate(task, node) {

        task(node);
        for (var x = 0; x < node.childNodes.length; x++) {
            var childNode = node.childNodes[x];
            this.iterate(task, childNode);
        }
    }
}

function attr(node) {
    var tmpArray;
    var tmpLength;
    var tmpString = '';
    var tmpDigitHolder = Array();
	var lastDigitLocation;
	var reg = new RegExp('[0-9]');
    for (var i in node.attributes) {
        // ensure nodeType is "attribute"
        if ( (node.attributes[i].nodeType == 2) ) {
            //ensure value matches slug 
            if (reg.test(node.attributes[i].value) && (node.attributes[i].nodeName != 'value') ) {
                // Parse out stuff before dash and increment
                tmpArray = node.attributes[i].value.split('-');
                tmpLength = node.attributes[i].value.split('-').length;
                tmpString = '';

				//Determine location of digits in tmpArray
				for (var j=0; j < tmpArray.length; j++) {
					if ( ! isNaN(parseInt(tmpArray[j])) ) {
						tmpDigitHolder.push(j);
					}
				}
				lastDigitLocation = tmpDigitHolder.pop();

				// Loop through array and increment only the last digit
                for (var j = 0; j < tmpArray.length; j++) {
                    if ( j == lastDigitLocation ) {
                        tmpString += parseInt(tmpArray[j]) + 1;
                    }
                    else {
                        tmpString += tmpArray[j];
                    }

					if( j != (tmpLength-1) ) {
						tmpString += '-';
					}
                }
                node.attributes[i].value = tmpString;
            }
        }
    }
}

function split_increment(text, delim) {

	var tmpDigit = 0;
	var tmpString = '';
	var tmpArray = text.split(delim);

	for( var j=0 ; j< tmpArray.length ; j++) {
		
		if( ! isNaN(parseInt(tmpArray[j])) ) {
			tmpDigit = parseInt(tmpArray[j]);
			tmpDigit += 1;
			tmpString += tmpDigit.toString();
		}
		else {
			tmpString += tmpArray[j];
		}

		if ( j != (tmpArray.length - 1) ) {
			tmpString += '-';
		}
	}

	return(tmpString);
}

function clone_div(selector) {
	$('#'+selector).after(function(index) {
		var value = $(this).find('legend:first').text();
		var bodyElement = $(this).clone(true);
		bodyElement.find('legend:first')
					.replaceWith('<legend>' 
						+ split_increment(value,'-') 
						+ '</legend>'
					);
		bodyElement = bodyElement.get(0)
		var htmlNodeIterator = new node_iterator();
		htmlNodeIterator.iterate(attr, bodyElement);
		return bodyElement;
	});
}
