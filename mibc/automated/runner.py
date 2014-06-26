import os
import sys

from doit.runner import Runner, MRunner, MThreadRunner
from doit.dependency import get_file_md5

import networkx

from ..util import serialize

from . import dag

class JenkinsRunner(Runner):
    
    def _cached_tasks(self, nodes, tasks_dict):
        for node in nodes:
            run_status = self.dep_manager.get_status(node._orig_task, 
                                                     tasks_dict)
            if run_status == 'up-to-date':
                yield node
            elif run_status == 'run':
                self._update_dependency_db(node._orig_task)
                continue

        self.dep_manager.close()

    def _update_dependency_db(self, task):
        for dep in task.file_dep:
            if not os.path.exists(dep):
                continue
            timestamp = os.path.getmtime(dep)
            current = self.dep_manager._get(task.name, dep)
            if current and current[0] == timestamp:
                continue
            size = os.path.getsize(dep)
            self.dep_manager._set(
                task.name, 
                dep, 
                (timestamp, size, get_file_md5(dep))
             )

    def run_all(self, task_dispatcher):
        task_dict = task_dispatcher.tasks
        the_dag, unordered_nodes = dag.assemble(task_dict.itervalues())
        cached_tasks = self._cached_tasks(unordered_nodes, task_dict)
        the_dag = dag.prune(the_dag, cached_tasks)
        return self._print_dag(the_dag)

    def _print_dag(self, dag, key="dag"):
        nodes = [ 
            {"node": node,
             "parents": dag.predecessors(node)}
            for node in networkx.algorithms.dag.topological_sort(dag) 
        ]
        return serialize({ key: nodes }, to_fp=sys.stdout)


RUNNER_MAP = {
    'jenkins': JenkinsRunner,
    'mrunner': MRunner,
    'runner': Runner,
    'mthreadrunner': MThreadRunner
}
