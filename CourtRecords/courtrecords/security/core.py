from courtrecords.models import Users,GuestUser,Config
from courtrecords.security.acl import ACL
from courtrecords.utilities.validators import Validators
from pyramid.decorator import reify
from pyramid.request import Request
from pyramid.security import Allow, Authenticated, ALL_PERMISSIONS, Everyone, unauthenticated_userid, has_permission


def groupfinder(userid, request):
    user = Users.load(id=userid)
    if user:
        return [user.group]
    return []

    
class RootACL(ACL):
    """ Root ACL for site root, permissions declared for all here """

    __name__ = None
    __parent__ = None
    __acl__ = [
        (Allow, Everyone, ACL.ANONYMOUS),
        (Allow, Authenticated, ACL.AUTHENTICATED),
        (Allow, 'Editor', ACL.AUTHENTICATED),
        (Allow, 'Administrator', ALL_PERMISSIONS),
        # add new permission here
        ]

    def __init__(self, request):
        self.request = request

        
class RequestExtension(Request):

    @reify
    def application_url(self):
        if Validators.bool(Config.get('force_https')):
            return (super(RequestExtension, self).application_url + self.registry.settings.get('apache_path_extension','')).replace('http:', 'https:')
        return super(RequestExtension, self).application_url + self.registry.settings.get('apache_path_extension','')
    
    @property
    def notification(self):
        msg = self.session.pop_flash()
        if msg:
            return msg[0]
        return None

    @property
    def user(self):
        userid = unauthenticated_userid(self)
        if userid is not None:
            return Users.load(id=userid)
        else:
            return GuestUser()
    
    @property
    def can_edit(self):
        return self.has_permissions(['Editor','Administrator'])
        
    @property  
    def can_admin(self):
        return self.has_permissions(['Administrator'])
        
    def has_permissions(self,permissions):
        """ String or List Allowed """ 
        if isinstance(permissions, list):
            for permission in permissions:
                if has_permission(permission, self.context, self):
                    return True
            return False
        else:
            return has_permission(permissions,self.context, self)
        
    def static_url_HTTPS(self, path):
        if Validators.bool(Config.get('force_https')):
            return self.static_url(path).replace('http:', 'https:')
        return self.static_url(path)  
        
        
        