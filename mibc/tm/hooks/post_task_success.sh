#!/bin/sh
##
## script executes after successful task run
##

#echo "post_task_success.sh"

# HMP2 architecture as of 12/16/14.
# We only wish to expose pipeline outputs - not processing outputs as originally
# intended.  Thus, only cleaned output will be linked in the processing area.

HMP2_PROCESSING_DIR=/seq/ibdmdb/processing
HMP2_PRIVATE_DIR=/seq/ibdmdb/private

link_all_public_products() {

  for product in `echo "${TaskProducts}"`
  do
    link_public_product "${product}"
  done

}

link_public_product() {

  file="$1"
  # if file doesn't exist; skip it
  if [ ! -f "${file}" ]; then
    echo "Warning: Product file +${file}+ doesn't exist."
    continue;
  fi
  
  # strip out current 3 prefix segments
  linkfile=`echo "${file}" | cut -d/ -f5-`
  linkfile="${HMP2_PROCESSING_DIR}"/"${linkfile}"
 
  # if link's directory doesn't exist, make it
  linkdir=`dirname "${linkfile}"`
  if [ ! -d "${linkdir}" ]; then
    mkdir -p "${linkdir}"
  fi
  
  ln -s "${file}" "${linkfile}"
  
  # copy the logfile for the product if it exists
  if [ -f "${file}.log.html" ]; then
      ln -s "${file}.log.html" "${linkfile}.log.html"
  fi
}

link_private_product() {
  
  # add private link for $1 
  file="$1"
  
  # if file doesn't exist; skip it
  if [ ! -f "${file}" ]; then
    echo "Warning: Product file +${file}+ doesn't exist."
    continue;
  fi
  
  # strip out current 3 prefix segments
  linkfile=`echo "${file}" | cut -d/ -f5-`
  linkfile="${HMP2_PRIVATE_DIR}"/"${linkfile}"
  
  # if link's directory doesn't exist, make it
  linkdir=`dirname "${linkfile}"`
  if [ ! -d "${linkdir}" ]; then
    mkdir -p "${linkdir}"
  fi
  
  ln -s "${file}" "${linkfile}"
  
  # copy the logfile for the product if it exists
  if [ -f "${file}.log.html" ]; then
      ln -s "${file}.log.html" "${linkfile}.log.html"
  fi
}

task=`echo ${TaskName} | sed 's/:.*$//'`
if [[ "${task}" == "breadcrumbs_pcoa_plot" ]]; then
  if [[ -n ${TaskOutputDirectory} ]]; then
    #touch ${TaskOutputDirectory}/taxonomy_profile.html
    TaskProducts="${TaskOutputDirectory}otu_table_merged.biom.pcl_pcoa_plot-BarcodeSequence.png ${TaskOutputDirectory}otu_table_merged.biom.pcl_pcoa_plot-LinkerPrimerSequence.png ${TaskOutputDirectory}otu_table_merged.biom.pcl_pcoa_plot-DOB.png ${TaskOutputDirectory}otu_table_merged.biom.pcl_pcoa_plot-Treatment.png ${TaskOutputDirectory}otu_table_merged.biom.pcl_pcoa_plot-Description.png ${TaskOutputDirectory}otu_table_merged.biom.pcl_pcoa_plot-sample.png"
  fi
fi

echo "Task: $task"

if [[ "${task}" == "merge_otu_tables" ]]; then
  if [ -f /seq/ibdmdb/centos6/qiime-dev/bin/activate ]; then
    source /seq/ibdmdb/centos6/bin/activate
    for file in `echo "${TaskProducts}"`
    do
      outfile=`echo ${file%.*}`
      outfile="${outfile}.hdf5"
      #qiime-dev_cmd biom convert -i "${file}" -o "${outfile}" --table-type="OTU table" --to-hdf5
      qiime-dev_cmd biom convert -i "${file}" -o "${outfile}" --to-hdf5
      if [ $? -eq 0 ]; then
        TaskProducts="$TaskProducts $outfile"
      fi
    done
  fi
fi

if [ "${task}" == "knead_data" ]; then

  # split the products appropriately
  for product in `echo "${TaskProducts}"`
  do
    echo "  knead_data product: $product"
    if `echo "${product}" | grep -q "contam"`; then
      link_private_product "${product}"
    elif `echo "${product}" | grep -q "clean"`; then
      link_public_product "${product}"
    fi
  done

elif [ "${task}"  == "merge_otu_tables" ]; then
  link_all_public_products
elif [ "${task}"  == "biom_to_tsv" ]; then
  link_all_public_products
elif [ "${task}"  == "stacked_bar_chart" ]; then
  link_all_public_products
elif [ "${task}"  == "breadcrumbs_pcoa_plot" ]; then
  link_all_public_products
fi

 
