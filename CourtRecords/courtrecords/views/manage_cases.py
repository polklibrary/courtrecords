
from courtrecords.security.acl import ACL
from courtrecords.models import DBSession, Users, Cases, Entities, ActionTypes, Counties, Roles, Containers, Courts, CallNumbers, Archives, Communities
from courtrecords.utilities.utility import has_interface
from courtrecords.views import BaseView
from pyramid.view import view_config
import transaction

class ManageCases(BaseView):

    @view_config(route_name='manage_cases', renderer='../themes/templates/admin/cases.pt', permission=ACL.EDITOR)
    def manage_cases(self):
        return self.response
        
        
    @view_config(route_name='manage_cases_get', renderer='json', permission=ACL.EDITOR)
    def manage_cases_get(self):
        
        order_headings = ['cases.id',
                          'cases.actiontype',
                          'cases.case_number',
                          'cases.year',
                          'cases.container_number',
                          'cases.subset',
                          'cases.county',
                          'cases.community',
                          'cases.address',
                          'cases.notes']
        
        # Determine Order
        order_index = int(self.request.params.get('order[0][column]', 0))
        order = order_headings[order_index] + ' ' + self.request.params.get('order[0][dir]', 'asc')
        limit = int(self.request.params.get('length', 15))
        offset = int(self.request.params.get('start',0))
        
        
        query = DBSession.query(Cases,Counties,Communities,ActionTypes,Archives,Courts,CallNumbers,Containers) \
                                                           .filter(Cases.actiontype == ActionTypes.id) \
                                                           .filter(Cases.county == Counties.id) \
                                                           .filter(Cases.community == Communities.id) \
                                                           .filter(Cases.archive == Archives.id) \
                                                           .filter(Cases.court == Courts.id) \
                                                           .filter(Cases.call_number == CallNumbers.id) \
                                                           .filter(Cases.container == Containers.id)
        count = query.count() # get total number of records
        objs = query.order_by(order).offset(offset).limit(limit).all()

        
        results = {"recordsTotal": count,
                   "recordsFiltered": count,
                   "data": []
        }
        for obj in objs:
            results['data'].append([
                obj.Cases.id,
                obj.ActionTypes.actiontype,
                obj.Cases.case_number,
                obj.Cases.year,
                obj.Containers.container,
                obj.Cases.container_number,
                obj.Cases.subset,
                obj.Counties.county,
                obj.Communities.community,
                obj.Courts.court,
                obj.CallNumbers.call_number,
                obj.Archives.name,
                obj.Cases.address,
                obj.Cases.notes
            ])
        
        return results
        
        