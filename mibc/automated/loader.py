import os
import re
from collections import OrderedDict

from doit.cmd_base import TaskLoader
from doit.exceptions import InvalidCommand

from anadama.pipelines import route
from anadama.util import guess_seq_filetype

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
        pipeline = self._get_basic_pipeline(project)
        pipeline = self._add_optional_pipelines(pipeline, project)
        return pipeline

    def _get_basic_pipeline(self, project):
        project_is_16s = getattr(project, "16s_data") == ["true"]
        products_dir = os.path.join(
            project.path, settings.workflows.product_directory)
        files_list = [ os.path.join(project.path, f) for f in project.filename ]
        pairs, files_list = infer_pairs(files_list)
        if project_is_16s:
            pipeline_cls = pipelines.SixteenSPipeline
            routes = route(
                files_list,
                [(r'\.biom$',         'otu_tables'),
                 (r'_demuxed\.f*a$',  'demuxed_fasta_files'),
                 (guess_seq_filetype, 'raw_seq_files')]
            )
        else:
            pipeline_cls = pipelines.WGSPipeline
            routes = route(
                files_list,
                [(r'\.sam$', 'alignment_result_files'),
                 # Catch all that didn't match at the bottom
                 (guess_seq_filetype, 'raw_seq_files')]
            )

        routes['raw_seq_files'].extend(pairs)

        return pipeline_cls(
            products_dir=products_dir,
            sample_metadata=project.map,
            # construct the rest of the options with the route
            # function
            **routes
        )

    def _add_optional_pipelines(self, basic_pipeline, project):
        if hasattr(project, 'visualize') and project.visualize == ["true"]:
            basic_pipeline.append(pipelines.VisualizationPipeline)

        return basic_pipeline


def infer_pairs(list_fnames):
    one_files, two_files, notpairs = _regex_filter(list_fnames)
    pairs = zip( sorted(one_files), sorted(two_files) )
    
    return pairs, notpairs


def _regex_filter(list_fnames):
    """Go through each name; group into R1, R2, or singleton based on a
    regular expression that searches for R1 or r2 or R2 or r1.

    """
    regex = re.compile(r'[-._ ][rR]([12])[-._ ]')
    one, two, notpairs = list(), list(), list()

    matches = zip( list_fnames, map(regex.search, list_fnames))
    for fname, regex_result in matches:
        if not regex_result:
            notpairs.append(fname)
        else:
            if regex_result.group(1) == "1":
                one.append(fname)
            elif regex_result.group(1) == "2":
                two.append(fname)
            else:
                notpairs.append(fname)    

    return one, two, notpairs
