import os, json

def init(directory):
    ''' method contains global variables '''
    global config
    config = {}
    # load configuration parameters (if they exist)
    path = os.path.join(directory, "configuration_parameters.txt")
    if os.path.exists(path):
        with open(path) as config_file:
            config = json.load(config_file)
            print "config loaded."

