#!/usr/bin/env python
import os.path
import json
import tasks
import time
import sys
import subprocess

QueueStatus = tasks.Enum(['RUNNING', 'PAUSED', 'STOPPED'])

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
        self.saved_governor = governor
        self.wslisteners = wslisteners
        self.queueStatus = QueueStatus.RUNNING
        self.root = None
        self.run = 1 # this should be read from filespace...

    def getTasks(self):
        return self.taskList

    def setupQueue(self):
        """ method starts the flow 
            at this point, no tasks have been run and the filesystem is quiet
            assume all tasks that have existing products on the filesystem 
            are complete.  
        """
        firsttime = True
        for key,task in self.taskList.iteritems():
            if task.getName() == 'root':
                self.root = task
                self.completedTasks.append(task)
                task.setCompleted(True)
                self.notify(task)
                task.cleanup()
            elif task.isComplete():
                firsttime = False;
                self.completedTasks.append(task)
                self.notify(task)
                task.cleanup()

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
        if firsttime:
            self.callHook("pre")

    def runQueue(self):

        """ attempts to spawn subprocesses in order to 
            launch all tasks in queuedTasks
            For now, this method will run until all jobs
            are finished...
        """

        updates_made = True
        while updates_made:

            updates_made = False
            still_waitingTasks = [];

            # loop thru waiting tasks
            if self.queueStatus != QueueStatus.STOPPED:
                for task in self.waitingTasks:
                    if task.hasFailed():
                        self.completedTasks.append(task)
                        self.notify(task)
                        updates_made = True
                        # We didn't run and we failed so do not invoke hook
                    elif task.canRun():
                        task.setStatus(tasks.Status.QUEUED)
                        self.queuedTasks.append(task)
                        self.notify(task)
                        updates_made = True
                    else:
                        still_waitingTasks.append(task)

                    self.waitingTasks = still_waitingTasks

            # loop thru queued tasks
            still_queuedTasks = []

            if self.queueStatus != QueueStatus.STOPPED:
                for task in self.queuedTasks:
                    if task.getStatus() == tasks.Status.QUEUED:
                        if self.governor > 0:
                            self.governor -= 1
                            task.run(self)
                            self.notify(task)
                        still_queuedTasks.append(task)

                    elif task.getStatus() == tasks.Status.FINISHED:
                        self.governor += 1
                        self.completedTasks.append(task)
                        self.notify(task)
                        updates_made = True
                        # We did run this job - call hook based on status
                        task.callHook()
                    elif task.getStatus() == tasks.Status.RUNNING:
                        still_queuedTasks.append(task)

                self.queuedTasks = still_queuedTasks

            elif self.queueStatus == QueueStatus.STOPPED:
                for task in self.queuedTasks:
                    if task.getStatus() == tasks.Status.FINISHED:
                        task.setReturnCode(None)
                        task.setResult(tasks.Result.NA)
                        task.setStatus(tasks.Status.QUEUED)
                        task.setCompleted(False)
                        self.notify(task)
                        # queue has stopped; task will be rolled back; don't call hook

        if self.isQueueEmpty():
            all_success = True
            for completedTask in self.completedTasks:
                if completedTask.getResult() is tasks.Result.FAILURE:
                    all_success = False
            if all_success:
                self.callHook("post")


    def cleanup(self):
        for task in self.waitingTasks:
            task.cleanup()
        for task in self.queuedTasks:
            task.cleanup_failure()


    def notify(self, task):
        for listener in self.wslisteners:
            listener.taskUpdate(task)

    def status(self):
        print >> sys.stderr, "=========================="
        #failed = [x for x in self.completedTasks if x.hasFailed()]
        #for task in self.completedTasks:
        #    print "  " + task.getName()
        #print >> sys.stderr, "completed tasks: (" + str(len(self.completedTasks)) + " " + str(len(failed)) + " failed.)"
        #for task in self.completedTasks:
        #    print "  " + task.getName()
        #print >> sys.stderr, "waiting tasks: " + str(len(self.waitingTasks))
        #for task in self.waitingTasks:
        #    print "  " + task.getName()
        #running = [task for task in self.queuedTasks if task.getStatus() == tasks.Status.RUNNING]
        #print >> sys.stderr, "queued tasks: " + str(len(self.queuedTasks)) + " (" + str(len(running)) + " running.)"

        print >> sys.stderr, "waiting tasks: " + str(len(self.waitingTasks))
        print >> sys.stderr, "queued tasks: " + str(len(self.queuedTasks))
        print >> sys.stderr, "finished tasks: " + str(len(self.completedTasks))
        print >> sys.stderr, "governor: " + str(self.governor)

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
            task.setScriptfile(rundirectory)

    def getStatus(self):
        return self.status

    def pauseQueue(self):
        print >> sys.stderr, "pauseQueue"
        self.queueStatus = QueueStatus.PAUSED
        self.governor = -99

    def stopQueue(self):
        print >> sys.stderr, "stopQueue"
        self.queueStatus = QueueStatus.STOPPED
        self.governor = -99
        #for task in self.queuedTasks[:]:
        for task in self.queuedTasks:
            if task.getStatus() == tasks.Status.RUNNING:
                task.cleanup()

    def startQueue(self):
        print >> sys.stderr, "startQueue"
        self.queueStatus = QueueStatus.RUNNING
        self.governor = self.saved_governor
        self.runQueue()

    def getQueueStatus(self):
        return self.queueStatus

    def callHook(self, pipeline):
        ''' Method spawns a child process that easily allows user defined things
            to run after the task completes.  This hook calls hooks/post_task_success.sh
            or hooks/post_task_failure.sh based on the task result. '''
        self.setupEnvironment()
        path = os.path.dirname(os.path.realpath(__file__))
        hook = str()
        if pipeline == "pre":
            hook = os.path.join(path, "hooks/pre_pipeline.sh")
        elif pipeline == "post":
            hook = os.path.join(path, "hooks/post_pipeline.sh")
        print >> sys.stderr, "hook: " + hook
        subprocess.call(hook, shell=True)


    def setupEnvironment(self):
        os.environ["TaskName"] = self.root.getName()
        os.environ["TaskResult"] = self.root.getResult()
        os.environ["TaskReturnCode"] = str(self.root.getReturnCode())
        os.environ["TaskScriptfile"] = self.root.getScriptfile()
        os.environ["TaskLogfile"] = self.root.getLogfile()
        productfiles = str()
        for file in self.root.getProducts():
            productfiles += file + " "
        os.environ["TaskProducts"] = productfiles

