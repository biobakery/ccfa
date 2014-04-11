
import sys

from bottle import (
    run,
    abort,
    route,
    request
)

from . import (
    settings,
    util
)

def authentication_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not request.headers.get("Authorization", "").startswith("Basic "):
            abort(401, 'Auth please!')
        return f(*args, **kwargs)
            
            

@route('/:#.*#')
@authentication_required
def debug():
    return util.serialize(dict(request.headers))

def main():
    run(host=settings.web.host, port=settings.web.port, 
        debug=True, reloader=True)

if __name__ == '__main__':
    ret = main()
    sys.exit(ret)
