
import sys
import logging
import optparse
from pprint import pformat
from contextlib import nested

from Bio import SeqIO

HELP="""%prog [options] -f <format> [-t <format>] [<file> [<file> [ ...]]]

%prog - Convert sequence files from one format to another, printing
results to stdout

Available formats:
""" 
HELP+=pformat(SeqIO._FormatToWriter.keys())

opts_list = [
    optparse.make_option('-f', '--format', action="store", 
                         dest="from_format", type="string",
                         help="The file format to convert from"),
    optparse.make_option('-t', '--to', action="store", 
                         dest="to_format", type="string", default="fasta",
                         help="The file format to convert to"),
     optparse.make_option('-l', '--logging', action="store", type="string",
                         dest="logging", default="INFO",
                         help="Logging verbosity, options are debug, info, "+
                         "warning, and critical")
]


def main():
    parser = optparse.OptionParser(option_list=opts_list, 
                                   usage=HELP)
    (opts, args) = parser.parse_args()
    logging.getLogger().setLevel(getattr(logging, opts.logging.upper()))
    logging.basicConfig(
        format="%(asctime)s %(levelname)s: %(message)s")

    if not opts.to_format:
        parser.print_usage()
        sys.exit(1)

    if args:
        input_files = [ open(f, 'r') for f in args ]
    else:
        input_files = [sys.stdin]

    with nested(*input_files):
        for in_file in input_files:
            logging.debug("Converting %s from %s to %s", 
                          in_file, opts.from_format, opts.to_format)
            sequences = SeqIO.parse(in_file, opts.from_format)
            for i, inseq in enumerate(sequences):
                SeqIO.write(inseq, sys.stdout, opts.to_format)
                if logging.getLogger().isEnabledFor(logging.DEBUG):
                    if i % 250 == 0 and i != 0:
                        logging.debug("Converted %d records", i)

                

if __name__ == '__main__':
    main()
