from sqlalchemy import Column,Integer,BigInteger,String,Unicode,Boolean,TIMESTAMP,ForeignKey,Table,Text
from sqlalchemy.orm import relation
from hashlib import sha1
from courtrecords.models import Base,DBSession,Model

import os,transaction,datetime



class Roles(Base,Model):
    __tablename__ = 'roles'
    
    __scaffold__ = [{'id': { 'widget': 'input', 'label': 'ID', 'attributes': {'type':'text', 'disabled':'true'} } },
                    {'role': { 'widget': 'input', 'label': 'Role', 'attributes': {'type':'text'} } },
                    {'price': { 'widget': 'input', 'label': 'Price', 'attributes': {'type':'text', 'class':'price-validator'} } },
    ]

    id = Column(Integer, primary_key=True)
    role = Column(Unicode(255))
    price = Column(Unicode(6))
    
    def __init__(self, **kwargs):
        self.role = kwargs.get('role','')
        self.price = kwargs.get('price','0.00')


        
    
    
    
    
    
    
    