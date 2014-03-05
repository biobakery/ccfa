#!/usr/bin/env python

import os
import sys
import json
import subprocess
from optparse import OptionParser, make_option

OPTIONS = [
    make_option('-w', "--workflow", action="store", type="string"),
    make_option('-l', "--list", action="store_true"),
    make_option('-o', "--scons_args", action="append", default=list()),
    make_option('-j', "--jenkins", action="store_true"),
]

from . import (
    MIBC_ENV_VAR,
    SCONS_BASE_CMD_LIST,
    SCONSTRUCT_PATH,

    workflows,
    interpret
)

def print_workflows():
    for _, workflow in workflows.all().iteritems():
        print "%s\t%s" %(workflow.func_name, workflow.func_doc)


def run_workflow(workflow, input_files, scons_arguments=list()):
    os.environ[MIBC_ENV_VAR] = json.dumps(
        {"workflow"   : workflow,
         "input_files": [ os.path.abspath(f) for f in input_files]}
     )
    return launch_scons(scons_arguments)


def build_directory(directory, scons_arguments=list()):
    os.environ[MIBC_ENV_VAR] = json.dumps(
        { "directory": os.path.abspath(directory) }
    )
    return launch_scons(scons_arguments)


def launch_scons(scons_arguments):
    #print " ".join(["MIBC_TARGET="+os.environ[MIBC_ENV_VAR]]+scons_cmd(scons_arguments))
    proc = subprocess.Popen(scons_cmd(scons_arguments), 
                            stderr=subprocess.STDOUT,
                            stdout=subprocess.PIPE)

    if '-n' in scons_arguments:
        dag = interpret.file(proc.stdout)
        json.dump(dag, sys.stdout)
    else:
        for line in iter(proc.stdout.readline, ''):
            print line.strip()

    return proc.wait()
    

def scons_cmd(extra_arguments):
    if not extra_arguments:
        extra_arguments = list()
    return SCONS_BASE_CMD_LIST + ['-f', SCONSTRUCT_PATH ] + extra_arguments
    

def main():
    opts, args = OptionParser(option_list=OPTIONS).parse_args()

    if opts.list:
        print_workflows()
        sys.exit()

    if opts.jenkins:
        opts.scons_args.append("-n")

    if opts.workflow:
        ret = run_workflow(opts.workflow, 
                           args,
                           scons_arguments=opts.scons_args)
    else:
        ret = build_directory(args[0], 
                              scons_arguments=args[1:])
                              

    sys.exit(ret)

        

if __name__ == '__main__':
    main()
