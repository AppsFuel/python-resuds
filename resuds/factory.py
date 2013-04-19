from suds import WebFault
from suds.sudsobject import Object

__all__ = (
    'SoapObject',
    'Factory',
)


class SoapObject(object):

    def __init__(self, name, attribute_keys, children_keys):
        self.cls_name = name
        self.attribute_keys = attribute_keys
        self.children_keys = children_keys
        self.attrs = dict((Factory.clean(attr), '') for attr in attribute_keys)
        self.children = dict((Factory.clean(child), None) for child in children_keys)

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


class EntityIdList(Object):

    def __init__(self, ids):
        Object.__init__(self)
        self.EntityId = ids

    def __unicode__(self):
        return ''.join('<EntityId>{0}</EntityId>'.format(i) for i in self.EntityId)


class Factory(object):

    @classmethod
    def rebuild(cls, obj):
        if not obj:
            return ''
        if not hasattr(obj, '__keylist__'):
            return str(obj)

        attrs = [attr for attr in obj.__keylist__ if attr.startswith('_')]
        children = [child for child in obj.__keylist__ if not child.startswith('_')]
        if cls.is_list(obj):
            if set(children) == set(['EntityId']):
                return SoapObject('EntityIdList', [], ['entityid'])
            return [Factory.rebuild(o) for o in obj[0]]

        soapObject = SoapObject(obj.__class__.__name__, attrs, children)
        for attr in attrs:
            setattr(soapObject, Factory.clean(attr), getattr(obj, attr))

        for child in children:
            el = getattr(obj, child)
            e = Factory.rebuild(el)
            setattr(soapObject, Factory.clean(child), e)

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
        if not hasattr(obj, 'cls_name'):
            return str(obj)
        if (obj.cls_name == 'EntityIdList'):
            return EntityIdList(obj.children['entityid'])
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
