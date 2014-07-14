#!/usr/bin/env python
import os.path
import json
import tasks
import time


class TaskManager(object):
    """ Parse the json dag passed in via cmdline args """

    def __init__(self, taskList, directory):
        self.taskList = taskList
        self.completedTasks = []
        self.waitingTasks = []
        self.queuedTasks = []
        self.directory = directory
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
                task.setCompleted()
            elif task.isComplete():
                print "task: " + task.getName() + " is complete."
                self.completedTasks.append(task)

        for key,task in self.taskList.iteritems():
            if task not in self.completedTasks:
                if task.canRun():
                    task.setStatus(tasks.Status.QUEUED)
                    self.queuedTasks.append(task)
                else:
                    task.setStatus(tasks.Status.WAITING)
                    self.waitingTasks.append(task)

    def runQueue(self):
        """ attempts to spawn subprocesses in order to 
            launch all tasks in queuedTasks
            For now, this method will run until all jobs
            are finished...
        """
        #import pdb; pdb.set_trace()
        while (len(self.waitingTasks) > 0) or (len(self.queuedTasks) > 0):

            # loop thru waiting tasks
            for task in self.waitingTasks[:]:
                print "waiting task " + task.getName()
                if task.canRun():
                    task.setStatus(tasks.Status.QUEUED)
                    self.queuedTasks.append(task)
                    self.waitingTasks.remove(task)
                if task.hasFailed():
                    #task.setStatus(task.Status.COMPLETED)
                    self.completedTasks.append(task)
                    self.waitingTasks.remove(task)

            # loop thru queued tasks
            for task in self.queuedTasks[:]:
                print "working on queued task " + task.getName()
                print task
                if task.getStatus() == tasks.Status.QUEUED:
                    task.run()
                elif task.getStatus() == tasks.Status.FINISHED:
                    self.completedTasks.append(task)
                    self.queuedTasks.remove(task)

            self.status()
            print ""
            time.sleep(5)


    def status(self):
        print "=========================="
        failed = [x for x in self.completedTasks if x.hasFailed()]
        #for task in self.completedTasks:
        print "completed tasks: " + str(len(self.completedTasks)) + " " + str(len(failed)) + " failed."
        #for task in self.completedTasks:
        #    print "  " + task.getName()
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

