
from os.path import join

from doit.task import dict_to_task

from .. import (
    settings
)

from . import (
    workflows,
    util
)

class Pathway(object):
    """ Class that encapsulates a set of workflows.
    """
    
    workflows = ()

    def __init__(self, project=None):
        """ Instantiate the Pathway and associate it with a project
        """
        self.project = project
        self.tasks   = None

    @staticmethod
    def _configure(workflow, project):
        """Configures a single workflow to produce a task. Should generally be
        overridden in base classes

        """
        return workflow(project)


    def configure(self, project=None):
        """Configure the workflows associated with this pathway by calling
        the workflow functions with the project as its only argument.

        Return the global doit config dict.

        Side effect: populate the tasks attribute with a list of doit tasks

        """
        if not project and not self.project:
            raise ValueError("Project is a required argument "
                             "when not already associated with a project")

        if project:
            self.project = project

        product_basedir = join(self.project.path, 
                               settings.workflows.product_directory)

        default_tasks = list()
        self.tasks = list()
        for workflow in self.workflows:
            task_dicts = self._configure(workflow, self.project)
            for d in task_dicts:
                util.new_file(*d.get("targets", []), basedir=product_basedir)
                default_tasks.append(d["name"])
                self.tasks.append( dict_to_task(d) )

        # return the global doit config dictionary
        return {
            "default_tasks": default_tasks,
            "continue":      True
        }


    def tasks(self):
        for task in self.tasks:
            yield task
    

class SixteenSPathway(Pathway):
    workflows = ()

class WGSPathway(Pathway):
    workflows = (workflows.metaphlan2,)

    def _configure(self, workflow, project):
        task_dicts = list()
        for sample_id, _ in project.map.groupby(0):
            files_batch = [ join(project.path, filename) 
                            for filename in project.filename
                            if str(sample_id) in filename ]
            if files_batch:
                task_dicts.append( workflows.metaphlan2(files_batch) )

        return task_dicts
