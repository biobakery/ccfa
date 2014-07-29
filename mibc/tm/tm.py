#!/usr/bin/env python
import os.path
import json
import tasks
import time
import sys

def nextNum(localDir):
    ''' Returns the next sequencial whole number.  Used for unique task ids. '''
    if True:
        # read counter from disk...
        counterFile=os.path.join(localDir + "/counter.txt")
        if os.path.isfile(counterFile):
            with open(counterFile) as f:
                counter = int(f.readline())
                counter += 1
        else:
            counter = 1 
        with open(counterFile, 'w+') as f:
            f.write(str(counter))
        return counter

class TaskManager(object):
    """ Parse the json dag passed in via cmdline args """

    def __init__(self, taskList, wslisteners, governor=99):
        self.taskList = taskList
        self.completedTasks = []
        self.waitingTasks = []
        self.queuedTasks = []
        self.governor = governor
        self.wslisteners = wslisteners
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
                self.notify(task)
            elif task.isComplete():
                self.completedTasks.append(task)
                self.notify(task)

        for key,task in self.taskList.iteritems():
            if task not in self.completedTasks:
                if task.canRun():
                    task.setStatus(tasks.Status.QUEUED)
                    self.queuedTasks.append(task)
                    self.notify(task)
                else:
                    task.setStatus(tasks.Status.WAITING)
                    self.waitingTasks.append(task)
                    self.notify(task)

    def runQueue(self):

        """ attempts to spawn subprocesses in order to 
            launch all tasks in queuedTasks
            For now, this method will run until all jobs
            are finished...
        """
        updates_made = True
        while updates_made:

            updates_made = False
            # loop thru waiting tasks
            for task in self.waitingTasks[:]:
                if task.canRun():
                    task.setStatus(tasks.Status.QUEUED)
                    self.queuedTasks.append(task)
                    self.waitingTasks.remove(task)
                    self.notify(task)
                    updates_made = True
                if task.hasFailed():
                    self.completedTasks.append(task)
                    self.waitingTasks.remove(task)
                    self.notify(task)
                    updates_made = True

            # loop thru queued tasks
            for task in self.queuedTasks[:]:
                if task.getStatus() == tasks.Status.QUEUED:
                    if self.governor > 0:
                        self.governor -= 1
                        task.run(self)
                        self.notify(task)
                elif task.getStatus() == tasks.Status.FINISHED:
                    self.governor += 1
                    self.completedTasks.append(task)
                    self.queuedTasks.remove(task)
                    self.notify(task)
                    updates_made = True

            # check for unrunable waiting tasks
            #for task in self.waitingTasks[:]:
            #    if not task.canRun():
            #        print "task: " + task.getSimpleName() + " possible dead task"
            #        problem = True
            #        for parentId in task.getParentIds():
            #            parentTask = task.getTaskList()[parentId]
            #            if parentTask not in self.completedTasks:
            #                print "task: " + task.getSimpleName() + " NOT dead task due to parent " + parentTask.getSimpleName() + " still tbd"
            #                problem = False
            #                break
            #        if problem:
            #            print "Warning: Task " + task.getName() + " cannot proceed - marking as failed"
            #            task.setComplete()
            #            task.setStatus(tasks.Status.FINISHED)
            #            task.setResult(tasks.Result.FAILURE)
            #            self.completedTasks.append(task)                
            #            self.waitingTasks.remove(task)
            #            self.notify(task)
            #self.status()

    def cleanup(self):
        for task in self.queuedTasks[:]:
            if task.getStatus() == tasks.Status.RUNNING:
                task.cleanup()


    def notify(self, task):
        for listener in self.wslisteners:
            listener.taskUpdate(task)

    def status(self):
        print >> sys.stderr, "=========================="
        failed = [x for x in self.completedTasks if x.hasFailed()]
        #for task in self.completedTasks:
        #    print "  " + task.getName()
        print >> sys.stderr, "completed tasks: (" + str(len(self.completedTasks)) + " " + str(len(failed)) + " failed.)"
        for task in self.completedTasks:
            print "  " + task.getName()
        print >> sys.stderr, "waiting tasks: " + str(len(self.waitingTasks))
        for task in self.waitingTasks:
            print "  " + task.getName()
        running = [task for task in self.queuedTasks if task.getStatus() == tasks.Status.RUNNING]
        print >> sys.stderr, "queued tasks: " + str(len(self.queuedTasks)) + " (" + str(len(running)) + " running.)"

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

    def setTaskOutputs(self, rundirectory):
        print "RUNDIRECTORY: " + rundirectory
        for k, task in self.getTasks().iteritems():
            task.setTaskNum(nextNum(rundirectory))
            task.setFilename(rundirectory)

