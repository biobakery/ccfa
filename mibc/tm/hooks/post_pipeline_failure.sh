#!/bin/sh
##
## script executes after failed pipeline run
##

#echo "post_pipeline_failure.sh"

if [ -n ${PipelineName} ]; then

  mail -s "hmp2 pipeline ${PipelineName} failure" kbayer@broadinstitute.org <<EOF
this is the mail body
no pipeline name here!
EOF

else

  mail -s 'hmp2 pipeline failure' kbayer@broadinstitute.org <<EOF
this is the mail body
no pipeline name here!
EOF

fi
