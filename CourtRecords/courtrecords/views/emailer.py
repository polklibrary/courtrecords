
from courtrecords.security.acl import ACL
from courtrecords.models import DBSession, Users, Entities, Cases, Counties, ActionTypes, Roles, Invoices, Statuses, Config
from courtrecords.views import BaseView
from pyramid.view import view_config
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Attachment,Message
from sqlalchemy import or_,and_,func

from datetime import date

class Emailer(object):

    @classmethod
    def send(cls, request, to, subject, body, signature='', link=''):
        try:
            sys_email = Config.get('system_email')
            body = body + '\n\n' + link + '\n\n' + signature
            message = Message(subject=subject,
                              sender=sys_email,
                              recipients=to,
                              body=body)
            mailer = get_mailer(request)
            mailer.send(message)
            
            return True
        except Exception as e:
            print "ERROR" + str(e)
            return False
