
from courtrecords.security.acl import ACL
from courtrecords.models import DBSession, Users, Cases, Entities, ActionTypes, Counties, Roles, Prefixs, Suffixs
from courtrecords.utilities.utility import has_interface
from courtrecords.views import BaseView
from pyramid.view import view_config
import transaction

class ManageEntities(BaseView):

    @view_config(route_name='manage_entities', renderer='../themes/templates/admin/entities.pt', permission=ACL.EDITOR)
    def manage_entities(self):
        return self.response
        
        
    @view_config(route_name='manage_entities_get', renderer='json', permission=ACL.EDITOR)
    def manage_entities_get(self):
        
        order_headings = ['entities.id',
                          'entities.case_id',
                          'entities.entity',
                          'entities.prefix',
                          'entities.lastname',
                          'entities.middlename',
                          'entities.firstname',
                          'entities.suffix',
                          'entities.alternatename',
                          'entities.role'
                          ]
        
        # Determine Order
        order_index = int(self.request.params.get('order[0][column]', 0))
        order = order_headings[order_index] + ' ' + self.request.params.get('order[0][dir]', 'asc')
        limit = int(self.request.params.get('length', 15))
        offset = int(self.request.params.get('start',0))
        
        
        query = DBSession.query(Entities,Roles,Prefixs,Suffixs).filter(Entities.role == Roles.id) \
                                                               .filter(Entities.suffix == Suffixs.id) \
                                                               .filter(Entities.prefix == Prefixs.id)
        count = query.count() # get total number of records
        objs = query.order_by(order).offset(offset).limit(limit).all()

        
        results = {"recordsTotal": count,
                   "recordsFiltered": count,
                   "data": []
        }
        for obj in objs:
            results['data'].append([
                obj.Entities.id,
                obj.Entities.case_id,
                obj.Entities.entity,
                obj.Prefixs.prefix,
                obj.Entities.lastname,
                obj.Entities.middlename,
                obj.Entities.firstname,
                obj.Suffixs.suffix,
                obj.Entities.alternatename,
                obj.Roles.role,
                '<a class="button red warning" href="' + self.request.application_url + '/manage/data/Entities/delete/' + str(obj.Entities.id) + '?back=' + self.request.application_url + '/manage/entities">Delete</a>'
            ])
        
        return results
        
        