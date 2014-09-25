#!/bin/sh
##
## script executes after successful task run
##

#echo "post_task_success.sh"

# for HMP2, successful products from all workflows EXCEPT human workflows (kneed/bmtagger etc)
# should be linked into separate directory structure (made available to webserver to serve)

HMP2_PROCESSING_DIR=/seq/ibdmdb/processing

function link_products {
  
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
  
}

task=`echo ${TaskName} | sed 's/:.*$//'`
if [[ "${task}" == "breadcrumbs_pcoa_plot" ]]; then
  if [[ -n ${TaskOutputDirectory} ]]; then
    #touch ${TaskOutputDirectory}/taxonomy_profile.html
    TaskProducts="${TaskOutputDirectory}otu_table_merged.biom.pcl_pcoa_plot-BarcodeSequence.png ${TaskOutputDirectory}otu_table_merged.biom.pcl_pcoa_plot-LinkerPrimerSequence.png ${TaskOutputDirectory}otu_table_merged.biom.pcl_pcoa_plot-DOB.png ${TaskOutputDirectory}otu_table_merged.biom.pcl_pcoa_plot-Treatment.png ${TaskOutputDirectory}otu_table_merged.biom.pcl_pcoa_plot-Description.png ${TaskOutputDirectory}otu_table_merged.biom.pcl_pcoa_plot-sample.png"
  fi
fi

if [[ "${task}" == "stacked_bar_chart" ]]; then
  if [[ -n ${TaskOutputDirectory} ]]; then
    #touch ${TaskOutputDirectory}/taxonomy_profile.html
  fi
fi

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

link_products


 
