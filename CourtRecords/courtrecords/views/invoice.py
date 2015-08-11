
from courtrecords.security.acl import ACL
from courtrecords.models import DBSession,Invoices,Config
from courtrecords.utilities.utility import Result2Dict
from courtrecords.utilities.validators import Validators
from courtrecords.views import BaseView
from pyramid.httpexceptions import HTTPFound
from pyramid.url import route_url
from pyramid.view import view_config
from sqlalchemy import or_,and_,func

import time
import urllib2, json

class Invoice(BaseView):

    @view_config(route_name='invoice', renderer='../themes/templates/invoice.pt', permission=ACL.ANONYMOUS)
    def invoice(self):
        hash = self.request.matchdict['hash']
        
        invoice = Invoices.load(hash=hash)
        records = invoice.get_records_raw()
        
        self.set('invoice', invoice)
        self.set('records', records)
        
        return self.response

        