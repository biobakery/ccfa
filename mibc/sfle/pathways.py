from itertools import chain

from .. import (
    settings
)

from . import (
    workflows
)

def path_16s(env, project):
    results = workflows.sixteen.demultiplex(env, project.map, project.filename)
    Default(list(chain(*results)))
    
    otu_tables = workflows.sixteen.pick_otus_closed_ref(
        env,
        [ r[-1] for r in results ],
        t = settings.workflows.sixteen.otu_taxonomy,
        r = settings.workflows.sixteen.otu_refseq
    )
    Default(otu_tables)


def path_wgs(env, project):
    for sample_id, _ in project.map.groupby(0):
        files_batch = [ filename for filename in project.filename
                        if str(sample_id) in filename ]
        
        product = workflows.metaphlan2(
            env, 
            files_list = files_batch,
            mpa_pkl    = settings.workflows.metaphlan2.mpa_pkl
            bowtie2db  = settings.workflows.metaphlan2.bowtie2db
        )
        Default(product)


