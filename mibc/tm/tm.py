#!/usr/bin/env python
import os.path
import json
import tasks
import time
import sys

class TaskManager(object):
    """ Parse the json dag passed in via cmdline args """

    def __init__(self, taskList, governor=99):
        self.taskList = taskList
        self.completedTasks = []
        self.waitingTasks = []
        self.queuedTasks = []
        self.governor = governor
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
        #while (len(self.waitingTasks) > 0) or (len(self.queuedTasks) > 0):
        if True:

            # loop thru waiting tasks
            for task in self.waitingTasks[:]:
                if task.canRun():
                    task.setStatus(tasks.Status.QUEUED)
                    self.queuedTasks.append(task)
                    self.waitingTasks.remove(task)
                if task.hasFailed():
                    self.completedTasks.append(task)
                    self.waitingTasks.remove(task)

            # loop thru queued tasks
            for task in self.queuedTasks[:]:
                if task.getStatus() == tasks.Status.QUEUED:
                    if self.governor > 0:
                        self.governor -= 1
                        task.run(self)
                elif task.getStatus() == tasks.Status.FINISHED:
                    self.governor += 1
                    self.completedTasks.append(task)
                    self.queuedTasks.remove(task)

            #self.status()
            #time.sleep(0.2)


    def status(self):
        print >> sys.stderr, "=========================="
        failed = [x for x in self.completedTasks if x.hasFailed()]
        #for task in self.completedTasks:
        print >> sys.stderr, "completed tasks: (" + str(len(self.completedTasks)) + " " + str(len(failed)) + " failed.)"
        #for task in self.completedTasks:
        #    print "  " + task.getName()
        print >> sys.stderr, "waiting tasks: " + str(len(self.waitingTasks))
        #for task in self.waitingTasks:
        #    print "  " + task.getName()
        running = [task for task in self.queuedTasks if task.getStatus() == tasks.Status.RUNNING]
        print >> sys.stderr, "queued tasks: " + str(len(self.queuedTasks)) + " (" + str(len(running)) + " running.)"
        #    print "  " + task.getName()

        print >> sys.stderr, "=========================="

    def isQueueEmpty(self):
        if len(self.waitingTasks) > 0:
            return False
        if len(self.queuedTasks) > 0:
            return False
        return True

    def getFifo(self):
        if fifo is not None:
            return fifo
        else:
            print "Warning: fifo is null"
            return None
