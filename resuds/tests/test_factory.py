import os
from unittest import TestCase
from httpretty import HTTPretty, httprettified
from suds.client import SoapClient
from resuds.tests import LOCALDIR
from resuds.api import ResudsClient
from resuds.factory import Factory, EntityIdList


class FactoryTestCase(TestCase):
    wsdl_file = 'file://' + os.path.join(LOCALDIR, 'inventory_service.wsdl')
    report_file = 'file://' + os.path.join(LOCALDIR, 'PublisherRevenueWS.wsdl')

    def testIsList(self):
        import collections
        self.assertTrue(self.factory.is_list(
            collections.namedtuple('MyList', [])()))
        self.assertFalse(self.factory.is_list(
            collections.namedtuple('Object', [])()))

    def testRebuildNoneObject(self):
        self.assertEquals('', self.factory.rebuild(None))

    def testRebuildPrimitiveType(self):
        self.assertEquals('12345', self.factory.rebuild(12345))

    def testRebuildDateTime(self):
        import datetime
        self.assertEquals('2013-02-22 00:00:00', self.factory.rebuild(
            datetime.datetime(2013, 02, 22)))

    def testBuildEmptyList(self):
        self.assertEquals([], self.factory.build(
            self.client.client.factory, []))

    def testBuildSimpleList(self):
        self.assertEquals([1, 4, 6, ], self.factory.build(
            self.client.client.factory, [1, 4, 6, ]))

    def testBuildComplicatedList(self):
        adspace = self.createAdspace()
        l = [adspace, ]
        self.assertEquals(
            '(AdspaceList){\n   Adspace[] = \n      (Adspace){\n         FormatResourceTypeList = \n            (FormatResourceTypeList){\n               FormatResourceType[] = \n                  (FormatResourceType){\n                     ResourceTypeIdList = \n                        (EntityIdList){\n                           EntityId[] = \n                              5,\n                              6,\n                        }\n                     _FormatId = 5\n                  },\n            }\n         CategoryIdList = \n            (EntityIdList){\n               EntityId[] = \n                  2345,\n                  65432,\n            }\n         ExcludedTopicIdList = \n            (EntityIdList){\n               EntityId = None\n            }\n         _Id = ""\n         _ExternalId = "externalId"\n         _Name = "adspaceName"\n         _Description = ""\n         _PublisherId = ""\n         _MediaChannelId = ""\n         _PlacementWidth = ""\n         _PlacementHeight = ""\n         _Active = ""\n         _LongTail = ""\n         _EstDailyUsers = "1"\n         _EstDailyImps = "1"\n         _AllowCompanionFlights = ""\n         _Test = "false"\n         _SupportConvTracking = "false"\n         _MinAllowedCPC = ""\n         _MinAllowedCPM = ""\n      },\n }',
            repr(self.factory.build(self.client.client.factory, l))
        )

    def testBuildSimpleObject(self):
        self.assertEquals('1', self.factory.build(
            self.client.client.factory, 1))

    def testBuildComplicatedObject(self):
        adspace = self.createAdspace()
        envelope = self.getEnvelope(adspace)
        self.assertEquals(
            '<?xml version="1.0" encoding="UTF-8"?>\n<SOAP-ENV:Envelope xmlns:ns0="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns1="http://Amobee.com/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">\n   <SOAP-ENV:Header/>\n   <ns0:Body>\n      <ns1:CreateAdspace>\n         <name>name</name>\n         <pwd>pwd</pwd>\n         <operatorId>opId</operatorId>\n         <Adspace ExternalId="externalId" Name="adspaceName" EstDailyUsers="1" EstDailyImps="1" Test="false" SupportConvTracking="false">\n            <FormatResourceTypeList>\n               <FormatResourceType FormatId="5">\n                  <ResourceTypeIdList>\n                     <EntityId>5</EntityId>\n                     <EntityId>6</EntityId>\n                  </ResourceTypeIdList>\n               </FormatResourceType>\n            </FormatResourceTypeList>\n            <CategoryIdList>\n               <EntityId>2345</EntityId>\n               <EntityId>65432</EntityId>\n            </CategoryIdList>\n         </Adspace>\n      </ns1:CreateAdspace>\n   </ns0:Body>\n</SOAP-ENV:Envelope>',
            envelope
        )

    def testCreateAdspaceSoapObject(self):
        self.setupDefaultSchemas()
        adspace = self.createAdspace()
        self.assertEquals(adspace.cls_name, 'Adspace')
        envelope = self.getEnvelope(adspace)
        self.assertEquals(
            '<?xml version="1.0" encoding="UTF-8"?>\n<SOAP-ENV:Envelope xmlns:ns0="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns1="http://Amobee.com/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">\n   <SOAP-ENV:Header/>\n   <ns0:Body>\n      <ns1:CreateAdspace>\n         <name>name</name>\n         <pwd>pwd</pwd>\n         <operatorId>opId</operatorId>\n         <Adspace ExternalId="externalId" Name="adspaceName" EstDailyUsers="1" EstDailyImps="1" Test="false" SupportConvTracking="false">\n            <FormatResourceTypeList>\n               <FormatResourceType FormatId="5">\n                  <ResourceTypeIdList>\n                     <EntityId>5</EntityId>\n                     <EntityId>6</EntityId>\n                  </ResourceTypeIdList>\n               </FormatResourceType>\n            </FormatResourceTypeList>\n            <CategoryIdList>\n               <EntityId>2345</EntityId>\n               <EntityId>65432</EntityId>\n            </CategoryIdList>\n         </Adspace>\n      </ns1:CreateAdspace>\n   </ns0:Body>\n</SOAP-ENV:Envelope>',
            envelope
        )

    def testGetUnexistentProperty(self):
        adspace = self.createAdspace()
        self.assertRaises(AttributeError, getattr, adspace, 'dummy')

    def testSetUnexistentProperty(self):
        adspace = self.createAdspace()
        self.assertRaises(
            AttributeError, setattr, adspace, 'dummy', 'dummyvalue')

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
            [5, 6, ], adspace.formatresourcetypelist[
                0].resourcetypeidlist.entityid
        )

    def testEntityIdList(self):
        adspace = self.client.create('Adspace')
        adspace.categoryidlist.entityid = [1, 2, 3, 4, ]
        envelope = self.getEnvelope(adspace)
        self.assertTrue('<CategoryIdList>' in envelope)
        self.assertTrue('<EntityId>1</EntityId>' in envelope)
        self.assertTrue('<EntityId>2</EntityId>' in envelope)
        self.assertTrue('<EntityId>3</EntityId>' in envelope)
        self.assertTrue('<EntityId>4</EntityId>' in envelope)
        self.assertTrue('</CategoryIdList>' in envelope)

    @httprettified
    def testCreateObjectWithoutOptionalParameters(self):
        self.setupDefaultSchemas()
        client = ResudsClient(FactoryTestCase.report_file, faults=False)

        criteria = client.create('PublisherRevenueCriteria')
        criteria.startdate = '2013-05-03+00:00'
        criteria.enddate = '2013-06-03+00:00'
        criteria.publisherid = 50214056
        envelope = self.getEnvelope(
            criteria, method='GetPublisherRevenueCSV', client=client)
        self.assertTrue('<criteria>' in envelope and '</criteria>' in envelope)
        self.assertTrue('<publisherId>50214056</publisherId>' in envelope)
        self.assertTrue('<startDate>2013-05-03+00:00</startDate>' in envelope)
        self.assertTrue('<endDate>2013-06-03+00:00</endDate>' in envelope)
        self.assertTrue('<endDate>2013-06-03+00:00</endDate>' in envelope)
        self.assertTrue('<adspaceId>' not in envelope)

    def testEntityIsListToString(self):
        entityIdList = EntityIdList(['value1', 'value2'])
        self.assertEquals(
            '<EntityId>value1</EntityId><EntityId>value2</EntityId>', str(entityIdList))

    @httprettified
    def setUp(self):
        self.setupDefaultSchemas()
        self.client = ResudsClient(FactoryTestCase.wsdl_file, faults=False)
        self.factory = Factory

    def getEnvelope(self, obj, method='CreateAdspace', client=None):
        if not client:
            client = self.client
        soapObject = Factory.build(client.client.factory, obj)
        method = getattr(client.client.service, method)
        c = SoapClient(method.client, method.method)
        return str(c.method.binding.input.get_message(c.method, ('name', 'pwd', 'opId', soapObject, ), {}))

    def setupDefaultSchemas(self):
        with open(os.path.join(LOCALDIR, 'XMLSchema.xsd')) as fp:
            body = fp.read()
        HTTPretty.register_uri(
            HTTPretty.GET, 'http://www.w3.org/2001/XMLSchema.xsd', body=body)

        with open(os.path.join(LOCALDIR, 'xml.xsd')) as fp:
            body = fp.read()
        HTTPretty.register_uri(
            HTTPretty.GET, 'http://www.w3.org/2001/xml.xsd', body=body)

    def createAdspace(self):
        adspace = self.client.create('Adspace')
        adspace.name = 'adspaceName'
        adspace.externalid = 'externalId'
        frt = self.client.create('FormatResourceType')
        frt.formatid = 5
        rtil = self.client.create('ResourceTypeIdList')
        rtil.entityid = [5, 6, ]
        frt.resourcetypeidlist = rtil
        adspace.formatresourcetypelist = [frt, ]
        cil = self.client.create('CategoryIdList')
        cil.entityid = [2345, 65432]
        adspace.categoryidlist = cil
        return adspace
