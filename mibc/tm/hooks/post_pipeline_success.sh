#!/bin/sh
##
## script executes after successful pipeline run
##

#echo "post_pipeline_success.sh"

if [[ -n ${PipelineName} ]]; then

  mail -s "hmp2 pipeline ${PipelineName} success" kbayer@broadinstitute.org <<EOF
no body.
EOF

else

  mail -s 'hmp2 pipeline success' kbayer@broadinstitute.org <<EOF
no pipeline name found!
EOF

fi

