# from MIBC: MIBC

$(document).ready ->

  MIBC.load_efovalidation = (user, proj) ->
    $("#loading").removeClass("hidden")
    $.get MIBC.config.api_base + ["projects", user, proj, "validate"].join "/"
      .done (data) ->
        MIBC.display_results $.parseJSON(data)
        MIBC.noerror()
      .error (jqxhr, status, errormsg) ->
        MIBC.error errormsg
      .always ->
        $("#loading").addClass("hidden")

  MIBC.load_samplemeta = (user, proj) ->
    $("#loading").removeClass("hidden")
    $.get MIBC.config.api_base + ["projects", user, proj].join "/"
      .done (data) ->
        MIBC.display_samplemeta $.parseJSON(data)
        MIBC.noerror()
      .error (jqxhr, status, errormsg) ->
        MIBC.error errormsg
      .always ->
        $("#loading").addClass("hidden")

  MIBC.clear = ->
    $("#results").empty()

  MIBC.display_samplemeta = (data) ->
    window.MIBCdata = data
    $("#results").append "<tr><th>" \
                         + data.map_headers.join("</th><th>") \
                         + "</th></tr>"
                 .append ( "<tr><td>"+row.join("</td><td>")+"</td></tr>" \
                           for row in data.map )



  $("#load_btn").click ->
    [user, proj] = ( $(query).val() for query in ["#load_usr", "#load_proj"] )
    MIBC.loadwrapper user, proj, MIBC.load_samplemeta

  $("#validate_btn").click ->
    [user, proj] = ( $(query).val() for query in ["#load_usr", "#load_proj"] )
    MIBC.loadwrapper user, proj, MIBC.load_efovalidation

  if window.location.hash?
    [user, proj] = window.location.hash.replace("#", "").split "/"
    if user? and proj?
      MIBC.loadwrapper user, proj, MIBC.load_samplemeta
    



