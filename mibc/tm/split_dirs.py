#!/usr/bin/env python
import os.path
import sys
import copy
import unittest
import subprocess


class Split_dirs(object):
    """ Create a directory tree based on the number of files requred 
        Primary use is for dispersing large numbers of files into a
        directory structure that can quickly be parsed by the o/s
        such that executing directory listings are responsive.

        Recommendations are to keep the number of files per directory
        to less than 100 (50 is better).  """

    def __init__(self, total_files, filenum=50, stub="dir-", path="tm_tmp"):
        """ Constructor takes the following:
            total_files - estimate the total number of files required for storage
            filenum - the number of files within each directory
            stub - the string used to name the directories
            path - location in filesystem of the starting directory (the root of the tree) 
        """

        self.filenum = filenum
        self.files = total_files
        self.stub = stub
        self.path = path
        self.indirection = 1
        self.computed_paths = []
        self.running_tally = 0;

        done = True
        for idx in range(1,100):
            if self.filenum ** idx > self.files:
                self.indirection = idx
                break

        # make root directory here (not in looping algorithm)
        if os.path.exists(self.path):
            if not os.access(self.path, os.W_OK):
                print >> sys.stderr, "Error: invalid permissions in directory %s " \
                         % os.path.join(os.getcwd(), self.path)
                return
        else:
            if not os.path.isabs(self.path):
                try:
                    os.mkdir(os.path.join(os.getcwd(), self.path))
                except:
                    print >> sys.stderr, "Error: could not create root directory %s " \
                          % os.path.join(os.getcwd(), self.path)
                    return
            else:
                try:
                    os.mkdir(self.path)
                except:
                    print >> sys.stderr, "Error: could not create root directory %s " \
                          % os.path.join(os.getcwd(), self.path)
                    return


        self.make_dirs(1, self.path)


    def _getFullPath(self, path):
        rootpath = os.path.abspath(os.getcwd())
        return os.path.join(rootpath, path)


    def make_dirs(self, sub_dir, path):
        """ make all the directories that will hold files here """

        if sub_dir < self.indirection:
            local_indirection = sub_dir +1

            for idx in range(0,self.filenum):
                if self.running_tally * self.filenum > self.files:
                    continue
                localpath = os.path.join(path, self.stub) + str(idx)
                try:
                    fullpath = self._getFullPath(localpath)
                    os.mkdir(fullpath)
                    if local_indirection == self.indirection:
                        self.computed_paths.append(fullpath)
                        self.running_tally += 1
                except:
                    print >> sys.stderr, "Error: " + str(sys.exc_info()[0])
                self.make_dirs(local_indirection, copy.deepcopy(localpath))


    def getPathGenerator(self):
        """ Returns a generator containing the path to use for each file.
            For example, if you have 10 files, you can call the generator
            10 times and each time it will give you a path based on your
            preferences.  The path can then be used to create a new file """

        local_tally = 0
        for idx, path in enumerate(self.computed_paths):
            for idx in range(0,self.filenum):
                local_tally +=1
                if self.files >= local_tally:
                    yield idx, path
                else:
                    return

class TestSplitDirs(unittest.TestCase):

    def setUp(self):
        #import pdb;pdb.set_trace()
        self.split_dirs = Split_dirs(18, filenum=4, path="/tmp/split_dirs/")
        
    def test_count_dirs(self):
        """ test with these parameters should produce this pattern of 8 dirs:
        split_dirs
        split_dirs/dir-1
        split_dirs/dir-1/dir-0
        split_dirs/dir-0
        split_dirs/dir-0/dir-3
        split_dirs/dir-0/dir-2
        split_dirs/dir-0/dir-1
        split_dirs/dir-0/dir-0
        """
        count = subprocess.check_output("find /tmp/split_dirs | wc -l",
                shell=True,
                stderr=subprocess.PIPE)[:-1]
        self.assertEqual(count, str(8))

    def test_count_files(self):
        count=0
        for filepath in self.split_dirs.getPathGenerator():
            count+=1
        self.assertEqual(count, 18)

    def tearDown(self):
        subprocess.call("rm -r /tmp/split_dirs", shell=True)

def main():

    # The following commented out command would generate a tree
    # for 180007 files with 15 files per directory starting at /tmp
    #
    #    split_dirs = Split_dirs(180007, filenum=15, path="/tmp/")
    #    for idx, path in split_dirs.getPathGenerator():
    #        open(os.path.join(path, str(idx)), 'a').close()
    pass

if __name__ == "__main__":
    unittest.main()

