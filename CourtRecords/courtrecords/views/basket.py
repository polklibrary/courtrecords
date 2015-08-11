
from courtrecords.security.acl import ACL
from courtrecords.models import DBSession,Cases,Entities,Invoices,Roles,Counties,ActionTypes,Archives,Statuses,Courts,Prefixs,Suffixs,Config
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

class Basket(BaseView):

    @view_config(route_name='basket', renderer='../themes/templates/basket.pt', permission=ACL.ANONYMOUS)
    def basket(self):
        self.set('records', [])
        
        if 'submit' in self.request.params:
            return self.create_invoice()
        else:   
            items = self.request.cookies.get('basket',False)
            if items:
                items = json.loads(urllib2.unquote(items))
                
                results = []
                price, total_price = 0.0, 0.0
                
                for k,v in items.items():
                
                    entity = DBSession.query(Entities,Roles).filter(Entities.case_id==int(v)).filter(Entities.role==Roles.id).first()
                    price = float(entity.Roles.price)
                    total_price += price
                    
                    results.append({
                        'id': v,
                        'price': '${:,.2f}'.format(price),
                    })

                self.set('records', results)
                self.set('total_price', '${:,.2f}'.format(total_price))
                self.set('message_before_ordering', Config.get('message_before_ordering'))
        
        return self.response

        
        
    def create_invoice(self):
        records = self.request.params.getall('records')
        
        if records:
            fullname = self.request.params.get('customer.name','')
            email = self.request.params.get('customer.email','')
            address = self.request.params.get('customer.address','')
            address2 = self.request.params.get('customer.address2','')
            phone = self.request.params.get('customer.phone','')
            agreement = Validators.bool(self.request.params.get('customer.agreement',0))
            checkout = self.request.params.getall('customer.checkout')
            deliver_digitally = False
            deliver_physically = False
            
            # Delivery Options
            for option in checkout:
                if option == 'digitally':
                    deliver_digitally = True
                if option == 'physically':
                    deliver_physically = True
                    
            # Prep Orders
            orders = []
            total_price = 0.0
            location_emails = {} # to notify any locations a request has been made
            for record in records:
                c = Cases.load(id=int(record))
                e = Entities.load(case_id=int(record))
                r = Roles.load(id=e.role)
                l = Archives.load(id=c.archive)
                
                location_emails[l.email] = l.email
                total_price += float(r.price)
                
                orders.append({'case':int(c.id), 'price' : r.price, 'location':int(l.id)})
                
            invoice = Invoices(fullname=fullname, email=email, address=address, county_state_zip=address2, phone=phone, records=orders, 
                               agreement_accepted=agreement, deliver_digitally=deliver_digitally, deliver_physically=deliver_physically,
                               total_price='${:,.2f}'.format(total_price))
            invoice.insert(self.request)
            invoice = Invoices.load(order='id desc')
            
            #Email Client
            starting_status = Statuses.load(order='priority asc')
            Emailer.send(self.request,
                         [email],
                         starting_status.email_subject,
                         starting_status.email_message,
                         link=self.request.application_url + '/invoice/' + invoice.hash
                         )
                         
            #Email Archives Involved
            Emailer.send(self.request,
                         list(location_emails),
                         'Order request has been placed',
                         'A new order request has been placed',
                         link=self.request.application_url + '/login?goto=' + self.request.application_url + '/manage/orders'
                         )
                         
                         
            response = HTTPFound(location=route_url('invoice', self.request, hash=invoice.hash))
            response.delete_cookie('basket')
            return response
            
        else:
            return self.response
        
