import subprocess
from collections import defaultdict

from .. import settings


class LDAP(object):
    
    _ldap_attrs = None

    @property
    def ldap_attrs(self):
        if self._ldap_attrs is None:
            opts = { "D": settings.ldap.bind_dn,
                     "w": settings.ldap.bind_pw,
                     "H": settings.ldap.url }
            
            args = "(uid=%s)" %(self.name)
            args = [args]

            cmd = list()
            for k, v in opts.iteritems():
                cmd.append( "-%s" %(k) )
                cmd.append( v )
                
            cmd.extend(args)

            process = subprocess.Popen(cmd, 
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE )
            out, err = process.communicate()
            
            if process.returncode != 0:
                raise IOError("Ldap user lookup failed, %s" %(err))

            self._ldap.attrs = defaultdict(list)
            for match in re.finditer(r'(\S+): (\S+)', out):
                key, val = match.groups()
                self._ldap.attrs[key].append(val)
            
        return self._ldap_attrs
        
                 
        
