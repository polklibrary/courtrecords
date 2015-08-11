from sqlalchemy import Column,Integer,BigInteger,String,Unicode,Boolean,TIMESTAMP,ForeignKey,Table,Text
from sqlalchemy.orm import relation
from hashlib import sha1
from courtrecords.models import Base,DBSession,Model

import os,transaction,datetime


class Courts(Base,Model):
    __tablename__ = 'courts'

    __scaffold__ = [{'id': { 'widget': 'input', 'label': 'ID', 'attributes': {'type':'text', 'disabled':'true'} } },
                    {'court': { 'widget': 'input', 'label': 'Court', 'attributes': {'type':'text'} } },
    ]

    id = Column(Integer, primary_key=True)
    court = Column(Unicode(55))
    
    def __init__(self, **kwargs):
        self.court = kwargs.get('court','')

