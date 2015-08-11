
from courtrecords.security.acl import ACL
from courtrecords.models import DBSession, Users, Entities, Cases, Counties, ActionTypes, Roles, Invoices, Statuses
from courtrecords.views import BaseView
from pyramid.view import view_config
from sqlalchemy import or_,and_,func

import transaction

class CronJobs(BaseView):

    @view_config(route_name='cronjob_anonymize', renderer='json', permission=ACL.ANONYMOUS)
    def cronjob_anonymize(self):
        try:
            last_status = Statuses.load(order='priority desc')
            invoices = Invoices.loadAll(status=last_status.id)
            for invoice in invoices:
                invoice.completed = True
                DBSession.flush()
            transaction.commit()
            return {'status':'200'}
        except Exception as e:
            print str(e)
            return {'status':'500'}
            
        
