
from courtrecords.security.acl import ACL
from courtrecords.security.cardhash import hash_transaction, generate_url
from courtrecords.models import DBSession,Cases,Entities,Invoices,Roles,CallNumbers,Counties,ActionTypes,Archives,Statuses,Courts,Prefixs,Suffixs,Config,Payments
from courtrecords.utilities.utility import Result2Dict,Results2Dict,GenerateOrderNumber
from courtrecords.utilities.validators import Validators
from courtrecords.views import BaseView
from courtrecords.views.emailer import Emailer
from pyramid.httpexceptions import HTTPFound
from pyramid.url import route_url
from pyramid.view import view_config
from sqlalchemy import or_,and_,func

import time
import urllib2, json, base64, urlparse

class Basket(BaseView):

    @view_config(route_name='basket', renderer='../themes/templates/basket.pt', permission=ACL.ANONYMOUS)
    def basket(self):
        self.set('records', [])
        fee_price = 0.0
        fee_desc = ''
        
        # SUCCESSFUL PAYMENT REDIRECTS HERE
        if self.request.params.get('transactionStatus','0') == '1':
            payments = Payments.load(order_number=self.request.params.get('orderNumber',''), hash=self.request.params.get('userChoice7',''))
            if payments and payments.order_number == self.request.params.get('orderNumber','') and payments.hash == self.request.params.get('userChoice7',''):
                payments.completed_successfully()
                return self.create_invoice()
            
        # HANDLE PAYMENT
        elif 'customer.payment' in self.request.params:
            return self.create_credit_passthrough()

        # SHOW BASKET/CART
        else:
            price, total_price = 0.0, 0.0
            self.set('show_divorce_message', False)
            
            decoded_params = base64.decodestring(self.request.params.get('h','').replace('H_','').replace('_TA5',''))
            decoded_params = urlparse.parse_qs(decoded_params)
        
            items = {}
            if len(decoded_params.get('items',[])) != 0:
                for item  in decoded_params.get('items')[0].split(','):
                    print item
                    items[item] = int(item)
            else:  
                items = self.request.cookies.get('basket',{})
                if items:
                    items = json.loads(urllib2.unquote(items))
                    
            if len(decoded_params.get('feeprice',[])) != 0:
                fee_price = float(decoded_params.get('feeprice')[0])
                fee_desc = base64.decodestring(str(decoded_params.get('feedesc')[0]))
                total_price += fee_price
                    
            if items:                
                results = []
                show_divorce_message = False
                for k,v in items.items():
                    entity = DBSession.query(Entities,Cases,Roles,CallNumbers).filter(Entities.case_id==int(v)).filter(Entities.role==Roles.id).filter(Entities.case_id==Cases.id).filter(Cases.call_number==CallNumbers.id).first()
                    price = float(entity.CallNumbers.price)
                    total_price += price
                    
                    results.append({
                        'id': v,
                        'price': '${:,.2f}'.format(price),
                    })
                    
                    if entity.Cases.actiontype == 17: # hardcoded but eh... very unlikely to change
                        show_divorce_message = True

                self.set('records', results)
                self.set('show_divorce_message', show_divorce_message)
                
            params = []
            if items:
                params.append('items=' + ','.join([str(v) for k,v in items.items()]))
            if fee_price > 0.0 and fee_desc:
                params.append('feeprice=' + str(fee_price))
                params.append('&feedesc=' + base64.encodestring(fee_desc).replace('\n',''))
                
            self.set('perma_cart', self.request.application_url + '/basket?h=H_' + base64.encodestring('&'.join(params)) + '_TA5')
            
            self.set('total_price', '${:,.2f}'.format(total_price))
            self.set('feeprice',fee_price)
            self.set('feeprice_fmt','${:,.2f}'.format(fee_price))
            self.set('feedesc',fee_desc)
            
        return self.response

        
        
    def create_invoice(self):
   
        # user information
        fullname = self.request.params.get('userChoice2','')
        email = self.request.params.get('email','')
        address = self.request.params.get('streetOne','')
        address2 = self.request.params.get('city','') + ', ' + self.request.params.get('state','') + ' ' + self.request.params.get('zip','')
        phone = self.request.params.get('userChoice3','')
        order_number = self.request.params.get('orderNumber','')
        
        notes = "Transation Status: " + self.request.params.get('transactionStatus','') + '\n' + \
                "Transation ID (Confirmation #): " + self.request.params.get('transactionId','') + '\n' + \
                "Transation Amount: " + '${:,.2f}'.format(float(self.request.params.get('transactionTotalAmount','0'))/100)  + '\n' + \
                "Transation Date: " + self.request.params.get('transactionDate','') + '\n' + \
                "Transation Message: " + self.request.params.get('transactionResultMessage','') + '\n' + \
                "Order Number: " + self.request.params.get('orderNumber','') + '\n'
        
        
        # Delivery Options
        deliver_digitally = self.request.params.get('userChoice4','0') == '1'
        deliver_physically = self.request.params.get('userChoice5','0') == '1'
        divorces_only = self.request.params.get('userChoice6','0') == '1'
        
        
        # calculate any fees
        feeprice = float(self.request.params.get('userChoice8',0.0))
        feeprice_fmt = '${:,.2f}'.format(feeprice)
        feedesc = base64.decodestring(self.request.params.get('userChoice9',''))
        feenote = feeprice_fmt + '\n' + feedesc

        # Prep Orders
        records = str(self.request.params.get('userChoice1','')).split('-')
        orders = []
        total_price = feeprice
        location_emails = {} # to notify any locations a request has been made
        for record in records:
            if record:
                c = Cases.load(id=int(record))
                e = Entities.load(case_id=int(record))
                r = Roles.load(id=e.role)
                l = Archives.load(id=c.archive)
                cn = CallNumbers.load(id=c.call_number)
                location_emails[l.email] = l.email
                total_price += float(cn.price)
                orders.append({'case':int(c.id), 'price' : cn.price, 'location':int(l.id)})
                
            
        invoice = Invoices(fullname=fullname, email=email, address=address, county_state_zip=address2, phone=phone, records=orders, fees=feenote,
                           agreement_accepted=True, deliver_digitally=deliver_digitally, deliver_physically=deliver_physically, 
                           divorces_only=divorces_only, order_number=order_number, notes=notes,
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
        
        
    def create_credit_passthrough(self):
        orderDeliveryDigital = 0
        orderDeliveryPhysical = 0
        orderDeliveryDivorceOnly = 0
        total_price = 0.0
        
        # RECORDS HANDLING
        records = self.request.params.getall('records')
        if records:
            #checkout = self.request.params.getall('customer.checkout')
                        
            # Delivery Options
            for option in self.request.params.getall('customer.checkout'):
                if option == 'digitally':
                    orderDeliveryDigital = 1
                if option == 'physically':
                    orderDeliveryPhysical = 1
                if option == 'divorces-only':
                    orderDeliveryDivorceOnly = 1
                    
            #location_emails = {} # to notify any locations a request has been made
            for record in records:
                c = Cases.load(id=int(record))
                # e = Entities.load(case_id=int(record))
                # r = Roles.load(id=e.role)
                # l = Archives.load(id=c.archive)
                cn = CallNumbers.load(id=c.call_number)
                
                #location_emails[l.email] = l.email
                total_price += float(cn.price)
                
        # FEE HANDLING
        feeprice = self.request.params.get('totalfee.price',0.0)
        feedesc = self.request.params.get('totalfee.desc','').strip()
        total_price += float(feeprice)


        order_number = GenerateOrderNumber(Config.get('credit_card_order_number_startswith'))
        payments = Payments(order_number=order_number) # register pending order number
        payment_hash = payments.hash
        payments.insert(self.request)
    
    
        timestamp = str(int(round(time.time() * 1000)))
        order_amount = int(total_price * 100) # must be made into cents
        
        redirectUrlParameters = [
            'payerFullName',
            'orderName',
            'orderNumber',
            'userChoice1',
            'userChoice2',
            'userChoice2',
            'userChoice3',
            'userChoice4',
            'userChoice5',
            'userChoice6',
            'userChoice7',
            'userChoice8',
            'userChoice9',
            'email',
            'streetOne',
            'city',
            'state',
            'zip',
            'daytimePhone',
            'transactionStatus',
            'transactionId',
            'transactionDate',
            'transactionResultMessage',
            'transactionTotalAmount',
        ]
        
        
        kwargs = {
            'orderType':Config.get('credit_card_order_type'), 
            'timestamp':timestamp, 
            'currentAmountDue':order_amount, 
            'amount':order_amount, 
            'orderNumber':order_number, 
            'orderName': self.request.params.get('customer.name',''),
            'userChoice1': '-'.join([str(r) for r in records]),
            'userChoice2': self.request.params.get('customer.name',''),
            'userChoice3': self.request.params.get('customer.phone',''),
            'userChoice4': str(orderDeliveryDigital),
            'userChoice5': str(orderDeliveryPhysical),
            'userChoice6': str(orderDeliveryDivorceOnly),
            'userChoice7': payment_hash,
            'userChoice8': str(feeprice),
            'userChoice9': base64.encodestring(str(feedesc)).replace('\n',''),
            'email': self.request.params.get('customer.email',''),
            'streetOne': self.request.params.get('customer.address',''),
            'city': self.request.params.get('customer.city',''),
            'state': self.request.params.get('customer.state',''),
            'zip': self.request.params.get('customer.zip',''),
            'daytimePhone': self.request.params.get('customer.phone',''),
            'redirectUrlParameters': ','.join(redirectUrlParameters),
            'key': Config.get('credit_card_hash_key'),
        }
        
        
        hash = hash_transaction(**kwargs)
        url = generate_url(Config.get('credit_card_processing_url'), hash, **kwargs)
        
        response = HTTPFound(location=url)
        return response
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
