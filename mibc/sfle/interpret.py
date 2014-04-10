"""Module for interpreting scons output from sfle.  The `file`
function is generally what you want; it parses the scons output from a
file-like-object and returns a DAG of what scons is doing.
"""

import re
import ast

from ..util import SerializableMixin

class SconsDirective(SerializableMixin):
    """A single 'job' for scons to do.  This class is essentially a struct
    of inputs, command(s), and outputs to build one
    product. Additionally, this class defines a `children` attribute,
    which contains one or more jobs to execute after the initial job
    completes.
    """

    serializable_attrs = [ "produces", "command", "depends", "children"]

    def __init__(self, produces=list(), command=str(), 
                       depends=list(),  children=list()):
        self.produces = only_list(produces)
        self.command  = command
        self.depends  = only_list(depends)
        self.children = only_list(children)

        # "unexported" attributes; not serialized 
        self.depth = 0
        self.parents = list()

        
    def __hash__(self):
        return hash(self.command)

    @classmethod
    def lex(cls, fp):
        for line in fp:
            match = re.match(r'oo scons [a-z]+: (.*)[ \t]*(\(.*\))', line)
            if match:
                command = match.group(1).strip()
                produces, depends = ast.literal_eval(match.group(2))
                yield SconsDirective(command  = command,
                                     produces = produces,
                                     depends  = depends)


def file(fp):
    return SconsDirective.lex(fp)

def only_list(iterable):
    if type(iterable) is str:
        return [iterable]
    else:
        return iterable
