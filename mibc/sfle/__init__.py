import os

def python_cmd():
    if "VIRTUAL_ENV" in os.environ:
        return "%s/bin/python" %(os.environ['VIRTUAL_ENV'])
    else:
        for d in os.environ['PATH'].split(':'):
            might_be_python = os.path.join(d, 'python')
            if os.path.exists(might_be_python):
                return might_be_python
        raise OSError("Unable to locate python somehow")

            
MIBC_ENV_VAR = 'MIBC_TARGET'
SCONS_BASE_CMD_LIST = [ python_cmd(),"/usr/bin/scons" ]
SCONSTRUCT_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "SConstruct"
)
