
import sys
import logging
import optparse
from pprint import pformat

from Bio import SeqIO

HELP="""%prog [options] -F <format> --fasta-out <file> --qual_out <file>

%prog - Read in a sequence file from stdin, splitting sequence records
        to a pair of fasta and qual files, specified by the
        --fasta-out and the --qual-out options

Available formats:
""" 
HELP+=pformat(SeqIO._FormatToIterator.keys())

opts_list = [
    optparse.make_option('-F', '--format', action="store", 
                         dest="from_format", type="string",
                         help="The file format to convert from"),
    optparse.make_option('-f', '--fasta-out', action="store", 
                         dest="fasta_outfile", type="string",
                         help="File to which to write fasta records"),
     optparse.make_option('-q', '--qual-out', action="store", 
                         dest="qual_outfile", type="string",
                         help="File to which to write qual records"),
     optparse.make_option('-l', '--logging', action="store", type="string",
                         dest="logging", default="INFO",
                         help="Logging verbosity, options are debug, info, "+
                         "warning, and critical")
]

def fa(record):
    return ">%s\n" %(record.id), "%s\n" %(str(record.seq[4:]))

def ql(record):
    return ">%s\n" %(record.id), "%s\n" %(
        ' '.join([ str(x) for x in record.letter_annotations['phred_quality'][4:] ])
    )

def main():
    parser = optparse.OptionParser(option_list=opts_list, 
                                   usage=HELP)
    (opts, args) = parser.parse_args()
    logging.getLogger().setLevel(getattr(logging, opts.logging.upper()))
    logging.basicConfig(
        format="%(asctime)s %(levelname)s: %(message)s")

    if not opts.fasta_outfile or not opts.qual_outfile:
        parser.print_usage()
        sys.exit(1)

    with open(opts.fasta_outfile, 'w') as fa_file, 
         open(opts.qual_outfile, 'w') as qual_file:
        for i, record in enumerate(SeqIO.parse(sys.stdin, opts.from_format)):
            fa_file.writelines(fa(record))
            qual_file.writelines(ql(record))
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                if i % 250 == 0:
                    logging.debug("Converted %d records", i)
            
                

if __name__ == '__main__':
    main()
