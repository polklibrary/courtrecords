
from courtrecords.models import Base,Model
from sqlalchemy import Column,Integer,BigInteger,String,Unicode,Boolean,TIMESTAMP,ForeignKey,Table,Text


class Statuses(Base,Model):
    __tablename__ = 'statuses'

    __scaffold__ = [{'id': { 'widget': 'input', 'label': 'ID', 'attributes': {'type':'text', 'disabled':'true'} } },
                    {'priority': { 'widget': 'input', 'label': 'Priority', 'attributes': {'type':'text', 'class':'number-validator'} } },
                    {'status': { 'widget': 'input', 'label': 'Status', 'attributes': {'type':'text'} } },
                    {'email_subject': { 'widget': 'input', 'label': 'Email Subject', 'attributes': {'type':'text'} } },
                    {'email_message': { 'widget': 'textarea', 'label': 'Email Message', 'attributes': {} } },
    ]
    
    id = Column(Integer, primary_key=True)
    priority = Column(Integer)
    status = Column(Unicode(55))
    email_subject = Column(Unicode(55))
    email_message = Column(Text)
    
    def __init__(self, **kwargs):
        self.priority = kwargs.get('priority',0)
        self.status = kwargs.get('status','')
        self.email_subject = kwargs.get('email_subject','')
        self.email_message = kwargs.get('email_message','')
    

    