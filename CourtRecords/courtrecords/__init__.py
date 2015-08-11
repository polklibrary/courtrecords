
from courtrecords.security.core import RequestExtension,RootACL,groupfinder
from courtrecords.models import DBSession
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from sqlalchemy import engine_from_config,exc
import warnings

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    warnings.filterwarnings('ignore', '.*use_labels*.', category=exc.SAWarning)
    
    session_factory = UnencryptedCookieSessionFactoryConfig('changelater')
    authorization_policy = ACLAuthorizationPolicy()
    authentication_policy = AuthTktAuthenticationPolicy('894983832', callback=groupfinder)
    config = Configurator(settings=settings,
                          authentication_policy=authentication_policy,
                          authorization_policy=authorization_policy,
                          request_factory=RequestExtension,
                          root_factory=RootACL,
                          session_factory=session_factory
    )
    
    config.add_static_view('themes', 'courtrecords:themes', cache_max_age=3600)
    
    # Public Stuff
    config.add_route('home', '/')
    config.add_route('about', '/about')
    config.add_route('contact', '/contact')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('register', '/register')
    config.add_route('search', '/search')
    config.add_route('get_results', '/search/get')
    config.add_route('basket', '/basket')
    config.add_route('invoice', '/invoice/{hash}')
    config.add_route('record', '/record/{id}')
    
    # Management Stuff
    config.add_route('manage', '/manage')
    config.add_route('manage_users', '/manage/users')
    config.add_route('manage_orders', '/manage/orders')
    config.add_route('manage_order', '/manage/orders/{id}')
    config.add_route('manage_list_data', '/manage/data/{table}')
    config.add_route('manage_getlist_data', '/manage/data/{table}/list')
    config.add_route('manage_add_data', '/manage/data/{table}/add')
    config.add_route('manage_edit_data', '/manage/data/{table}/edit/{id}')
    config.add_route('manage_delete_data', '/manage/data/{table}/delete/{id}')
    config.add_route('manage_entities', '/manage/entities')
    config.add_route('manage_entities_get', '/manage/entities/get')
    config.add_route('manage_cases', '/manage/cases')
    config.add_route('manage_cases_get', '/manage/cases/get')
    config.add_route('manage_records_next', '/manage/records/next')
    config.add_route('manage_records_previous', '/manage/records/previous')
    config.add_route('manage_records', '/manage/records/{case_id}')
    config.add_route('manage_importer', '/manage/importer')
    config.add_route('manage_search', '/manage/search')
    config.add_route('manage_search_quick', '/manage/search/quick')
    config.add_route('manage_utilities', '/manage/utilities')
    
    # System Stuff
    config.add_route('cronjob_anonymize', '/cronjob/anonymize')
    
    # Basic Authentication Tests
    config.add_route('test_anon', '/test/anonymous')
    config.add_route('test_auth', '/test/authenticated')
    config.add_route('test_edit', '/test/editor')
    config.add_route('test_admin', '/test/administrator')
    
    
    config.include('pyramid_mailer') 
    config.scan()
    return config.make_wsgi_app()

