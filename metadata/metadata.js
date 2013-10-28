$(document).ready(function(){

    MIBC = {};

    MIBC._val = function( el ) {
	return el.type == "checkbox" ?
	    el.checked
	    : el.value
    };

    MIBC.generate_metadata = function() {
	var records = {},
	    rows    = [];

	$('#metadata input[required]').each(function(i, el){
	    if (typeof(records[this.name]) === "undefined") {
		records[this.name] = [MIBC._val(this)]
	    } else {
		records[this.name].push(MIBC._val(this))
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

    MIBC.url = function( el ){
	$(el).attr( 'href',
		    'data:Content-type: text/plain, '+
		    escape(MIBC.generate_metadata()) );
    };

    // Validation logic

    validator = $('form').validate({
	debug: true,

	errorLabelContainer : "#message_box",
	wrapper             : "span",

	invalidHandler : function( event, validator ) {
	    $('#message_box').removeClass("hidden");
	},

	successHandler : function( event, validator ) {
	    $(this).removeClass('btn-primary').addClass('btn-success');
	},

	rules : {
	    "16s_data": {
		required : false
	    },
	    submit_to_insdc: {
		required: false
	    }
	},

	messages: {
	    pi_first_name            : "Please include a first name for the principle investigator",
	    pi_last_name             : "Please fill in the principle investigator's last name",
	    pi_contact_email         : "Please provide an email from the principle investigator",
	    lab_name                 : "Please define a lab for this data submission",
	    researcher_first_name    : "Please fill in a first name for the researcher",
	    researcher_last_name     : "Please fill in a last name for the researcher",
	    researcher_contact_email : "Please provide an email address for the researcher",
	    study_title              : "Please give your study a title",
	    study_description        : "Please describe the question your study is addressing",
	    sample_type              : "Please select a sample type",
	    collection_start_date    : "Please give a valid date for when data collection started",
	    collection_end_date      : "Please give a valid date for when data collection finished",
	    geo_loc_name             : "Please supply the geographic location of your sequence",
	    lat_lon                  : "Please give the latitude and longitude of your location",
	    feature                  : "Please describe the feature presented",
	    reverse_primer           : "Please fill in the reverse primer you used",
	    platform                 : "Please fill in what platform you used for 16s sequencing",
	    filename                 : "Please include at least one Filename"
	}

    });
    
    // Event listeners
    
    $('.rowadd').click( function() {
	gparents = $(this).parent().parent();
	anchor = $(gparents).clone().insertAfter(gparents).find('a');
	anchor.on('click', MIBC.rowdel);
	anchor.children().first().removeClass('rowadd icon-plus-sign').addClass('icon-minus-sign');
    });

    $('#metadata input[type=checkbox]').click( function() {
	row = $("#"+this.name);
	row.toggleClass('hidden'); 
	row.children().attr('required', function(idx, oldAttr){ return !oldAttr });
    });
    
    $('#save_btn').click( function() {
	if ( $('form').valid() || $('#save_override')[0].checked ) {
	    $(this).removeClass('btn-primary').addClass('btn-success');
	    MIBC.url(this);
	} else {
	    $(this).removeClass('btn-primary').addClass('btn-danger');
	    $(this).attr('href', '#');
	}
    });
    
});