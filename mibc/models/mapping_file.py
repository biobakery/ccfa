
"""
Functions and classes representing sample-specific metadata
"""

import os
import operator
import itertools
from collections import namedtuple


class MappingFile(list):
    """MappingFile is a list of namedtuples
    """

    def __init__(self, name, basepath=None, project=None, 
                 data=list(), keys=list(), autopopulate=False):
        if not any((basepath, project)):
            raise ValueError("Must provide a path and/or a project")

        if basepath:
            self.path = os.path.join(basepath, name)
        elif project:
            self.path = os.path.join(project.path, name)

        self.extend(data)
        self.keys = keys

        self._autopopulated = False
        if autopopulate:
            self.autopopulate()


    def autopopulate(self):
        if not self._autopopulated:
            with open(self.path, 'r') as f:
                del self[:]
                self.extend(_deserialize(f))
            self._autopopulated = True


    def save(self):
        with open(self.path, 'w+') as f:
            dump(self.keys, self, f)


    def groupby(self, query):
        """group items by index or key, eg column 1 or the "SampleID column"
        """
        if type(query) is int:
            keyfunc = operator.itemgetter(query)
        else:
            keyfunc = operator.attrgetter(query)

        data = sorted(self, key=keyfunc)
        return itertools.groupby(data, key=keyfunc)


def load(name, basepath=None):
    if basepath:
        return MappingFile(name, basepath, autopopulate=True)
    else:
        if os.path.exists(name):
            name, basepath = os.path.split(name)
            return MappingFile(name, basepath, autopopulate=True)

    raise IOError("Unable to load mapping file from disk. "
                  "Name %s, basepath %s" %(name, basepath))
            
    
def _deserialize(file_pointer):
    """Returns a list of namedtuples according to the contents of the
    file_pointer
    """
    header = [ s.replace('#', '') 
               for s in file_pointer.readline().split() ]

    cls = namedtuple('Sample', header, rename=True)

    return [ 
        cls._make(row.split()) 
        for row in file_pointer.read().strip().split('\n')
    ]


def dump(keys, data, file_pointer):
    keys[0] = '#'+keys[0]
    print >> file_pointer, '\t'.join(keys)

    for row_list in data:
        print >> file_pointer, '\t'.join(row_list)
