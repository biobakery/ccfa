#!/usr/bin/env python
import tasks, optparse, sys, json, pprint, parser
import os
import tm as TM
import signal
import tempfile
from pprint import pprint

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
    optparse.make_option('-i', '--input', action="store", type="string",
                         dest="dagfile", help="Specify json encrypted dag file"),
    optparse.make_option('-d', '--directory', action="store", type="string", default="",
                         dest="directory", help="Specify directory where all tasks and logfiles are stored.  Default is the current working directory."),
    optparse.make_option('-l', '--l', action="store",
                         dest="location", type="string", 
                         help="The location for running tasks (local, slurm, or lsf)"),
    optparse.make_option('-g', '--governor', action="store", type="int", default="999",
                         dest="governor", help="Rate limit the number of concurrent tasks.  Useful for limited resource on local desktops / laptops.")
    #optparse.make_option('-o', '--o', action="store", type="string",
    #                     dest="output_file", 
    #                     help="The FASTA output file."),
]

locations = ('local', 'slurm', 'lsf')
fifo = None
global opts, p, data

def fileHandling():
   
    '''create directory structure to store metadata from tasks'''

    hash, product = p.getHashTuple()
    #print "hash: " + hash + " product: " + product

    hashdirectory = opts.directory + "/" + hash
    #print "final directory: " + hashdirectory

    # create task directory if it doesn't exist
    run = "/run1"
    if not os.path.exists(hashdirectory):
        os.makedirs(hashdirectory)
        rundirectory = hashdirectory + run
        os.makedirs(rundirectory)
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
        os.symlink(hashdirectory, symlink)

    p.setTaskDir(rundirectory)
    graph = p.getJsonGraph()
    with open(rundirectory + "/graph.json", 'w') as graphFile:
        graphFile.write("loadData(\n")
        graphFile.write(graph)
        graphFile.write("\n);")

def namedPipe():
    global fifo, pipename, tmpdir
    # create the named pipe
    tmpdir = tempfile.mkdtemp()
    pipename = os.path.join(tmpdir, 'fifo')
    print "named pipe: " + pipename
    try:
        os.mkfifo(pipename)
    except OSError, e:
        print "Failed to create FIFO: %s" % e
    else:
        print "setting fifo!"
        fifo = open(pipename, 'w')

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
        print "jsonString: " + jsonString
        data = json.loads(jsonString);
    else:
        jsonfile = open(opts.dagfile)
        jsondata = jsonfile.read()
        data = json.loads(jsondata);
        jsonfile.close()


def main():
    global opts, p, fifo, argParser
    fifo = None

    def sigtermSetup():
        signal.signal(signal.SIGTERM, sigtermHandler)
        signal.signal(signal.SIGINT, sigtermHandler)

    def sigtermHandler(signum, frame):
        print "caught signal " + str(signum)
        print "cleaning up..."

        if fifo is not None:
            fifo.close()
            os.remove(pipename)
            os.rmdir(tmpdir)
        else:
            print "fifo was null"
        sys.exit(0)

    argParser = optparse.OptionParser(option_list=opts_list,
                                   usage=HELP)
    (opts, args) = argParser.parse_args()
    optionHandling()

    # signals
    sigtermSetup()
    #namedPipe()

    p = parser.Parser(data, opts.location.upper(), sys.stdout)

    fileHandling()

    tm = TM.TaskManager(p.getTasks())
    tm.setupQueue()
    tm.runQueue(opts.governor)


if __name__ == '__main__':
    main()
