
from courtrecords.security.acl import ACL
from courtrecords.models import DBSession,Users, Invoices
from courtrecords.utilities.utility import has_interface
from courtrecords.views import BaseView
from courtrecords.views.manage_data import ManageData,Import
from pyramid.view import view_config
import transaction

class ManageDataList(ManageData):

    @view_config(route_name='manage_list_data', renderer='../themes/templates/admin/data-list.pt', permission=ACL.EDITOR)
    def manage_list_data(self):
        table = str(self.request.matchdict['table'])
        table_class = Import('courtrecords.models', table)
        has_interface(table_class,'__scaffold__')
        
        # Generate table header
        thead = []
        for s in table_class.__scaffold__:
            for k,v in s.items():
                thead.append(v['label'])
                
        
        self.set('allow_adding', getattr(table_class, '__allow_adding__', True))
        self.set('friendly_table', getattr(table_class, '__tablelabel__', table))
        self.set('friendly_table_singular', getattr(table_class, '__tablelabel__', table)[:-1])
        self.set('thead', thead)
        self.set('table', table)
        self.set('table_singular', table[:-1])
        return self.response
        
        
    @view_config(route_name='manage_getlist_data', renderer='json', permission=ACL.EDITOR)
    def manage_getlist_data(self):
        
        table = str(self.request.matchdict['table'])
        table_class = Import('courtrecords.models', table)
            
        # Generate table header
        header_unique = []
        for s in table_class.__scaffold__:
            for k,v in s.items():
                header_unique.append(k)
        
        # Determine Order
        order_index = int(self.request.params.get('order[0][column]', 0))
        order = header_unique[order_index] + ' ' + self.request.params.get('order[0][dir]', 'asc')
        limit = int(self.request.params.get('length', 15))
        offset = int(self.request.params.get('start',0))
        
        
        query = DBSession.query(table_class)
        count = query.count() # get total number of records
        objs = query.order_by(order).offset(offset).limit(limit).all()

        
        results = {"recordsTotal": count,
                   "recordsFiltered": count,
                   "data": []
        }
        for obj in objs:
            tmp = []
            for h in header_unique:
                tmp.append(getattr(obj, h))
            tmp.append('') # empty for "option" column
            results['data'].append(tmp)
        
        return results
        
        