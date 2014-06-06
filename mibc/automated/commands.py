
from doit.cmd_run import Run
from doit.cmd_list import List
from doit.cmd_base import DoitCmdBase
from doit.cmdparse import CmdOption

from .loader import LOADER_MAP


opt_loader = dict(
    name  = "loader",
    short = "l",
    long  = "loader",
    default = "projectloader",
    help = "Choose which loader to use when loading tasks"
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
        #TODO actually instantiate the loader, don't just get a string


        

opt_project = dict(
    name  = "project",
    short = "p",
    long  = "project",
    default = "project",
    help = "Path to the project to build"
)

class RunProject(ProjectCmdBase, Run):
    my_opts = (opt_project,)

class ListProject(ProjectCmdBase, List):
    my_opts = (opt_project,)

all = (RunProject, ListProject)
