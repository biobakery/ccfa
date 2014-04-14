
import sys
from functools import wraps

from bottle import (
    run,
    get,
    abort,
    request
)

from . import (
    settings,
    models,
    util
)

repo = models.Repository()

def authentication_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not request.headers.get("Authorization", "").startswith("Basic "):
            abort(401, 'Auth please!')
        return f(*args, **kwargs)
    return wrapper
            
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
    project = repo.users[username].projects[projectname]
    if project.exists():
        return util.serialize(project)
    else:
        abort(404, 'Project not found')


def main():
    run(host=settings.web.host, port=settings.web.port, 
        debug=True, reloader=True)

if __name__ == '__main__':
    ret = main()
    sys.exit(ret)
