
import os
import operator
import itertools.groupby
from collections import defaultdict

def demultiplex(env, samples, infiles_list **opts):
    infiles_list  = [env.fin(f_str) for f_str in files_list]
    outfiles_list = list() #built in the outermost for loop

    all_opts = {
        "M"           : 2,
        "barcode-type": "variable_length"
    }.update(opts)

    for sample_id, sample_group in itertools.groupby(
            samples, operator.attrgetter("SampleID")):
        sample_dir = env.ex(None, sample_id, "mkdir")
        
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
            (key, ",".join(val)) for key, val in map_dict
        ])
        env.ex(None, map_fname, "mibc_map_writer" **map_dict)

        # Split the sequence file into fasta and qual
        fa_fname    = env.fout(os.path.join(sample_id, "%s.fa" %(sample_id)))
        qual_fname  = env.fout(os.path.join(sample_id, "%s.qual" %(sample_id)))
        input_seq_files = [ f for f in input_files
                            if sample_id in f ]
        env.ex(input_seq_files, 
               [fa_fname, qual_fname], 
               "mibc_fastq_split", 
               inpipe=True
               fasta_out=fa_fname,
               qual_out=qual_fname,
        )
        
        # Finally, run the qiime script to demultiplex
        split_seqs_fname = env.fout(os.path.join(sample_id, "seqs.fna"))
        env.ex([map_fname, fa_fname, qual_fname], 
               split_seqs_fname,
               "split_libraries.py"
               m=map_fname,
               f=fa_fname,
               q=qual_fname,
               o=sample_dir.abspath,
               **all_opts
        )
        
        to_return = (map_fname, fa_fname, qual_fname, split_seqs_fname)
        ret.append(to_return)

    return ret


def pick_otus_closed_ref(env, infiles_list, **opts):
    
    infiles_list =  [ env.fin(f) for f in infiles_list ]
    outfiles_list = [ 
        env.fout( os.path.join(f.srcnode().abspath, 
                               "otus", 
                               "otu_table.biom") )
        for f in infiles_list
    ]
        
    all_opts = {
        "t": "", #taxonomy
        "r": "", #reference sequence
    }.update(opts)

    for infile, outfile in zip(infiles_list, outfiles_list):
        env.ex( infile, outfile, "pick_closed_reference_otus.py",
                i=infile, o=outfile.srcnode().abspath, **all_opts )


    return outfiles_list

