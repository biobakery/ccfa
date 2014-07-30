#!/usr/bin/env python
import tasks, optparse, sys, json, pprint, parser
import os
import tm as TM
import signal
import tempfile
from pprint import pprint
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web 
from tornado.web import RequestHandler
import re


HELP="""%prog [options] [-i <json encoded inputfile>] [-l location] [-g governor]

%prog - TM (Task Manager) parses the tasks contained in the given 
json encoded directed acyclic graph (DAG) file.  This command
is designed to read the json encoded DAG from stdin.  However, a filename 
may be specified for input (-i filename.json) if that method is preferred.
location currently can be one of three values: local, slurm, or lsf.

NOTE:

This command requires pysam and samtools to be install.  Samfile
checks for valid header and chromosome name defininitions are turned
off which mandates processing only unmapped reads.

"""

opts_list = [
    optparse.make_option('-v', '--verbose', action="store_true",
                         dest="verbose", default=False,
                         help="Turn on verbose output (to stderr)"),
    optparse.make_option('-p', '--port', action="store", type="string",
                         dest="port", default=8888, help="Specify port daemon listens on"),
]


global opts, p, data, wslisteners
locations = ('local', 'slurm', 'lsf')
tmgrs = []
wslisteners = []

def optionHandling():
    global ports, data

    if opts.ports is None:
        opts.ports = 8888

def fileHandling():

    '''create directory structure to store metadata from tasks'''

    global hashdirectory, rundirectory

    hash, product = p.getHashTuple()
    #print "hash: " + hash + " product: " + product

    hashdirectory = opts.directory + "/" + hash
    #print "final directory: " + hashdirectory

    # create task directory if it doesn't exist
    run = "/run1"
    if not os.path.exists(hashdirectory):
        os.makedirs(hashdirectory)
        rundirectory = hashdirectory + run
    else:
        # get the last run and increment it by one
        runnum = 1
        for run in os.walk(hashdirectory).next()[1]:
            #print "run: " + run
            curnum = int(run[3:])
            if runnum < curnum:
                runnum = curnum
        runnum += 1;
        #print "runnum: " + str(runnum)
        rundirectory = hashdirectory + "/run" + str(runnum)

    os.makedirs(rundirectory)

    # create link to directory if it doesn't exist
    symlinkdir = opts.directory + "/by_task_name"
    if not os.path.exists(symlinkdir):
        os.makedirs(symlinkdir)

    symlink = symlinkdir + "/" + product
    #print "symlink: " + symlink
    if not os.path.exists(symlink):
        print "symlink: " + hashdirectory + "  " + symlink
        os.symlink(hashdirectory, symlink)

    graph = p.getJsonGraph()
    with open(rundirectory + "/graph.json", 'w') as graphFile:
        graphFile.write(graph)


class WSHandler(tornado.websocket.WebSocketHandler):
    @tornado.web.asynchronous

    def open(self):
        print 'new websocket connection'
        wslisteners.append(self)
        #self.write_message("Hello Some World")

    def on_message(self, message):
        data = json.loads(message)
        print "data: " + str(data)
        if 'dag' in data:
            print "opening file: " + rundirectory + "/graph.json"
            with open(rundirectory + "/graph.json", 'r') as f:
                dag = f.read()
            jsondict = json.loads(dag)
            d = {'dag': jsondict}
            return_msg = json.dumps(d)
            self.write_message(return_msg)
        if 'status' in data:
            print "status message received."
            for k, task in p.getTasks().iteritems():
                self.taskUpdate(task)

        #print 'message received %s' % message

    def on_close(self):
        print 'connection closed'
        wslisteners.remove(self)

    def taskUpdate(self, task):
        if task.getStatus() == tasks.Status.FINISHED:
            d = {'taskUpdate': {'task': task.getName(), 'status': task.getResult()}}
        else:
            d = {'taskUpdate': {'task': task.getName(), 'status': task.getStatus() }}
        return_msg = json.dumps(d)
        self.write_message(return_msg)

class WebHandler(RequestHandler):
    def get(self):
        print "new web connection"
        self.render(os.path.join(opts.directory, "index.html"))
        #with open(hashdirectory + "/index.htmln", 'r') as f:
        #    json_data = f.read()
        #self.write(json_data)

class TaskHandler(RequestHandler):
    def get(self, more):
        print "new task connection: " + more

        targetTask = self.get_argument("task", None, True)
        if targetTask == "root":
            self.write("<html><body> Root task has no log file to display.</body></html>")
            return

        for k, task in tm.getTasks().iteritems():
            if task.getName() == targetTask:
                if os.path.exists(task.getFilename() + ".log"):
                    self.render(task.getFilename() + ".log")
                #elif getLastAvailableTaskRun(task) is not None:
                #    self.write('<html><head><meta http-equiv="refresh" content="3,url={url}"/></head>'
                #        .format(url=getLastAvailableTaskRun(task)))
                #    self.write('<body> Redirecting to the last avaiable log for this task... </body></html>')
                else:
                    self.write('''<html><body>task has no output log for the current run.  <P>Either it hasn't
                            run yet, or it was successfully executed during a previous run.</body></html>''')
                return
        self.write("Error: task {task} doesn't exist".format(task=targetTask))

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)', text) ]

def getLastAvailableTaskRun(task):
    ''' search all available runs for the given task and return the latest
        logfile available'''
    filename = os.path.basename(task.getFilename()) + ".log"
    runs = [ runs for runs in os.walk(hashdirectory).next()[1] ]
    runs.sort(key=natural_keys, reverse=True)
    for run in runs:
        tryFilename = hashdirectory + "/" + run + "/" + filename
        print "tryFilename: " + tryFilename
        if os.path.exists(tryFilename):
            print "success: " + tryFilename
            return tryFilename
    return None


def main():
    global opts, p, argParser, tmgrs

    def sigtermSetup():
        signal.signal(signal.SIGTERM, sigtermHandler)
        signal.signal(signal.SIGINT, sigtermHandler)

    def sigtermHandler(signum, frame):
        print "caught signal " + str(signum)
        print "cleaning up..."
        if tm is not None:
            tm.cleanup()
        print "shutting down webserver..."
        sys.exit(0)

    argParser = optparse.OptionParser(option_list=opts_list,
                                   usage=HELP)
    (opts, args) = argParser.parse_args()
    optionHandling()

    # signals
    sigtermSetup()

    p = parser.Parser(data, opts.location.upper(), sys.stdout)

    fileHandling()
    p.setTaskOutputs(rundirectory)
    
    tm = TM.TaskManager(p.getTasks(), wslisteners, opts.governor)
    tm.setupQueue()
    tm.runQueue()

    print "opts.directory: " + opts.directory

    routes = (
        ( r'/',           WebHandler),
        ( r'/websocket/', WSHandler),
        ( r'/task(.*)',   TaskHandler), 
        ( r'/(scripts.*)',       tornado.web.StaticFileHandler, 
                           {"path": opts.directory}
        ),
        ( r'/(styles.*)',       tornado.web.StaticFileHandler, 
                           {"path": opts.directory}
        ),
    )

    app_settings = dict( 
        static_path=opts.directory,
        debug=True
        )

    app = tornado.web.Application( routes, **app_settings )
    app.listen(8888)
    print "webserver listening on localhost:8888..."
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.start()


if __name__ == '__main__':
    main()