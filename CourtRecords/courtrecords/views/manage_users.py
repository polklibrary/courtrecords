
from courtrecords.security.acl import ACL
from courtrecords.models import DBSession, Users, Entities, Cases, Counties, ActionTypes, Roles, Invoices, Statuses
from courtrecords.views import BaseView
from pyramid.view import view_config
from sqlalchemy import or_,and_,func

from datetime import date

class Manage(BaseView):

    @view_config(route_name='manage_users', renderer='../themes/templates/admin/users.pt', permission=ACL.EDITOR)
    def manage_users(self):
    
        self.set('users', Users.loadAll(order='id asc'))

        return self.response
