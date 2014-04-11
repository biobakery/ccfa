import os
import json

def stat(path, f):
    return os.stat(
        os.path.join(path,f)
        )

class retcodes:
    SYS_ERROR  = 1
    USER_ERROR = 2

###
# Serialization, etc

def deserialize_csv(file_handle):
    for i, line in enumerate(file_handle):
        cols = line.split('\t')
        if line.strip() == "":
            continue
        if len(cols) < 2:
            raise AttributeError(
                "Improper formatting in file %s - "
                "only %d column(s) found on line %d" % (
                    file_handle.name, len(cols), i)
            )

        yield ( 
            cols[0], 
            [ col.strip() for col in cols[1].split(',') ] 
            )
        
def serialize(obj, to_fp=None):
    defaultfunc = lambda o: o._serializable_attrs
    if to_fp:
        return json.dump(obj, to_fp, default=defaultfunc)
    else:
        return json.dumps(obj, default=defaultfunc)

def deserialize(s=None, from_fp=None):
    if s:
        return json.loads(s)
    elif from_fp:
        return json.load(from_fp)

class SerializableMixin(object):
    """Mixin that defines a few methods to simplify serializing objects
    """

    serializable_attrs = []

    @property
    def _serializable_attrs(self):
        if hasattr(self, "_custom_serialize"):
            return self._custom_serialize()
        else:
            return dict([
                (key, getattr(self, key))
                for key in self.serializable_attrs
            ])
