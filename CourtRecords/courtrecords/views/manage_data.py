
from courtrecords.security.acl import ACL
from courtrecords.models import DBSession,Users, Invoices
from courtrecords.utilities.validators import Validators
from courtrecords.views import BaseView
from pyramid.view import view_config

def Import(module_name,class_name):
    """ Dynamic Import to protect against Circular Import Errors """
    mod = __import__(module_name, fromlist=[class_name])
    return getattr(mod, class_name)

class ManageData(BaseView):

    def _element_generator(self, scaffold, object):
        html = []
        for s in scaffold:
            for k,v in s.items():
                html.append( self._create_form_label(k, v['label']) ) # LABEL
                
                options = {}
                if 'options' in v:
                    options = v['options']
                    
                option_type = ''
                if 'option_type' in v:
                    option_type = v['option_type']
                    
                attributes = {}
                if 'attributes' in v:
                    attributes = v['attributes']


                    
                html.append( self._create_form_element(v['widget'], attributes, options, option_type, k, getattr(object, k)) ) # FORM ELEMENT
        return html
        
    def _create_form_element(self, element, attributes, options, option_type, name, content):
        if name == 'id' and content == None:
            content = 'To be determined'
            
        html = '<' + element + ' id="form-' + name + '"'
        for k,v in attributes.items():
            html += ' ' + k + '="' + v + '"'
        html += ' name="form.' + name + '"'
        
        if element == 'input':
            html += 'value="' + str(content) + '" />'  #close input and add value
        elif element == 'select':
            html += '>'
            for k,v in options.items():
                html += '<option value="' + str(v) + '"'
                
                if option_type == 'bool':
                    if Validators.bool(v) == content:
                        html += ' selected="true" '
                if option_type == 'int':
                    if int(v) == content:
                        html += ' selected="true" '
                if option_type == 'str':
                    if str(v) == content:
                        html += ' selected="true" '
                    
                html += '>' + k + '</option>'
            html += '</' + element + '>'
        else:
            html += '>' + str(content) + '</' + element + '>'
        return html
        
    def _create_form_label(self, name, label):
        return '<label for="form-' + name + '">' + label + '</label>'
