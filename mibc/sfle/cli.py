#!/usr/bin/env python

import os
import sys
import subprocess
from optparse import OptionParser, make_option

OPTIONS = [
    make_option('-w', "--workflow", action="store", type="string"),
    make_option('-l', "--list", action="store_true"),
    make_option('-o', "--scons_args", action="append", default=list()),
    make_option('-j', "--jenkins", action="store_true"),
    make_option('-v', "--verbose", action="store_true"),
]

from . import (
    MIBC_ENV_VAR,
    SCONS_BASE_CMD_LIST,
    SCONSTRUCT_PATH,

    workflows,
    interpret
)

from ..util import serialize

def print_workflows():
    for _, workflow in workflows.all().iteritems():
        print "%s\t%s" %(workflow.func_name, workflow.func_doc)


def run_workflow(workflow, input_files, 
                 scons_arguments=list(), verbose=False, dry_run=False):
    os.environ[MIBC_ENV_VAR] = serialize(
        {"workflow"   : workflow,
         "input_files": [ os.path.abspath(f) for f in input_files],
         "dry_run"    : dry_run}
     )
    return launch_scons(scons_arguments, verbose=verbose, dry_run=dry_run)


def build_directory(directory, 
                    scons_arguments=list(), verbose=False, dry_run=False):
    os.environ[MIBC_ENV_VAR] = serialize(
        {"directory": os.path.abspath(directory),
         "dry_run"  : dry_run}
    )
    return launch_scons(scons_arguments, verbose=verbose, dry_run=dry_run)


def launch_scons(scons_arguments, verbose=False, dry_run=False):
    if verbose:
        print " ".join(["MIBC_TARGET="+os.environ[MIBC_ENV_VAR]]+\
                       scons_cmd(scons_arguments))
    proc = subprocess.Popen(scons_cmd(scons_arguments), 
                            stderr=subprocess.STDOUT,
                            stdout=subprocess.PIPE)

    if dry_run:
        dag = interpret.file(proc.stdout)
        serialize(list(dag), to_fp=sys.stdout)
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

    if opts.workflow:
        ret = run_workflow(opts.workflow, 
                           args,
                           scons_arguments=opts.scons_args,
                           dry_run=opts.jenkins,
                           verbose=opts.verbose)
    else:
        opts.scons_args.extend(args[1:])
        ret = build_directory(args[0], 
                              scons_arguments=opts.scons_args,
                              dry_run=opts.jenkins,
                              verbose=opts.verbose)
                              

    sys.exit(ret)

        

if __name__ == '__main__':
    main()
