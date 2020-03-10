from sqlalchemy import Column,Integer,BigInteger,String,Unicode,Boolean,TIMESTAMP,ForeignKey,Table
from sqlalchemy.orm import relation
from hashlib import sha1
from courtrecords.models import Base,DBSession,Model

import os,transaction,datetime,random,hashlib


class Payments(Base,Model):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    order_number = Column(Unicode(64), unique=True)
    hash = Column(Unicode(255))
    
    def __init__(self, **kwargs):
        self.order_number = kwargs.get('order_number','')
        self.hash = hashlib.md5(str(random.random()) + str(random.randint(1,1000000000))).hexdigest()

    def completed_successfully(self):
        DBSession.delete(self)
        transaction.commit()