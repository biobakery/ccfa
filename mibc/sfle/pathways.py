from itertools import chain

from .. import (
    settings
)

from . import (
    workflows
)

def path_16s(env, project, dry_run=False):
    results = workflows.sixteen.demultiplex(
        env, project.map, project.filename, dry_run=dry_run)
    
    otu_tables = workflows.sixteen.pick_otus_closed_ref(
        env,
        [ r[-1] for r in results ],
        input_untracked_files = False,
        dry_run = dry_run,
        t = settings.workflows.sixteen.otu_taxonomy,
        r = settings.workflows.sixteen.otu_refseq
    )

    return list(chain(*results)) + otu_tables


def path_wgs(env, project, dry_run=False):
    to_build = list()
    for sample_id, _ in project.map.groupby(0):
        files_batch = [ filename for filename in project.filename
                        if str(sample_id) in filename ]
        
        product = workflows.metaphlan2(
            env, 
            files_list = files_batch,
            dry_run    = dry_run
        )
        to_build.append(product)

    return to_build


