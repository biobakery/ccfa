import os

def deserialize_csv(file_handle):
    for line in file_handle:
        cols = line.split('\t')
        if len(cols) < 2:
            raise AttributeError(
                "Improper formatting in file %s - only %d column(s) found." % (
                    file_handle.name, len(cols))
            )

        yield ( 
            cols[0], 
            [ col.strip() for col in cols[1].split(',') ] 
            )
        
def stat(path, f):
    return os.stat(
        os.path.join(path,f)
        )