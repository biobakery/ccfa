#!/usr/bin/env python
import os
import logging
import subprocess, tempfile

def nextNum():
    if 'counter' in locals():
        counter += 1
    else: 
        # read counter from disk...
        counterFile=os.getcwd() + "/counter.txt"
        if os.path.isfile(counterFile):
            with open(counterFile) as f:
                counter = int(f.readline())
                counter += 1
        else:
            counter = 1

        with open(counterFile, 'w+') as f:
            f.write(str(counter))
    return counter 

class Enum(set):
    """ duplicates basic java enum functionality """
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError
    def __setattr__(self, name, value):
        print "__setattr__"
    def __delattr__(self, name):
        print "__delattr__"

Status = Enum(['WAITING', 'QUEUED', 'RUNNING', 'FINISHED'])
Type = Enum(['LOCAL', 'SLURM', 'LSF', 'EC2'])
Result = Enum(['NA', 'SUCCESS', 'FAILURE'])

class Task(object):
    """ Parent class for all tasks """

    def __init__(self, jsondata, taskList, directory):
        self.taskList = taskList
        self.directory = directory
        self.completed = False
        self.json_node = jsondata['node']
        self.json_parents = jsondata['parents']
        self.status = Status.WAITING
        self.num = nextNum()
        self.taskType = Type.EC2
        self.result = Result.NA
        self.pid = None
        self.parents = []

    def getTaskNum(self):
        return self.num
   
    def setCompleted(self):
        self.completed = True

    def isComplete(self):
        return self.completed

    def run(self):
        #print "in parent Task class setting status to RUNNING"
        self.status = Status.RUNNING

    def canRun(self):
        for dependency in self.json_node['depends']:
            if (not os.path.isfile(dependency)):
                print "dependency not found: " + dependency
                return False
        #import pdb;pdb.set_trace()
        for parentId in self.getParentIds():
            if not self.taskList[parentId].isComplete():
                return False
        return True

    def doAllProductsExist(self):
        """ Method should only be used prior to running any tasks! """
        for product in self.json_node['produces']:
            if (not os.path.isfile(product)):
                return False
        return True

    def hasFailed(self):
        # first check our static 'flags' for status
        if self.isComplete():
            if self.getResult() == Result.FAILURE:
                return True
        # next check if we've finished running
        if self.pid is not None:
            if self.pid.poll() == 0:
                return False
            else:
                # we've failed - set our states
                self.setCompleted()
                self.setStatus(Status.FINISHED)
                self.setResult(Result.FAILURE)
                return True
        # next check if our parents have failed
        for parentId in self.getParentIds():
            if self.taskList[parentId].hasFailed():
                self.setCompleted()
                self.setStatus(Status.FINISHED)
                self.setResult(Result.FAILURE)
                return True
        return False

    def getParentIds(self):
        idList = []
        for parent in self.json_parents:
            idList.append(parent['id'])
        return idList

    def getStatus(self):
        if self.isComplete():
            self.status = Status.FINISHED
        elif self.pid is not None:
            if self.pid.poll() is not None:
                if self.pid.poll() == 0:
                    print "COMPLETED TASK: " + self.getName()
                    self.status = Status.FINISHED
                    self.result = Result.SUCCESS
                else:
                    print "COMPLETED (FAILED) TASK: " + self.getName() + " " + str(self.pid.poll())
                    self.status = Status.FINISHED
                    self.result = Result.FAILURE
                self.setCompleted()
        if self.result == Result.NA:
            print "Warning: status is " + self.status + " but result is " + self.result
        return self.status

    def setStatus(self, givenStatus):
        if (givenStatus in Status):
            self.status = givenStatus
        else: 
            logging.error("Setting task status to unknown status: " + givenStatus)

    def setResult(self, givenResult):
        if givenResult in Result:
            self.result == givenResult
        else:
            logging.error("Setting task result to unknown result: " + givenResult)

    def getResult(self):
        self.getStatus() # force check subprocess for completion
        return self.result

    def getType(self):
        return self.taskType

    def getId(self):
        return self.json_node['id']

    def cleanupPid(self):
        os.unlink(script.name)

    def getCommand(self):
        return self.json_node['command']

    def getName(self):
        return self.json_node['name']

    def getJson(self):
        return self.json_node

    def __str__(self):
        return "Task: " + self.json_node['name']

class LocalTask(Task):
    """ Tasks run on local workstation"""

    def __init__(self, jsondata, taskList, directory):
        super(LocalTask, self).__init__(jsondata, taskList, directory)
        self.taskType = Type.LOCAL

    def run(self):
        print "running local task: " + self.getName()
        super(LocalTask, self).run()
        # create subprocess script
        script = tempfile.NamedTemporaryFile(dir=self.directory, delete=False)
        sub = """#!/bin/sh
                 #{scriptname}
                 source /aux/deploy2/bin/activate
                 cat {name} > {name}.log
                 {script} >> {name}.log 2>&1 
              """.format(scriptname=self.getName(), script=self.getCommand(), name=script.name)
        script.write(sub)
        script.close()
        os.chmod(script.name, 0755)
        scriptpath = os.path.abspath(script.name)
        print "scriptname: " + scriptpath
        # spawn subprocess script & store process id/obj
        self.pid = subprocess.Popen([scriptpath])

