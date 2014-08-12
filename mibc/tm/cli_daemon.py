#!/usr/bin/env python
import tasks, optparse, sys, json, pprint, parser
import os
import tm as TaskManager
import tm_daemon
import signal
import tempfile
from pprint import pprint
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web 
from tornado.web import RequestHandler
import re
import globals


HELP="""%prog [-p port] [-c configuration ] 

%prog - TMD (Task Manager Daemon) runs the tornado web service on a 
given port and listens for both HTTP connections and websocket
connections from clients.  

Currently, the daemon only listens on localhost to prevent being
exposed too much.

It will serve static web content (the AnADAMA status page) to 
webbrowsers.  It will also communicate over a websocket from
javascript in the webbrowser or from the cli.py interface.
Communication via the websocket is json encoded.

-p gives the port that the daemon will listen on.
-c 
"""

opts_list = [
    optparse.make_option('-v', '--verbose', action="store_true",
                         dest="verbose", default=False,
                         help="Turn on verbose output (to stderr)"),
    optparse.make_option('-p', '--port', action="store", type="string",
                         dest="port", default=8888, help="Specify port daemon listens on"),
    optparse.make_option('-c', '--configuration', action="store", type="string",
                         dest="directory", default=os.getcwd(), help="Specify configuration file "),
]


global opts, p, data, wslisteners
locations = ('local', 'slurm', 'lsf')
tmgrs = {}
wslisteners = []

def optionHandling():
    global port, data

    if opts.port is None:
        opts.port = 8888


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
        if 'tm' in data:
            setupTm(data['tm'])

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

def setupTm(tm_data):
    ''' each call sets up a new task manager controlling the tasks
        within each dag.'''
    #import pdb;pdb.set_trace()
    # parse the dag from mibc_build
    p = parser.Parser(tm_data['dag'], tm_data['location'].upper(), sys.stdout)
    rundirectory = tm_data['rundirectory']
    hashdirectory = tm_data['hashdirectory']
    governor = tm_data['governor']
    directory = tm_data['directory']
    graph = p.getJsonGraph()
    if not os.path.exists(rundirectory + "/graph.json"):
        with open(rundirectory + "/graph.json", 'w') as graphFile:
            graphFile.write(graph)

    # store the tm parameters to disk
    tm_datapath = os.path.join(hashdirectory, "tm_data.json")
    if not os.path.exists(tm_datapath):
        with open(tm_datapath, 'w') as f:
            f.write(json.dumps(tm_data))
   
    # create TaskManager and give it the tasks to run
    tm = TaskManager.TaskManager(p.getTasks(), wslisteners, governor)
    tm.setTaskOutputs(rundirectory)
    tm.setupQueue()
    tm.runQueue()
    d = {}
    d['tm'] = tm
    d['tm_data'] = tm_data
    tmgrs[hash] = d


def main():
    global opts, p, argParser, tmgrs


    def sigtermSetup():
        signal.signal(signal.SIGTERM, sigtermHandler)
        signal.signal(signal.SIGINT, sigtermHandler)

    def sigtermHandler(signum, frame):
        print "caught signal " + str(signum)
        print "cleaning up..."
        for tm in tmgrs:
            tm.cleanup()
        print "shutting down webserver..."
        sys.exit(0)

    argParser = optparse.OptionParser(option_list=opts_list,
                                   usage=HELP)
    (opts, args) = argParser.parse_args()
    optionHandling()

    # load configuration parameters (if they exist)
    print "loading globals"
    globals.init(os.path.dirname(opts.directory))

    # signals
    sigtermSetup()

    # parse the dag from mibc_build
    #p = parser.Parser(data, opts.location.upper(), sys.stdout)


    #fileHandling()
    #p.setTaskOutputs(rundirectory)
   
    # create TaskManager and give it the tasks to run
    #tm = TM.TaskManager(p.getTasks(), wslisteners, opts.governor)
    #tm.setupQueue()
    #tm.runQueue()

    # get our installed location
    currentFile = os.path.realpath(__file__)
    path = os.path.dirname(currentFile)
    web_install_path = os.path.join(path, "anadama_flows")

    tm_daemon = Tm_daemon()
    tm_daemon.run(opts.port)

if __name__ == '__main__':
    main()
else:
    main()
