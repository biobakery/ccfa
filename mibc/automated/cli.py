#!/usr/bin/env python

import sys

from doit.doit_cmd import DoitMain

from . import commands

class Main(DoitMain):
    def get_commands(self):
        cmds = DoitMain.get_commands(self)
        for extra_cmd_cls in commands.all:
            extra_cmd = extra_cmd_cls()
            cmds[extra_cmd.name] = extra_cmd
        return cmds

def main():
    ret = Main().run(sys.argv[1:])
    sys.exit(ret)

if __name__ == '__main__':
    main()
