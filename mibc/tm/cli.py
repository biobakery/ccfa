#!/usr/bin/env python
import tasks, optparse, sys, json, pprint, parser
import os
import tm as TM
from pprint import pprint

HELP="""%prog [options] [-i <json encoded inputfile>] [-l location]

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
                         dest="directory", help="Specify directory where all tasks and logfiles are stored.  Default is /var/tmp/anadama_flows"),
    optparse.make_option('-l', '--l', action="store",
                         dest="location", type="string", 
                         help="The location for running tasks (local, slurm, or lsf)"),
    #optparse.make_option('-o', '--o', action="store", type="string",
    #                     dest="output_file", 
    #                     help="The FASTA output file."),
]

locations = ('local', 'slurm', 'lsf')

def main():
    global opts
    argParser = optparse.OptionParser(option_list=opts_list,
                                   usage=HELP)
    (opts, args) = argParser.parse_args()

    #if opts.verbose:
    #    if opts.bamformat:
    #        print >> sys.stderr, "processing BAM format (binary)."
    #    else:
    #        print >> sys.stderr, "processing SAM format (ascii)."

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
        print "directory: " + opts.directory
        if opts.directory is "":
            opts.directory = "/var/tmp/anadama_flows"

        if not os.access(opts.directory, os.W_OK):
            print >> sys.stderr, "directory " + opts.directory + " is not writable."
            argParser.print_usage()
            sys.exit(1)
    else:
        opts.directory = "/var/tmp/anadama_flows"

    # create task directory if it doesn't exist
    if not os.path.exists(opts.directory):
        os.makedirs(opts.directory)

    print "directory: " + opts.directory

    if input is "-":
        data = json.load(sys.stdin);
    else:
        jsonfile = open(opts.dagfile)
        jsondata = jsonfile.read()
        print len(str(jsondata))
        data = json.loads(jsondata);
        jsonfile.close()

    p = parser.Parser(data, opts.location.upper(), opts.directory)

    tm = TM.TaskManager(p.getTasks(), opts.directory)
    tm.setupQueue()
    tm.runQueue()

if __name__ == '__main__':
    main()
