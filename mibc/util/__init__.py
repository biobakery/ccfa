import os
import json
import datetime
import inspect

def stat(path, f):
    return os.stat(
        os.path.join(path,f)
        )

class retcodes:
    SYS_ERROR  = 2
    USER_ERROR = 1

def generator_flatten(gen):
    for item in gen:
        if inspect.isgenerator(item):
            for value in generator_flatten(item):
                yield value
        else:
            yield item

class SerializationError(TypeError):
    pass

def deserialize_tsv(file_handle):
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
            [ col.strip() for col in cols[1:] ] 
            )
        
def _defaultfunc(obj):
    if hasattr(obj, '_serializable_attrs'):
        return obj._serializable_attrs
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
        
    raise SerializationError("Unable to serialize object %s" %(obj))
        

def serialize(obj, to_fp=None):
    if to_fp:
        return json.dump(obj, to_fp, default=_defaultfunc)
    else:
        return json.dumps(obj, default=_defaultfunc)

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

def islambda(func):
    return getattr(func,'func_name') == '<lambda>'


