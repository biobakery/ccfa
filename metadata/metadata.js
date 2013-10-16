$(document).ready(function(){

    MIBC = {};

    MIBC._val = function(el) {
	if (el.type == "checkbox") {
	    return el.checked
	} else {
	    return el.value
	}
    }

    MIBC.generate_metadata = function() {
	var records = {},
	    rows    = [];

	$('#metadata input').each(function(i, el){
	    if (typeof(records[this.placeholder]) === "undefined") {
		records[this.placeholder] = [MIBC._val(this)]
	    } else {
		records[this.placeholder].push(MIBC._val(this))
	    }
	});
	$.each(records, function(key, val){ 
	    rows.push(
		[
		    key, 
		    val.join(',')
		].join('\t')
	    );
	});
	return rows.join('\n');
    };

    // Event listeners
    
    $('.rowadd').click(function() {
	gparents = $(this).parent().parent();
	$(gparents).clone().insertAfter(gparents).children().remove('a');
    });

    $('#metadata input[type=checkbox]').click( function(){
	row = $("#"+this.placeholder);
	row.toggleClass('hidden'); 
	row.children().attr('required', function(idx, oldAttr){ return !oldAttr });
    });

    $('#save_btn').click(function() {
	inputs = $('#metadata input');
	inputs.validate();
	$(this).attr( 'href',
			  'data:Content-type: text/plain, '+
			  escape(MIBC.generate_metadata()) );
    });
    
});