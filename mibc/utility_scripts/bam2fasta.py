#!/usr/bin/env python

import pysam
import os
import sys
import optparse
from Bio import SeqIO, Seq, SeqRecord

HELP="""%prog [options] [-i <input>] [-o <output>]

%prog - Convert BAM format data to FASTA format data.  This command
is designed to use stdin and stdin (piped input and output).  However,
a filename may be specified for input (-i filename.bam) and output
(-o filename.fa) if that method is preferred.

NOTE:

This command requires pysam and samtools to be install.  Samfile
checks for valid header and chromosome name defininitions are turned
off which mandates processing only unmapped reads.

"""

opts_list = [
    optparse.make_option('-v', '--verbose', action="store_true",
                         dest="verbose", default=False,
                         help="Turn on verbose output (to stderr)"),
    optparse.make_option('-s', '--samfile', action="store_false",
                         dest="bamformat", default=False,
                         help="Process Samfile (ascii text)"),
    optparse.make_option('-b', '--bamfile', action="store_true",
                         dest="bamformat", default=True,
                         help="Process Bamfile (binary) - the default"),
    optparse.make_option('-i', '--i', action="store",
                         dest="input_file", type="string", 
                         help="The BAM/SAM input file to convert"),
    optparse.make_option('-o', '--o', action="store", type="string",
                         dest="output_file", 
                         help="The FASTA output file."),
]

def main():
    global opts
    parser = optparse.OptionParser(option_list=opts_list,
                                   usage=HELP)
    (opts, args) = parser.parse_args()

    if opts.verbose:
        if opts.bamformat:
            print >> sys.stderr, "processing BAM format (binary)."
        else:
            print >> sys.stderr, "processing SAM format (ascii)."

    if opts.input_file:
        if not os.path.isfile(opts.input_file):
            print >> sys.stderr, "opts.input_file not found."
            parser.print_usage()
            sys.exit(1)
        else:
            input = opts.input_file
            if opts.verbose:
                print >> sys.stderr, "Input is: ", opts.input_file
    else:
        input = "-" 
        if opts.verbose:
            print >> sys.stderr, "Input is stdin."

    if opts.output_file:
        if os.path.isfile(opts.output_file):
            print >> sys.stderr, "output_file already exists."
            parser.print_usage()
            sys.exit(1)
        else:
            if opts.verbose:
                print >> sys.stderr, "Output is: ", opts.output_file
            with open(opts.output_file, "w") as out_handle: 
                SeqIO.write(bam_to_rec(input), out_handle, "fasta")
    else:
        if opts.verbose:
            print >> sys.stderr, "Output is stdout."
        with sys.stdout as out_handle:
            SeqIO.write(bam_to_rec(input), out_handle, "fasta")


def bam_to_rec(in_file):
    """Generator to convert BAM files into Biopython SeqRecords.
    """
    if opts.bamformat:
        mode = "rb"
    else: 
        mode = "r"

    bam_file = pysam.Samfile(in_file, mode, check_header=False, check_sq=False)
    for read in bam_file:
        seq = Seq.Seq(read.seq)
        if read.is_reverse:
            seq = seq.reverse_complement()
        rec = SeqRecord.SeqRecord(seq, read.qname, "", "")
        yield rec

if __name__ == '__main__':
    main()

