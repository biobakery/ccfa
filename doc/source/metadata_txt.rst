.. _metadata-txt:

###############################
metadata.txt - Project metadata
###############################

The metadata.txt file is a project's description. The file contains tab
separated values listing key-value pairs. The first column is the key,
while columns left of the key specify a list of values.

Required metadata keys
======================
``study_title``
    str

``study_description``
    str

``sample_type``
    str

``filename``
    list of strings

``16s_data``
    true or false

``visualize``
    true or false

``platform``
    choices("illumina" "454")


Optional metadata keys
======================

``pi_first_name``
    list of strings

``pi_last_name``
    list of strings

``pi_contact_email``
    list of strings

``lab_name``
    list of strings

``researcher_first_name``
    list of strings

``researcher_last_name``
    list of strings

``researcher_contact_email``
    list of strings

``collection_start_date``
    date-like str

``collection_end_date``
    date-like str

``submit_to_insdc``
    true or false

``reverse_primer``
    str

``skiptasks``
    list of strings
