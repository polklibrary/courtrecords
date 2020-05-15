
from courtrecords.models import Base,Model
from sqlalchemy import Column,Integer,BigInteger,String,Unicode,Boolean,TIMESTAMP,ForeignKey,Table,Text


class Statuses(Base,Model):
    __tablename__ = 'statuses'

    __scaffold__ = [{'id': { 'widget': 'input', 'label': 'ID', 'attributes': {'type':'text', 'disabled':'true'} } },
                    {'priority': { 'widget': 'input', 'label': 'Priority', 'attributes': {'type':'text', 'class':'number-validator'} } },
                    {'status': { 'widget': 'input', 'label': 'Status', 'attributes': {'type':'text'} } },
                    {'paid': { 'widget': 'select', 'label': 'Payment Success Trigger', 
                        'attributes': {'title':'This is the status set after successful payment.'},
                        'option_type': 'int',
                        'options': {'Yes':1,'No':0,},
                    } },
                    {'email_subject': { 'widget': 'input', 'label': 'Email Subject', 'attributes': {'type':'text'} } },
                    {'email_message': { 'widget': 'textarea', 'label': 'Email Message', 'attributes': {} } },
                    {'color': { 'widget': 'input', 'label': 'Status Color', 'attributes': {'type':'text'} } },
    ]
    
    id = Column(Integer, primary_key=True)
    priority = Column(Integer)
    paid = Column(Integer)
    status = Column(Unicode(55))
    email_subject = Column(Unicode(55))
    email_message = Column(Text)
    color = Column(Unicode(10))
    
    def __init__(self, **kwargs):
        self.priority = kwargs.get('priority',0)
        self.status = kwargs.get('status','')
        self.paid = kwargs.get('paid',0)
        self.email_subject = kwargs.get('email_subject','')
        self.email_message = kwargs.get('email_message','')
        self.color = kwargs.get('color','#333333')
    

    