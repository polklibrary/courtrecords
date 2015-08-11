
from courtrecords.models import Users
from courtrecords.security.acl import ACL
from courtrecords.security.decorators import protected
from courtrecords.views import BaseView
from pyramid.view import view_config

class Home(BaseView):

    @view_config(route_name='test_anon', renderer='json', permission=ACL.ANONYMOUS)
    def test_anon(self):
        return 'You have successfully accessed this page'
        
    @view_config(route_name='test_auth', renderer='json', permission=ACL.AUTHENTICATED)
    def test_auth(self):
        return 'You have successfully accessed this page'
        
    @view_config(route_name='test_edit', renderer='json', permission=ACL.EDITOR)
    def test_edit(self):
        self.test_method()
        return 'You have successfully accessed this page'
        
    @view_config(route_name='test_admin', renderer='json', permission=ACL.ADMINISTRATOR)
    def test_admin(self):
        return 'You have successfully accessed this page'
        
        
    @protected([ACL.EDITOR])
    def test_method(self):
        print "RUNNING TEST METHOD"