import os.path
import mimetypes

def extract(env, infiles_list, guess_from, dry_run=False, override=None):
    maj_file_type, min_file_type = mimetypes.guess_type(guess_from)
    if override:
        min_file_type = override
    if min_file_type == 'gzip':
        outfiles_list = [ env.File( out = os.path.splitext(in_file)[0] ).abspath
                          for in_file in infiles_list ]
        env.ex(infiles_list, 
               outfiles_list,
               "zcat",
               verbose=True,
               dry_run=dry_run)
    elif min_file_type == 'bzip2':
        outfiles_list = [ env.File( out = os.path.splitext(in_file)[0] ).abspath
                          for in_file in infiles_list ]
        env.ex(infiles_list, 
               outfiles_list,
               "bzcat",
               verbose=True,
               dry_run=dry_run)
    else:
        return infiles_list

    return outfiles_list
            
