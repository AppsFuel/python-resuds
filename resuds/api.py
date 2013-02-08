import datetime
from suds.client import Client, RequestContext, WebFault
from suds.sax.text import Text as SoapText

__all__ = (
    'ResudsClient',
)


class ResudsClient(object):
    def __init__(self, wsdl_uri, **options):
        self.client = Client(wsdl_uri, **options)
        self.import_methods()

    def import_methods(self):
        self.methods = {}
        for el in self.client.sd[0].ports[0][1]:
            self.methods[str(el[0])] = [(str(t[0]), str(t[1].type[0])) for t in el[1]]

    def create(self, soap_object_name, **kwargs):
        soapObject = ElementFactory.rebuild(self.client.factory.create(soap_object_name))
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
                args.append(ElementFactory.build(self.client.factory, kwargs[param_name]))
            else:
                args.append(kwargs[param_name])
        return args

    def create_function(self, method, name):
        def func(**kwargs):
            args = self.create_args(method, kwargs)
            res = getattr(self.client.service, name)(*args)
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


class SoapObject(object):
    def __init__(self, name, attribute_keys, children_keys):
        self.cls_name = name
        self.attribute_keys = attribute_keys
        self.children_keys = children_keys
        self.attrs = dict((ElementFactory.clean(attr), '') for attr in attribute_keys)
        self.children = dict((ElementFactory.clean(child), None) for child in children_keys)

    def __setattr__(self, k, v):
        if k in ('cls_name', 'attribute_keys', 'children_keys', 'attrs', 'children'):
            super(SoapObject, self).__setattr__(k, v)
        elif k in self.attrs:
            self.attrs[k] = v
        elif k in self.children:
                self.children[k] = v
        else:
            raise AttributeError(self.cls_name, k)

    def __getattr__(self, k):
        if k in self.attrs:
            return self.attrs[k]
        elif k in self.children:
            return self.children[k]
        else:
            raise AttributeError(self.cls_name, k)

    def __repr__(self):
        return self.cls_name + '(' + repr(self.attrs) + ', ' + repr(self.children) + ')'


class ElementFactory(object):
    @classmethod
    def rebuild(cls, obj):
        if not obj:
            return ''
        if isinstance(obj, (int, float, str)):
            return str(obj)
        if cls.is_list(obj):
            return [ElementFactory.rebuild(o) for o in obj[0]]

        attrs = [attr for attr in obj.__keylist__ if attr.startswith('_')]
        children = [child for child in obj.__keylist__ if not child.startswith('_')]
        soapObject = SoapObject(obj.__class__.__name__, attrs, children)
        for attr in attrs:
            setattr(soapObject, ElementFactory.clean(attr), getattr(obj, attr))

        for child in children:
            el = getattr(obj, child)
            if el.__class__.__name__ == 'NoneType':
                continue
            elif isinstance(el, SoapText):
                setattr(soapObject, ElementFactory.clean(child), str(el))
                continue
            elif el.__class__.__name__ == 'EntityIdList':
                setattr(soapObject, ElementFactory.clean(child), *[e[1] for e in el])
                continue
            elif isinstance(el, datetime.datetime):
                setattr(soapObject, ElementFactory.clean(child), el)
                continue

            el_attrs = [el_attr for el_attr in el.__keylist__ if el_attr.startswith('_')]
            el_children = [el_child for el_child in el.__keylist__ if not el_child.startswith('_')]

            l = []
            for child_el in el[0]:
                l.append(ElementFactory.rebuild(child_el))

            setattr(soapObject, ElementFactory.clean(child), l)

        return soapObject

    @staticmethod
    def is_list(obj):
        return 'List' in obj.__class__.__name__

    @staticmethod
    def clean(name):
        if name.startswith('_'):
            return name[1:].lower()
        else:
            return name.lower()

    @classmethod
    def build(cls, factory, obj):
        if isinstance(obj, (tuple, list)):
            return cls.create_list(factory, obj)
        else:
            return cls.create_object(factory, obj)

    @classmethod
    def create_object(cls, factory, obj):
        if isinstance(obj, (int, float, str)):
            return str(obj)
        soap = factory.create(obj.cls_name)
        for key in obj.attribute_keys:
            setattr(soap, key, getattr(obj, cls.clean(key)))
        for key in obj.children_keys:
            setattr(soap, key, cls.build(factory, getattr(obj, cls.clean(key))))
        return soap

    @classmethod
    def create_list(cls, factory, l):
        soaptypes = filter(lambda x: isinstance(x, SoapObject), l)
        if len(l) == 0 or len(soaptypes) == 0:
            return l
        else:
            element_class_name = l[0].cls_name
            obj_list = factory.create(element_class_name + 'List')
            setattr(obj_list, element_class_name, [cls.build(factory, el) for el in l])
            return obj_list
