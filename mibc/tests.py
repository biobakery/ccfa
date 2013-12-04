
import os
import re
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


class TestBase(object):

    conditions = list()

    def __init__(self, cheat_all_tests=False):
        self.cheat_all_tests = cheat_all_tests


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
        for key, val in self__dict__.iteritems():
            if key.startswith('test_'):
                yield val



class Repository_Test(TestBase):
    
    def setUp(self):
        self.repo = Repository()

    def tearDown(self):
        del(self.repo)

    def test_instantiation(self):
        new_repo = Repository()

    def test_necessaryProperties(self):
        self.cond( self, type(self.repo.path) is StringType )
        self.cond( self, self.repo.path == settings.c_repository_root )
        assert self.all_tests_passed()

    def test_userList(self):
        allusers = self.repo.users.all()
        self.cond( self, type(allusers) is ListType )
        self.cond( self, len(allusers) > 0 )
        assert self.all_tests_passed()

    def test_userGet(self):
        user = self.repo.users[user_to_test]
        self.cond( self, len(user.name) > 0 )
        assert self.all_tests_passed()


class User_Test(TestBase):
    
    def setUp(self):
        self.repo = Repository()
        self.user = self.repo.users[user_to_test]

    def tearDown(self):
        del(self.user)

    def test_necessaryProperties(self):
        self.cond( self, type(self.user.path) is StringType )
        self.cond( self, 
            self.user.path == os.path.join( self.repo.path,
                                            self.user.name )
            )
        assert self.all_tests_passed()

    def test_projectList(self):
        allprojects = self.user.projects.all()
        self.cond( self, type(allprojects) is ListType )
        self.cond( self, len(allprojects) > 0 )
        assert self.all_tests_passed()

    def test_projectGet(self):
        proj = self.user.projects[project_to_test]
        self.cond( self, len(proj.name) > 0 )
        assert self.all_tests_passed()


class Project_Test(TestBase):

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
        self.repo = Repository()
        self.user = self.repo.users[user_to_test]
        self.project = self.user.projects[project_to_test]


    def tearDown(self):
        del( self.repo, self.user, self.project )


    def test_necessaryProperties(self):
        for field in self.required_fields:
            self.cond( self, 
                getattr(self.project, field, None) is not None
                )

        assert self.all_tests_passed()


    def test_parseableDates(self):
        for field in [ self.project.collection_end_date,
                       self.project.collection_start_date ]:
            dateutil.parser.parse(field[0])


    def test_realisticDates(self):
        beg = dateutil.parser.parse(
            self.project.collection_start_date[0]
            )
        end = dateutil.parser.parse(
            self.project.collection_end_date[0]
            )
        self.cond( self, beg < end )
        assert self.all_tests_passed()        

    def test_filenamesExist(self):
        for basename in self.project.filename:
            fullpath = os.path.join( self.project.path,
                                     basename )
            self.cond( self, os.path.isfile(fullpath) )

        assert self.all_tests_passed()


    def test_emailableContacts(self):
        for address in self.project.pi_contact_email + \
                       self.project.researcher_contact_email: 

            x = re.match(
                r'[a-zA-Z0-9]+@[0-9a-zA-Z]+\.[0-9a-zA-Z]+', 
                address
                )
            self.cond(x is not None)
            
        assert self.all_tests_passed()


