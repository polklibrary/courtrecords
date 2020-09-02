
from courtrecords.security.acl import ACL
from courtrecords.models import DBSession, Users, Entities, Cases, Counties, ActionTypes, Roles, Invoices, Statuses, Config
from courtrecords.views import BaseView
from pyramid.view import view_config
from sqlalchemy import or_,and_,func
import time, datetime, transaction

class Manage(BaseView):

    @view_config(route_name='manage', renderer='../themes/templates/admin/manage.pt', permission=ACL.EDITOR)
    def manage(self):
        
        self.purge_old_pending_orders()
    
        self.set('counties_count', self.fast_count(DBSession.query(Counties)))
        self.set('actiontypes_count', self.fast_count(DBSession.query(ActionTypes)))
        self.set('roles_count', self.fast_count(DBSession.query(Roles)))
        self.set('cases_count', self.fast_count(DBSession.query(Cases)))
        self.set('entities_count', self.fast_count(DBSession.query(Entities)))
    
        complete_status = Statuses.load(order='priority desc')
        self.set('orders_open', self.fast_count(DBSession.query(Invoices).filter(Invoices.status != complete_status.id)))
        self.set('orders_closed', self.fast_count(DBSession.query(Invoices).filter(Invoices.status == complete_status.id)))
    
        self.set('problems', self.problem_finder())
        
        return self.response
        
        
    def problem_finder(self):
        return {
            'entities_no_case' : DBSession.query(Entities).filter(Entities.case_id == 0).all(),
            'entities_no_prefix' : DBSession.query(Entities).filter(Entities.prefix == 0).all(),
            'entities_no_suffix' : DBSession.query(Entities).filter(Entities.suffix == 0).all(),
            'entities_no_role' : DBSession.query(Entities).filter(Entities.role == 0).all(),
            'case_year_issues' : DBSession.query(Cases).filter(Cases.year != 0).filter(or_( Cases.year < 1800 , Cases.year > datetime.date.today().year)).all(),
            'case_no_county' : DBSession.query(Cases).filter(Cases.county == 0).all(),
            'case_no_actiontype' : DBSession.query(Cases).filter(Cases.actiontype == 0).all(),
            #'case_no_case_number' : DBSession.query(Cases).filter(Cases.case_number == '').all(),
        }
       
        
    def fast_count(self,q):
        """ SQLAlchemy's query .count() is extremly slow, about 3-5 seconds.  This does the same thing under 1 second. """
        count_q = q.statement.with_only_columns([func.count()]).order_by(None)
        count = q.session.execute(count_q).scalar()
        return count 
        
    def purge_old_pending_orders(self):
        pending_status = Statuses.load(order='priority asc')
        secs = int(Config.get('seconds_to_purge_pending_orders', 900))
        now_time = datetime.datetime.now()
        stale_time = now_time - datetime.timedelta(seconds=secs)
        query = DBSession.query(Invoices).filter(Invoices.status == pending_status.id).filter(Invoices.created <= stale_time)
        
        for obj in query.all():
            DBSession.delete(obj)
        transaction.commit()

        
    
    
    
    
    