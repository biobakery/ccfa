"""Module for interpreting scons output from sfle.  The `file`
function is generally what you want; it parses the scons output from a
file-like-object and returns a DAG of what scons is doing.
"""

import re
import os
import ast
from collections import deque
from itertools import chain

class SconsDirective(dict):
    """A single 'job' for scons to do.  This class is essentially a struct
    of inputs, command(s), and outputs to build one
    product. Additionally, this class defines a `children` attribute,
    which contains one or more jobs to execute after the initial job
    completes.
    """
    def __init__(self, produces=list(), command=str(), 
                       depends=list(),  children=list()):
        self.produces = self["produces"] = maybe_tuple(produces)
        self.command  = self["command"]  = command
        self.depends  = self["depends"]  = maybe_tuple(depends)
        self.children = self["children"] = maybe_tuple(children)
        super(SconsDirective, self).__init__()
        
    def __hash__(self):
        return hash((self.produces, self.command, self.depends, self.children))

    def append(self, item):
        tmp = list(self.children)
        tmp.append(item)
        self.children = self["children"] = tuple(tmp) 

    def extend(self, iterable):
        tmp = list(self.children) + list(iterable)
        self.children = self["children"] = tuple(tmp)

    @classmethod
    def lex(cls, fp):
        listy_thing = cls()
        for line in fp:
            match = re.match(r'oo scons [a-z]+: (.*)[ \t]?(\(.*\))', line)
            if match:
                command = match.group(1)
                produces, depends = ast.literal_eval(match.group(2))
                already_exists = tuple([f for f in depends
                                        if os.path.exists(f)])
                yield cls(command  = command,
                          produces = produces,
                          depends  = depends), already_exists


    @staticmethod
    def build(node, parents):
        needed = set(node.depends)
        have = set()
        for parent in reversed(parents):
            map(have.add, parent.produces)
            if needed == have:
                parent.append(node)
                return None
        # the loop fell through; not enough dependencies have been met
        return node, parents


    @classmethod
    def parse(cls, fp):
        directive_deque, extant_files = zip(*SconsDirective.lex(fp))
        graph = cls(produces=list(chain(*extant_files)))
        directive_deque = deque( (d, (graph,)) for d in directive_deque )

        while directive_deque:
            node, parents = directive_deque.popleft()
            ret = SconsDirective.build(node, parents)
            if ret:
                node, parents = ret
                directive_deque.append((node, parents))

        return graph



def file(fp):
    dag = SconsDirective.parse(fp)
    return dag

def maybe_tuple(iterable):
    if type(iterable) is str:
        # slightly unclear notation; return a tuple of length 1
        # containing the string
        return (iterable,)
    else:
        return tuple(iterable)
        

