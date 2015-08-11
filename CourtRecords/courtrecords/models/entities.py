from sqlalchemy import Column,Integer,BigInteger,String,Unicode,Boolean,TIMESTAMP,ForeignKey,Table,Text
from sqlalchemy.orm import relationship, backref, relation
from hashlib import sha1
from courtrecords.models import Base,DBSession,Model

import os,transaction,datetime


class Entities(Base,Model):
    __tablename__ = 'entities'

    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey('cases.id'))
    case = relationship('Cases', backref='entities')
    entity = Column(Unicode(255))
    prefix = Column(Integer)
    lastname = Column(Unicode(55))
    firstname = Column(Unicode(55))
    middlename = Column(Unicode(55))
    suffix = Column(Integer)
    alternatename = Column(Unicode(55))
    role = Column(Integer, ForeignKey('roles.id'))
    roles = relationship('Roles')
    import_file = Column(Unicode(25))
    created = Column(TIMESTAMP, default=datetime.datetime.now())
    updated = Column(TIMESTAMP, default=datetime.datetime.now())
    
    def __init__(self, **kwargs):
        self.actiontype = kwargs.get('actiontype','Unknown')
        self.case_id = kwargs.get('case_id',0)
        self.entity = kwargs.get('entity','')
        self.prefix = kwargs.get('prefix','')
        self.lastname = kwargs.get('lastname','')
        self.firstname = kwargs.get('firstname','')
        self.middlename = kwargs.get('middlename','')
        self.suffix = kwargs.get('suffix','')
        self.alternatename = kwargs.get('alternatename','')
        self.role = kwargs.get('role',0)
        self.import_file = kwargs.get('import_file','not provided')


        
    
    
    
    
    
    
    