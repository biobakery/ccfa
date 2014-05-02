MIBC = {}

MIBC.config =
  api_base: "/mibc/"

MIBC.error = (msg) ->
  $("#errmsg").text(msg).removeClass("hidden")

MIBC.noerror = ->
  $("#errmsg").empty().addClass("hidden")

MIBC.loadwrapper = (user, proj, loadfunc) ->
  if not user? or not proj?
    MIBC.error "Need a User name and Project name, please"
    return
  if $("#results").children().length > 0
    MIBC.clear()
  $("#load_btn").attr "href", "#"+[user, proj].join("/")
  loadfunc user, proj
  MIBC.noerror()
    
MIBC.url = (el) ->
  $(el).attr
    href: "data:Content-type: text/plain, " + escape(MIBC.generate_metadata())
    download: "metadata.txt"
  return
