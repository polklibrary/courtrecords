
from courtrecords.security.acl import ACL
from courtrecords.models import DBSession, Users, Cases, Entities, ActionTypes, Counties, Roles, Suffixs, Prefixs, Archives, Courts, Containers, CallNumbers, Config
from courtrecords.utilities.utility import has_interface
from courtrecords.views import BaseView
from courtrecords.views.manage_data import ManageData,Import
from pyramid.httpexceptions import HTTPFound
from pyramid.url import route_url
from pyramid.view import view_config
import transaction, re, datetime

class ManageUtilities(ManageData):

    @view_config(route_name='manage_utilities', renderer='../themes/templates/admin/utilities.pt', permission=ACL.EDITOR)
    def manage_utilities(self):

        if self.request.params.get('edit.Form.reindex.year',''):
            cases = DBSession.query(Cases).all()
            for case in cases:
                print str(case.id)
                year = str(case.year_text)
                if not year:
                    year = str(case.year) # treat as string like input
                year_only, full_date = self._determine_year(year)
                case.year = int(year_only)
                case.year_text = str(full_date)
                
            DBSession.flush()
            transaction.commit()
            
        if self.request.params.get('edit.Form.reindex.fulltext',''):
            self._fulltext_reindex()
    
    
        return self.response
        
    def _determine_year(self,year):
        if len(year) == 4:
            return int(year), str(year)
        elif year == '0':
            return int(year), ''
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
            
    """ STOP:  IF change is made, make sure it is changed in manage_records.py """
    def _fulltext_reindex(self):
        print "REINDEXING ALL FULL TEXT ---------"
            
        fields_to_index = Config.load(name='fulltext_fields_to_index')
        indexes = fields_to_index.value.split(',')
        
        cases = DBSession.query(Cases).all()
        counter = 0
        for case in cases:
            counter+=1
            entities = DBSession.query(Entities).filter_by(case_id=case.id).all() #Entities.loadAll(case_id=case.id)
            
            fulltext = ""
            for index in indexes:
                try:
                    if 'case.' in index:
                        field = index.split('.').pop()
                        fulltext += getattr(case, field) + ' '
                    elif 'entity.' in index:
                        field = index.split('.').pop()
                        for e in entities:
                            fulltext += getattr(e, field) + ' '
                        
                except Exception as e:
                    print str(e)
                    pass #ignore
            
            fulltext = fulltext.replace('\n',' ').replace('\r',' ') # drop new lines
            fulltext = re.sub('[^A-Za-z0-9\s]+', '', fulltext) # clean up special characters
            fulltext = re.sub('\s+', ' ', fulltext).strip() # enforce single white space
            case.full_text = fulltext.lower()

            if counter % 5000 == 0:
                print str(counter) + " records indexed"
                DBSession.flush()
                
        DBSession.flush()
        transaction.commit()
