#!/usr/bin/env python
import os.path

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

    def __init__(self, jsondata):
        self.json_node = jsondata['node']
        self.json_parents = jsondata['parents']
        self.status = Status.WAITING
        self.num = nextNum()
        self.taskType = Type.EC2
        self.result = Result.NA

    def getTaskNum(self):
        return self.num
    
    def run(self):
        print "not implemented in base class"

    def canRun(self):
        for dependency in self.json_node['depends']:
            if (not os.path.isfile(dependency)):
                print "dependency not found: " + dependency
                return False
        return True

    def isFinished(self):
        for product in self.json_node['produces']:
            if (not os.path.isfile(product)):
                return False
        return True

    def getParentIds(self):
        idList = []
        for parent in self.json_parents:
            idList.append(parent['id'])
        return idList

    def getStatus(self):
        return self.status

    def getResultStatus(self):
        return self.result

    def getType(self):
        return self.taskType

    def getID(self):
        return self.json_node['id']

    def getName(self):
        return self.json_node['name']

    def getJson(self):
        return self.json_node

    def __str__(self):
        return "Task: " + self.json_node['name']

class LocalTask(Task):
    """ Tasks run on local workstation"""

    def __init__(self, jsondata):
        super(LocalTask, self).__init__(jsondata)
        self.taskType = Type.LOCAL

    def run(self):
        print "running task on local host.  tbd..."

