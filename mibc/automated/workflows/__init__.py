from .wgs import metaphlan2
from .general import (
    extract, 
    fastq_split,
    sequence_convert
)
from .sixteen import (
    write_map, 
    demultiplex, 
    pick_otus_closed_ref, 
    merge_otu_tables
)

all = (
    metaphlan2, 
    extract, fastq_split, sequence_convert,
    write_map, demultiplex, pick_otus_closed_ref, merge_otu_tables
)


