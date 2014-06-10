
from doit.runner import Runner, MRunner, MThreadRunner

class JenkinsRunner(Runner):
    pass

RUNNER_MAP = {
    'jenkins': JenkinsRunner,
    'mrunner': MRunner,
    'runner': Runner,
    'mthreadrunner': MThreadRunner
}
