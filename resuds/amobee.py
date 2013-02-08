from suds.client import RequestContext, WebFault
from resuds.api import ResudsClient, ElementFactory

__all__ = (
    'AmobeeClient',
)


class AmobeeClient(ResudsClient):
    def __init__(self, wsdl_uri, user, password, operator_id, **options):
        super(AmobeeClient, self).__init__(wsdl_uri, **options)
        self.set_credential(user, password, operator_id)

    def set_credential(self, user, password, operator_id):
        self.user = user
        self.password = password
        self.operator_id = operator_id

    def import_methods(self):
        self.methods = {}
        for el in self.client.sd[0].ports[0][1]:
            self.methods[str(el[0])] = [(str(t[0]), str(t[1].type[0])) for t in el[1][3:]]

    def create_function(self, method, name):
        def func(**kwargs):
            args = self.create_args(method, kwargs)
            res = getattr(self.client.service, name)(self.user, self.password, self.operator_id, *args)
            if isinstance(res, RequestContext):
                return res
            elif res.__class__ is not tuple:
                return ElementFactory.rebuild(res)
            code, soap = res
            if code / 100 != 2:
                raise WebFault(code, soap)
            return ElementFactory.rebuild(soap)
        func.__name__ = name
        return func
