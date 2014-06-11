import sys
import six
import codecs
import operator
from collections import defaultdict, deque

from doit.task import Task
from doit.exceptions import InvalidCommand
from doit.cmd_run import Run
from doit.control import TaskControl
from doit.runner import Runner, MRunner, MThreadRunner
from doit.reporter import REPORTERS
from doit.cmd_list import List
from doit.cmd_base import DoitCmdBase
from doit.cmdparse import CmdOption

from ..util import serialize

from . import dag
from .loader import LOADER_MAP
from .runner import RUNNER_MAP

opt_loader = dict(
    name  = "loader",
    short = "l",
    long  = "loader",
    default = "projectloader",
    help = "Choose which loader to use when loading tasks",
    type=str
)

opt_project = dict(
    name  = "project",
    short = "P",
    long  = "project",
    default = "project",
    help = "Path to the project to build",
    type=str
)

opt_runner = dict(
    name  = "runner",
    long  = "runner",
    default = "MRunner",
    help = ("Runner to use for building the project."
            " Choices: "+",".join(RUNNER_MAP.keys()) ),
    type=str
)

opt_tmpfiles = dict(
    name    = "tmpfiledir",
    long    = "tmpfiledir",
    default = "/tmp",
    help    = "Where to save temporary files",
    type=str
)


class ProjectCmdBase(DoitCmdBase):

    my_base_opts = (opt_loader,)
    my_opts = ()

    def set_options(self):
        opt_list = (self.base_options + self._loader.cmd_options +
                    self.cmd_options + self.my_base_opts + self.my_opts)
        return [CmdOption(opt) for opt in opt_list]

    def execute(self, *args, **kwargs):
        loader_cls = LOADER_MAP[ self.opt_values.get("loader") ]
        self._loader = loader_cls()
        super(ProjectCmdBase, self).execute(*args, **kwargs)
        

class RunProject(ProjectCmdBase, Run):
    my_opts = (opt_project, opt_runner)

    def _execute(self, outfile,
                 verbosity=None, always=False, continue_=False,
                 reporter='default', num_process=0, par_type='process',
                 single=False):
        """
        @param reporter: (str) one of provided reporters or ...
                         (class) user defined reporter class 
                                 (can only be specified
                                 from DOIT_CONFIG - never from command line)
                         (reporter instance) - only used in unittests
        """
        # get tasks to be executed
        # self.control is saved on instance to be used by 'auto' command
        self.control = TaskControl(self.task_list)
        self.control.process(self.sel_tasks)

        if single:
            for task_name in self.sel_tasks:
                task = self.control.tasks[task_name]
                if task.has_subtask:
                    for task_name in task.task_dep:
                        sub_task = self.control.tasks[task_name]
                        sub_task.task_dep = []
                else:
                    task.task_dep = []

        # reporter
        if isinstance(reporter, six.string_types):
            if reporter not in REPORTERS:
                msg = ("No reporter named '%s'."
                       " Type 'doit help run' to see a list "
                       "of available reporters.")
                raise InvalidCommand(msg % reporter)
            reporter_cls = REPORTERS[reporter]
        else:
            # user defined class
            reporter_cls = reporter

        # verbosity
        if verbosity is None:
            use_verbosity = Task.DEFAULT_VERBOSITY
        else:
            use_verbosity = verbosity
        show_out = use_verbosity < 2 # show on error report

        # outstream
        if isinstance(outfile, six.string_types):
            outstream = codecs.open(outfile, 'w', encoding='utf-8')
        else: # outfile is a file-like object (like StringIO or sys.stdout)
            outstream = outfile

        # run
        try:
            # FIXME stderr will be shown twice in case of task error/failure
            if isinstance(reporter_cls, type):
                reporter_obj = reporter_cls(outstream, {'show_out':show_out,
                                                        'show_err': True})
            else: # also accepts reporter instances
                reporter_obj = reporter_cls


            run_args = [self.dep_class, self.dep_file, reporter_obj,
                        continue_, always, verbosity]
            if num_process > 0:
                run_args.append(run_args)

            RunnerClass = RUNNER_MAP.get(self.opt_values["runner"])
            if not RunnerClass:
                RunnerClass = self._discover_runner_class(
                    num_process, par_type)

            runner = RunnerClass(*run_args)
            return runner.run_all(self.control.task_dispatcher())
        finally:
            if isinstance(outfile, str):
                outstream.close()

    def _discover_runner_class(self, num_process, par_type):
        if num_process == 0:
            return Runner
        else:
            if par_type == 'process':
                RunnerClass = MRunner
                if MRunner.available():
                    return MRunner
                else:
                    RunnerClass = MThreadRunner
                    sys.stderr.write(
                        "WARNING: multiprocessing module not available, " +
                        "running in parallel using threads.")
            elif par_type == 'thread':
                    return MThreadRunner
            else:
                msg = "Invalid parallel type %s"
                raise InvalidCommand(msg % par_type)



class ListDag(ProjectCmdBase, List):
    my_opts = (opt_project, opt_tmpfiles)

    name = "dag"

    def _execute(self, subtasks=False, quiet=True, status=False,
                 private=False, list_deps=False, template=None, pos_args=None):
        filter_tasks = pos_args
        tasks = dict([(t.name, t) for t in self.task_list])

        if filter_tasks:
            print_list = self._list_filtered(tasks, filter_tasks, subtasks)
        else:
            print_list = self._list_all(tasks, subtasks)

        if not private:
            print_list = [t for t in print_list if (not t.name.startswith('_'))]
            
        dag.TMP_FILE_DIR = self.opt_values["tmpfiledir"]
        the_dag = dag.assemble(print_list)
        return self._print_dag(the_dag)


    def _print_dag(self, dag):
        return { "dag": serialize(dag, to_fp=sys.stdout) }

class ListProject(ProjectCmdBase, List):
    my_opts = (opt_project,)

all = (RunProject, ListProject, ListDag)
