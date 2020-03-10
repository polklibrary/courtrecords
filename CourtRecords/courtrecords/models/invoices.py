from courtrecords.utilities.utility import GenerateOrderNumber
from courtrecords.models import Base,DBSession,Model,Entities,Cases,Roles,Counties,Containers,ActionTypes,Archives
from sqlalchemy import Column,Integer,BigInteger,String,Unicode,Boolean,TIMESTAMP,ForeignKey,Table,Text
from sqlalchemy.orm import relationship, backref, relation
from sqlalchemy import or_,and_,func

import datetime,json,hashlib,time


class Invoices(Base,Model):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True)
    order_number = Column(Unicode(64))
    hash = Column(Unicode(512))
    fullname = Column(Unicode(55))
    email = Column(Unicode(55))
    address = Column(Unicode(255))
    county_state_zip = Column(Unicode(255))
    phone = Column(Unicode(14))
    status = Column(Integer)
    total_price = Column(Integer)
    agreement_accepted = Column(Boolean)
    deliver_digitally = Column(Boolean)
    deliver_physically = Column(Boolean)
    divorces_only = Column(Boolean)
    notes = Column(Text)
    records = Column(Text)
    fees = Column(Text)
    completed = Column(Boolean)
    created = Column(TIMESTAMP, default=datetime.datetime.now())
    
    def __init__(self, **kwargs):
        self.actiontype = kwargs.get('actiontype','Unknown')
        self.fullname = kwargs.get('fullname','')
        self.email = kwargs.get('email','')
        self.address = kwargs.get('address','')
        self.county_state_zip = kwargs.get('county_state_zip','')
        self.phone = kwargs.get('phone','')
        self.status = kwargs.get('status',1)
        self.total_price = kwargs.get('total_price',0)
        self.agreement_accepted = kwargs.get('agreement_accepted',False)
        self.deliver_digitally = kwargs.get('deliver_digitally',False)
        self.deliver_physically = kwargs.get('deliver_physically',False)
        self.divorces_only = kwargs.get('divorces_only',False)
        self.completed = kwargs.get('completed',False)
        self.records = json.dumps(kwargs.get('records',[]))
        self.fees = kwargs.get('fees','')
        self.hash = hashlib.sha256(kwargs.get('order_number', 'error')).hexdigest()
        self.order_number = kwargs.get('order_number', None)
        self.created = datetime.datetime.now()
        self.notes = kwargs.get('notes','')

    def set_records(self,records):
        self.records = json.dumps(records)
            
    def get_records_raw(self):
        return json.loads(self.records)
            
    def get_records(self):
        records = json.loads(self.records)

        clauses = []
        results = []
        for record in records:
            query = DBSession.query(Cases,Entities,Roles,Counties,ActionTypes,Archives,Containers) \
                                                                        .filter(Cases.id==int(record['case'])) \
                                                                        .filter(Entities.case_id==Cases.id) \
                                                                        .filter(Entities.role==Roles.id) \
                                                                        .filter(Cases.county==Counties.id) \
                                                                        .filter(Cases.archive==Archives.id) \
                                                                        .filter(Cases.container==Containers.id) \
                                                                        .filter(Cases.actiontype==ActionTypes.id)
        
            results.append({
                'case': query.first(),
                'price': record['price'],
            })

        return results
    
    @property
    def get_total_records(self):
        return len(json.loads(self.records))
    
    @property
    def next_status(self):
        from courtrecords.models import Statuses
        return Statuses.load(id=self.status+1)
        
    @property
    def previous_status(self):
        from courtrecords.models import Statuses
        return Statuses.load(id=self.status-1)
    
    @property
    def get_status(self):
        from courtrecords.models import Statuses
        return Statuses.load(id=self.status)
    
    @property
    def secure_phone(self):
        return '*-***-***-' + self.phone[-4:]

    @property
    def secure_address(self):
        return self.county_state_zip
        
    @property
    def secure_email(self):
        try:
            parts = self.email.split('@')
            mail = parts.pop()
            hidden = ''
            for i in range(3, len(parts.pop())):
                hidden += '*'
            return self.email[:3] + hidden + '@' + mail
        except:
            return 'Error occured with your email'