from sqlalchemy import Column,Integer,BigInteger,String,Unicode,Boolean,TIMESTAMP,ForeignKey,Table,Text
from sqlalchemy.orm import relation
from hashlib import sha1
from courtrecords.models import Base,DBSession,Model

import os,transaction,datetime


class Counties(Base,Model):
    __tablename__ = 'counties'

    __scaffold__ = [{'id': { 'widget': 'input', 'label': 'ID', 'attributes': {'type':'text', 'disabled':'true'} } },
                    {'county': { 'widget': 'input', 'label': 'County', 'attributes': {'type':'text'} } },
    ]

    id = Column(Integer, primary_key=True)
    county = Column(Unicode(255))
    
    def __init__(self, **kwargs):
        self.county = kwargs.get('county','')


        
    
    
    
    
    
    
    