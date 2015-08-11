from courtrecords.security.acl import ACL
from courtrecords.security.decorators import protected
from sqlalchemy import or_
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from zope.sqlalchemy import ZopeTransactionExtension
import os,transaction,datetime

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Model(object):
    
    def insert(self, request):
        DBSession.add(self)
        DBSession.flush()
        tmp = self.id
        transaction.commit()
        return tmp
    
    @protected([ACL.AUTHENTICATED,ACL.EDITOR,ACL.ADMINISTRATOR])
    def save(self, request):
        DBSession.flush()
        transaction.commit()

    @protected([ACL.EDITOR,ACL.ADMINISTRATOR])
    def remove(self):
        DBSession.delete(self)
        transaction.commit()
        
    @classmethod
    def _load(cls,**kwargs):
        """ Main Loader """
        
        query = DBSession.query(cls)
        
        for key in kwargs:
            if key not in ['order','like','offset','limit']:
                query = query.filter(getattr(cls,key)==kwargs[key])
        if 'like' in kwargs:
            for key,value in kwargs.get('like').items():
                query = query.filter(getattr(cls,key).like('%'+value+'%'))
        if 'order' in kwargs:
            query = query.order_by(kwargs.get('order'))
        if 'offset' in kwargs:
            query = query.offset(kwargs.get('offset'))
        if 'limit' in kwargs:
            query = query.limit(kwargs.get('limit'))

        return query
    
    @classmethod
    def load(cls,**kwargs):
        return cls._load(**kwargs).first()
        
    @classmethod
    def loadAll(cls,**kwargs):
        return cls._load(**kwargs).all()
        
        
        

# Import Shortcuts
from courtrecords.models.users import Users,GuestUser
from courtrecords.models.entities import Entities
from courtrecords.models.cases import Cases
from courtrecords.models.actiontypes import ActionTypes
from courtrecords.models.counties import Counties
from courtrecords.models.roles import Roles
from courtrecords.models.suffixs import Suffixs
from courtrecords.models.prefixs import Prefixs
from courtrecords.models.config import Config
from courtrecords.models.archives import Archives
from courtrecords.models.callnumbers import CallNumbers
from courtrecords.models.containers import Containers
from courtrecords.models.courts import Courts
from courtrecords.models.statuses import Statuses
from courtrecords.models.invoices import Invoices