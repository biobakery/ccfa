import os
from collections import OrderedDict

from doit.cmd_base import TaskLoader
from doit.exceptions import InvalidCommand

from anadama.pipelines import route

from anadama_workflows import pipelines

from .. import models, settings

class ProjectLoader(TaskLoader):

    def load_tasks(self, cmd, opt_values, pos_args):
        project_path = os.path.realpath(opt_values["project"])
        project = models.Project.from_path(project_path)
        if not project.exists():
            raise InvalidCommand("project %s doesn't exist" %(project_path))

        pipeline = self.get_tasks(project)
        config = pipeline.configure()
        return pipeline.tasks(), config


    def get_tasks(self, project):
        project_is_16s = getattr(project, "16s_data") == ["true"]
        products_dir = os.path.join(
            project.path, settings.workflows.product_directory)
        files_list = [ os.path.join(project.path, f) for f in project.filename ]
        if project_is_16s:
            routes = route(
                files_list,
                [(r'\.biom$',        'otu_tables'),
                 (r'_demuxed\.f*a$', 'demuxed_fasta_files'),
                 (r'.*',             'raw_seq_files')]
            )
            return pipelines.SixteenSPipeline(
                products_dir=products_dir,
                samples=project.map,
                # construct the rest of the keyword arguments with the
                # route function
                **routes
            )
        else:
            routes = route(
                files_list,
                [(r'\.sam$', 'alignment_result_files'),
                 # Catch all that didn't match at the bottom
                 (r'.*',     'raw_seq_files')]
            )
            return pipelines.WGSPipeline(
                products_dir=products_dir,
                # construct the rest of the options with the route function
                **routes
            )
