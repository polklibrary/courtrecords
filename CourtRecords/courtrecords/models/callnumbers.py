from sqlalchemy import Column,Integer,BigInteger,String,Unicode,Boolean,TIMESTAMP,ForeignKey,Table,Text
from sqlalchemy.orm import relation
from hashlib import sha1
from courtrecords.models import Base,DBSession,Model

import os,transaction,datetime


class CallNumbers(Base,Model):
    __tablename__ = 'callnumbers'

    __scaffold__ = [{'id': { 'widget': 'input', 'label': 'ID', 'attributes': {'type':'text', 'disabled':'true'} } },
                    {'call_number': { 'widget': 'input', 'label': 'Call Number', 'attributes': {'type':'text'} } },
    ]

    id = Column(Integer, primary_key=True)
    call_number = Column(Unicode(55))
    
    def __init__(self, **kwargs):
        self.call_number = kwargs.get('call_number','')
