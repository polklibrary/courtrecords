from sqlalchemy import Column,Integer,BigInteger,String,Unicode,Boolean,TIMESTAMP,ForeignKey,Table,Text
from sqlalchemy.orm import relation
from hashlib import sha1
from courtrecords.models import Base,DBSession,Model

import os,transaction,datetime,re


class Config(Base,Model):
    __tablename__ = 'config'

    __scaffold__ = [{'id': { 'widget': 'input', 'label': 'ID', 'attributes': {'type':'text', 'disabled':'true'} } },
                    {'name': { 'widget': 'input', 'label': 'Name', 'attributes': {'type':'text'} } },
                    {'value': { 'widget': 'textarea', 'label': 'Value', 'attributes': {'rows':'4', 'cols':'20', 'class': 'mce-content-body' } } },
                    {'use_editor': { 'widget': 'select', 'label': 'Edit with TinyMCE', 'options': { 'Yes':'1', 'No':'0' }, 'option_type':'bool' } },
                    {'note': { 'widget': 'textarea', 'label': 'Note', 'attributes': {'rows':'4', 'cols':'20'} } },
    ]

    
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(25))
    value = Column(Unicode(255))
    use_editor = Column(Boolean)
    note = Column(Text)
    
    def __init__(self, **kwargs):
        self.name = kwargs.get('name','')
        self.value = kwargs.get('value','')
        self.note = kwargs.get('notes','')
        self.use_editor = kwargs.get('use_editor',0)


    @classmethod
    def get(cls, name,purify=False):
        text = DBSession.query(cls).filter(cls.name == name).first().value
        if purify:
            text = re.sub('<[^<]+?>', '', text)
        return text
    
    
    
    
    