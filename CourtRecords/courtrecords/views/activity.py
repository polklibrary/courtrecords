
from courtrecords.security.acl import ACL
from courtrecords.models import DBSession, Users, Entities, Cases, Counties, ActionTypes, Roles, Invoices, Statuses, Config
from courtrecords.views import BaseView
from pyramid.view import view_config
from sqlalchemy import or_,and_,func

import transaction, time

class Activity(BaseView):

    @view_config(route_name='activity', renderer='json', permission=ACL.ANONYMOUS)
    def activity(self):
    
        type = self.request.params.get('type','')
        
        if type == 'check':
            if self.request.user.id != 0:
                ts = self.request.user.session_timestamp
                now = (int(time.time())) - int(Config.get('session_timeout'))
                if ts < now: 
                    return {
                        'type':'check',
                        'guest':0, 
                        'logout':1,
                    }
                else:
                    return {
                        'type':'check',
                        'guest':0, 
                        'logout':0,
                    }
            
            return {
                'type':'check',
                'guest':1, 
                'logout':0,
            }
            
        if type == 'refresh':
            if self.request.user.id != 0:
                self.request.user.update_session_timestamp()
                return {
                    'type':'refresh',
                    'guest':0, 
                    'refresh':1,
                }
            else:
                return {
                    'type':'refresh',
                    'guest':1, 
                    'refresh':0,
                }
                
        return {
            'type':'nothing',
        }
