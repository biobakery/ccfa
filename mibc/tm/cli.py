#!/usr/bin/env python
import tasks, optparse, sys, json, pprint, parser
import os
import tm as TM
import signal
import tempfile
from pprint import pprint
import websocket
import re
import hashlib
import globals


HELP="""%prog [options] [-i <json encoded inputfile>] [-l location] [-g governor] [-p port]

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
    optparse.make_option('-i', '--input', action="store", type="string",
                         dest="dagfile", help="Specify json encrypted dag file"),
    optparse.make_option('-d', '--directory', action="store", type="string", default="",
                         dest="directory", help="Specify directory where all tasks and logfiles are stored.  Default is the current working directory."),
    optparse.make_option('-l', '--l', action="store",
                         dest="location", type="string", 
                         help="The location for running tasks (local, slurm, or lsf)"),
    optparse.make_option('-g', '--governor', action="store", type="int", default="999",
                         dest="governor", help="Rate limit the number of concurrent tasks.  Useful for limited resource on local desktops / laptops."),
    optparse.make_option('-p', '--port', action="store", type="int", default="8888",
                         dest="port", help="Specify the port of the webserver - defaults to 8888.")
    #optparse.make_option('-o', '--o', action="store", type="string",
    #                     dest="output_file", 
    #                     help="The FASTA output file."),
]


global opts, p, data, wslisteners
locations = ('local', 'slurm', 'lsf')
wslisteners = []

def fileHandling():
   
    '''create directory structure to store metadata from tasks'''

    global hashdirectory, rundirectory

    hash, product = peekForHash(data)

    hashdirectory = opts.directory + "/" + hash

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

def optionHandling():
    global opts, data

    if opts.dagfile:
        if not os.path.isfile(opts.dagfile):
            print >> sys.stderr, "opts.dagfile not found."
            argParser.print_usage()
            sys.exit(1)
        else:
            input = opts.dagfile
            if opts.verbose:
                print >> sys.stderr, "Input is: ", opts.dagfile
    else:
        input = "-" 
        if opts.verbose:
            print >> sys.stderr, "Input is stdin."

    if opts.location is None:
        print >> sys.stderr, "location not specified."
        argParser.print_usage()
        sys.exit(1)

    elif opts.location not in locations:
        print >> sys.stderr, "location not of type 'local', 'slurm', or 'lsf'."
        argParser.print_usage()
        sys.exit(1)

    if opts.directory is not None:
        if opts.directory is "":
            opts.directory = os.getcwd() + "/anadama_flows"
    else:
        opts.directory = os.getcwd() + "/anadama_flows"

    if not os.access(os.path.dirname(opts.directory), os.W_OK):
        print >> sys.stderr, "directory " + opts.directory + " is not writable."
        argParser.print_usage()
        sys.exit(1)

    if input is "-":
        #jsonString = iter(stdin.readline, '')
        jsonString = sys.stdin.read()
        #print "jsonString: " + jsonString
        data = json.loads(jsonString);
    else:
        jsonfile = open(opts.dagfile)
        jsondata = jsonfile.read()
        data = json.loads(jsondata);
        jsonfile.close()

def peekForHash(data):
    nodes = data['dag']
    for entry in nodes:
        node = entry['node']
        if 'produces' in node and len(node['produces']) > 0:
            md5 = hashlib.md5()
            md5.update(node['produces'][0])
            name = node['name'].split(':')[0]
            return (str(md5.hexdigest())[:5], name)

                
def main():
    global opts, p, argParser, tm, config

    # read in options
    argParser = optparse.OptionParser(option_list=opts_list,
                                   usage=HELP)
    (opts, args) = argParser.parse_args()
    optionHandling()

    # load configuration parameters (if they exist)
    print "loading globals"
    globals.init(os.path.dirname(opts.directory))

    # if os.path.exists(os.path.join(opts.directory, "/configuration_parameters.txt")):
    #    with open("./configuration_parameters") as config_file:
    #        config = json.load(config_file)

    # setup output directories
    fileHandling()
   
    # get our installed location
    currentFile = os.path.realpath(__file__)
    path = os.path.dirname(currentFile)
    web_install_path = os.path.join(path, "anadama_flows")

    # create json to send to server
    sys.stdin

    d = {'tm': 
            {'dag': data, 
                'location': opts.location, 
                'directory': opts.directory,
                'rundirectory': rundirectory,
                'hashdirectory': hashdirectory,
                'governor': opts.governor}}
    msg = json.dumps(d)
    print >> sys.stderr, msg
    # connect to daemon (or start it)
    ws = websocket.create_connection("ws://localhost:" + str(opts.port) + "/websocket/")
    #import pdb;pdb.set_trace()
    ws.send(msg)
    ws.close()

if __name__ == '__main__':
    main()
