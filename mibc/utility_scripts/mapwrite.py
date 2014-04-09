
import sys
from collections import OrderedDict


USAGE = """
%(prog)s - Write map.txt files according to command line arguments

Example: %(prog)s SampleID=a,b,c,d Description=Bob,Joe,Sally,Francine

""" % (dict(prog=sys.argv[0]))


def main():

    args = sys.argv[1:]
    delimiter = args[0]

    if not args:
        print >> sys.stderr, USAGE
        sys.exit(1)

    args_dict = OrderedDict([
        (arg.split('=')[0], arg.split('=')[1].split(',')) 
        for arg in args[1].split(delimiter)
    ])

    print >> sys.stdout, "#" + "\t".join(args_dict.keys())
    for row in zip(*args_dict.values()):
        print >> sys.stdout, "\t".join(row)


if __name__ == '__main__':
    main()
