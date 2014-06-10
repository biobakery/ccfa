import sys
from operator import add, attrgetter, itemgetter
from collections import defaultdict, deque

from doit.loader import flat_generator

from ..util import SerializableMixin
from . import picklerunner

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
            self._cmd = picklerunner.tmp(self._orig_task).path
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


nodes_by_dep = dict()
nodes_by_target = dict()
nodes = list()
def assemble(tasks):
    global nodes_by_dep, nodes_by_target, nodes
    nodes = [ DagNode.from_doit_task(t) for t in tasks ]
    done = set()
    nodes_by_dep = indexby(nodes, attr="deps")
    nodes_by_target = indexby(nodes, attr="targets")

    def _walk_down(node):
        children_groups = [
            (tip_node, map_targets_to_children(tip_node, nodes_by_dep))
            for tip_node in outermost_children(node)
        ]
        if any(children for _, children in children_groups):
            for tip_node, children in children_groups:
                map(tip_node.children.add, children)
                map(lambda child: child.parents.add(tip_node), children)
                for child in children:
                    return _walk_down(child)
        else:
            return node

    def _walk_up(node):
        parents = map_deps_to_parent(node, nodes_by_target)
        if len(parents) > 1:
            global nodes_by_dep, nodes_by_target, nodes
            group = DagNodeGroup(*parents)
            map(node.parents.add, group.parents)
            group.children.add(node)
            map(nodes.remove, parents)
            for parent in parents:
                nodes_by_target, nodes_by_dep = _update_indices(
                    parent, group, nodes_by_target, nodes_by_dep)
            return _walk_up(group)
        if len(parents) == 1:
            map(node.parents.add, parents)
            map(lambda parent: parent.children.add(node), parents)
            return _walk_up(parents[0])
        else:
            return node
    
    for node in nodes:
        node = _walk_down(node)
        node = _walk_up(node)
        done.add(node)

    return  DagNode(name="root",
                    action_func=None, 
                    targets=list(), 
                    deps=list(), 
                    children=list(done), 
                    parents=None)


def indexby(task_list, attr):
    key_func = attrgetter(attr)
    idx = defaultdict(list)
    for task in task_list:
        for item in key_func(task):
            idx[item].append(task)
            
    return idx

def map_targets_to_children(node, idx):
    who_needs_our_stuff = map(lambda x: idx.pop(x, []), node.targets)
    who_needs_our_stuff = reduce(add, who_needs_our_stuff, []) 
    return list(set(who_needs_our_stuff))

def map_deps_to_parent(node, idx):
    who_fills_my_deps = map(lambda x: idx.get(x, []), node.deps)
    who_fills_my_deps = reduce(add, who_fills_my_deps, []) 
    return list(set(who_fills_my_deps))

def all_children(node):
    yield node
    if node.children:
        for child in node.children:
            yield all_children(child)


def outermost_children(node):
    for child, _ in flat_generator(all_children(node)):
        if not child.children:
            yield child

def _update_indices(parent, group, nodes_by_target, nodes_by_dep):
    for attr, idx in (("targets",nodes_by_target), ("deps",nodes_by_dep)):
        for item in getattr(parent, attr):
            l = idx[item]
            l.remove(parent)
            l.append(group)
        
    return nodes_by_target, nodes_by_dep


    # def _walk_up(node):
    #     global nodes_by_target, nodes_by_dep
    #     parents = map_deps_to_parent(node, nodes_by_target)
    #     if any(parents):
    #         group = DagNodeGroup(*parents)
    #         nodes.appendleft(group)
    #         # remove is expensive; hope it doesn't happen too often
    #         try:
    #             map(nodes.remove, parents)
    #             for parent in parents:
    #                 nodes_by_target, nodes_by_dep = _update_indices(
    #                     parent, group, nodes_by_target, nodes_by_dep)
    #         except ValueError:
    #             import pdb; pdb.set_trace()
    #         _walk_up(node)
    #     elif len(parents) == 1:
    #         map(node.parents.add, parents)
    #         map(lambda parent: parent.children.add(node), parents)
    #         _walk_up(node)
    #     else:
    #         return node
