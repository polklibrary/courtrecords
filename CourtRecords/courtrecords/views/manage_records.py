
from courtrecords.security.acl import ACL
from courtrecords.models import DBSession, Users, Cases, Entities, ActionTypes, Counties, Roles, Suffixs, Prefixs, Archives, Courts, Containers, CallNumbers
from courtrecords.utilities.utility import has_interface
from courtrecords.views import BaseView
from courtrecords.views.manage_data import ManageData,Import
from pyramid.httpexceptions import HTTPFound
from pyramid.url import route_url
from pyramid.view import view_config
import transaction, re, datetime

class ManageRecords(ManageData):


    @view_config(route_name='manage_records_previous', permission=ACL.EDITOR)
    def manage_records_previous(self):
        case_id = int(self.request.params.get('case',''))
        call_number = int(self.request.params.get('call_number',''))
        
        cases = DBSession.query(Cases).filter(Cases.call_number == call_number).order_by('id asc').all()
        previous = 0
        for i, case in enumerate(cases):
            if case.id == case_id:
                previous = i-1
                break
        if previous == -1:
            previous = len(cases)-1
        return HTTPFound(location=route_url('manage_records', self.request, case_id=cases[previous].id))

    @view_config(route_name='manage_records_next', permission=ACL.EDITOR)
    def manage_records_next(self):
        case_id = int(self.request.params.get('case',''))
        call_number = int(self.request.params.get('call_number',''))
        
        cases = DBSession.query(Cases).filter(Cases.call_number == call_number).order_by('id asc').all()
        next = 0
        for i, case in enumerate(cases):
            if case.id == case_id:
                next = i+1
                break
        if next == len(cases):
            next = 0
                                                
        return HTTPFound(location=route_url('manage_records', self.request, case_id=cases[next].id))

    @view_config(route_name='manage_records', renderer='../themes/templates/admin/records.pt', permission=ACL.EDITOR)
    def manage_records(self):
        case_id = self.request.matchdict['case_id']
        if case_id != 'new':
            case_id = int(case_id)
        
        # Handle Saving
        if 'edit.Form.submit.save' in self.request.params or 'edit.Form.submit.savenext' in self.request.params:
            self._save(case_id)
            if 'edit.Form.submit.savenext' in self.request.params:
                return HTTPFound(location=route_url('manage_records', self.request, case_id='new'))
            return HTTPFound(location=route_url('manage_records', self.request, case_id=case_id))
        
        # Handle Loading Information on screen
        if case_id == 'new' or case_id == 0:
            case = None
        else:
            case = DBSession.query(Cases,Counties,ActionTypes,Archives).filter(Cases.id == case_id) \
                                                                      .filter(Cases.actiontype == ActionTypes.id) \
                                                                      .filter(Cases.county == Counties.id) \
                                                                      .filter(Cases.archive == Archives.id) \
                                                                      .first()

        entities = []
        if case_id != 'new':
            entities = DBSession.query(Entities,Roles).filter(Entities.case_id == case_id) \
                                                        .filter(Entities.role == Roles.id) \
                                                        .order_by('entity asc').all()
        
        self.set('case',case)
        self.set('year',self._get_year)
        self.set('case_id',case_id)
        self.set('entities',entities)
        self.set('actiontypes',ActionTypes.loadAll(order="actiontype asc"))
        self.set('containers',Containers.loadAll(order="container asc"))
        self.set('courts',Courts.loadAll(order="court asc"))
        self.set('call_numbers',CallNumbers.loadAll(order="call_number asc"))
        self.set('archives',Archives.loadAll(order="name asc"))
        self.set('roles',Roles.loadAll(order="role asc"))
        self.set('counties',Counties.loadAll(order="county asc"))
        self.set('prefixs',Prefixs.loadAll(order="prefix asc"))
        self.set('suffixs',Suffixs.loadAll(order="suffix asc"))
        return self.response
        
    
    def _save(self, case_id):
        entities, new_entities = {}, {}
        cases, new_cases = {}, {}
        
        for k,v in self.request.params.items():
            action, table, attr, id = k.split('.')
            if action == 'edit':
                if table == 'Entities':
                    if id not in entities:
                        entities[id] = { attr : v }
                    else:
                        entities[id][attr] = v
                        
                if table == 'Cases':
                    if id not in cases:
                        cases[id] = { attr : v }
                    else:
                        cases[id][attr] = v
                        
            if action == 'new':
                if table == 'Entities':
                    if id not in new_entities:
                        new_entities[id] = { attr : v }
                    else:
                        new_entities[id][attr] = v
                        
                if table == 'Cases':
                    if id not in new_cases:
                        new_cases[id] = { attr : v }
                    else:
                        new_cases[id][attr] = v
                        
                        
            #new_cases[id]['year'] = self._determine_year
                        
        # save new cases
        for k,v in new_cases.items():
            case = Cases()
            for attr,value in v.items():
                setattr(case,attr,value)
            case.year = self._determine_year(case.year_text)[0]
            case_id = case.insert(self.request)
        
        # save new entities
        for k,v in new_entities.items():
            entity = Entities()
            for attr,value in v.items():
                setattr(entity,attr,value)
            entity.case_id = case_id
            entity.insert(self.request)
                        
        # save existing cases
        for k,v in cases.items():
            case = Cases.load(id=k)
            for attr,value in v.items():
                setattr(case,attr,value)
            case.year = self._determine_year(case.year_text)[0]
            case.save(self.request)
        
        # save existing entities
        for k,v in entities.items():
            entity = Entities.load(id=k)
            for attr,value in v.items():
                setattr(entity,attr,value)
            entity.save(self.request)
            
    def _get_year(self, case):
        if not case.year_text:
            return case.year
        return case.year_text
            
            
    def _determine_year(self,year):
        if len(year) == 4:
            return int(year), str(year)
        elif year.count('-') == 1 or year.count(',') == 1: 
            syear, eyear = re.split(r'[-,]*', year)
            return syear.strip(), str(year)
        else:
            class FakeDate(object):
                pass
            dt = FakeDate()
            setattr(dt, 'year', year)
            try:
                dt = datetime.datetime.strptime(year, '%m/%d/%Y')
            except:
                pass #ignore
            try:
                dt = datetime.datetime.strptime(year, '%Y/%m/%d')
            except:
                pass #ignore
            try:
                dt = datetime.datetime.strptime(year, '%m-%d-%Y')
            except:
                pass #ignore
            try:
                dt = datetime.datetime.strptime(year, '%Y-%m-%d')
            except:
                pass #ignore
            return dt.year, str(year)