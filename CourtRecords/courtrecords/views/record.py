
from courtrecords.security.acl import ACL
from courtrecords.models import DBSession,Cases,Entities,Invoices,Roles,Counties,ActionTypes,Archives,Statuses,Courts,Prefixs,Suffixs,Containers,CallNumbers
from courtrecords.utilities.utility import Result2Dict,Results2Dict
from courtrecords.utilities.validators import Validators
from courtrecords.views import BaseView
from courtrecords.views.emailer import Emailer
from pyramid.httpexceptions import HTTPFound
from pyramid.url import route_url
from pyramid.view import view_config
from sqlalchemy import or_,and_,func

import time
import urllib2, json

class Record(BaseView):

    @view_config(route_name='record', renderer='../themes/templates/record.pt', permission=ACL.ANONYMOUS)
    def record(self):
        id = int(self.request.matchdict['id'])
        self.set('mode', self.request.params.get('mode',False))
        
        case = DBSession.query(Cases,Counties,Courts,ActionTypes,Archives,Containers,CallNumbers).filter(Cases.id==id) \
                                                                           .filter(Cases.county==Counties.id) \
                                                                           .filter(Cases.court==Courts.id) \
                                                                           .filter(Cases.actiontype==ActionTypes.id) \
                                                                           .filter(Cases.container==Containers.id) \
                                                                           .filter(Cases.call_number==CallNumbers.id) \
                                                                           .filter(Cases.archive==Archives.id).first()

        entities = DBSession.query(Entities,Roles,Suffixs,Prefixs).filter(Entities.case_id==case.Cases.id) \
                                                                  .filter(Entities.role==Roles.id) \
                                                                  .filter(Entities.suffix==Suffixs.id) \
                                                                  .filter(Entities.prefix==Prefixs.id).order_by('entity asc').all()

        record = {
            'case': case,
            'verses' : self.determine_verses(entities, case.ActionTypes.actiontype),
            'entities': entities,
            'price': '${:,.2f}'.format( float(entities[0].Roles.price) ),
        }
        self.set('record', record)

        
        return self.response
    
    
    
    
    def determine_verses(self, entities, actiontype):
        verses = ''
        
        if 'probate' in actiontype.lower():
            for entity in entities:
                name = entity.Entities.entity
                if not name:
                    name = "Unknown"
                verses = name + ' - ' + actiontype
        elif 'naturalization' in actiontype.lower():
            for entity in entities:
                name = entity.Entities.entity
                if not name:
                    name = "Unknown"
                verses = name + ' - ' + actiontype
        else:
            plaintiffs = filter( lambda x:  x.Roles.id == 1, entities) # plaintiff
            defendants = filter( lambda x:  x.Roles.id == 2, entities) # defendant
            
            ptmp = []
            for p in plaintiffs[:2]:
                pname = p.Entities.entity
                if not pname:
                    pname = "Unknown"
                ptmp.append(pname)
                
            dtmp = []
            for d in defendants[:2]:
                dname = d.Entities.entity
                if not dname:
                    dname = "Unknown"
                dtmp.append(dname)

                
            verses = ' & '.join(ptmp)
                
            if len(plaintiffs) > 2:
                verses += ' et al. '
            
            verses += ' VS. ' + ' & '.join(dtmp)
                
            if len(defendants) > 2:
                verses += ' et al. '

        return verses
        
        