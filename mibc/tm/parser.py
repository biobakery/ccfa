#!/usr/bin/env python
import os.path
import json
import tasks
import time
import sys


class Parser(object):
    """ Parse the json dag passed in via cmdline args """

    def __init__(self, data, taskType):
        self.taskList = {}

        nodes = data['dag']
        for node in nodes:
            if taskType == tasks.Type.LOCAL:
                task = tasks.LocalTask(node)
                if task.getId in self.taskList:
                    print "Error: duplicate task Identifier: " + task.getId
                    sys.exit(-1)
                self.taskList[task.getID] = task;
            else
                print "Task type: " + taskType + " not supported (yet)"
                sys.exit(0);

        # set the parent indexes for each task
        #for k, task in self.taskList.iteritems():
        #    for parentId            


    def getTasks(self):
        return self.taskList


    def getTask(self, idx):
        if idx in taskList:
            return taskList[idx]
        print "Error: " + idx + " not in taskList."
        return None

