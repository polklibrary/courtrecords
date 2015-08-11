from sqlalchemy import Column,Integer,BigInteger,String,Unicode,Boolean,TIMESTAMP,ForeignKey,Table,Text
from sqlalchemy.orm import relation
from courtrecords.models import Base,DBSession,Model


class Suffixs(Base,Model):
    __tablename__ = 'suffixs'
    
    __scaffold__ = [{'id': { 'widget': 'input', 'label': 'ID', 'attributes': {'type':'text', 'disabled':'true'} } },
                    {'suffix': { 'widget': 'input', 'label': 'Suffix', 'attributes': {'type':'text'} } },
    ]

    id = Column(Integer, primary_key=True)
    suffix = Column(Unicode(25))
    
    def __init__(self, **kwargs):
        self.suffix = kwargs.get('suffix','')

    