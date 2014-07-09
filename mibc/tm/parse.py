#!/usr/bin/env python
import os.path
import json
import tasks


#Status = Enum(['WAITING', 'QUEUED', 'RUNNING', 'FINISHED'])

class Parse(object):
    """ Parse the json dag passed in via cmdline args """

    def __init__(self, data):
        self.taskList = []
        self.data = data

        nodes = data['dag']
        for node in nodes:
            self.taskList.append(tasks.Task(node))

    def getTasks(self):
        return self.taskList



