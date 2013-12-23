import sys
import logging
import optparse
from pprint import pformat

from Bio import SeqIO

HELP="""%prog [options] -f <format> -t <format> <file> [<file> [<file> [ ...]]]

%prog - Convert sequence files from one format to another, printing
results to stdout

Available formats:
""" 
HELP+=pformat(SeqIO._FormatToWriter.keys())

opts_list = [
    optparse.make_option('-f', '--from', action="store", 
                         dest="from_format", type="string",
                         help="The file format to convert from"),
    optparse.make_option('-t', '--to', action="store", 
                         dest="to_format", type="string",
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

    if not opts.to_format or not opts.from_format:
        parser.print_usage()
        sys.exit(1)

    for arg in args:
        logging.debug("Converting %s from %s to %s", 
                      arg, opts.from_format, opts.to_format)
        with open(arg, 'r') as f:
            records = iter( r for r in SeqIO.parse(f, opts.from_format) )
            n = SeqIO.write(records, sys.stdout, opts.to_format)
            logging.debug("Converted %d records", n)
            
                

if __name__ == '__main__':
    main()
