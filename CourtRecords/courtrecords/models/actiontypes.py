from sqlalchemy import Column,Integer,BigInteger,String,Unicode,Boolean,TIMESTAMP,ForeignKey,Table,Text
from sqlalchemy.orm import relation
from hashlib import sha1
from courtrecords.models import Base,DBSession,Model

import os,transaction,datetime


class ActionTypes(Base,Model):
    __tablename__ = 'actiontypes'

    __scaffold__ = [{'id': { 'widget': 'input', 'label': 'ID', 'attributes': {'type':'text', 'disabled':'true'} } },
                    {'actiontype': { 'widget': 'input', 'label': 'Action Type', 'attributes': {'type':'text'} } },
    ]

    
    id = Column(Integer, primary_key=True)
    actiontype = Column(Unicode(255))
    
    def __init__(self, **kwargs):
        self.actiontype = kwargs.get('actiontype','')


        
    
    
    
    
    
    
    