
from doit.cmd_base import TaskLoader
from doit.exceptions import InvalidCommand

from .. import models

from . import pathways

class Loader(TaskLoader):

    def load_tasks(self, cmd, opt_values, pos_args):
        project_path = opt_values["project"]
        project = models.Project.from_path(project_path)
        if not project.exists():
            raise InvalidCommand("project %s doesn't exist" %(project_path))

        task_group = self.get_tasks(project)
        config = task_group.configure(project)
        return task_group.tasks, config


    def get_tasks(self, project):
        project_is_16s = getattr(project, "16s_data") == ["true"]
        if project_is_16s:
            return pathways.SixteenSPathway(project)
        else:
            return pathways.WGSPathway(project)


LOADER_MAP = {
    None: Loader,
    "projectloader": Loader
}