
from courtrecords.security.acl import ACL
from courtrecords.models import DBSession,Users, Invoices
from courtrecords.utilities.utility import has_interface
from courtrecords.views import BaseView
from courtrecords.views.manage_data import ManageData,Import
from pyramid.httpexceptions import HTTPFound
from pyramid.url import route_url
from pyramid.view import view_config
import transaction

class ManageDataDelete(ManageData):

    @view_config(route_name='manage_delete_data', renderer='string', permission=ACL.EDITOR)
    def manage_delete_data(self):
        table = str(self.request.matchdict['table'])
        table_class = Import('courtrecords.models', table)
        back = self.request.params.get('back','')
        id = int(self.request.matchdict['id'])
        #has_interface(table_class,'__scaffold__')
        
        obj = DBSession.query(table_class).filter(getattr(table_class,'id')==id).first()
        DBSession.delete(obj)
        transaction.commit()
        
        if back:
            return HTTPFound(location=back)
        return HTTPFound(location=route_url('manage_list_data', self.request, table=table))

        