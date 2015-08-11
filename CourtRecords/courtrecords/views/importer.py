
from courtrecords.security.acl import ACL
from courtrecords.models import DBSession,Users,Cases,Entities,ActionTypes,Counties,Roles,Suffixs,Prefixs,CallNumbers,Courts,Containers,Archives
from courtrecords.utilities.utility import Results2Dict,FindInList
from courtrecords.views import BaseView
from pyramid.view import view_config
from sqlalchemy import or_,and_,func

import datetime,time,csv,json,re

class ManageImporter(BaseView):

    roles = None
    counties = None
    actiontypes = None
    suffixs = None
    prefixs = None

    @view_config(route_name='manage_importer', renderer='../themes/templates/admin/importer.pt', permission=ACL.ADMINISTRATOR)
    def manage_importer(self):
            
        # Do one look up for speed
        self.roles = Results2Dict(Roles.loadAll())
        self.counties = Results2Dict(Counties.loadAll())
        self.courts = Results2Dict(Courts.loadAll())
        self.callnumbers = Results2Dict(CallNumbers.loadAll())
        self.containers = Results2Dict(Containers.loadAll(order='container asc'))
        self.actiontypes = Results2Dict(ActionTypes.loadAll())
        self.suffixs = Results2Dict(Suffixs.loadAll())
        self.prefixs = Results2Dict(Prefixs.loadAll())
            
        if 'submit' in self.request.params:
            #case_override = json.loads(self.request.params.get('case.override','{}'))
            #entity_override = json.loads(self.request.params.get('entity.override','{}'))
            
            entities = self.request.POST['entities'].file
            entities_fields = self.request.params.get('entity.fields').split(',')
            cases = self.request.POST['cases'].file
            case_fields = self.request.params.get('case.fields').split(',')
            
            archive_id = self.request.params.get('archive',0)
            
            print "CREATING CASES --------------"
            cases_id_map = self.createCases_returnMap(cases,case_fields,archive_id)
            
            print "CREATING ENTITIES ----------------"
            fix = (self.request.params.get('firstname.fix','0') == '1')
            self.createEntitiesCleanup(entities,entities_fields,cases_id_map,fix)
            #else:
            #    self.createEntities(entities,entities_fields,cases_id_map)
            
            
        self.set('archives', Archives.loadAll(order='name asc'))
        self.set('containers', self.containers)
        self.set('callnumbers', self.callnumbers)
        return self.response

    
    def createCases_returnMap(self, file, fields, archive_id):
        data = {}
        reader = csv.reader(file, skipinitialspace=True, delimiter=b',', quoting=csv.QUOTE_MINIMAL, quotechar=b'"')
        for line in reader:
            row = {}
            case_id = 0
            for f,d in zip(fields, line):
                c = d.strip()
                if str(f) == 'case_id':
                    case_id = int(c)
                elif str(f) == 'year':
                    row['year'], row['year_text'] = self._determine_year(c)
                elif str(f) == 'actiontype':
                    row['actiontype'] = FindInList(self.actiontypes,'actiontype',c, default={'id':35,'actiontype':''})['id']
                elif str(f) == 'county':
                    row['county'] = FindInList(self.counties,'county',c, default={'id':1,'county':''})['id']
                elif str(f) == 'court':
                    row['court'] = FindInList(self.courts,'court',c, default={'id':1,'court':''})['id']
                elif str(f) == 'call_number':
                    row['call_number'] = FindInList(self.callnumbers,'call_number',c, default={'id':8,'call_number':''})['id']
                elif str(f) == 'container':
                    row['container'] = FindInList(self.containers,'container',c, default={'id':1,'container':''})['id']
                else:
                    row[f] = c.replace('\n','').replace('\r','').replace('"','')

            row['archive'] = archive_id
            row['import_file'] = self.request.params.get('import.marker','not provided')
            
            # ENFORCE CONTAINER TYPE
            container_enforcer = int(self.request.params.get('container.enforcer',0))
            if container_enforcer != 0:
                row['container'] = int(container_enforcer)
            
            # ENFORCE CALLNUMBER
            callnumber_enforcer = int(self.request.params.get('callnumber.enforcer',0))
            if callnumber_enforcer != 0:
                row['call_number'] = int(callnumber_enforcer)
                
            cases = Cases(**row)
            lastid = cases.insert(self.request)
            print "Uploaded Case ID: " + str(lastid)
            data[case_id] = lastid
            
        return data
            
            
            
    def createEntitiesCleanup(self,file, fields, cases_map, fix):
        
        reader = csv.reader(file, skipinitialspace=True, delimiter=b',', quoting=csv.QUOTE_MINIMAL, quotechar=b'"')
        for line in reader:
            row = {}
            for f,d in zip(fields, line):
                c = d.strip()
                if f == 'case_id':
                    if c == '':
                        row[f] = 0
                    else:
                        row[f] = cases_map[int(c)]
                elif str(f) == 'role':
                    row['role'] = FindInList(self.roles,'role',c,default={'id':1,'role':''})['id']
                elif str(f) == 'prefix':
                    row['prefix'] = FindInList(self.prefixs,'prefix',c,default={'id':1,'prefix':''})['id']
                elif str(f) == 'suffix':
                    row['suffix'] = FindInList(self.suffixs,'suffix',c,default={'id':1,'suffix':''})['id']
                else:
                    row[f] = c.replace('\n','').replace('\r','').replace('"','').strip()
            
            row['import_file'] = self.request.params.get('import.marker','not provided')
            
            if fix:
                self._fix_firstname_issues_and_insert(row)
            else:
                entities = Entities(**row)
                lastid = entities.insert(self.request)
                print "Uploaded Entity ID: " + str(lastid)
            
            
            
            
    def _fix_firstname_issues_and_insert(self, row):
        firstname = row['firstname'].replace(' and ', '|')
        firstname = firstname.replace(' & ', '|')
        firstname = firstname.replace(', ', '|')
        
        entities = firstname.split('|')
        for e in entities:
            p,f,m,s = self._fix_firstnames(e)
            row['firstname'] = f
            row['middlename'] = m
            row['prefix'] = FindInList(self.prefixs,'prefix',p,default={'id':1,'prefix':''})['id']
            row['suffix'] = FindInList(self.suffixs,'suffix',s,default={'id':1,'suffix':''})['id']
            
            entities = Entities(**row)
            lastid = entities.insert(self.request)
            print "Uploaded 'CLEANED' Entity ID: " + str(lastid)

            
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
            
            
    def _fix_firstnames(self,firstname):
        found_suffix = ''
        found_prefix = ''
        found_middlename = ''
        
        #remove prefixes
        prefixs = [ str(p.prefix) for p in Prefixs.loadAll() if p.prefix != '']
        for p in prefixs:
            if p in firstname:
                found_prefix = p
                firstname = firstname.replace(p,'')
        
        #remove suffixes
        suffixs = [ str(s.suffix) for s in Suffixs.loadAll() if s.suffix != '']
        for s in suffixs:
            if s in firstname:
                found_suffix = s
                firstname = firstname.replace(s,'')
        
        # Get middle and first name and clean them up
        firstname = re.sub( '\s+', ' ', firstname).strip()
        name = firstname.strip().split(' ')
        if len(name) == 2:
            found_middlename = name[1].strip() #clean white spaces
        if len(name) == 1 or len(name) == 2:
            firstname = name[0].strip() #clean white spaces 
        
        return (found_prefix,firstname,found_middlename,found_suffix)
        
        
        
        
        
        
        
        
        
        
