
from email.utils import parseaddr
import re, datetime, urllib

class Validators(object):

    @classmethod
    def alias(cls,alias):
        """ TODO: improve later """
        return (len(alias) > 3 and len(alias) < 15 and re.match('^[A-Za-z0-9_-]+$', alias) is not None)

    @classmethod
    def password(cls,password):
        return (len(password) > 7 and len(password) < 20 and re.search('\d+',password) and re.search('[a-zA-Z]',password))

    @classmethod
    def email(cls,email):
        e = re.compile('([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)')
        return (len(e.findall(email)) > 0)
        #return (parseaddr(email)[1] != '')

    @classmethod
    def sanatize_textsafe(cls,text):
        """ Remove all types of spaces """
        return re.sub('[<>/+{}&@~`]','',text)
        
    @classmethod
    def sanatize(cls,text):
        """ Remove all types of spaces """
        return text.replace(' ','')
        
    @classmethod
    def bool(cls,o):
        if isinstance(o, str) or isinstance(o, unicode):
            return o.lower() in ['true','t','y','yes','1','on']
        elif isinstance(o, int):
            return (o > 0)
        elif isinstance(o, list):
            return (len(o) > 0)
        else:
            return bool(o)

        
        