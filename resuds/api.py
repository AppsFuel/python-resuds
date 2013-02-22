import datetime
from suds.client import Client, RequestContext, WebFault
from resuds.cache import FolderCache
from resuds.factory import Factory, SoapObject

__all__ = (
    'ResudsClient',
    'SoapException',
    'FolderCache',
)


class SoapException(Exception):
    def __init__(self, fault):
        desc = fault.cms_error.errordescription if hasattr(fault.cms_error, 'errordescription') else ''
        super(Exception, self).__init__(desc)
        self.fault = fault


class ResudsClient(object):
    def __init__(self, wsdl_uri, **options):
        self.client = Client(wsdl_uri, **options)
        self.import_methods()

    def import_methods(self):
        self.methods = {}
        for el in self.client.sd[0].ports[0][1]:
            self.methods[str(el[0])] = [(str(t[0]), str(t[1].type[0])) for t in el[1]]

    def create(self, soap_object_name, **kwargs):
        soapObject = Factory.rebuild(self.client.factory.create(soap_object_name))
        for k, v in kwargs.iteritems():
            setattr(soapObject, k, v)
        return soapObject

    def __getattr__(self, name):
        try:
            method = self.methods[name]
        except KeyError:
            raise NotImplementedError(name)
        return self.create_function(method, name)

    def create_args(self, method, kwargs):
        args = []
        for param_name, t in method:
            if isinstance(kwargs[param_name], SoapObject):
                args.append(Factory.build(self.client.factory, kwargs[param_name]))
            else:
                args.append(kwargs[param_name])
        return args

    def create_function(self, method, name):
        def func(**kwargs):
            try:
                args = self.create_args(method, kwargs)
                res = self.call_function(name, *args)
                print 'res', res
                if isinstance(res, RequestContext):
                    return res
                elif res.__class__ is not tuple:
                    return Factory.rebuild(res)
                code, soap = res
                if code / 100 != 2:
                    raise WebFault(soap, code)
                return Factory.rebuild(soap)
            except WebFault, e:
                print 'e', e
                obj = Factory.rebuild(e.fault)
                raise SoapException(obj)
        func.__name__ = name
        return func

    def call_function(self, name, *args):
        return getattr(self.client.service, name)(*args)
