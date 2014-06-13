from ... import (
    settings
)

from ..util import (
    addtag,
    addext,
    guess_seq_filetype,
    biopython_to_metaphlan,
    dict_to_cmd_opts,
    new_file
)

from . import (
    starters
)

def metaphlan2(files_list, **opts):
    """Workflow to transform WGS sequences to OTU tables, now with doit
    """
    infiles_list  = files_list
    outfile       = new_file(addext(files_list[0], "metaphlan2"))
    bowtie2out    = new_file(addext(files_list[0], "bowtie2out.txt"))

    all_opts = { 'bt2_ps'   : 'very-sensitive',
                 'bowtie2db': settings.workflows.metaphlan2.bowtie2db,
                 'mpa_pkl'  : settings.workflows.metaphlan2.mpa_pkl,
    }
    all_opts.update(opts)
    all_opts = dict_to_cmd_opts(all_opts)

    seqtype = guess_seq_filetype(infiles_list[0])
    if seqtype not in ('fasta', 'fastq'):
        raise ValueError("Need sequences in fasta or fastq format")

    cmd = starters.cat(infiles_list, guess_from=infiles_list[0])
    cmd += (" | metaphlan2.py"
            + " --bowtie2out="+bowtie2out
            + " --output_file="+outfile
            + " --input_type="+biopython_to_metaphlan[seqtype]
            + " "+all_opts )

    return dict(name     = "metaphlan2:"+outfile,
                actions  = [cmd],
                file_dep = infiles_list,
                targets  = [outfile, bowtie2out])
