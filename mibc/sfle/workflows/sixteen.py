
import os
import operator
import itertools
from collections import OrderedDict

from . import misc

from .util import guess_seq_filetype


def demultiplex(env, samples, infiles_list, dry_run=False, **opts):
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

        # Generate map.txt file for a sampleID
        map_fname = env.fout(os.path.join(sample_id, "map.txt"))
        map_dict = OrderedDict([ (key, []) 
                                 for key in sample_group[0]._fields])
        for _, samples_bycode in itertools.groupby(
                sample_group, operator.attrgetter("BarcodeSequence")):
            # get the first (hopefully only) sample from the samples
            # grouped by ID then barcode. Ignore any other samples
            # under the same ID for the same barcode
            sample = samples_bycode.next()
            for k, v in sample._asdict().iteritems():
                # uniq-ify to make qiime happy
                if k == 'SampleID':
                    v += "_" + sample.BarcodeSequence
                map_dict[k].append(v)

        map_dict = OrderedDict([
            (key, ",".join(val)) for key, val in map_dict.iteritems()
        ])
        env.ex([], map_fname, "mibc_map_writer",
               args = (
                   "^^",
                   "^^".join([ name + "=" + value 
                               for name, value in map_dict.iteritems() ])
               ),
               outpipe = map_fname, 
               verbose = True, 
               dry_run = dry_run)

        # Split the sequence file into fasta and qual

        # TODO: should probably check with the consortium about this...
        try:
            input_seq_files = [ 
                f for f in infiles_list
                if any(s.Run_accession in f for s in sample_group) 
            ]
        except AttributeError:
            input_seq_files = infiles_list

        extracted = misc.extract(
            env, input_seq_files, 
            guess_from=input_seq_files[0], dry_run=dry_run
        )

        split_seqs_fname = env.fout(os.path.join(sample_id, "seqs.fna"))
        sequence_type = guess_seq_filetype(input_seq_files[0])
        if sequence_type == 'fasta':
            to_split = extracted
            to_return = tuple([map_fname] + extracted + [split_seqs_fname])

            # don't split
            qiime_args = dict( m=map_fname,
                               f=",".join(
                                   [str(f_name) for f_name in extracted]
                               ),
                               o=os.path.split(map_fname)[0],
                               **all_opts )
        else:
            fa_fname    = env.fout(
                os.path.join(sample_id, "%s.fa" %(sample_id)))
            qual_fname  = env.fout(
                os.path.join(sample_id, "%s.qual" %(sample_id)))
            to_split = [fa_fname, qual_fname]
            to_return = (map_fname, fa_fname, qual_fname, split_seqs_fname)

            env.ex( extracted,
                    [fa_fname, qual_fname],
                    "mibc_fastq_split", 
                    verbose = True,
                    dry_run = dry_run,
                    
                    format    = sequence_type,
                    fasta_out = fa_fname,
                    qual_out  = qual_fname
            )
            qiime_args = dict( m=map_fname,
                               f=fa_fname,
                               q=qual_fname,
                               o=os.path.split(map_fname)[0],
                               **all_opts )

        # Finally, run the qiime script to demultiplex
        env.ex( [map_fname] + to_split,
                split_seqs_fname,
                "qiime_cmd split_libraries.py",
                verbose=True,
                dry_run=dry_run,
                _nopositional=True,
                **qiime_args
        )
        
        outfiles_list.append(to_return)

    return outfiles_list


def pick_otus_closed_ref(env, infiles_list, 
                         input_untracked_files=True, dry_run=False, **opts):
    """Workflow to predict what OTUs are present in a set of metagenomic
    sequences
    """
    if input_untracked_files:
        infiles_list =  [ env.fin(f) for f in infiles_list ]

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
        env.ex( infile,          outfile, "pick_closed_reference_otus.py",
                verbose=True,    i=infile, o=os.path.dirname(outfile), 
                dry_run=dry_run, **all_opts )

    return outfiles_list

