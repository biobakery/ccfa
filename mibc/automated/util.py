import re
import os
import errno
import mimetypes

biopython_to_metaphlan = {
    "fasta": "multifasta",
    "fastq": "multifastq",
    "bam"  : "bam",
}

def addext(name_str, tag_str):
    return name_str + "." + tag_str

def addtag(name_str, tag_str):
    match = re.match(r'([^.]+)(\..*)', name_str)
    if match:
        base, ext = match.groups()
        return base + "_" + tag_str + ext
    else:
        return name_str + "_" + tag_str

def guess_seq_filetype(guess_from):
    if re.search(r'\.f.*q', guess_from): #fastq, fnq, fq
        return 'fastq'
    elif re.search(r'\.f.*a', guess_from): #fasta, fna, fa
        return 'fasta'
    elif '.sff' in guess_from:
        return 'sff'
    elif '.bam' in guess_from:
        return 'bam'

def dict_to_cmd_opts_iter(opts_dict, sep="=", singlesep=" "):
    """sep separates long options and their values, singlesep separates
    short options and their values e.g. --long=foobar vs -M 2

    """

    for key, val in opts_dict.iteritems():
        if len(key) > 1:
            key = "--%s"% (key)
        else:
            key = "-%s"% (key)
            
        if val:
            if len(key) == 2:
                yield key+singlesep+val
            else:
                yield key+sep+val
        else:
            yield key


def dict_to_cmd_opts(opts_dict, sep="=", singlesep=" "):
    return " ".join(dict_to_cmd_opts_iter(
        opts_dict, sep=sep, singlesep=singlesep))


def mkdirp(path):
    try:
        return os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def _new_file(*names, **opts):
    basedir = opts.get("basedir")
    for name in names:
        if basedir is not None:
            name = os.path.join(basedir, name)
        
        dir = os.path.dirname(name)
        if not os.path.exists(dir):
            mkdirp(dir)

        yield name

def new_file(*names, **opts):
    iterator = _new_file(*names, basedir=opts.get("basedir"))
    if len(names) == 1:
        return iterator.next()
    else:
        return list(iterator)

def is_compressed(fname):
    recognized_compression_types = ("gzip", "bzip2")
    return mimetypes.guess_type(fname)[1] in recognized_compression_types

def filter_compressed(fname_list):
    """Return only files that are known to be compressed and in a
    recognized compression format"""

    return [
        fname for fname in fname_list
        if is_compressed(fname)
    ]
