
c_repository_root = "/var/www/ccfa/data/files/users"

class email(object):
    default_from_addr = "ccfa.mibc@gmail.com"
    default_subject   = "A note from the CCFA MIBC"
    default_smtp_serv = "localhost"

class ldap(object):
    url     = "dc2-rc"
    bind_dn = "CN=clusterldap,OU=Unmanaged Service Accounts,DC=rc,DC=domain"
    bind_pw = r'p$e9e!A2'
    
