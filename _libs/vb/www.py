import cherrypy, urllib.parse
from alt.dict_ import dict_

def form_params(kwargs, default=None):

    params = dict_()
    for key, value in kwargs.items():
        if value!='':
            params[key] = value

    if (cherrypy.request.method=='POST' and params) or not kwargs:
        if not kwargs:
            params = default
        cgi = urllib.parse.urlencode(params)
        raise cherrypy.HTTPRedirect(cherrypy.url() + '?' + cgi)

    return params
