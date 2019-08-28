from sqlalchemy import Column,Integer,BigInteger,String,Unicode,Boolean,TIMESTAMP,ForeignKey,Table,Text
from sqlalchemy.orm import relationship, backref
from hashlib import sha1
from courtrecords.models import Base,DBSession,Model

import os,transaction,datetime


class Cases(Base,Model):
    __tablename__ = 'cases'

    id = Column(Integer, primary_key=True)
    actiontype = Column(Integer, ForeignKey('actiontypes.id'))
    actiontypes = relationship("ActionTypes")
    case_number = Column(Unicode(55))
    year = Column(Integer(4))
    year_text = Column(Unicode(25))
    container = Column(Integer, ForeignKey('containers.id'))
    containers = relationship("Containers")
    container_number = Column(Unicode(25))
    subset = Column(Unicode(25))
    county = Column(Integer, ForeignKey('counties.id'))
    counties = relationship("Counties")
    community = Column(Integer, ForeignKey('communities.id'))
    communities = relationship("Communities")
    court = Column(Integer, ForeignKey('courts.id'))
    courts = relationship("Courts")
    call_number = Column(Integer, ForeignKey('callnumbers.id'))
    call_numbers = relationship("CallNumbers")
    archive = Column(Integer, ForeignKey('archives.id'))
    archives = relationship("Archives")
    address = Column(Text)
    notes = Column(Text)
    full_text = Column(Text)
    import_file = Column(Unicode(25))
    created = Column(TIMESTAMP, default=datetime.datetime.now())
    updated = Column(TIMESTAMP, default=datetime.datetime.now())
    
    def __init__(self, **kwargs):
        self.actiontype = kwargs.get('actiontype',35)
        self.case_number = kwargs.get('case_number','')
        self.year = kwargs.get('year',1000)
        self.year_text = kwargs.get('year_text','')
        self.container = kwargs.get('container',4)
        self.container_number = kwargs.get('container_number','')
        self.subset = kwargs.get('subset','')
        self.county = kwargs.get('county',0)
        self.community = kwargs.get('community',0)
        self.court = kwargs.get('court',0)
        self.call_number = kwargs.get('call_number',0)
        self.archive = kwargs.get('archive',0)
        self.address = kwargs.get('address','')
        self.notes = kwargs.get('notes','')
        self.full_text = kwargs.get('notes','')
        self.import_file = kwargs.get('import_file','not provided')


        
    
    
    
    
    
    
    