
from courtrecords.security.acl import ACL
from courtrecords.models import DBSession,Users,Cases,Entities,ActionTypes,Counties,Roles,Archives,Courts,Config,Containers,Communities
from courtrecords.utilities.utility import Result2Dict,Results2Dict
from courtrecords.utilities.validators import Validators
from courtrecords.views import BaseView
from pyramid.view import view_config
from sqlalchemy import or_,and_,func

import time, datetime, re, HTMLParser, shlex

class Search(BaseView):

    @view_config(route_name='search', renderer='../themes/templates/search.pt', permission=ACL.ANONYMOUS)
    def search(self):
        #names
        self.set('entity', self.request.params.get('entity',''))
        self.set('escaped_entity', self.request.params.get('entity','').replace('"','\\"').replace("'","\\'"))
        self.set('everything', self.request.params.get('everything',''))
        self.set('escaped_everything', self.request.params.get('everything','').replace('"','\\"').replace("'","\\'"))
        self.set('firstname', self.request.params.get('firstname',''))
        self.set('escaped_firstname', self.request.params.get('firstname','').replace('"','\\"').replace("'","\\'"))
        self.set('keywords', self.request.params.get('keywords',''))
        self.set('escaped_keywords', self.request.params.get('keywords','').replace('"','\\"').replace("'","\\'"))
        self.set('mode', self.request.params.get('mode',False))
        
        #dates
        self.set('start_date', int(self.request.params.get('start_date', 0)))
        self.set('end_date', int(self.request.params.get('end_date', datetime.datetime.today().year)))
        sd = DBSession.query(Cases).filter(Cases.year > 1800).order_by('year asc').first()
        if sd:
            self.set('earliest_recorded_date', sd.year)
        else: 
            self.set('earliest_recorded_date', 1800)
        ed = DBSession.query(Cases).filter(Cases.year < datetime.datetime.today().year).order_by('year desc').first()
        if ed:
            self.set('last_recorded_date', ed.year)
        else: 
            self.set('last_recorded_date', datetime.datetime.today().year)
        
        #types
        actiontypes = [ int(at) for at in self.request.params.getall('actiontypes') ]
        self.set('actiontypes', actiontypes)
        self.set('actiontypes_list', ActionTypes.loadAll(order='actiontype asc'))
        
        #counties
        counties = [ int(at) for at in self.request.params.getall('counties') ]
        self.set('counties', counties)
        self.set('counties_list', Counties.loadAll(order='county asc'))
        
        #communities
        communities = [ int(at) for at in self.request.params.getall('communities') ]
        self.set('communities', communities)
        self.set('communities_list', Communities.loadAll(order='community asc'))
        
        #roles
        roles = [ int(r) for r in self.request.params.getall('roles') ]
        self.set('roles', roles)
        self.set('roles_list', Roles.loadAll(order='role asc'))
        
        #archives
        archives = [ int(l) for l in self.request.params.getall('archives') ]
        self.set('archives', archives)
        self.set('archives_list', Archives.loadAll(order='name asc'))
        
        #courts
        courts = [ int(l) for l in self.request.params.getall('courts') ]
        self.set('courts', courts)
        self.set('courts_list', Courts.loadAll(order='court asc'))
        
        #entities
        self.set('total_records', Entities.TotalCount())
        
        
        return self.response
        
        
    @view_config(route_name='get_results', renderer='json', permission=ACL.ANONYMOUS)
    def get_results(self):
        
        timer_start = time.time()
        
        order_headings = ['entities.id','entities.entity','entities.middlename','entities.firstname','entities.role','cases.year','cases.county','cases.community','cases.address']
        order_index = int(self.request.params.get('order[0][column]',0))
        order = order_headings[order_index] + ' ' + self.request.params.get('order[0][dir]', 'asc')
        
        
        entity = HTMLParser.HTMLParser().unescape(self.request.params.get('entity',''))
        firstname = HTMLParser.HTMLParser().unescape(self.request.params.get('firstname',''))
        keywords = HTMLParser.HTMLParser().unescape(self.request.params.get('keywords',''))
        everything = HTMLParser.HTMLParser().unescape(self.request.params.get('everything',''))
        start_date = int(self.request.params.get('start_date', 0))
        end_date = int(self.request.params.get('end_date', datetime.datetime.today().year))
        case_types = filter(lambda x: x!=0, [ int(ct) for ct in self.request.params.getall('case_types[]') if ct ])
        communities = filter(lambda x: x!=0, [ int(c) for c in self.request.params.getall('communities[]') if c ])
        counties = filter(lambda x: x!=0, [ int(c) for c in self.request.params.getall('counties[]') if c ])
        roles = filter(lambda x: x!=0, [ int(r) for r in self.request.params.getall('roles[]') if r ])
        archives = filter(lambda x: x!=0, [ int(l) for l in self.request.params.getall('archives[]') if l ])
        courts = filter(lambda x: x!=0, [ int(c) for c in self.request.params.getall('courts[]') if c ])
        
        offset = int(self.request.params.get('start',0))
        limit = int(self.request.params.get('length',15))
        mode = self.request.params.get('mode', 'basic')

        
        allobjs = []
        query = DBSession.query(Cases,Entities,Roles,Counties,Communities,ActionTypes,Archives,Courts,Containers)
        
        if entity:
            print "ENTITY FILTER"
            query = query.filter(Entities.entity.like('%'+entity+'%')) #only do % right side, otherwise will ignore sql indexing
        if firstname:
            print "FIRSTNAME FILTER"
            query = query.filter(Entities.firstname.like(firstname+'%'))  #only do % right side, otherwise will ignore sql indexing
        # if everything:
            # print "EVERYTHING FILTER"
            # words = shlex.split(everything.lower())
            # for word in words:
                # query = query.filter(Cases.full_text.like('%'+word+'%'))
        if everything:
            print "EVERYTHING FILTER"
            words = shlex.split(everything.lower())
            against = ''
            for word in words:
                if ' ' in word:
                    against += '"' + word + '" ' 
                elif '+' not in word and '-' not in word:
                    against += '+' + word + ' ' 
                else:
                    against += word + ' ' 
            query = query.filter(" MATCH(cases.full_text) AGAINST('" + against + "' IN BOOLEAN MODE) ")
            
            
        if keywords:
            print "KEYWORDS FILTER"
            words = keywords.replace(',',' ').split(' ')
            for word in words:
                query = query.filter(or_(Cases.notes.like('%' + word.strip() + '%'), Entities.alternatename.like('%' + word.strip() + '%'))) # will be slow
        
        if start_date > 0 and end_date < 2050:
            print "YEAR FILTER"
            query = query.filter(and_(Cases.year <= end_date, Cases.year >= start_date))
        
        if case_types:
            print "ACTION TYPE FILTER " + str(case_types)
            clauses = []
            for case_type in case_types:
                if case_type != 0: # 0 is reserved for All
                    clauses.append( (Cases.actiontype == case_type) )
            query = query.filter(or_(*clauses))
            
        if counties:
            print "COUNTIES TYPE FILTER " + str(counties)
            clauses = []
            for county in counties:
                if county != 0: # 0 is reserved for All
                    clauses.append( (Cases.county == county) )
            query = query.filter(or_(*clauses))
            
        if roles:
            print "ROLES TYPE FILTER " + str(roles)
            clauses = []
            for role in roles:
                if role != 0: # 0 is reserved for All
                    clauses.append( (Entities.role == role) )
            query = query.filter(or_(*clauses))
            
        if communities:
            print "COMMUNITIES TYPE FILTER " + str(communities)
            clauses = []
            for community in communities:
                if community != 0: # 0 is reserved for All
                    clauses.append( (Cases.community == community) )
            query = query.filter(or_(*clauses))
            
            
        if archives:
            print "ARCHIVES TYPE FILTER " + str(archives)
            clauses = []
            for archive in archives:
                if archive != 0: # 0 is reserved for All
                    clauses.append( (Cases.archive == archive) )
            query = query.filter(or_(*clauses))
            
        if courts:
            print "COURTS TYPE FILTER " + str(courts)
            clauses = []
            for court in courts:
                if court != 0: # 0 is reserved for All
                    clauses.append( (Cases.court == court) )
            query = query.filter(or_(*clauses))
        

        # Table joining, do last because FT index runs first.
        query = query.filter(Cases.court==Courts.id) \
                  .filter(Cases.actiontype==ActionTypes.id)  \
                  .filter(Cases.archive==Archives.id) \
                  .filter(Cases.county==Counties.id) \
                  .filter(Cases.community==Communities.id) \
                  .filter(Cases.container==Containers.id) \
                  .filter(Entities.case_id==Cases.id) \
                  .filter(Entities.role==Roles.id) 
                  
        # Do not count with query.count() because it is slow. It avgs 3s a lookup
        count = self.fast_count(query.with_entities(Cases.id)) #worst case is 2s
        

        # order, limit, offset
        query = query.order_by(order) # set the order
        allobjs = query.all() # ULTRA FAST
        
        print "QUERY TIME: " + str((time.time() - timer_start))
        print str(query)
                
        objs = allobjs[offset:(offset+limit)] # ULTRA FAST
        #objs = query.offset(offset).limit(limit).all() # offset and limit records for better lookup speed

        facets = []
        if offset == 0: # only rebuild facets on start of new search
            facets = self.fast_make_facets(allobjs) # must be done before offset and limit 

        results = {"recordsTotal": count,
                   "recordsFiltered": count,
                   "facets": facets,
                   "data": []
        }
        
        for obj in objs:
            results['data'].append(
                [obj.Entities.id,
                 obj.Entities.entity,
                 obj.Entities.firstname,
                 obj.Entities.middlename,
                 obj.Roles.role,
                 obj.Cases.year,
                 obj.Counties.county,
                 obj.Communities.community,
                 re.sub('\s+', ' ', obj.Cases.address.replace('\n',' ').replace('\r','')).strip(),                 
                 '', # image row, just ignore
                 {'_case': Result2Dict(obj.Cases),
                  '_entity':Result2Dict(obj.Entities),
                  #'_county': Result2Dict(obj.Counties),
                  #'_role': Result2Dict(obj.Roles),
                  #'_court': Result2Dict(obj.Courts),
                  #'_actiontype': Result2Dict(obj.ActionTypes),
                  #'_container': Result2Dict(obj.Containers),
                  #'_archive': Result2Dict(obj.Archives),
                  #'_other_entities':self.get_other_entities(obj.Entities),
                 }
                ]
            )
        
        return results
        
    
    def get_other_entities(self,entity):
        entities = Entities.loadAll(case_id=entity.case_id)
        return filter(lambda x: x['id'] != entity.id, Results2Dict(entities))


    def fast_make_facets(self, results):
        facets = []
        
        # ActionTypes Facets
        if Validators.bool( Config.get('enable_facet_casetypes', purify=True) ):
            actiontypes = ActionTypes.loadAll(order='actiontype asc');
            _types = {'name' : 'actiontypes' , 'clean_name': 'Case Types', 'data' :[]};
            for at in actiontypes:
                if at.actiontype != '':
                    _types['data'].append({'facet':at.actiontype, 'id': at.id, 'count': len(filter(lambda x: x.Cases.actiontype == at.id, results)) })
            facets.append(_types)
          
        # County Facets
        if Validators.bool( Config.get('enable_facet_counties', purify=True) ):
            counties = Counties.loadAll(order='county asc');
            _counties = {'name' : 'counties' , 'clean_name': 'Counties', 'data' :[]};
            for county in counties:
                if county.county != '':
                    _counties['data'].append({'facet':county.county, 'id': county.id, 'count':len(filter(lambda x: x.Cases.county == county.id, results)) })
            facets.append(_counties)
            
        # Community Facets
        if Validators.bool( Config.get('enable_facet_communities', purify=True) ):
            communities = Communities.loadAll(order='community asc');
            _communities = {'name' : 'communities' , 'clean_name': 'Communities', 'data' :[]};
            for community in communities:
                if community.community != '':
                    _communities['data'].append({'facet':community.community, 'id': community.id, 'count':len(filter(lambda x: x.Cases.community == community.id, results)) })
            facets.append(_communities)
          
        # Roles Facets
        if Validators.bool( Config.get('enable_facet_roles', purify=True) ):
            roles = Roles.loadAll(order='role asc');
            _roles = {'name' : 'roles' , 'clean_name': 'Roles', 'data' :[]};
            for role in roles:
                if role.role != '':
                    _roles['data'].append({'facet':role.role, 'id': role.id, 'count':len(filter(lambda x: x.Entities.role == role.id, results)) })
            facets.append(_roles)

        # Courts Facets
        if Validators.bool( Config.get('enable_facet_courts', purify=True) ):
            courts = Courts.loadAll(order='court asc');
            _court = {'name' : 'courts' , 'clean_name': 'Courts', 'data' :[]};
            for court in courts:
                if court.court != '':
                    _court['data'].append({'facet':court.court, 'id': court.id, 'count':len(filter(lambda x: x.Cases.court == court.id, results)) })
            facets.append(_court)
        
        # Archive Facets
        if Validators.bool( Config.get('enable_facet_archives', purify=True) ):
            archives = Archives.loadAll(order='name asc');
            _archives = {'name' : 'archives' , 'clean_name': 'Archives', 'data' :[]};
            for archive in archives:
                if archive.name != '':
                    _archives['data'].append({'facet':archive.name, 'id': archive.id, 'count':len(filter(lambda x: x.Cases.archive == archive.id, results)) })
            facets.append(_archives)

    
        return facets
    
    
    
    """ DO NOT USE, VERY SLOW """
    def make_facets(self,query):
        facets = []
        
        # ActionTypes Facets
        if Validators.bool( Config.get('enable_facet_casetypes', purify=True) ):
            actiontypes = ActionTypes.loadAll(order='actiontype asc');
            _types = {'name' : 'actiontypes' , 'clean_name': 'Case Types', 'data' :[]};
            for at in actiontypes:
                subquery = query.filter(Cases.actiontype==at.id)
                if at.actiontype != '':
                    _types['data'].append({'facet':at.actiontype, 'id': at.id, 'count':self.fast_count(subquery)})
            facets.append(_types)
        
        
        # County Facets
        if Validators.bool( Config.get('enable_facet_counties', purify=True) ):
            counties = Counties.loadAll(order='county asc');
            _counties = {'name' : 'counties' , 'clean_name': 'Counties', 'data' :[]};
            for county in counties:
                subquery = query.filter(Cases.county==county.id)
                if county.county != '':
                    _counties['data'].append({'facet':county.county, 'id': county.id, 'count':self.fast_count(subquery)})
            facets.append(_counties)
            
        # Community Facets
        if Validators.bool( Config.get('enable_facet_communities', purify=True) ):
            communities = Communities.loadAll(order='community asc');
            _communities = {'name' : 'communities' , 'clean_name': 'Communities', 'data' :[]};
            for community in communities:
                subquery = query.filter(Cases.community==community.id)
                if community.community != '':
                    _communities['data'].append({'facet':community.community, 'id': community.id, 'count':self.fast_count(subquery)})
            facets.append(_communities)
        
        # Roles Facets
        if Validators.bool( Config.get('enable_facet_roles', purify=True) ):
            roles = Roles.loadAll(order='role asc');
            _roles = {'name' : 'roles' , 'clean_name': 'Roles', 'data' :[]};
            for role in roles:
                subquery = query.filter(Entities.role==role.id)
                if role.role != '':
                    _roles['data'].append({'facet':role.role, 'id': role.id, 'count':self.fast_count(subquery)})
            facets.append(_roles)

        # Courts Facets
        if Validators.bool( Config.get('enable_facet_courts', purify=True) ):
            courts = Courts.loadAll(order='court asc');
            _court = {'name' : 'courts' , 'clean_name': 'Courts', 'data' :[]};
            for court in courts:
                subquery = query.filter(Cases.court==court.id)
                if court.court != '':
                    _court['data'].append({'facet':court.court, 'id': court.id, 'count':self.fast_count(subquery)})
            facets.append(_court)
        
        # Archive Facets
        if Validators.bool( Config.get('enable_facet_archives', purify=True) ):
            archives = Archives.loadAll(order='name asc');
            _archives = {'name' : 'archives' , 'clean_name': 'Archives', 'data' :[]};
            for archive in archives:
                subquery = query.filter(Cases.archive==archive.id)
                if archive.name != '':
                    _archives['data'].append({'facet':archive.name, 'id': archive.id, 'count':self.fast_count(subquery)})
            facets.append(_archives)

        return facets
        
        
        
        
    def fast_count(self,q):
        """ SQLAlchemy's query .count() is extremly slow, about 3-5 seconds.  This does the same thing under 1 second. """
        count_q = q.statement.with_only_columns([func.count()]).order_by(None)
        count = q.session.execute(count_q).scalar()
        return count 

        
    tstart = 0
    def print_start(self):
        self.tstart = time.time()
        
    def print_end(self):
        print str((time.time() - self.tstart)) + ' seconds'
        
        
        
        
        
        
        
        
        
        
        