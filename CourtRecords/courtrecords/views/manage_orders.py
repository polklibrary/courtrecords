
from courtrecords.security.acl import ACL
from courtrecords.models import Users, Invoices, Statuses, Archives
from courtrecords.utilities.validators import Validators
from courtrecords.views import BaseView
from courtrecords.views.emailer import Emailer
from pyramid.view import view_config

class ManageOrders(BaseView):

    @view_config(route_name='manage_orders', renderer='../themes/templates/admin/orders.pt', permission=ACL.EDITOR)
    def manage_orders(self):
        self.set('invoices',Invoices.loadAll(order='created desc'))
        return self.response
        
        
        
class ManageOrder(BaseView):

    @view_config(route_name='manage_order', renderer='../themes/templates/admin/order.pt', permission=ACL.EDITOR)
    def manage_order(self):
        id = int(self.request.matchdict['id'])
        
        if 'invoice.submit' in self.request.params:
            invoice = Invoices.load(id=id)
            invoice.fullname = self.request.params.get('invoice.fullname','')
            invoice.email = self.request.params.get('invoice.email','')
            invoice.phone = self.request.params.get('invoice.phone','')
            invoice.address = self.request.params.get('invoice.address','')
            invoice.county_state_zip = self.request.params.get('invoice.county_state_zip','')
            invoice.status = int(self.request.params.get('invoice.status',1))
            invoice.deliver_digitally = Validators.bool(self.request.params.get('invoice.deliver_digitally',0))
            invoice.deliver_physically = Validators.bool(self.request.params.get('invoice.deliver_physically',0))
            
            
            final_status = Statuses.load(order='priority desc')
            if final_status.id == invoice.status:
                invoice.completed = True
            
            if Validators.bool(self.request.params.get('invoice.status.emailer',0)):
                status = Statuses.load(id=invoice.status)
                orders_data = invoice.get_records_raw()
                archive = Archives.load(id=orders_data[0]['location'])
                
                Emailer.send(self.request,
                             [invoice.email],
                             status.email_subject,
                             status.email_message,
                             signature=archive.email_signature,
                             link=self.request.application_url + '/invoice/' + invoice.hash
                             )
                
                
        
        invoice = Invoices.load(id=id)
        self.set('invoice',invoice)
        self.set('records',invoice.get_records())
        self.set('statuses',Statuses.loadAll(order='priority asc'))
        return self.response
