#!/bin/sh
##
## script executes after successful task run
##

#echo "post_task_success.sh"

# for HMP2, successful products from all workflows EXCEPT human workflows (kneed/bmtagger etc)
# should be linked into separate directory structure (made available to webserver to serve)

HMP2_PROCESSING_DIR=/seq/ibdmdb/processing

# add link exposing job products to webserver
for file in `echo "${TaskProducts}"`
do

  # if file doesn't exist; skip it
  if [ ! -f "${file}" ]; then
    echo "Warning: Product file +${file}+ doesn't exist."
    continue;
  fi

  # strip out current 3 prefix segments
  linkfile=`echo "${file}" | cut -d/ -f5-`
  linkfile="${HMP2_PROCESSING_DIR}"/"${linkfile}"
  #echo "file: ${file}"
  #echo "linkfile: ${linkfile}"

  # if link's directory doesn't exist, make it
  linkdir=`dirname "${linkfile}"`
  if [ ! -d "${linkdir}" ]; then
    #echo "creating dir: ${linkdir}"
    mkdir -p "${linkdir}"
  fi

  ln -s "${file}" "${linkfile}"

done
