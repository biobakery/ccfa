#!/usr/bin/env python
import os, sys
import logging
import subprocess, tempfile
import tornado
import signal
import hashlib
from time import sleep
import globals

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
Result = Enum(['NA', 'SUCCESS', 'RUN_PREVIOUSLY', 'FAILURE'])

class Task(object):
    """ Parent class for all tasks """

    def __init__(self, jsondata, taskList, fifo):
        self.taskList = taskList
        self.fifo = fifo
        self.directory = "NA"
        self.completed = False
        self.json_node = jsondata['node']
        self.json_parents = jsondata['parents']
        self.setStatus(Status.WAITING)
        self.taskType = Type.EC2
        self.result = Result.NA
        self.return_code = None
        self.pid = None
        self.parents = []
        self.tm = None
        # before any tasks are run, find out if this task already ran
        if self.doAllProductsExist():
            self.setCompleted(True)
            self.setStatus(Status.FINISHED)
            self.result = Result.RUN_PREVIOUSLY

    def getTaskNum(self):
        return self.num

    def setTaskNum(self, num):
        self.num = num

    def getTaskId(self):
        return str(self.getTaskNum()) + "-" + self.getSimpleName()

    def getTaskList(self):
        return self.taskList
  
    def setFilename(self, path):
        self.setOutputDirectory(path)
        self.filename = os.path.join(path, str(self.getTaskNum()) + "-" + self.getSimpleName())

    def getFilename(self):
        return self.filename

    def setCompleted(self, flag):
        self.completed = flag

    def isComplete(self):
        return self.completed

    def setReturnCode(self, code):
        self.return_code = code

    def getReturnCode(self):
        return self.return_code

    def run(self, callback):
        #print "in parent Task class setting status to RUNNING"
        self.setStatus(Status.RUNNING)
        self.tm = callback

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
                self.setCompleted(True)
                return True
        return False

    def getParentIds(self):
        idList = []
        for parent in self.json_parents:
            idList.append(parent['id'])
        return idList

    def getStatus(self):
        if not self.isComplete() and self.return_code is not None:
            if self.return_code == 0:
                print >> sys.stderr, "FINISHED TASK: " + self.getName()
                self.setStatus(Status.FINISHED)
                self.result = Result.SUCCESS
            else:
                print >> sys.stderr, "FINISHED (FAILED) TASK: " + self.getName() + " " + str(self.getReturnCode())
                self.setStatus(Status.FINISHED)
                self.result = Result.FAILURE
            self.setCompleted(True)
        if self.status == Status.FINISHED and self.result == Result.NA:
            print "Warning: task " + self.getName() + " status is " + self.status + " but result is " + self.result +" and completed is " + str(self.isComplete())
        return self.status

    def setStatus(self, givenStatus):
        if (givenStatus in Status):
            self.status = givenStatus
            if self.fifo is not None:
                print >> self.fifo, "Task " + self.getName() + " status is now " + givenStatus
        else: 
            logging.error("Setting task status to unknown status: " + givenStatus)

    def setResult(self, givenResult):
        if givenResult in Result:
            self.result = givenResult
        else:
            logging.error("Setting task result to unknown result: " + givenResult)

    def getResult(self):
        return self.result

    def getProducts(self):
        return self.json_node['produces']

    def getType(self):
        return self.taskType

    def getId(self):
        return self.json_node['id']

    def getCommand(self):
        return self.json_node['command']

    def getName(self):
        return self.json_node['name']

    def getSimpleName(self):
        return self.getName().split(':')[0]

    def getJson(self):
        return self.json_node

    def setOutputDirectory(self, givenDir):
        self.directory = givenDir

    def callback(self, exit_code):
        print "callback task: " + self.getName() + " " + str(exit_code)
        self.setReturnCode(exit_code)
        self.tm.runQueue()

    def cleanup(self):
        print "cleaning up " + self.getName()
        #if self is not None and self.pid is not None and self.pid.pid is not None:
        try:
            os.kill({self.pid.pid}, signal.SIGTERM)
        except (AttributeError, TypeError):
            print self.getName() + " job removed."
        for product in self.getProducts():
            if os.path.exists(product):
                print "removing " + product
                os.unlink(product)

    def __str__(self):
        return "Task: " + self.json_node['name']

class LocalTask(Task):
    """ Tasks run on local workstation"""

    def __init__(self, jsondata, taskList, fifo):
        super(LocalTask, self).__init__(jsondata, taskList, fifo)
        self.taskType = Type.LOCAL

    def run(self, callback):
        super(LocalTask, self).run(callback)
        # create subprocess script
        #script = tempfile.NamedTemporaryFile(dir=self.directory, delete=False)
        script = self.getFilename()
        sub = """#!/bin/sh
source {SOURCE_PATH}
echo "<PRE>" > {name}.log
date >> {name}.log
echo {scriptname} >> {name}.log
echo "-- script --" >> {name}.log
cat {name} >> {name}.log
echo >> {name}.log
echo "-- end script --" >> {name}.log
echo "-- task cmd output --" >> {name}.log
/usr/bin/env time -p -a -o {name}.log {script} >> {name}.log 2>&1
cmd_exit=`echo $?`
echo "-- end task cmd output --" >> {name}.log
date >> {name}.log
exit $cmd_exit
"""     .format(scriptname=self.getName(), 
                       script=self.getCommand(), 
                       name=script,
                       SOURCE_PATH=globals.config['SOURCE_PATH'])
        with open(script, 'w+') as f:
          f.write(sub)

        os.chmod(script, 0755)
        scriptpath = os.path.abspath(script)
        self.pid = tornado.process.Subprocess([scriptpath])
        self.pid.set_exit_callback(self.callback)

    def __str__(self):
        str = """Task: {name}
                 Result: {result}
                 Status: {status}""".format(name=self.getName(), result = self.result, status=self.status)
        return str


class LSFTask(Task):
    """ Tasks run on LSF queue """

    def __init__(self, jsondata, taskList, fifo):
        super(LSFTask, self).__init__(jsondata, taskList, fifo)
        self.taskType = Type.LSF

    def run(self, callback):
        super(LSFTask, self).run(callback)
        # create subprocess script
        cluster_script = os.path.join(globals.config['TEMP_PATH'], self.getTaskId() + ".sh")
        monitor_script =  os.path.join(globals.config['TEMP_PATH'], self.getTaskId() + "-monitor.sh")
        sub = """#!/bin/sh
#BSUB {CLUSTER_QUEUE}
#BSUB -o {OUTPUT}
source {SOURCE_PATH}
{picklescript} -r
"""     .format(CLUSTER_QUEUE=globals.config['CLUSTER_QUEUE'],
                picklescript=self.getCommand(), 
                SOURCE_PATH=globals.config['SOURCE_PATH'],
                OUTPUT=monitor_script+".log")
                 
        with open(cluster_script, 'w+') as f:
          f.write(sub)
        os.chmod(cluster_script, 0755)

        #import pdb;pdb.set_trace()
        sub = """#!/bin/sh
# kickoff and monitor LSF cluster job

# setup LSF environment
eval export DK_ROOT="/broad/software/dotkit";
. /broad/software/dotkit/ksh/.dk_init
use LSF >> {log}

which bsub >> {log}
if [ $? != 0 ];then
  echo "can't find use" >> {log}
  reuse LSF >> {log}
fi

# launch job

echo "eval {CLUSTER_JOB} {taskname} < {cluster_script}" >> {log}
jobid_str=`eval {CLUSTER_JOB} {taskname} < "{cluster_script}"`
echo "jobid_str: +${{jobid_str}}+" >> {log}
job_id=`echo ${{jobid_str}} | awk -v i={CLUSTER_JOBID_POS} '{{printf $i}}' | sed 's/^<//' | sed 's/>$//'`

echo "job_id: +${{job_id}}+" >> {log}

# monitor job
done="no"
while [ "${{done}}" != "yes" ]; do

  raw_output=`{CLUSTER_QUERY} ${{job_id}}`
  echo "raw_output: ${{raw_output}}" >> {log}
  regex="${{job_id}}[\t ]"
  output=`{CLUSTER_QUERY} ${{job_id}} | grep "$regex" | awk -v i={CLUSTER_STATUS_POS} '{{printf $i}}'`
  echo "output: ${{output}}" >> {log}

  case ${{output}} in

    PEND)      ;;
    RUN)       ;;
    DONE)      STATUS="OK" && done="yes";;
    COMPLETED) STATUS="OK" && done="yes";;
    EXIT)      STATUS="FAILED" && done="yes";;
    FAILED)    STATUS="FAILED" && done="yes";;
    CANCELLED|CANCELLED+) STATUS="CANCEL" && done="yes";;
    TIMEOUT)   export STATUS="TIMEOUT" && done="yes";;
    NODE_FAIL) export STATUS="RETRY" && done="yes";;
    *)         ;;

  esac

  sleep 60
done
if [ "$STATUS" != "OK" ]; then
    exit -1
else 
    exit 0
fi

"""     .format(cluster_script=cluster_script,
                   CLUSTER_JOB=globals.config['CLUSTER_JOB'],
                   taskname=self.getTaskId(),
                   CLUSTER_JOBID_POS=globals.config["CLUSTER_JOBID_POS"],
                   CLUSTER_QUERY=globals.config["CLUSTER_QUERY"],
                   CLUSTER_STATUS_POS=globals.config["CLUSTER_STATUS_POS"],
                   log=monitor_script+".log")
        with open(monitor_script, 'w+') as f:
          f.write(sub)

        os.chmod(monitor_script, 0755)
        scriptpath = os.path.abspath(monitor_script)
        self.pid = tornado.process.Subprocess([scriptpath])
        self.pid.set_exit_callback(self.callback)

    def __str__(self):
        str = """Task: {name}
                 Result: {result}
                 Status: {status}""".format(name=self.getName(), result = self.result, status=self.status)
        return str

