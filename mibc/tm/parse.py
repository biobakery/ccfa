#!/usr/bin/env python
import os.path
import json
import tasks


#Status = Enum(['WAITING', 'QUEUED', 'RUNNING', 'FINISHED'])

class Parse(object):
    """ Parse the json dag passed in via cmdline args """

    def __init__(self, data):
        self.taskList = []
        self.completedTasks = []
        self.waitingTasks = []
        self.queuedTasks = []
        self.data = data
        self.run = 1 # this should be read from filespace...

        nodes = data['dag']
        for node in nodes:
            self.taskList.append(tasks.Task(node))

    def getTasks(self):
        return self.taskList


    def setupQueue(self):
        """ method starts the flow 
            need to keep track of what run we are on - has this
            flow been processed before???
        """
        for task in self.taskList:
            if task.getName() == 'root':
                self.completedTasks.append(task)
            elif task.isFinished():
                self.completedTasks.append(task)

        for task in self.taskList:
            if task not in self.completedTasks:
                if task.canRun():
                    self.queuedTasks.append(task)
                else:
                    self.waitingTasks.append(task)

       
    def parseQueue(self):
        """ method searches waiting queue for tasks that
            could be queued to run 
        """
        for task in self.waitingTasks[:]:
            if task.canRun():
                self.queuedTasks.append(task)
                self.waitingTasks.remove(task)

    def status(self):
        print "=========================="
        print "completed tasks: " + str(len(self.completedTasks))
        print "waiting tasks: " + str(len(self.waitingTasks))
        print "queued tasks: " + str(len(self.queuedTasks))
        print "=========================="

