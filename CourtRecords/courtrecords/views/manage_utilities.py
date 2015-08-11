
from courtrecords.security.acl import ACL
from courtrecords.models import DBSession, Users, Cases, Entities, ActionTypes, Counties, Roles, Suffixs, Prefixs, Archives, Courts, Containers, CallNumbers
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