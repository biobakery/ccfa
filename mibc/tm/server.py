import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import os, sys
 
 
class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print 'new connection'
        self.write_message("Hello World")
      
    def on_message(self, message):
        print 'message received %s' % message
 
    def on_close(self):
      print 'connection closed'
 
 
#application = tornado.web.Application([
#    (r'/ws', WSHandler),
#])

def tmHandler(*args, **kwargs):
    print "tmHander() called."
    for k,v in enumerate(args):
        print v.rstrip('\n')
    #print "tmHander() exiting."
    tmpid.stdout.read_until('\n', callback=tmHandler)
 
def tmHandlerError(*args, **kwargs):
    #print "tmHanderError() called."
    #for k,v in enumerate(args):
    #    print 'tmHandlerError: {0}, {1}'.format(k, v)
    #print "tmHanderError() exiting."
    tmpid.stderr.read_until('\n', callback=tmHandlerError)


if __name__ == "__main__":

    global tmpid
    #jsonfile = os.path.join(os.getcwd(), "data.json")
    # launch our task manager
    nullfile = open(os.devnull, 'w')

    tmpid = tornado.process.Subprocess(['mibc_tm', '-l', 'local', '-g', '1'], 
            stdin=tornado.process.Subprocess.STREAM,
            stdout=tornado.process.Subprocess.STREAM,
            stderr=tornado.process.Subprocess.STREAM)

    tmpid.stdout.read_chunk_size = 4
    #fd = tmpid.stdout.fileno()
    #print type(fd)

    tmpid.stdout.read_until('\n', callback=tmHandler)
    tmpid.stderr.read_until('\n', callback=tmHandlerError)

    data = sys.stdin.read()
    print >> tmpid.stdin, data
    tmpid.stdin.close()
    print "finsihed with data"

    routes = (
        ( r'/', WSHandler),
        )

    app_settings = dict(
        static_path=os.path.join(os.path.dirname(__file__), 'static'),
        template_path=os.path.join(os.path.dirname(__file__), 'templates'),
        debug='debug')
    app = tornado.web.Application( routes, **app_settings )
    app.listen(8888)
    ioloop = tornado.ioloop.IOLoop.instance()

    try:
        ioloop.start()
    except KeyboardInterrupt:
        log.info('Keyboard interrupt. Shutting down...')

    #http_server = tornado.httpserver.HTTPServer(application)
    #http_server.listen(8888)
    #tornado.ioloop.IOLoop.instance().start()
