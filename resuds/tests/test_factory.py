import os
from unittest import TestCase
from httpretty import HTTPretty, httprettified
from resuds.tests import LOCALDIR
from resuds.api import ResudsClient
from resuds.factory import Factory


class FactoryTestCase(TestCase):
    wsdl_file = 'file://' + os.path.join(LOCALDIR, 'inventory.wsdl')

    def testIsList(self):
        import collections
        self.assertTrue(self.factory.is_list(collections.namedtuple('MyList', [])()))
        self.assertFalse(self.factory.is_list(collections.namedtuple('Object', [])()))

    def testRebuildNoneObject(self):
        self.assertEquals('', self.factory.rebuild(None))

    def testRebuildPrimitiveType(self):
        self.assertEquals('12345', self.factory.rebuild(12345))

    def testRebuildDateTime(self):
        import datetime
        self.assertEquals('2013-02-22 00:00:00', self.factory.rebuild(datetime.datetime(2013, 02, 22)))

    def testBuildEmptyList(self):
        self.assertEquals([], self.factory.build(self.client.client.factory, []))

    def testBuildSimpleList(self):
        self.assertEquals([1, 4, 6, ], self.factory.build(self.client.client.factory, [1, 4, 6, ]))

    def testBuildComplicatedList(self):
        adspace = self.createAdspace()
        l = [adspace, ]
        self.assertEquals(
            '(AdspaceList){\n   Adspace[] = \n      (Adspace){\n         FormatResourceTypeList = \n            (FormatResourceTypeList){\n               FormatResourceType[] = \n                  (FormatResourceType){\n                     ResourceTypeIdList[] = \n                        5,\n                        6,\n                     _FormatId = 5\n                  },\n            }\n         CategoryIdList[] = <empty>\n         ExcludedTopicIdList[] = <empty>\n         _Id = ""\n         _ExternalId = "externalId"\n         _Name = "adspaceName"\n         _Description = ""\n         _PublisherId = ""\n         _MediaChannelId = ""\n         _PlacementWidth = ""\n         _PlacementHeight = ""\n         _Active = ""\n         _LongTail = ""\n         _EstDailyUsers = "1"\n         _EstDailyImps = "1"\n         _AllowCompanionFlights = ""\n         _Test = "false"\n         _SupportConvTracking = "false"\n         _MinAllowedCPC = ""\n         _MinAllowedCPM = ""\n      },\n }',
            repr(self.factory.build(self.client.client.factory, l))
        )

    def testBuildSimpleObject(self):
        self.assertEquals('1', self.factory.build(self.client.client.factory, 1))

    def testBuildComplicatedObject(self):
        adspace = self.createAdspace()
        self.assertEquals(
            '(Adspace){\n   FormatResourceTypeList = \n      (FormatResourceTypeList){\n         FormatResourceType[] = \n            (FormatResourceType){\n               ResourceTypeIdList[] = \n                  5,\n                  6,\n               _FormatId = 5\n            },\n      }\n   CategoryIdList[] = <empty>\n   ExcludedTopicIdList[] = <empty>\n   _Id = ""\n   _ExternalId = "externalId"\n   _Name = "adspaceName"\n   _Description = ""\n   _PublisherId = ""\n   _MediaChannelId = ""\n   _PlacementWidth = ""\n   _PlacementHeight = ""\n   _Active = ""\n   _LongTail = ""\n   _EstDailyUsers = "1"\n   _EstDailyImps = "1"\n   _AllowCompanionFlights = ""\n   _Test = "false"\n   _SupportConvTracking = "false"\n   _MinAllowedCPC = ""\n   _MinAllowedCPM = ""\n }',
            repr(self.factory.build(self.client.client.factory, adspace))
        )

    def testCreateAdspaceSoapObject(self):
        self.setupDefaultSchemas()
        adspace = self.createAdspace()
        self.assertEquals(adspace.cls_name, 'Adspace')
        self.assertEquals(
            "Adspace({'estdailyusers': 1, 'minallowedcpm': '', 'description': '', 'placementheight': '', 'allowcompanionflights': '', 'placementwidth': '', 'mediachannelid': '', 'longtail': '', 'estdailyimps': 1, 'test': false, 'externalid': 'externalId', 'active': '', 'supportconvtracking': false, 'publisherid': '', 'id': '', 'minallowedcpc': '', 'name': 'adspaceName'}, {'excludedtopicidlist': [], 'formatresourcetypelist': [FormatResourceType({'formatid': 5}, {'resourcetypeidlist': [5, 6]})], 'categoryidlist': []})",
            repr(adspace)
        )

    def testGetUnexistentProperty(self):
        adspace = self.createAdspace()
        self.assertRaises(AttributeError, getattr, adspace, 'dummy')

    def testSetUnexistentProperty(self):
        adspace = self.createAdspace()
        self.assertRaises(AttributeError, setattr, adspace, 'dummy', 'dummyvalue')

    def testChangeObjectProperty(self):
        adspace = self.createAdspace()
        adspace.name = 'NewName'
        self.assertEquals('NewName', adspace.name)

    def testAddListToObject(self):
        adspace = self.createAdspace()
        self.assertEquals(
            5, adspace.formatresourcetypelist[0].formatid
        )
        self.assertEquals(
            [5, 6, ], adspace.formatresourcetypelist[0].resourcetypeidlist
        )

    @httprettified
    def setUp(self):
        self.setupDefaultSchemas()
        self.client = ResudsClient(FactoryTestCase.wsdl_file, faults=False)
        self.factory = Factory

    def setupDefaultSchemas(self):
        with open(os.path.join(LOCALDIR, 'XMLSchema.xsd')) as fp:
            body = fp.read()
        HTTPretty.register_uri(HTTPretty.GET, 'http://www.w3.org/2001/XMLSchema.xsd', body=body)

        with open(os.path.join(LOCALDIR, 'xml.xsd')) as fp:
            body = fp.read()
        HTTPretty.register_uri(HTTPretty.GET, 'http://www.w3.org/2001/xml.xsd', body=body)

    def createAdspace(self):
        adspace = self.client.create('Adspace')
        adspace.name = 'adspaceName'
        adspace.externalid = 'externalId'
        frt = self.client.create('FormatResourceType', formatid=5, resourcetypeidlist=[5, 6, ])
        frtl = [frt, ]
        adspace.formatresourcetypelist = frtl
        return adspace
