from resuds.api import ResudsClient

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

    def call_function(self, name, *args):
        return getattr(self.client.service, name)(self.user, self.password, self.operator_id, *args)
