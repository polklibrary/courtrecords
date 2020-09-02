
from courtrecords.security.acl import ACL
from courtrecords.security.cardhash import hash_transaction, generate_url, generate_return_url
from courtrecords.models import DBSession,Cases,Entities,Invoices,Roles,CallNumbers,Counties,ActionTypes,Archives,Statuses,Courts,Prefixs,Suffixs,Config
from courtrecords.utilities.utility import Result2Dict,Results2Dict,GenerateOrderNumber
from courtrecords.utilities.validators import Validators
from courtrecords.views import BaseView
from courtrecords.views.emailer import Emailer
from pyramid.httpexceptions import HTTPFound
from pyramid.url import route_url
from pyramid.view import view_config
from sqlalchemy import or_,and_,func

import time
import urllib2, json, base64, urlparse, transaction

class Basket(BaseView):

    @view_config(route_name='basket', renderer='../themes/templates/basket.pt', permission=ACL.ANONYMOUS)
    def basket(self):
        self.set('records', [])
        fee_price = 0.0
        fee_desc = ''
        
        
        # SUCCESSFUL PAYMENT REDIRECTS HERE
        if self.request.params.get('transactionStatus','0') in ['1','5','6','8']:
            invoice = Invoices.load(order_number=self.request.params.get('orderNumber',''))
            if invoice:
                return self.payment_success_process()
            
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
                    items[item] = int(item)
            else:  
                items = self.request.cookies.get('basket',{})
                if items:
                    items = json.loads(urllib2.unquote(items))
                    
            if len(decoded_params.get('feeprice',[])) != 0:
                fee_price = float(decoded_params.get('feeprice')[0])
                fee_desc = str(decoded_params.get('feedesc')[0])
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
                params.append('&feedesc=' + fee_desc)
                
            self.set('perma_cart', self.request.application_url + '/basket?h=H_' + base64.encodestring('&'.join(params)) + '_TA5')
            
            self.set('total_price', '${:,.2f}'.format(total_price))
            self.set('feeprice',fee_price)
            self.set('feeprice_fmt','${:,.2f}'.format(fee_price))
            self.set('feedesc',fee_desc)
            
        return self.response

        
        
    def payment_success_process(self):
        order_number = self.request.params.get('orderNumber','')
        notes = "Transation Status: " + self.request.params.get('transactionStatus','') + '\n' + \
                "Transation ID (Confirmation #): " + str(self.request.params.get('transactionId','')) + '\n' + \
                "Transation Amount: " + '${:,.2f}'.format(float(self.request.params.get('transactionTotalAmount','0'))/100)  + '\n' + \
                "Transation Date: " + self.request.params.get('transactionDate','') + '\n' + \
                "Transation Message: " + self.request.params.get('transactionResultMessage','') + '\n' + \
                "Order Number: " + str(order_number) + '\n'
        
        invoice = Invoices.load(order_number=order_number)
        invoice.status = 2
        invoice.notes = notes
        

        # Get Archive Emails
        location_emails = []
        for record in json.loads(invoice.records):
            location_emails.append(Archives.load(id=record['location']).email)

        #Email Client
        starting_status = Statuses.load(paid=1)
        Emailer.send(self.request,
                     [invoice.email],
                     starting_status.email_subject,
                     starting_status.email_message,
                     link=self.request.application_url + '/invoice/' + invoice.hash
                     )
                     
        #Email Archives Involved
        Emailer.send(self.request,
                     location_emails,
                     'Order request has been placed',
                     'A new order request has been placed',
                     link=self.request.application_url + '/login?goto=' + self.request.application_url + '/manage/orders'
                     )
                     
        response = HTTPFound(location=route_url('invoice', self.request, hash=invoice.hash))
        response.delete_cookie('basket')

        DBSession.flush()
        transaction.commit()

        return response
        
        
    def create_credit_passthrough(self):
        total_price = 0.0
        deliver_digitally = False
        deliver_physically = False
        divorces_only = False

        fullname = self.request.params.get('customer.name','')
        email = self.request.params.get('customer.email','')
        address = self.request.params.get('customer.address','')
        city = self.request.params.get('customer.city','')
        state = self.request.params.get('customer.state','')
        zip = self.request.params.get('customer.zip','')
        phone = self.request.params.get('customer.phone','')
        address2 = city + ', ' + state + ' ' + zip

        # Delivery Options
        for option in self.request.params.getall('customer.checkout'):
            if option == 'digitally':
                deliver_digitally = True
            if option == 'physically':
                deliver_physically = True
            if option == 'divorces-only':
                divorces_only = True

        # FEE HANDLING
        feeprice = float(self.request.params.get('totalfee.price', 0.0))
        feedesc = self.request.params.get('totalfee.desc','').strip()
        feeprice_fmt = '${:,.2f}'.format(feeprice)
        feenote = feeprice_fmt + '\n' + feedesc
        total_price += feeprice
        order_number = GenerateOrderNumber(Config.get('credit_card_order_number_startswith'))
 
        # Create Pending Order
        orders = []
        records = self.request.params.getall('records')
        if records: 
            for record in records:
                if record:
                    c = Cases.load(id=int(record))
                    cn = CallNumbers.load(id=c.call_number)
                    l = Archives.load(id=c.archive)
                    total_price += float(cn.price)
                    orders.append({'case':int(c.id), 'price' : cn.price, 'location':int(l.id)})
                    
        invoice = Invoices(fullname=fullname, email=email, address=address, county_state_zip=address2, phone=phone, records=orders, fees=feenote,
                           agreement_accepted=True, deliver_digitally=deliver_digitally, deliver_physically=deliver_physically, 
                           divorces_only=divorces_only, order_number=order_number,
                           total_price='${:,.2f}'.format(total_price))
        invoice.insert(self.request)
        invoice = Invoices.load(order='id desc')

        timestamp = str(int(round(time.time() * 1000)))
        order_amount = int(total_price * 100) # must be made into cents
        redirectUrlParameters = [
            'orderNumber',
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
            'orderName': fullname,
            # 'userChoice1': '-'.join([str(r) for r in records]),
            # 'userChoice2': self.request.params.get('customer.name',''),
            # 'userChoice3': self.request.params.get('customer.phone',''),
            # 'userChoice4': str(orderDeliveryDigital),
            # 'userChoice5': str(orderDeliveryPhysical),
            # 'userChoice6': str(orderDeliveryDivorceOnly),
            # 'userChoice7': payment_hash,
            # 'userChoice8': str(feeprice),
            # 'userChoice9': 'blank',  # nothing
            # 'userChoice10': 'blank',  # nothing
            #'userChoice11': base64.encodestring(str(feedesc)).replace('\n',''),
            'email': email,
            'streetOne': address,
            'city': city,
            'state': state,
            'zip': zip,
            'daytimePhone': phone,
            'redirectUrlParameters': ','.join(redirectUrlParameters),
            'key': Config.get('credit_card_hash_key'),
        }
        
        
        hash = hash_transaction(**kwargs)
        url = generate_url(Config.get('credit_card_processing_url'), hash, **kwargs)
        
        response = HTTPFound(location=url)
        return response
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
