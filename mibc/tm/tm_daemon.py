#!/usr/bin/env python
import tasks, optparse, sys, json, pprint, parser
import os
import tm as TaskManager
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

global opts, p, data, wslisteners, default_hash

# Datastructure is as follows
# tmgrs: dictionary containing collection of task managers keyed by their hash
#  tmgrs['hash'] = tmEntry
# each task manager entry is a dictionary of various items:
#  tmEntry['parser'] = parser
#  tmEntry['rundirectory'] = path to run directory
#  tmEntry['hashdirectory'] = path to hash directory
#  tmEntry['governor'] = tm governor 
#  tmEntry['location'] = path to config and pickle scripts
#  tmEntry['graph'] = D3 javascript formatted graph
#  tmEntry['tm'] = task manager

tmgrs = {}
tmEntry = {}
wslisteners = []

class Tm_daemon(object):
    ''' Tm_daemon class encapsulates daemon logic necessary to run tornado 
        app server and supporting request handlers.  It provides the data
        structures necessary to contain multiple task managers based on a
        hash key.  The hash value is currently generated by taking the 
        text string of the first product in the given DAG.  This hash is
        thought to be unique based on the product having a full path that
        is wrapped up in the location on the data of the filesystem.  We
        use the first 5 characters of the entire hash.  Collisions are
        unlikely with 5 characters (but certainly possible).
    '''
    default_hash = None

    def setupTm(self, tm_data):
        ''' each call sets up a new task manager controlling the tasks
            within each dag.'''
        # parse the dag from mibc_build
        tmEntry['parser'] = parser.Parser(tm_data['dag'], tm_data['type'].upper(), sys.stdout)
        tmEntry['rundirectory'] = tm_data['rundirectory']
        tmEntry['hashdirectory'] = tm_data['hashdirectory']
        tmEntry['governor'] = tm_data['governor']
        tmEntry['location'] = tm_data['location']
        tmEntry['graph'] = tmEntry['parser'].getJsonGraph()
        if not os.path.exists(tmEntry['rundirectory'] + "/graph.json"):
            with open(tmEntry['rundirectory'] + "/graph.json", 'w') as graphFile:
                graphFile.write(tmEntry['graph'])

        # store the tm parameters to disk
        tm_datapath = os.path.join(tmEntry['hashdirectory'], "tm_data.json")
        if not os.path.exists(tm_datapath):
            with open(tm_datapath, 'w') as f:
                f.write(json.dumps(tm_data))
   
        # create TaskManager and give it the tasks to run
        tmEntry['tm'] = TaskManager.TaskManager(tmEntry['parser'].getTasks(), wslisteners, tmEntry['governor'])
        tmEntry['tm'].setTaskOutputs(tmEntry['rundirectory'])
        tmEntry['tm'].setupQueue()
        tmEntry['tm'].runQueue()
        hash = tmEntry['parser'].getHashTuple()[0]
        tmgrs[hash] = tmEntry
        Tm_daemon.default_hash = hash

    def run(self, port):
        ''' method runs the tornado webservice - it does not return. '''
        # get location from first tm entry
        for k,entry in tmgrs.iteritems():
            tmEntry = entry
            break

        # setup Tornado async webservice
        routes = (
            ( r'/',           WebHandler),
            ( r'/websocket/', WSHandler),
            ( r'/task(.*)',   TaskHandler),
            ( r'/(scripts.*)',       tornado.web.StaticFileHandler, {"path": tmEntry['location']}),
            ( r'/(styles.*)',       tornado.web.StaticFileHandler, {"path": tmEntry['location']}),
        )

        app_settings = dict(
            static_path=tmEntry['location'],
            debug=True
            )

        app = tornado.web.Application( routes, **app_settings )
        app.listen(port)
        print "webserver listening on localhost:" + str(port) + "..."
        ioloop = tornado.ioloop.IOLoop.instance()
        ioloop.start()

    @staticmethod
    def cleanup():
        for k,entry in tmgrs.iteritems():
            tmEntry = entry
            tmEntry['tm'].cleanup()


class WSHandler(tornado.websocket.WebSocketHandler):
    @tornado.web.asynchronous

    def open(self):
        print 'new websocket connection'
        wslisteners.append(self)
        #self.write_message("Hello Some World")

    def on_message(self, message):
        data = json.loads(message)
        print "data: " + str(data)
        tmEntry = tmgrs[Tm_daemon.default_hash]
        if 'dag' in data:
            print "opening file: " + tmEntry['rundirectory'] + "/graph.json"
            with open(tmEntry['rundirectory'] + "/graph.json", 'r') as f:
                dag = f.read()
            jsondict = json.loads(dag)
            d = {'dag': jsondict}
            return_msg = json.dumps(d)
            self.write_message(return_msg)
        if 'status' in data:
            print "status message received."
            for k, task in tmEntry['parser'].getTasks().iteritems():
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
        print "defauolt_hash: " + Tm_daemon.default_hash
        print tmgrs.keys()
        print tmgrs.values()
        print "defauolt_hash: " + Tm_daemon.default_hash
        tmEntry = tmgrs[Tm_daemon.default_hash]
        self.render(os.path.join(tmEntry['location'], "index.html"))
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

        tmEntry = tmgrs[Tm_daemon.default_hash]

        for k, task in tmEntry['tm'].getTasks().iteritems():
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
    tmEntry = tmgrs[Tm_daemon.default_hash]
    filename = os.path.basename(task.getFilename()) + ".log"
    runs = [ runs for runs in os.walk(tmEntry['hashdirectory']).next()[1] ]
    runs.sort(key=natural_keys, reverse=True)
    for run in runs:
        tryFilename = tmEntry['hashdirectory'] + "/" + run + "/" + filename
        print "tryFilename: " + tryFilename
        if os.path.exists(tryFilename):
            print "success: " + tryFilename
            return tryFilename
    return None

