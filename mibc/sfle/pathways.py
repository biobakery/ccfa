from itertools import chain

from .. import (
    settings
)

from . import (
    workflows
)

def path_16s(env, project):
    results = workflows.sixteen.demultiplex(env, project.map, project.filename)
    
    otu_tables = workflows.sixteen.pick_otus_closed_ref(
        env,
        [ r[-1] for r in results ],
        input_untracked_files = False,
        t = settings.workflows.sixteen.otu_taxonomy,
        r = settings.workflows.sixteen.otu_refseq
    )

    return list(chain(*results)) + otu_tables


def path_wgs(env, project):
    to_build = list()
    for sample_id, _ in project.map.groupby(0):
        files_batch = [ filename for filename in project.filename
                        if str(sample_id) in filename ]
        
        product = workflows.metaphlan2(
            env, 
            files_list = files_batch,
            mpa_pkl    = settings.workflows.metaphlan2.mpa_pkl,
            bowtie2db  = settings.workflows.metaphlan2.bowtie2db,
        )
        to_build.append(product)

    return to_build


