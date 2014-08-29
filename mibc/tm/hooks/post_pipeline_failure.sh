#!/bin/sh
##
## script executes after failed pipeline run
##

#echo "post_pipeline_failure.sh"
mail -s 'hmp2 pipeline failure' kbayer@broadinstitute.org <<EOF
this is the mail body
need a pipeline name here!
EOF
