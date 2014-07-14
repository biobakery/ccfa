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
        # before any tasks are run, find out if this task already ran
        if self.doAllProductsExist():
            self.setCompleted()
            self.status = Status.FINISHED
            self.result = Result.SUCCESS

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
        for parentId in self.getParentIds():
            if not self.taskList[parentId].isComplete():
                return False
        for dependency in self.json_node['depends']:
            if (not os.path.isfile(dependency)):
                print "dependency not found: " + dependency
                return False
        return True

    def doAllProductsExist(self):
        """ Method should only be used prior to running any tasks! """
        for product in self.json_node['produces']:
            if (not os.path.isfile(product)):
                return False
        return True

    def hasFailed(self):
        if self.getStatus() == Status.FINISHED:
            if self.getResult() == Result.FAILURE:
                return True
            if self.getResult() == Result.NA:
                print "Warning: task " + self.getName() + " is complete but result is NA"
        # next check if our parents have failed
        for parentId in self.getParentIds():
            if self.taskList[parentId].hasFailed():
                self.setStatus(Status.FINISHED)
                self.setResult(Result.FAILURE)
                self.setCompleted()
                return True
        return False

    def getParentIds(self):
        idList = []
        for parent in self.json_parents:
            idList.append(parent['id'])
        return idList

    def getStatus(self):
        if not self.isComplete() and self.pid is not None:
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
        if self.status == Status.FINISHED and self.result == Result.NA:
            print "Warning: task " + self.getName() + " status is " + self.status + " but result is " + self.result +" and completed is " + str(self.isComplete())
        return self.status

    def setStatus(self, givenStatus):
        if (givenStatus in Status):
            self.status = givenStatus
        else: 
            logging.error("Setting task status to unknown status: " + givenStatus)

    def setResult(self, givenResult):
        if givenResult in Result:
            self.result = givenResult
        else:
            logging.error("Setting task result to unknown result: " + givenResult)

    def getResult(self):
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
        #print "scriptname: " + scriptpath
        # spawn subprocess script & store process id/obj
        self.pid = subprocess.Popen([scriptpath])

    def __str__(self):
        str = """Task: {name}
                 Result: {result}
                 Status: {status}""".format(name=self.getName(), result = self.result, status=self.status)
        return str
