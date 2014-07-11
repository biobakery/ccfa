#!/usr/bin/env python
import os.path
import json
import tasks
import time


class TaskManager(object):
    """ Parse the json dag passed in via cmdline args """

    def __init__(self, taskList):
        self.taskList = taskList
        self.completedTasks = []
        self.waitingTasks = []
        self.queuedTasks = []
        self.data = data
        self.run = 1 # this should be read from filespace...

    def getTasks(self):
        return self.taskList

    def setupQueue(self):
        """ method starts the flow 
            at this point, no tasks have been run and the filesystem is quiet
            assume all tasks that have existing products on the filesystem 
            are complete.  
        """
        for key,task in self.taskList.iteritems():
            if task.getName() == 'root':
                self.completedTasks.append(task)
            elif task.isStaticallyFinished():
                self.completedTasks.append(task)
                task.setComplete()

        for key,task in self.taskList.iteritems():
            if task not in self.completedTasks:
                if task.canRun():
                    self.queuedTasks.append(task)
                else:
                    self.waitingTasks.append(task)

    def runQueue(self):
        """ attempts to spawn subprocesses in order to 
            launch all tasks in queuedTasks
            For now, this method will run until all jobs
            are finished...
        """
        while (len(self.waitingTasks) > 0) or (len(self.queuedTasks) > 0):

            # loop thru waiting tasks
            for task in self.waitingTasks[:]:
                if task.canRun():
                    self.queuedTasks.append(task)
                    task.setStauts(tasks.Status.QUEUED)
                    self.waitingTasks.remove(task)

            # loop thru queued tasks
            for task in self.queuedTasks[:]:
                if task.getStatus() == tasks.Status.QUEUED:
                    task.setStatus(tasks.Status.RUNNING)
                    task.run()
                elif task.getStatus() == tasks.Status.FINISHED:
                    self.completedTasks.append(task)
                    self.queuedTasks.remove(task)

            self.status()
            print ""
            time.sleep(5)
            self.parseQueue()


    def status(self):
        print "=========================="
        failed = [x for x in self.completedTasks if x.hasFailed()]
        #for task in self.completedTasks:
        print "completed tasks: " + str(len(self.completedTasks)) + " " + str(len(failed)) + " failed."
        #for task in self.completedTasks:
        #    print "  " + task.getName()
        print "waiting tasks: " + str(len(self.waitingTasks))
        #for task in self.waitingTasks:
        #    print "  " + task.getName()
        print "queued tasks: " + str(len(self.queuedTasks))
        #for task in self.queuedTasks:
        #    print "  " + task.getName()

        print "=========================="

    def isQueueEmpty(self):
        if len(self.waitingTasks) > 0:
            return False
        if len(self.queuedTasks) > 0:
            return False
        return True

