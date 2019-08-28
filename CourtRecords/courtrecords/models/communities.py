from sqlalchemy import Column,Integer,BigInteger,String,Unicode,Boolean,TIMESTAMP,ForeignKey,Table,Text
from sqlalchemy.orm import relation
from hashlib import sha1
from courtrecords.models import Base,DBSession,Model

import os,transaction,datetime


class Communities(Base,Model):
    __tablename__ = 'communities'

    __scaffold__ = [{'id': { 'widget': 'input', 'label': 'ID', 'attributes': {'type':'text', 'disabled':'true'} } },
                    {'community': { 'widget': 'input', 'label': 'Community', 'attributes': {'type':'text'} } },
    ]

    id = Column(Integer, primary_key=True)
    community = Column(Unicode(255))
    
    def __init__(self, **kwargs):
        self.community = kwargs.get('community','')


        
    
    
    
    
    
    
    