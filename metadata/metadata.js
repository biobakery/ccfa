$(document).ready(function(){

    MIBC = {};

    MIBC._val = function( el ) {
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

    MIBC.rowdel = function() {
	$(this).parents().filter('.row').remove();
    };

    //

    $('form').validate({
	debug: true
    });

    // Event listeners

    $('.rowadd').click(function() {
	gparents = $(this).parent().parent();
	anchor = $(gparents).clone().insertAfter(gparents).find('a');
	anchor.on('click', MIBC.rowdel);
	anchor.children().first().removeClass('rowadd icon-plus-sign').addClass('icon-minus-sign');
    });

    $('#metadata input[type=checkbox]').click( function(){
	row = $("#"+this.placeholder);
	row.toggleClass('hidden'); 
	row.children().attr('required', function(idx, oldAttr){ return !oldAttr });
    });

    $('#save_btn').click(function() {
	if ( $('form').valid() ) {
	    $(this).attr( 'href',
			  'data:Content-type: text/plain, '+
			  escape(MIBC.generate_metadata()) );
	} else {
	    console.log("Not saving file b/c the form is invalid!");
	}
    });
    
});