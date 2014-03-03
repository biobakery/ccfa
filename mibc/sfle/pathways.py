def path_16s(env, project):
    pass

def path_wgs(env, project):
    for sample_id, _ in project.map.groupby(0):
        files_batch = [ filename for filename in project.filename
                        if str(sample_id) in filename ]
        
        product = workflows.metaphlan2(
            env, 
            files_list = files_batch,
            mpa_pkl    = "/home/vagrant/metaphlan-dev/v_20/mpa.200.pkl",
            bowtie2db  = "/home/vagrant/metaphlan-dev/v_20/mpa.200.ffn"
        )
        Default(product)


