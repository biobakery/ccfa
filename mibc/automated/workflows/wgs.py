from ... import (
    settings
)

from ..util import (
    addtag,
    addext,
    guess_seq_filetype,
    biopython_to_metaphlan,
    dict_to_cmd_opts
)

from . import (
    starters
)

def metaphlan2(files_list, **opts):
    """Workflow to transform WGS sequences to OTU tables, now with doit
    """
    infiles_list  = files_list
    outfile       = addext(files_list[0], "metaphlan2")
    bowtie2out    = addext(files_list[0], "bowtie2out.txt")

    all_opts = { 'bt2_ps'   : 'very-sensitive',
                 'bowtie2db': settings.workflows.metaphlan2.bowtie2db,
                 'mpa_pkl'  : settings.workflows.metaphlan2.mpa_pkl,
    }
    all_opts.update(opts)
    all_opts = dict_to_cmd_opts(all_opts)

    cmd = starters.cat(infiles_list, guess_from=infiles_list[0])

    seqtype = guess_seq_filetype(infiles_list[0])
    if seqtype != 'fasta':
        cmd += (" | mibc_convert"+
                " --format="+guess_seq_filetype(infiles_list[0])+
                " --to=fasta" )

    cmd += (" | metaphlan2.py"
            + " --bowtie2out="+bowtie2out
            + " --output_file="+outfile
            + " --input_type="+biopython_to_metaphlan['fasta']
            + " "+all_opts )

    return dict(name     = outfile,
                actions  = [cmd],
                file_dep = infiles_list)
