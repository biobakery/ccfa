"""Series of workflow functions to work with sfle

Workflow functions take the oo env from sfle along with a list of files to process.

These functions return a list of output files generated by the function
"""

import re
import os
import sys
import mimetypes

from .. import (
    settings
)


def addext(name_str, tag_str):
    return name_str + "." + tag_str

def addtag(name_str, tag_str):
    match = re.match(r'([^.]+)(\..*)', name_str)
    if match:
        base, ext = match.groups()
        return base + "_" + tag_str + ext
    else:
        return name_str + "_" + tag_str


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

    chain = chain_starters.cat(env, infiles_list, guess_from = infiles_list[0])

    env.chain( "metaphlan2.py",
               verbose     = True,
               in_pipe     = chain,
               stop        = outfile,

               bowtie2db   = settings.workflows.metaphlan2.bowtie2db
               mpa_pkl     = settings.workflows.metaphlan2.mpa_pkl
               bowtie2out  = bowtie2out,
               output_file = outfile,
               input_type  = guess_seq_filetype(infiles_list[0]),
               **all_opts )

    return outfile


def all():
    return dict( 
        (item.func_name, item)
        for item in sys.modules[__name__].__dict__.itervalues()
        if getattr(item, "func_name", None) 
        and getattr(item, "func_doc", None) 
        and re.match(r'^[Ww]orkflow', item.func_doc.strip())
    )


class chain_starters:

    @staticmethod
    def cat(env, infiles_list, guess_from):
        maj_file_type, min_file_type = mimetypes.guess_type(guess_from)
        if min_file_type == 'gzip':
            return env.chain("zcat", start=infiles_list, verbose=True)
        elif min_file_type == 'bzip2':
            return env.chain("bzcat", start=infiles_list, verbose=True)
        else:
            return env.chain("cat", start=infiles_list, verbose=True)

def guess_seq_filetype(guess_from):
    if re.search(r'\.f.*q', guess_from): #fastq, fnq, fq
        return 'multifastq'
    elif re.search(r'\.f.*a', guess_from): #fasta, fna, fa
        return 'multifasta'
    elif '.sff' in guess_from:
        return 'sff'
