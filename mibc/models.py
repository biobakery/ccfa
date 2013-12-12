import os
from datetime import datetime

import settings
import util

default_repo = None
            
class Repository(object):

    def __init__(self, path=settings.c_repository_root):
        self.path = path
        self.users = UserRoster(self)

        # first initialized repo is the default seems good to me
        global default_repo
        if default_repo is None:
            default_repo = self

        self._last_updated = None


    def newly_updated(self, since=datetime.now()):
        return [ 
            u for u in self.users.all() if since < u.last_updated 
            ]


    @property
    def last_updated(self):
        if not self._last_updated:
            self._last_updated = max( util.stat(self.path, f).st_mtime
                                      for f in os.listdir(self.path) )
            self._last_updated = datetime.fromtimestamp(self.last_updated)

        return self._last_updated


    def __eq__(self, other):
        return self.path == other.path
    
    def __str__(self):
        return "<Repository('%s')>" % self.path

    def __repr__(self):
        return "Repository"

    def __hash__(self):
        return self.path



class User(object):
    
    def __init__(self, name, repo=None, autopopulate=False):
        self.name = name
        self.repo = repo if repo is not None else default_repo

        self.path = os.path.join(self.repo.path, name)
        self.projects = ProjectRoster(self)

        self._last_updated = None

        
    def newly_updated(self, since=datetime.now()):
        return [ 
            p for p in self.projects.all() if since < p.last_updated 
            ]


    @property
    def last_updated(self):
        if not self._last_updated:
            self._last_updated = max( util.stat(self.path, f).st_mtime
                                      for f in os.listdir(self.path) )
            self._last_updated = datetime.fromtimestamp(self.last_updated)

        return self._last_updated


    def __str__(self):
        return "<User '%s'>" % self.name
                                 
    def __repr__(self):
        return "User"



class Project(object):
    
    def __init__(self, name, user, autopopulate=False):
        self.name = name
        self.user = user
        self.path = os.path.join(user.path, name)

        if autopopulate:
            self.autopopulate()


    def autopopulate(self):
        self.__dict__.update( self._gather('metadata.txt') )
        self.map = self._gather('map.txt')

        self.last_updated = max( util.stat(self.path, f).st_mtime
                                 for f in os.listdir(self.path) )
        self.last_updated = datetime.fromtimestamp(self.last_updated)


    def _gather(self, filename):
        p = os.path.join(self.path, filename)
        with open(p) as f:
            return dict( (key, val)
                         for (key, val) in util.deserialize_csv(f) )


    def __getattr__(self, name):
        self.autopopulate()
        return getattr(self, name)

    def __str__(self):
        return "<Project(%s, %s) >" % (self.user.name, self.name)

    def __repr__(self):
        return "Project"



class BaseRoster(object):

    parent = None

    def __init__(self, MemberClass):
        self.MemberClass = MemberClass


    def get(self, key):
        return self.MemberClass( key, self.parent )


    def all(self):
        paths = [ os.path.abspath( os.path.join(self.parent.path, f) )
                  for f in os.listdir(self.parent.path) ]

        return [ self.MemberClass( os.path.basename(path),
                                   self.parent, 
                                   autopopulate=False )
                 for path in paths if os.path.isdir(path) ]


    def __getitem__(self, key):
        return self.get(key)



class ProjectRoster(BaseRoster):

    def __init__(self, user):
        self.MemberClass = Project
        self.parent = user


        
class UserRoster(BaseRoster):
    
    def __init__(self, repo):
        self.MemberClass = User
        self.parent = repo

