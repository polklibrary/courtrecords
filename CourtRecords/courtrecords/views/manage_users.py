
from courtrecords.security.acl import ACL
from courtrecords.models import DBSession, Users, Entities, Cases, Counties, ActionTypes, Roles, Invoices, Statuses, Config
from courtrecords.utilities.validators import Validators
from courtrecords.views import BaseView
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.url import route_url
from sqlalchemy import or_,and_,func

from datetime import date

class ManageUsers(BaseView):

    @view_config(route_name='manage_users', renderer='../themes/templates/admin/users.pt', permission=ACL.EDITOR)
    def manage_users(self):
        self.set('users', Users.loadAll(order='id asc'))
        return self.response
        
    def get_auth_type(self, id):
        if id == Users.AUTH_LDAP:
            return "LDAP"
        return "Local"
        
class ManageUsersAdd(BaseView):

    @view_config(route_name='manage_users_add', renderer='../themes/templates/admin/users_add.pt', permission=ACL.ADMINISTRATOR)
    def manage_users_add(self):
        self.set('err_message', '')
        
        if 'user.submit' in self.request.params:
            email = Validators.sanatize(self.request.params.get('user.email',''))
            group = self.request.params.get('user.group','')
            password = Validators.sanatize(self.request.params.get('user.password',''))
            auth_type = int(self.request.params.get('user.auth_type',Users.AUTH_LOCAL))
            
            if not Validators.email(email):
                self.set('err_message', 'Invalid email')
            
            if not Validators.is_acl(group):
                self.set('err_message', 'Invalid ACL Group')
            
            if not Validators.password(password, Config):
                self.set('err_message', 'Invalid Password')
                
            user = Users(email=email, password=password, group=group, auth_type=auth_type)
            user.insert(self.request)
            
            return HTTPFound(location=route_url('manage_users', self.request))
        
        return self.response
        
        
class ManageUser(BaseView):

    @view_config(route_name='manage_user', renderer='../themes/templates/admin/user.pt', permission=ACL.EDITOR)
    def manage_user(self):
        id = self.request.matchdict['id']
        self.set('err_message', '')
        
        if 'user.submit' in self.request.params:
            user = Users.load(id=id)
            email = Validators.sanatize(self.request.params.get('user.email',''))
            group = self.request.params.get('user.group','')
            password = Validators.sanatize(self.request.params.get('user.password',''))
            auth_type = int(self.request.params.get('user.auth_type',Users.AUTH_LOCAL))
            
            user.auth_type = auth_type
            
            if not Validators.email(email):
                self.set('err_message', 'Invalid email')
            else:
                user.email = email
            
            if not Validators.is_acl(group):
                self.set('err_message', 'Invalid ACL Group')
            else:
                user.group = group
            
            if auth_type == Users.AUTH_LOCAL:
                if password == '':
                    pass
                elif not Validators.password(password, Config):
                    self.set('err_message', 'Invalid Password')
                elif user.check_old_passwords(password):
                    self.set('err_message', 'Already used password')
                else:
                    user.set_password(password)
                    user.update_password_timestamp()
                    
            user.save(self.request)
            
        if 'user.unlock' in self.request.params:
            user = Users.load(id=id)
            user.password_failures = 0
            user.save(self.request)
            
        if 'user.delete' in self.request.params:
            user = Users.load(id=id)
            user.remove_admin_only(self.request)
            response = HTTPFound(location=route_url('manage_users', self.request))
            return response
            
        user = Users.load(id=id)
        self.set('user',user)
        self.set('is_locked', "No")
        if user.password_failures >= int(Config.get('max_login_failures')):
            self.set('is_locked', "Yes")
        return self.response
