
from courtrecords.security.acl import ACL
from courtrecords.models import DBSession, Users, Entities, Cases, Counties, ActionTypes
from courtrecords.utilities.utility import Result2Dict,Results2Dict
from courtrecords.utilities.validators import Validators
from courtrecords.views import BaseView
from courtrecords.views.emailer import Emailer
from pyramid.view import view_config

class ManageSearch(BaseView):

    @view_config(route_name='manage_search', renderer='../themes/templates/admin/search.pt', permission=ACL.EDITOR)
    def manage_search(self):
        
        
        return self.response

    @view_config(route_name='manage_search_quick', renderer='json', permission=ACL.EDITOR)
    def manage_search_quick(self):
        
        firstname = self.request.params.get('firstname','')
        entity = self.request.params.get('entity','')
        
        query = DBSession.query(Cases,Entities,Counties,ActionTypes) \
                                  .filter(Cases.county==Counties.id) \
                                  .filter(Cases.actiontype==ActionTypes.id) \
                                  .filter(Entities.case_id==Cases.id)
        if entity:
            query = query.filter(Entities.entity.like('%'+entity+'%')) #only do % right side, otherwise will ignore sql indexing
        if firstname:
            query = query.filter(Entities.firstname.like(firstname+'%'))  #only do % right side, otherwise will ignore sql indexing
        query = query.order_by('entity asc')
        
        results = query.all()
        entities = []
        for result in results:
            entities.append({'entity': Result2Dict(result.Entities),
                             'case': Result2Dict(result.Cases),
                             'actiontype': Result2Dict(result.ActionTypes),
                             'county': Result2Dict(result.Counties) })
        
        return entities
