
# from MIBC: MIBC

$(document).ready ->

  MIBC.error = (msg) ->
    $("#errmsg").text(msg).removeClass("hidden")

  MIBC.noerror = ->
    $("#errmsg").empty().addClass("hidden")

  MIBC.loadwrapper = (user, proj) ->
    if not user? or not proj?
      MIBC.error "Need a User name and Project name, please"
      return
    if $("#validation_errors").children().length > 0
      MIBC.clear()
    $("#load_btn").attr "href", "#"+[user, proj].join("/")
    MIBC.load_validation user, proj
    MIBC.noerror()
    
  MIBC.load_validation = (user, proj) ->
    $("#loading").removeClass("hidden")
    $.get MIBC.config.api_base + ["projects", user, proj, "validate"].join "/"
      .done (data) ->
        MIBC.display_results $.parseJSON(data)
        MIBC.noerror()
      .error (jqxhr, status, errormsg) ->
        MIBC.error errormsg
      .always ->
        $("#loading").addClass("hidden")

  MIBC.clear = ->
    $("#validation_errors").empty()
    $("#status").addClass "hidden"

  MIBC.display_results = (data) ->
    window.MIBCdata = data
    allclear = true
    for report in data
      [status, message] = report
      if status is not true
        allclear = false
        $("#validation_errors").append $("#error_tpl").clone().text(message)
    if allclear is true
      $("#status")
        .removeClass("hidden btn-danger glyphicon-thumbs-down")
        .addClass("btn-success glyphicon-thumbs-up")
    else
      $("#status")
        .removeClass("hidden btn-success glyphicaon-thumbs-up")
        .addClass("btn-danger glyphicon-thumbs-down")


  $("#load_btn").click ->
    [user, proj] = ( $(query).val() for query in ["#load_usr", "#load_proj"] )
    MIBC.loadwrapper user, proj

  if window.location.hash?
    [user, proj] = window.location.hash.replace("#", "").split "/"
    if user? and proj?
      MIBC.loadwrapper user, proj
    



