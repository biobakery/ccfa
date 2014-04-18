import os

c_repository_root = "/vagrant/data/ccfa/users"
settings_env_var  = "MIBC_SETTINGS_FILE"

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

class workflows(object):
    class metaphlan2(object):
        bowtie2db = "/vagrant/metaphlandb/mpa.200.ffn"
        mpa_pkl   = "/vagrant/metaphlandb/mpa.200.pkl"
    class sixteen(object):
        otu_taxonomy = "/vagrant/ccfa/data/gg_13_8_otus/taxonomy/99_otu_taxonomy.txt"
        otu_refseq   = "/vagrant/ccfa/data/gg_13_8_otus/rep_set/99_otus.fasta"


class web(object):
    host = "0.0.0.0"
    port = 8080

# Pay no attention to that man behind the curtain

_settings_file = ""
if settings_env_var in os.environ:
    _settings_file = os.environ[settings_env_var]
else:
    # please go from global to local in this tuple literal as the last
    # item, if it exists, is used as the settings file
    for _p in ("/etc/mibc/settings.py", "settings.py"):
        if os.path.exists(_p):
            _settings_file = _p

if _settings_file:
    import imp
    _mod = imp.load_source("settings", _settings_file)
    globals().update([
        ( _s, getattr(_mod,_s) )
        for _s in dir(_mod)
        if not _s.startswith('__')
    ])

try:
    with open("/etc/ldap.conf") as f:
        for match in re.finditer(r'\s*bindpw\s+(\S+)', f.read()):
            # catch the last bindpw in the ldap.conf
            ldap.bind_pw = match.group(1)
except:
    pass
