
import os
import operator
import itertools
from collections import defaultdict

from . import chain_starters

from .util import guess_seq_filetype


def demultiplex(env, samples, infiles_list, **opts):
    """Workflow to demultiplex sequences from raw 16s sequences according
    to SampleID
    """

    infiles_list  = [env.fin(f_str) for f_str in infiles_list]
    outfiles_list = list() #built in the outermost for loop

    all_opts = {
        "M"           : 2,
        "barcode-type": "variable_length"
    }
    all_opts.update(opts)

    for sample_id, sample_group in itertools.groupby(
            samples, operator.attrgetter("SampleID")):
        sample_group = list(sample_group)

        sample_dir = env.ex([], sample_id, "mkdir", verbose=True)
        
        # Generate map.txt file for a sampleID
        map_fname   = env.fout(os.path.join(sample_id, "map.txt"))
        map_dict = defaultdict(list)
        for _, samples_bycode in itertools.groupby(
                sample_group, operator.attrgetter("BarcodeSequence")):
            # get the first (hopefully only) sample from the samples
            # grouped by ID then barcode. Ignore any other samples
            # under the same ID for the same barcode
            sample = samples_bycode.next()
            for k, v in sample._asdict().iteritems():
                map_dict[k].append(v)

        map_dict = dict([
            (key, ",".join(val)) for key, val in map_dict.iteritems()
        ])
        env.ex([], map_fname, "mibc_map_writer", verbose=True, **map_dict)

        # Split the sequence file into fasta and qual
        fa_fname    = env.fout(os.path.join(sample_id, "%s.fa" %(sample_id)))
        qual_fname  = env.fout(os.path.join(sample_id, "%s.qual" %(sample_id)))

        # TODO: should probably check with the consortium about this...
        input_seq_files = [ f for f in infiles_list
                            if any(s.Run_accession in f for s in sample_group) ]

        cat_chain = chain_starters.cat(
            env, input_seq_files, guess_from=input_seq_files[0])

        env.chain("mibc_fastq_split", 
                  verbose = True,
                  inpipe  = cat_chain,
                  stop    = [fa_fname, qual_fname], 

                  format    = guess_seq_filetype(input_seq_files[0]),
                  fasta_out = fa_fname,
                  qual_out  = qual_fname,
        )
        # Finally, run the qiime script to demultiplex
        split_seqs_fname = env.fout(os.path.join(sample_id, "seqs.fna"))
        env.ex([map_fname, fa_fname, qual_fname], 
               split_seqs_fname,
               "split_libraries.py",
               verbose=True,
               m=map_fname,
               f=fa_fname,
               q=qual_fname,
               o=sample_dir[0].abspath,
               **all_opts
        )
        
        to_return = (map_fname, fa_fname, qual_fname, split_seqs_fname)
        outfiles_list.append(to_return)

    return outfiles_list


def pick_otus_closed_ref(env, infiles_list, input_untracked_files=True, **opts):
    """Workflow to predict what OTUs are present in a set of metagenomic
    sequences
    """
    if input_untracked_files:
        infiles_list =  [ env.fin(f) for f in infiles_list ]
    else:
        infiles_list = [ str( env.lenv.File(f) ) for f in infiles_list ]

    outfiles_list = [ 
        env.fout( # What's a guy gotta do to get a path around here?
            os.path.join(
                os.path.abspath(
                    os.path.dirname(f)
                ),
                "otus", 
                "otu_table.biom"
            )
        )
        for f in infiles_list
    ]
        
    all_opts = {
        "t": "", #taxonomy
        "r": "", #reference sequence
    }
    all_opts.update(opts)

    for infile, outfile in zip(infiles_list, outfiles_list):
        env.ex( infile,       outfile, "pick_closed_reference_otus.py",
                verbose=True, i=infile, o=os.path.dirname(outfile), 
                **all_opts )


    return outfiles_list

