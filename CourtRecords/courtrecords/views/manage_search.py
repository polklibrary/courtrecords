
from courtrecords.security.acl import ACL
from courtrecords.models import DBSession, Users, Entities, Cases, Counties, ActionTypes
from courtrecords.utilities.utility import Result2Dict,Results2Dict
from courtrecords.utilities.validators import Validators
from courtrecords.views import BaseView
from courtrecords.views.emailer import Emailer
from pyramid.view import view_config
from sqlalchemy import or_,and_,func

import time, datetime, re, HTMLParser, shlex

class ManageSearch(BaseView):

    @view_config(route_name='manage_search', renderer='../themes/templates/admin/search.pt', permission=ACL.EDITOR)
    def manage_search(self):
        
        
        return self.response

    @view_config(route_name='manage_search_quick', renderer='json', permission=ACL.EDITOR)
    def manage_search_quick(self):
        
        keywords = self.request.params.get('keywords','')
        everything = self.request.params.get('everything','')
        #firstname = self.request.params.get('firstname','')
        #entity = self.request.params.get('entity','')
        
        query = DBSession.query(Cases,Entities,Counties,ActionTypes) \
                                  .filter(Cases.county==Counties.id) \
                                  .filter(Cases.actiontype==ActionTypes.id) \
                                  .filter(Entities.case_id==Cases.id)
                                  
                                  
        if everything:
            words = shlex.split(everything.lower())
            against = ''
            for word in words:
                if ' ' in word:
                    against += '"' + word + '" ' 
                elif '+' not in word and '-' not in word:
                    against += '+' + word + ' ' 
                else:
                    against += word + ' ' 
            query = query.filter(" MATCH(cases.full_text) AGAINST('" + against + "' IN BOOLEAN MODE) ")
            
        # if everything:
            # print "EVERYTHING FILTER"
            # words = shlex.split(everything.lower())
            # for word in words:
                # query = query.filter(Cases.full_text.like(word+'%'))
        if keywords:
            words = keywords.replace(',',' ').split(' ')
            for word in words:
                query = query.filter(or_(Cases.notes.like('%' + word.strip() + '%'), Entities.alternatename.like('%' + word.strip() + '%'))) # will be slow
        
        # if entity:
            # query = query.filter(Entities.entity.like('%'+entity+'%')) #only do % right side, otherwise will ignore sql indexing
        # if firstname:
            # query = query.filter(Entities.firstname.like(firstname+'%'))  #only do % right side, otherwise will ignore sql indexing
        query = query.order_by('entity asc')
        
        results = query.all()
        entities = []
        for result in results:
            entities.append({'entity': Result2Dict(result.Entities),
                             'case': Result2Dict(result.Cases),
                             'actiontype': Result2Dict(result.ActionTypes),
                             'county': Result2Dict(result.Counties) })
        
        return entities
