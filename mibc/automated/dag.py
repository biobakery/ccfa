import sys
from operator import add, attrgetter, itemgetter
from collections import defaultdict, deque

from ..util import SerializableMixin, generator_flatten
from . import picklerunner

TMP_FILE_DIR = "/tmp"

class DagNode(SerializableMixin):
    def __init__(self, name, action_func, targets, deps, children, parents):
        self.name = name
        self.action_func = action_func
        self.targets = set(targets)
        self.deps = set(deps)
        self.children = set(children)
        self.parents = parents

        self._orig_task = None
        if self.action_func is None:
            self.action_func = self.execute

        self._cmd = ""
         
    @property
    def _command(self):
        if self._orig_task and not self._cmd:
            self._cmd = picklerunner.tmp(
                self._orig_task, 
                dir=TMP_FILE_DIR
            ).path
        return self._cmd

    def execute(self):
        self.action_func()

    def _custom_serialize(self):
        ret =  {
            "id": hash(self),
            "name": self.name,
            "command": self._command,
            "produces": list(self.targets),
            "depends": list(self.deps),
            "children": [child._custom_serialize() for child in self.children]
        }
        return ret
        

    @classmethod
    def from_doit_task(cls, task):
        ret = cls(
            name = task.name,
            action_func = task.execute,
            targets = task.targets,
            deps = task.file_dep,
            children = list(),
            parents = set()
        )
        ret._orig_task = task
        return ret

    def __hash__(self):
        return hash(tuple(self.targets)+tuple(self.deps))
        

    def __str__(self):
        return "DagNode: " +str(self.name)

    __repr__ = __str__


class DagNodeGroup(DagNode):

    def __init__(self, *nodes):
        self.name = "Group: "+", ".join([n.name for n in nodes])
        self.action_func = lambda *args, **kwargs: None
        self._nodes = nodes
        for attr in ("targets", "deps", "children", "parents"):
            union = reduce( lambda s, other: s.union(other),
                            [getattr(n, attr) for n in nodes], set() )
            setattr(self, attr, union)
    
    def _custom_serialize(self):
        return {
            "id": hash(self),
            "name": self.name,
            "command": "; ".join(node._command for node in self._nodes
                                 if node._command),
            "produces": list(self.targets),
            "depends": list(self.deps),
            "children": [child._custom_serialize() for child in self.children]
        }

    def __str__(self):
        return str(self.name)

    __repr__ = __str__


class Assembler(object):
    def __init__(self, tasks):
        self.tasks = tasks
        self.nodes_by_dep = dict()
        self.nodes_by_target = dict()
        self.nodes = list()


    def assemble(self):
        self.nodes = [ DagNode.from_doit_task(t) for t in self.tasks ]
        self.nodes_by_dep = indexby(self.nodes, attr="deps")
        self.nodes_by_target = indexby(self.nodes, attr="targets")
        done = set()

        for node in self.nodes:
            node = self._walk_down(node)
            node = self._walk_up(node)
            done.add(node)
            
        return  DagNode(name="root",
                        action_func=None, 
                        targets=list(), 
                        deps=list(), 
                        children=list(done), 
                        parents=None)


    def _walk_down(self, node):
        children_groups = [
            (tip_node, self._map_targets_to_children(tip_node))
            for tip_node in outermost_children(node)
        ]
        if any(children for _, children in children_groups):
            for tip_node, children in children_groups:
                map(tip_node.children.add, children)
                map(lambda child: child.parents.add(tip_node), children)
                for child in children:
                    return self._walk_down(child)
        else:
            return node

    def _walk_up(self, node):
        parents = self._map_deps_to_parent(node)
        if len(parents) > 1:
            group = DagNodeGroup(*parents)
            map(node.parents.add, group.parents)
            group.children.add(node)
            self._sub_nodes_for_group(parents, group)
            return self._walk_up(group)
        if len(parents) == 1:
            map(node.parents.add, parents)
            map(lambda parent: parent.children.add(node), parents)
            return self._walk_up(parents[0])
        else:
            return node
    
    def _sub_nodes_for_group(self, nodes, group):
        # expensive; hope it doesn't happen too often
        map(self.nodes.remove, nodes)
        for node in nodes:
            for attr, idx in (("targets",self.nodes_by_target), 
                              ("deps",self.nodes_by_dep)):
                for item in getattr(node, attr):
                    l = idx[item]
                    l.remove(node)
                    l.append(group)
            
    def _map_targets_to_children(self, node):
        """Destroys the index as it searches for targets; good since all
        children of the current node shouldn't at the same time be
        children of other nodes.
        """
        idx = self.nodes_by_dep
        who_needs_our_stuff = map(lambda x: idx.pop(x, []), node.targets)
        flattened = reduce(add, who_needs_our_stuff, []) 
        return list(set(flattened)) # deduped

    def _map_deps_to_parent(self, node):
        """non-destructive search; many different nodes can rely on the same
        parent.
        """
        idx = self.nodes_by_target 
        who_fills_my_deps = map(lambda x: idx.get(x, []), node.deps)
        flattened = reduce(add, who_fills_my_deps, []) 
        return list(set(flattened)) # deduped


def group_by_depth(dag):
    """return a list of lists, where each item in the list is a list of
    nodes that can be run in parallel
    """
    levels = list()
    for child, depth in generator_flatten(all_children(dag)):
        try:
            levels[depth].append(child)
        except IndexError:
            for _ in range(len(levels), depth+1):
                levels.append(list())
            levels[depth].append(child)

    for level in levels:
        for node in level:
            node.children = []

    return levels

                

def indexby(task_list, attr):
    key_func = attrgetter(attr)
    idx = defaultdict(list)
    for task in task_list:
        for item in key_func(task):
            idx[item].append(task)
            
    return idx

def all_children(node, depth=0):
    yield node, depth
    if node.children:
        depth += 1
        for child in node.children:
            yield all_children(child, depth=depth)


def outermost_children(node):
    for child, _ in generator_flatten(all_children(node)):
        if not child.children:
            yield child

def assemble(tasks):
    return Assembler(tasks).assemble()
