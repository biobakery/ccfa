"""General purpose workflows"""

import os

from ..util import (
    addext,
    guess_seq_filetype,
    new_file
)

from . import starters

def extract(files_list):
    actions = list()
    targets = list()
    for fname in files_list:
        _, min_file_type = mimetypes.guess_type(fname)
        if min_file_type == 'gzip':
            actions.append( "gunzip "+fname )
            targets.append( os.path.splittext(fname)[0] )
        if min_file_type == 'bzip2':
            actions.append( "bunzip2 "+fname )
            targets.append( os.path.splittext(fname)[0] )
        else:
            pass

    return {
        "name": "decompress",
        "targets": targets,
        "actions": actions,
        "file_dep": infiles_list
    }


def fastq_split(files_list, name, dir, reverse_complement=False):
    fasta_fname = new_file(addext(name, "fa"), basedir=dir)
    qual_fname = new_file(addext(name, "qual"), basedir=dir)

    seqtype = guess_seq_filetype(files_list[0])
    cmd = ("mibc_fastq_split"+
           " --fasta_out="+fasta_fname+
           " --qual_out="+qual_fname+
           " --format="+seqtype)

    if reverse_complement:
        cmd += " -r"

    cmd += " "+" ".join(files_list)

    return {
        "name": "fastq_split_"+name,
        "actions": [cmd],
        "file_dep": files_list,
        "targets": [fasta_fname, qual_fname]
    }

