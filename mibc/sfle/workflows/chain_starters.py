import mimetypes

def cat(env, infiles_list, guess_from):
    maj_file_type, min_file_type = mimetypes.guess_type(guess_from)
    if min_file_type == 'gzip':
        return env.chain("zcat", start=infiles_list, verbose=True)
    elif min_file_type == 'bzip2':
        return env.chain("bzcat", start=infiles_list, verbose=True)

    # if it's completely unrecognized, just return cat
    return env.chain("cat", start=infiles_list, verbose=True)
            
