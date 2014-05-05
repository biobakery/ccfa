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

  MIBC.extract_from_dom = ->
    ( (field.innerText for field in row.children) \
      for row in $("#results tr").get() )

  MIBC.serialize = (arr) ->
    rows = ( row.join('\t') for row in arr )
    rows.join('\n')

  MIBC.display_samplemeta = (data) ->
    window.MIBCdata = data
    $("#results").append "<tr><th>" \
                         + data.map_headers.join("</th><th>") \
                         + "</th></tr>"
                 .append ( "<tr><td>"+row.join("</td><td>")+"</td></tr>" \
                           for row in data.map )

  MIBC.finish_edit = (el) ->
    v = el.value
    $(el).parent()
      .empty()
      .text(v)
      .removeClass("in_edit")
      .click(MIBC.start_edit)

  MIBC.start_edit = ->
    return if $(this).hasClass "in_edit" 
    t = this.innerText
    $(this).empty().append( $("<input>").attr(
        type:  "text"
        value: t
        width: "100%"
      ).on(
        blur: ->
          MIBC.finish_edit(this)
        keyup: ->
          MIBC.finish_edit(this) if event.which is MIBC.keys.ENTER
      )
    ).addClass("in_edit")

  $("#load_btn").click ->
    [user, proj] = ( $(query).val() for query in ["#load_usr", "#load_proj"] )
    MIBC.loadwrapper user, proj, MIBC.load_samplemeta

  $("#validate_btn").click ->
    [user, proj] = ( $(query).val() for query in ["#load_usr", "#load_proj"] )
    MIBC.loadwrapper user, proj, MIBC.load_efovalidation

  $("#save_btn").click ->
    a = MIBC.extract_from_dom()
    MIBC.url this, MIBC.serialize(a), "map.txt"

  $("#results").on "click", "td", MIBC.start_edit

  if window.location.hash?
    [user, proj] = window.location.hash.replace("#", "").split "/"
    if user? and proj?
      MIBC.loadwrapper user, proj, MIBC.load_samplemeta
    



