from sqlalchemy import Column,Integer,BigInteger,String,Unicode,Boolean,TIMESTAMP,ForeignKey,Table,Text
from sqlalchemy.orm import relation
from hashlib import sha1
from courtrecords.models import Base,DBSession,Model

import os,transaction,datetime


class Archives(Base,Model):
    __tablename__ = 'archives'

    __scaffold__ = [{'id': { 'widget': 'input', 'label': 'ID', 'attributes': {'type':'text', 'disabled':'true'} } },
                    {'name': { 'widget': 'input', 'label': 'Name', 'attributes': {'type':'text'} } },
                    {'email': { 'widget': 'input', 'label': 'Email', 'attributes': {'type':'text'} } },
                    {'phone': { 'widget': 'input', 'label': 'Phone', 'attributes': {'type':'text'} } },
                    {'email_signature': { 'widget': 'input', 'label': 'Email Signature', 'attributes': {'type':'text'} } },
    ]

    
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(55))
    email = Column(Unicode(55))
    phone = Column(Unicode(55))
    email_signature = Column(Text)
    
    def __init__(self, **kwargs):
        self.name = kwargs.get('name','')
        self.email = kwargs.get('email','')
        self.phone = kwargs.get('phone','')
        self.email_signature = kwargs.get('email_signature','')

    @classmethod
    def get_location(cls,entity=None,case=None):
        from courtrecords.models import Entities, Cases
        id = 0
        if entity:
            e = Entities.load(id=entity)
            case = e.case_id
        if case:
            c = Cases.load(id=case)
            id = c.archive
        if id:
            return Archives.load(id=id)
        return None
        
    
    
    
    