#!/bin/sh
##
## script executes prior to first pipeline run
##

#echo "pre_pipeline.sh"

#!/bin/sh
##
## script executes after successful pipeline run
##

#echo "post_pipeline_success.sh"

HMP2_DATA_DIR=/seq/ibdmdb/data_deposition
HMP2_PROCESSING_DIR=/seq/ibdmdb/processing
HMP2_PUBLIC_DIR=/seq/ibdmdb/public

if [[ -n ${PipelineName} ]]; then

  mail -s "hmp2 pipeline ${PipelineName} started" kbayer@broadinstitute.org <<EOF
no body.
EOF

else

  mail -s 'hmp2 pipeline started' kbayer@broadinstitute.org <<EOF
no pipeline name found!
EOF

fi

