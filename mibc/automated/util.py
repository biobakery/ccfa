import re

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

def dict_to_cmd_opts(opts_dict):
    opts_list = [
        "--%s=%s"% (key, val)
        for key, val in opts_dict.iteritems()
    ]
    return " ".join(opts_list)
