#!/usr/bin/env python
import os.path
import json
import tasks
import time


#Status = Enum(['WAITING', 'QUEUED', 'RUNNING', 'FINISHED'])

class Parse(object):
    """ Parse the json dag passed in via cmdline args """

    def __init__(self, data, taskType):
        self.taskList = []
        self.completedTasks = []
        self.waitingTasks = []
        self.queuedTasks = []
        self.data = data
        self.run = 1 # this should be read from filespace...

        nodes = data['dag']
        for node in nodes:
            if taskType == tasks.Type.LOCAL:
                self.taskList.append(tasks.LocalTask(node))

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

    def runQueue(self):
        """ attempts to spawn subprocesses in order to 
            launch all tasks in queuedTasks
            For now, this method will run until all jobs
            are finished...
        """
        #import pdb; pdb.set_trace()
        while (len(self.waitingTasks) > 0) or (len(self.queuedTasks) > 0):
            for task in self.queuedTasks[:]:
                if task.getStatus() == tasks.Status.WAITING:
                    task.setStatus(tasks.Status.QUEUED)
                elif task.getStatus() == tasks.Status.QUEUED:
                    print "running task: " + task.getName()
                    task.run()
                elif task.getStatus() == tasks.Status.FINISHED:
                    self.completedTasks.append(task)
                    self.queuedTasks.remove(task)
                else:
                    # tasks here are either still running or have finished
                    pid = task.getPid()
                    if pid.poll() is not None:
                        task.setStatus(tasks.Status.FINISHED)

            self.status()
            print ""
            time.sleep(10)
            self.parseQueue()


    def status(self):
        print "=========================="
        print "completed tasks: " + str(len(self.completedTasks))
        for task in self.completedTasks:
            print "  " + task.getName()
        print "waiting tasks: " + str(len(self.waitingTasks))
        for task in self.waitingTasks:
            print "  " + task.getName()
        print "queued tasks: " + str(len(self.queuedTasks))
        for task in self.queuedTasks:
            print "  " + task.getName()

        print "=========================="

    def isQueueEmpty(self):
        if len(self.waitingTasks) > 0:
            return False
        if len(self.queuedTasks) > 0:
            return False
        return True

