#!/bin/sh
##
## script executes after successful pipeline run
##

#echo "post_pipeline_success.sh"

HMP2_DATA_DIR=/seq/ibdmdb/data_deposition
HMP2_PROCESSING_DIR=/seq/ibdmdb/processing
HMP2_PUBLIC_DIR=/seq/ibdmdb/public
extensions="png html biom tsv hdf5 txt"

function get_files {
  ext=$1
  if [ $ext == "txt" ]; then
    find ${TaskOutputDirectory} -name \*."${ext}" -maxdepth 1
  else
    find ${TaskOutputDirectory} -name \*."${ext}"
  fi
}

# first copy metadata 'map.txt' file from deposition into mibc_products
TaskInputDirectory=`dirname ${TaskOutputDirectory}`
if [ -f ${TaskInputDirectory}/map.txt ] && [ ! -f ${TaskOutputDirectory}/map.txt ]; then
  echo "copying metadata into output directory ${TaskOutputDirectory}"
  cp ${TaskInputDirectory}/map.txt ${TaskOutputDirectory}/map.txt
fi

if [[ -n ${PipelineName} ]]; then

  # touch file in output directory to indicate full results available (this is picked up via website)
  touch ${TaskOutputDirectory}/complete.html

  for extension in $extensions
  do
    for file in `get_files $extension`
    do
      echo $file

      # if file doesn't exist; skip it
      if [ ! -f "${file}" ]; then
        echo "Warning: Product file +${file}+ doesn't exist."
        continue;
      fi
  
      # strip out current 3 prefix segments
      linkfile=`echo "${file}" | cut -d/ -f5-`
      linkfile="${HMP2_PUBLIC_DIR}"/"${linkfile}"
      #echo "file: ${file}"
      #echo "linkfile: ${linkfile}"
  
      # if link's directory doesn't exist, make it
      linkdir=`dirname "${linkfile}"`
      if [ ! -d "${linkdir}" ]; then
        #echo "creating dir: ${linkdir}"
        mkdir -p "${linkdir}"
      fi

      if [ $extension == "hdf5" ] || [ $extension == "txt" ]; then
        cp "${file}" "${linkfile}"
      else
        ln -s "${file}" "${linkfile}"
      fi
      
    done
  done

  mail -s "hmp2 pipeline ${PipelineName} success" kbayer@broadinstitute.org <<EOF
no body.
EOF

else

  mail -s 'hmp2 pipeline success' kbayer@broadinstitute.org <<EOF
no pipeline name found!
EOF

fi

