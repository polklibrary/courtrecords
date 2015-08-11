from pyramid.httpexceptions import HTTPForbidden

def protected(permissions):
    def wrap_func(fn):
        def wrap_func_args(context,*args):
            request = None
            try:
                request = context.request
            except:
                for arg in args:
                    if arg.__class__.__name__ == 'RequestExtension':
                        """ Object introspection above """
                        request = arg
                        
            if request == None:
                raise Exception('No request reference found')
            
            if request.user.group not in permissions:
                raise HTTPForbidden()
            
            return fn(context,*args)
        return wrap_func_args
    return wrap_func
    

