import logging
import optparse
from pprint import pprint

from .render import render_to_email

from .. import models
from ..validate import validate

opts_list = [
    optparse.make_option('-n', '--dry-run', action="store_true", 
                         dest="dry_run",
                         help="Instead of emailing users, print the email."),
     optparse.make_option('-l', '--logging', action="store", type="string",
                         dest="logging", default="INFO",
                         help="Logging verbosity, options are debug, info, "+
                         "warning, and critical")
]

repo = models.Repository()

def _parse_path(*paths):
    project_set = set()
    for path in paths:
        path = path.split("/")
        user = repo.users[path[0]]
        if len(path) > 1:
            project = path[1]
            project_set.add( user.projects[project] )
        else:
            for project in user.projects.all():
                project_set.add( project )

    return list(project_set)


def _maybe_email_somebody( results_list, project, dry_run=False ):
    email = getattr(project, "researcher_contact_email", False)
    if not email:
        # Go get it from ldap
        email = project.user.ldap_attrs['mail']

    context = dict( errors = results_list,
                    project = project )

    if dry_run:
        s = "Project %s Validation Results" %(project.name)
        print s
        print "-"*len(s)
        print "To: %s" %(email)
        pprint(context)
        print "-"*len(s)
        print
    else:
        render_to_email( context, list(email) )


def main():
    parser = optparse.OptionParser(option_list=opts_list)
    (opts, args) = parser.parse_args()
    logging.getLogger().setLevel(getattr(logging, opts.logging.upper()))
    logging.basicConfig(
        format="%(asctime)s %(levelname)s: %(message)s")

    projects_to_validate = _parse_path(*args)
    for project in projects_to_validate:
        results = validate(project)
        results = set([ msg
                        for indicator, msg in results
                        if indicator is not True ])

        if len(results) > 0:
            _maybe_email_somebody( list(results), project, opts.dry_run )
        else:
            logging.info("No issues found with project %s" %(project.name))


if __name__ == '__main__':
    main()
