"""Module for interpreting scons output from sfle.  The `file`
function is generally what you want; it parses the scons output from a
file-like-object and returns a DAG of what scons is doing.

Note that scons must be using the --tree=derived|all|status option.
Otherwise, you'll get an exception.
"""

import re
import ast

class ExecutionGraph(list):
    """A directed acyclic graph of what scons is doing. It's represented
    internally as a list of SconsDirectives
    """

    def __init__(self, *args, **kwargs):
        self.dag = kwargs.pop("dag", { "root": [] })
        return super(ExecutionGraph, self).__init__(*args, **kwargs)

    @classmethod
    def lex(cls, fp):
        listy_thing = cls()

        for line in fp:
            match = re.match(r'oo scons: (.*)[ \t]+(\(.*\))', line)
            if match:
                command = match.group(1)
                produces, depends = ast.literal_eval(match.group(2))
                listy_thing.append(
                    SconsDirective(command  = command, 
                                   produces = produces,
                                   depends  = depends)
                )

        return listy_thing



class SconsDirective(dict):
    """A single 'job' for scons to do.  This class is essentially a struct
    of inputs, command(s), and outputs to build one
    product. Additionally, this class defines a `children` attribute,
    which contains one or more jobs to execute after the initial job
    completes.
    """
    def __init__(self, produces=list(), command=str(), 
                       depends=list(), children=list()):
        self.produces = self["produces"] = produces
        self.command  = self["command"]  = command
        self.depends  = self["depends"]  = depends
        self.children = self["children"] = children


def file(fp):
    dag = ExecutionGraph.lex(fp)
    return dag
