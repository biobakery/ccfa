
from . import (
    settings
)

from . import chain_starters

from .util import (
    addtag,
    addext,
    guess_seq_filetype,
    biopython_to_metaphlan
)


def metaphlan(env, files_list, **opts):
    """Workflow to transform WGS sequences to OTU tables.
    """

    infiles_list  = [env.fin(f_str) for f_str in files_list]
    outfiles_list = [ env.fout( addtag(f_str, 'metaphlan') )
                      for f_str in files_list ]

    all_opts = { 'bt2_ps'   : 'very-sensitive' }
    all_opts.update(opts)

    for fin_obj, fout_obj in zip(infiles_list, outfiles_list):
        env.ex(
            fin_obj, fout_obj,
            "metaphlan.py %s %s" %(fin_obj, fout_obj),
            **all_opts
        )

    return outfiles_list


def metaphlan2(env, files_list, **opts):
    """Workflow to transform WGS sequences to OTU tables, but better!
    """
    infiles_list  = [env.fin(f_str) for f_str in files_list]
    outfile       = env.fout(addext(files_list[0], "metaphlan2"))
    bowtie2out    = env.fout(addext(files_list[0], "bowtie2out.txt"))

    all_opts = { 'bt2_ps'   : 'very-sensitive' }
    all_opts.update(opts)

    step_one = chain_starters.cat(
        env, infiles_list, guess_from = infiles_list[0])

    env.chain( "metaphlan2.py",
               verbose     = True,
               in_pipe     = step_one,
               stop        = outfile,

               bowtie2db   = settings.workflows.metaphlan2.bowtie2db,
               mpa_pkl     = settings.workflows.metaphlan2.mpa_pkl,
               bowtie2out  = bowtie2out,
               output_file = outfile,
               input_type  = biopython_to_metaphlan[
                   guess_seq_filetype(infiles_list[0])],
               **all_opts )

    return outfile

