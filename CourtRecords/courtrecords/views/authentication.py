from courtrecords.models import Users,Config
from courtrecords.security.acl import ACL
from courtrecords.views import BaseView
from courtrecords.utilities.validators import Validators

from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember,forget
from pyramid.url import route_url
from pyramid.view import view_config

class Login(BaseView):

    @view_config(route_name='login', renderer='../themes/templates/login.pt', permission=ACL.ANONYMOUS)
    def login(self):
        self.set('issue','')
        if 'submit' in self.request.params:
            email = self.request.params.get('email',None)
            password = self.request.params.get('pass',None)
            goto = self.request.params.get('goto','')
            if email and password:
                user = Users.load(email=email)
                if user:
                    if user.validate_password(password):
                        if not goto:
                            return HTTPFound(location=route_url('home', self.request), headers=remember(self.request, user.id))
                        else:
                            return HTTPFound(location=goto, headers=remember(self.request, user.id))
                    else:
                        self.set('issue','Incorrect credentials')
                else:
                    self.set('issue','No user found')
            else:
                self.set('issue','No user or password provided')

        return self.response
        

class Logout(BaseView):

    @view_config(route_name='logout', permission=ACL.AUTHENTICATED)
    def logout(self):
        return HTTPFound(route_url('home', self.request), headers=forget(self.request))
       
       
class Registration(BaseView):

    @view_config(route_name='register', renderer='../themes/templates/register.pt', permission=ACL.ANONYMOUS)
    def register(self):
        if Validators.bool(Config.get('enable_registration')):
            self.set('issue',None)
            self.set('allow_registration',True)
            
            if 'submit' in self.request.params:
                email = self.request.params.get('email','')
                password = self.request.params.get('pass','')
                repassword = self.request.params.get('repass','')
                
                if Users.load(email=email):
                    self.set('issue','This email is already in use.')
                    return self.response
                if not Validators.email(email):
                    self.set('issue','Your email is not valid.')
                    return self.response
                if not Validators.password(password):
                    self.set('issue','Your passwor id not valid.')
                    return self.response
                    
                if repassword != password:
                    self.set('issue','Your passwords do not match.')
                    return self.response
                    
                user = Users(email=email,password=password)
                user.add_user()
                return HTTPFound(location=route_url('login', self.request))
        else:
            self.set('issue','Registration is disabled')
            self.set('allow_registration',None)
            
        return self.response