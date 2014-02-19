#!/usr/bin/env python

import os
import sys
import subprocess

from . import (
    MIBC_ENV_VAR,
    SCONS_BASE_CMD_LIST,
    SCONSTRUCT_PATH,
)

def scons_cmd(extra_arguments):
    return SCONS_BASE_CMD_LIST + ['-f', SCONSTRUCT_PATH ] + extra_arguments
    
def export_vars(arg):
    path = os.path.abspath(arg)
    os.environ[MIBC_ENV_VAR] = path

def main():
    arg, scons_arguments = sys.argv[1], sys.argv[2:]
    export_vars(arg)
    print " ".join(scons_cmd(scons_arguments))
    proc = subprocess.Popen(scons_cmd(scons_arguments), 
                            stderr=subprocess.STDOUT,
                            stdout=subprocess.PIPE)

    while proc.poll() is None:
        for line in proc.stdout:
            print line.strip()

    sys.exit( proc.returncode )
        

if __name__ == '__main__':
    main()
