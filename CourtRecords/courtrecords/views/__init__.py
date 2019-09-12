

class BaseView(object):

    def __init__(self, request):
        self.request = request
        self.context = getattr(request, 'context', None)
        self.response = {}
        

    def notify(self, message, level=0):
        self.request.session.flash({'text': message, 'cls':'message-level-' + str(level)})
        
    def settings(self,name,default=None):
        try:
            return self.request.registry.settings[name]
        except:
            return default

    def set(self, name, value, default=None):
        try:
            self.response[name] = value
        except:
            self.response[name] = default
        
    def get(self, name):
        return self.response[name];
