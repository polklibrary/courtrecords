
from courtrecords.security.acl import ACL
from courtrecords.models import Users, Config
from courtrecords.views import BaseView
from pyramid.view import view_config

class Home(BaseView):

    @view_config(route_name='home', renderer='../themes/templates/home.pt', permission=ACL.ANONYMOUS)
    def home(self):
        return self.response
       
       
class About(BaseView):

    @view_config(route_name='about', renderer='../themes/templates/about.pt', permission=ACL.ANONYMOUS)
    def about(self):
        return self.response
        
        
class Contact(BaseView):

    @view_config(route_name='contact', renderer='../themes/templates/contact.pt', permission=ACL.ANONYMOUS)
    def contact(self):
        return self.response
        
        
