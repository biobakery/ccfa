$(document).ready ->
  MIBC = {}
  MIBC._val = (el) ->
    (if el.type is "checkbox" then el.checked else el.value)

  MIBC.generate_metadata = ->
    records = {}
    rows = []
    $("#metadata input[required], #metadata select[required]").each (i, el) ->
      if typeof (records[@name]) is "undefined"
        records[@name] = [MIBC._val(this)]
      else
        records[@name].push MIBC._val(this)
      return

    $.each records, (key, val) ->
      rows.push [
        key
        val.join(",")
      ].join("\t")
      return

    rows.join "\n"

  MIBC.rowdel = ->
    $(this).parents().filter(".row").remove()
    return

  MIBC.url = (el) ->
    $(el).attr
      href: "data:Content-type: text/plain, " + escape(MIBC.generate_metadata())
      download: "metadata.txt"

    return

  
  # Validation logic
  validator = $("form").validate(
    debug: true
    errorLabelContainer: "#message_box"
    wrapper: "span"
    invalidHandler: (event, validator) ->
      $("#message_box").removeClass "hidden"
      return

    successHandler: (event, validator) ->
      $(this).removeClass("btn-primary").addClass "btn-success"
      return

    rules:
      "16s_data":
        required: false

      submit_to_insdc:
        required: false

    messages:
      pi_first_name: "Please include a first name for the principle investigator"
      pi_last_name: "Please fill in the principle investigator's last name"
      pi_contact_email: "Please provide an email from the principle investigator"
      lab_name: "Please define a lab for this data submission"
      researcher_first_name: "Please fill in a first name for the researcher"
      researcher_last_name: "Please fill in a last name for the researcher"
      researcher_contact_email: "Please provide an email address for the researcher"
      study_title: "Please give your study a title"
      study_description: "Please describe the question your study is addressing"
      sample_type: "Please select a sample type"
      collection_start_date: "Please give a valid date for when data collection started"
      collection_end_date: "Please give a valid date for when data collection finished"
      geo_loc_name: "Please supply the geographic location of your sequence"
      lat_lon: "Please give the latitude and longitude of your location"
      feature: "Please describe the feature presented"
      reverse_primer: "Please fill in the reverse primer you used"
      platform: "Please fill in what platform you used for 16s sequencing"
      filename: "Please include at least one Filename"
  )
  
  # Event listeners
  $(".rowadd").click ->
    gparents = $(this).parent().parent()
    anchor = $(gparents).clone().insertAfter(gparents).find("a")
    anchor.on "click", MIBC.rowdel
    anchor.children().first().removeClass("rowadd icon-plus-sign").addClass "icon-minus-sign"
    return

  $("#metadata input[type=checkbox]").click ->
    row = $("#" + @name)
    row.toggleClass "hidden"
    row.children().attr "required", (idx, oldAttr) ->
      not oldAttr

    return

  $("#save_btn").click ->
    if $("form").valid() or $("#save_override")[0].checked
      $(this).removeClass("btn-primary").addClass "btn-success"
      MIBC.url this
    else
      $(this).removeClass("btn-primary").addClass "btn-danger"
      $(this).attr "href", "#"
    return

  return

