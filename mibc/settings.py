import re

c_repository_root = "/var/www/ccfa/data/files/users"

class email(object):
    default_from_addr = "ccfa.mibc@gmail.com"
    default_subject   = "A note from the CCFA MIBC"
    default_smtp_serv = "localhost"

class ldap(object):
    url         = "ldaps://dc2-rc/"
    bind_dn     = "CN=clusterldap,OU=Unmanaged Service Accounts,DC=rc,DC=domain"
    bind_pw     = ""
    search_base = "DC=rc,DC=domain"
    
class users(object):
    ignored = ['admin']


try:
    with open("/etc/ldap.conf") as f:
        for match in re.finditer(r'\s*bindpw\s+(\S+)', f.read()):
            # catch the last bindpw in the ldap.conf
            ldap.bind_pw = match.group(1)
except:
    pass
