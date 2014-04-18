
import sys
from functools import wraps
from itertools import izip, chain

from bottle import (
    run,
    get,
    abort,
    request
)

from . import (
    settings,
    validate,
    models,
    util,
    efo
)

repo = models.Repository()

def authentication_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not request.headers.get("Authorization", "").startswith("Basic "):
            abort(401, 'Auth please!')
        return f(*args, **kwargs)
    return wrapper
            
def project_or_404(username, projectname):
    project = repo.users[username].projects[projectname]
    if not project.exists():
        abort(404, "Project not found")
    else:
        return project


@get('/')
@get('//')
@authentication_required
def root_get():
    return util.serialize({ 'users': repo.users.all() })

@get('/<name>')
@get('//<name>')
def user_get(name):
    user = repo.users[name]
    if user.exists():
        return util.serialize(user)
    else:
        abort(404, 'User not found')

@get('/<username>/<projectname>')
@get('//<username>/<projectname>')
def project_get(username, projectname):
    project = project_or_404(username, projectname)
    return util.serialize(project)



@get('/<username>/<projectname>/validate')
@get('//<username>/<projectname>/validate')
def validate_get(username, projectname):
    project = project_or_404(username, projectname)
    validation_results = validate.validate(project)
    return util.serialize(validation_results)

@get('/<username>/<projectname>/mapvalidate')
@get('//<username>/<projectname>/mapvalidate')
def mapvalidate_get(username, projectname):
    project = project_or_404(username, projectname)
    
    to_validate = list()
    for line_idx, line in enumerate(chain(
            (project.map_headers,), project.map)):
        guesses = enumerate(efo.guess(*line).items())
        to_validate.extend(
            [ ((line_idx, col_idx), efo_id)
              for col_idx, (efo_id, guess) in guesses 
              if guess is True]
        )

    coords, efo_ids = izip(*to_validate)
    validation_results = zip(coords,efo.parallel_validate(*efo_ids).items())

    return util.serialize(validation_results)
        


def main():
    run(host=settings.web.host, port=settings.web.port, 
        debug=True, reloader=True)

if __name__ == '__main__':
    ret = main()
    sys.exit(ret)
