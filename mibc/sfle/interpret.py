"""Module for interpreting scons output from sfle.  The `file`
function is generally what you want; it parses the scons output from a
file-like-object and returns a DAG of what scons is doing.

Note that scons must be using the --tree=derived|all|status option.
Otherwise, you'll get an exception.
"""

import re
import ast
from collections import defaultdict

class ExecutionGraph(list):
    """A directed acyclic graph of what scons is doing. It's represented
    internally as a list of SconsDirectives
    """

    @classmethod
    def parse(cls, fp):
        by_dep = defaultdict(set)
        directive_list = list(SconsDirective.lex(fp))
        for i, directive in enumerate(directive_list):
            # add each product to the by_product dict
            map( lambda dep: by_dep[dep].add((i, directive)),
                 directive.depends )

        def recurse(node):
            for product in node.produces:
                for directive_idx, child in by_dep[product]:
                    del directive_list[directive_idx]
                    node.children.append(recurse(child))
            return node

        graph = cls()
        while len(directive_list) > 0:
            top_level_node = directive_list.popleft()
            graph.append(recurse(top_level_node))

        return graph


class SconsDirective(dict):
    """A single 'job' for scons to do.  This class is essentially a struct
    of inputs, command(s), and outputs to build one
    product. Additionally, this class defines a `children` attribute,
    which contains one or more jobs to execute after the initial job
    completes.
    """
    def __init__(self, produces=list(), command=str(), 
                       depends=list(),  children=list()):
        self.produces = self["produces"] = tuple(produces)
        self.command  = self["command"]  = command
        self.depends  = self["depends"]  = tuple(depends)
        self.children = self["children"] = tuple(children)
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
                yield cls(command  = command, 
                          produces = produces,
                          depends  = depends)


def file(fp):
    dag = ExecutionGraph.parse(fp)
    return dag
