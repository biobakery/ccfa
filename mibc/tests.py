
import os
import re
import datetime
from types import *

import dateutil.parser

from models import (
    Repository,
    Project,
    User,
)
import settings


user_to_test    = "example_user"
project_to_test = "example_proj"


class ValidatorBase(object):

    conditions = list()

    def __init__(self, base=None, cheat_all_tests=False):
        self.cheat_all_tests = cheat_all_tests
        self.base = base

    def cond(self, cond, mesg):
        if cond is True:
            self.conditions.append((True, ""))
        else:
            self.conditions.append((cond, mesg))


    def all_tests_passed(self):
        if self.cheat_all_tests:
            return True
        else:
            ret = all([cond[0] for cond in self.conditions])
            self.conditions = list()
            return ret

    def __iter__(self):
        for key in dir(self):
            if key.startswith('test_'):
                yield getattr(self, key)



class Repository_Test(ValidatorBase):
    
    def setUp(self):
        if self.base:
            self.repo = base
        else:
            self.repo = Repository()

    def tearDown(self):
        del(self.repo)

    def test_instantiation(self):
        new_repo = Repository()

    def test_necessaryProperties(self):
        self.cond( type(self.repo.path) is StringType,
                   "Repository has no path"
        )
        self.cond( os.path.isdir(self.repo.path),
                   "The Repository path %s does not exist" %(self.repo.path)
        )
        assert self.all_tests_passed()

    def test_userList(self):
        allusers = self.repo.users.all()
        self.cond( type(allusers) is ListType,
                   "Unable to list users in repository"
        )
        self.cond( len(allusers) > 0,
                   "No users, even the example user, are found"
        )
        assert self.all_tests_passed()

    def test_userGet(self):
        user = self.repo.users[user_to_test]
        self.cond( len(user.name) > 0,
                   "Failed to test user %s"%(user.name)
        )
        assert self.all_tests_passed()


class User_Test(ValidatorBase):
    
    def setUp(self):
        if self.base:
            self.repo = self.base.repo
            self.user = self.base
        else:
            self.repo = Repository()
            self.user = self.repo.users[user_to_test]

    def tearDown(self):
        del(self.user)
        del(self.repo)

    def test_necessaryProperties(self):
        self.cond( type(self.user.path) is StringType,
                   "The user %s has a path that isn't a string"%(self.user.name)
        )
        self.cond( self.user.path == os.path.join( self.repo.path,
                                                   self.user.name ),
                   str("The path attribute for user %s "
                       "does not match the user's name")%(self.user.name)
        )
        assert self.all_tests_passed()

    def test_projectList(self):
        allprojects = self.user.projects.all()
        self.cond( type(allprojects) is ListType,
                   "Unable to list all projects under user %s"%(self.user.name)
        )
        self.cond( len(allprojects) > 0,
                   "User %s has no projects" %(self.user.name)
        )
        assert self.all_tests_passed()

    def test_projectGet(self):
        proj = self.user.projects[project_to_test]
        self.cond( len(proj.name) > 0,
                   "Failed to retrieve the project %s from user %s" %(
                       project_to_test, self.user.name)
        )
        assert self.all_tests_passed()


class Project_Test(ValidatorBase):

    required_fields = [
        "pi_first_name",
        "pi_last_name",
        "pi_contact_email",
        "lab_name",
        "researcher_first_name",
        "researcher_last_name",
        "researcher_contact_email",
        "study_title",
        "study_description",
        "filename",
        "collection_start_date",
        "collection_end_date"
        ]

    def setUp(self):
        if self.base:
            self.repo = self.base.user.repo
            self.user = self.base.user
            self.project = self.base
        else:
            self.repo = Repository()
            self.user = self.repo.users[user_to_test]
            self.project = self.user.projects[project_to_test]

    def tearDown(self):
        del( self.repo, self.user, self.project )


    def test_necessaryProperties(self):
        for field in self.required_fields:
            self.cond( getattr(self.project, field, None) is not None,
                       "Project %s is missing required field %s" %(
                           self.project, field )
            )

        assert self.all_tests_passed()


    def test_parseableDates(self):
        for field in [ self.project.collection_end_date,
                       self.project.collection_start_date ]:
            try:
                date = dateutil.parser.parse(field[0])
            finally:
                self.cond( type(date) is type(datetime.datetime(2013,12,05)),
                           "%s has an unreadable date %s"%(
                               self.project, field[0])
                )

        assert self.all_tests_passed()


    def test_realisticDates(self):
        beg = dateutil.parser.parse(
            self.project.collection_start_date[0]
            )
        end = dateutil.parser.parse(
            self.project.collection_end_date[0]
            )
        self.cond( beg <= end,
                   str("%s has a end collection date "
                       "before its start collection date" )%(self.project)
        )
        assert self.all_tests_passed()        

    def test_filenamesExist(self):
        for basename in self.project.filename:
            fullpath = os.path.join( self.project.path,
                                     basename )
            self.cond( os.path.isfile(fullpath),
                       "%s File specified %s does not exist" %(
                           self.project, fullpath)
            )

        assert self.all_tests_passed()


    def test_emailableContacts(self):
        for address in self.project.pi_contact_email + \
                       self.project.researcher_contact_email: 

            x = re.match(
                r'[a-zA-Z0-9]+@[0-9a-zA-Z]+\.[0-9a-zA-Z]+', 
                address
                )
            self.cond(x is not None,
                      "%s Email address %s is not readable" %(
                          self.project, address)
            )
            
        assert self.all_tests_passed()

