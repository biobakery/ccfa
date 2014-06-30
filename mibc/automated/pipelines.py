import os
from os.path import join
from collections import Counter

from anadama import util
from anadama.pipelines import Pipeline as AnadamaPipeline

import anadama_workflows as workflows

from .. import (
    settings
)

class Pipeline(AnadamaPipeline):
    """ Class that encapsulates a set of workflows.
    """

    def __init__(self, project, *args, **kwargs):
        """ Instantiate the Pipeline and associate it with a project
        """
        self.project = project
        super(Pipeline, self).__init__(*args, **kwargs)


    def configure(self, project, *args, **kwargs):
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

        return super(Pipeline, self).configure(*args, **kwargs)


class SixteenSPipeline(Pipeline):

    @staticmethod
    def _filter_files_for_sample(files_list, sample_group, basedir):
        try:
            return [ 
                join(basedir, f) for f in files_list
                if any(s.Run_accession in f for s in sample_group) 
            ]
        except AttributeError:
            return [ join(basedir, f) for f in files_list ]

    
    @staticmethod
    def _determine_barcode_type(sample_group):
        lengths = ( len(s.BarcodeSequence) for s in sample_group )
        length_histogram = Counter(lengths)

        if len(length_histogram) > 1:
            return "variable_length"
        else:
            bcode_len = length_histogram.most_common(1)[0][0]
            return str(bcode_len)

    @staticmethod
    def _all_otu_tables(project, products_dir):
        ret = list()
        for sample_id, _ in project.map.groupby(0):
            ret.append( 
                os.path.realpath(
                    join(products_dir, sample_id, "otus", "otu_table.biom") 
                )
            )
        return ret

    def _configure(self):
        project = self.project
        products_dir = join(project.path, settings.workflows.product_directory)
        all_files = project.filename
        compressed_files = util.filter_compressed(all_files)
        if compressed_files:
            all_files = [
                os.path.splitext(f)[0] if util.is_compressed(f) else f
                for f in project.filename
            ]
            yield workflows.general.extract(compressed_files)

        for sample_id, sample_group in project.map.groupby(0):
            sample_dir = join(products_dir, sample_id)
            sample_group = list(sample_group)
            yield workflows.sixteen.write_map(sample_group, sample_dir)

            files_list = self._filter_files_for_sample(
                all_files, sample_group, basedir=project.path)
            yield workflows.general.fastq_split(
                files_list, name=sample_id, dir=sample_dir)

            bcode_type = self._determine_barcode_type(sample_group)
            yield workflows.sixteen.demultiplex(
                input_dir=sample_dir, name_base=sample_id,
                qiime_opts={
                    "barcode-type": bcode_type,
                    "M": "2"
                })

            otu_dir = join(sample_dir, "otus")
            yield workflows.sixteen.pick_otus_closed_ref(
                input_dir=sample_dir, output_dir=otu_dir)

        # now merge all otus together
        yield workflows.merge_otu_tables(
            self._all_otu_tables(project, products_dir),
            name=project.name+"_merged.biom",
            output_dir=products_dir
        )



class WGSPipeline(Pipeline):
    def _configure(self):
        project = self.project
        products_dir = join(project.path, settings.workflows.product_directory)
        for sample_id, _ in project.map.groupby(0):
            files_batch = [ join(project.path, filename) 
                            for filename in project.filename
                            if sample_id in filename ]
            if not files_batch:
                continue
            sample_dir = join(products_dir, sample_id)
            fastq_file = util.new_file(sample_id+"_merged.fastq", 
                                       basedir=sample_dir)
            yield workflows.sequence_convert(files_batch, fastq_file)
            yield workflows.metaphlan2([fastq_file])

            bam_file = util.new_file(fastq_file+".sam", basedir=sample_dir)
            yield workflows.bowtie2_align([fastq_file], bam_file)
            yield workflows.humann([bam_file], workdir=sample_dir)


