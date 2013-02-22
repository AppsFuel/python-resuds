import os
from unittest import TestCase
from httpretty import HTTPretty, httprettified
from suds.client import RequestContext
from resuds.api import ResudsClient, SoapException
from resuds.tests import LOCALDIR


class ResudsClientTestCase(TestCase):
    wsdl_file = 'file://' + os.path.join(LOCALDIR, 'inventory.wsdl')

    @httprettified
    def setUp(self):
        self.setupDefaultSchemas()
        self.client = ResudsClient(ResudsClientTestCase.wsdl_file, faults=False)

    def testGetMethods(self):
        self.assertEquals(
            self.client.methods,
            {
                'SearchCategoryByCriteria': [('name', 'string'), ('pwd', 'string'), ('operatorId', 'int'), ('categoryCriteria', 'categoryCriteria')],
                'SearchAdspaceByCriteria': [('name', 'string'), ('pwd', 'string'), ('operatorId', 'int'), ('adspaceCriteria', 'adspaceCriteria')],
                'GetCategoryList': [('name', 'string'), ('pwd', 'string'), ('operatorId', 'int')],
                'UpdateAdspace': [('name', 'string'), ('pwd', 'string'), ('operatorId', 'int'), ('Adspace', 'Adspace')],
                'CreateAdspace': [('name', 'string'), ('pwd', 'string'), ('operatorId', 'int'), ('Adspace', 'Adspace')],
                'UpdateCategory': [('name', 'string'), ('pwd', 'string'), ('operatorId', 'int'), ('Category', 'Category')],
                'GetAdSpaceList': [('name', 'string'), ('pwd', 'string'), ('operatorId', 'int')],
                'DeleteCategory': [('name', 'string'), ('pwd', 'string'), ('operatorId', 'int'), ('categoryId', 'int')],
                'GetContextualCategoryList': [('name', 'string'), ('pwd', 'string'), ('operatorId', 'int')],
                'GetAdSpaceByExternalId': [('name', 'string'), ('pwd', 'string'), ('operatorId', 'int'), ('externalId', 'string')],
                'GetCategoryGroupList': [('name', 'string'), ('pwd', 'string'), ('operatorId', 'int')],
                'GetCategoryById': [('name', 'string'), ('pwd', 'string'), ('operatorId', 'int'), ('categoryId', 'int')],
                'DeleteAdSpace': [('name', 'string'), ('pwd', 'string'), ('operatorId', 'int'), ('adSpaceId', 'int')],
                'GetAdSpaceById': [('name', 'string'), ('pwd', 'string'), ('operatorId', 'int'), ('adSpaceId', 'int')],
                'CreateCategory': [('name', 'string'), ('pwd', 'string'), ('operatorId', 'int'), ('Category', 'Category')],
                'GetAdSpaceSalesHouses': [('name', 'string'), ('pwd', 'string'), ('operatorId', 'int'), ('adSpaceId', 'int')]
            }
        )

    def testUnexistentMethod(self):
        self.assertRaises(NotImplementedError, getattr, self.client, 'unexistentMethod')

    @httprettified
    def testNoSendRequest(self):
        self.setupDefaultSchemas()
        client = ResudsClient(ResudsClientTestCase.wsdl_file, nosend=True)
        res = client.GetAdSpaceList(name='', pwd='', operatorId='')
        self.assertEquals(res.__class__, RequestContext)

    @httprettified
    def testFaultRequest(self):
        self.setupHttpPretty('GetAdSpaceById')
        client = ResudsClient(ResudsClientTestCase.wsdl_file, faults=True)
        adspace_id = 32645
        res = client.GetAdSpaceById(name='', pwd='', operatorId='', adSpaceId=adspace_id)
        self.assertEquals(res.cls_name, 'Adspace')

    @httprettified
    def testWebFaultExceptionOnHttpError(self):
        self.setupHttpPretty('InvalidGetAdSpaceById', status_code=500)
        client = ResudsClient(ResudsClientTestCase.wsdl_file, faults=False)
        adspace_id = 1234567890
        self.assertRaises(SoapException, client.GetAdSpaceById, name='', pwd='', operatorId='', adSpaceId=adspace_id)

    @httprettified
    def testGetObjectList(self):
        self.setupHttpPretty('GetAdSpaceList')
        adspacelist = self.client.GetAdSpaceList(name='', pwd='', operatorId='')
        self.assertEquals(len(adspacelist), 3)
        self.assertEquals([adspace.cls_name for adspace in adspacelist], ['Adspace', ] * len(adspacelist))

    @httprettified
    def testGetObject(self):
        self.setupHttpPretty('GetAdSpaceById')
        adspace_id = 32645
        adspace = self.client.GetAdSpaceById(name='', pwd='', operatorId='', adSpaceId=adspace_id)
        self.assertEquals(adspace.id, adspace_id)

    @httprettified
    def testCreateAdspace(self):
        self.setupHttpPretty('CreateAdspace')

        adspace = self.client.create('Adspace')
        frt = self.client.create('FormatResourceType', formatid=5, resourcetypeidlist=[5, 6, ])
        frtl = [frt, ]
        adspace.formatresourcetypelist = frtl
        adspace.name = 'adspaceName'
        adspace.longtail = 1

        res = self.client.CreateAdspace(name='', pwd='', operatorId='', Adspace=adspace)
        self.assertTrue(res.isdigit())

    @httprettified
    def testNoneTypeObjectInRebuild(self):
        self.setupHttpPretty('deleteAdspace')
        self.client.DeleteAdSpace(name='', pwd='', operatorId='', adSpaceId=123456)

    @httprettified
    def testComplicateCase(self):
        self.setupDefaultSchemas()
        with open(os.path.join(LOCALDIR, 'getReport.wsdl')) as fp:
            body = fp.read()
        HTTPretty.register_uri(
            HTTPretty.POST,
            'http://localhost/publisher',
            body=body,
            status=200,
        )
        client = ResudsClient('file://' + os.path.join(LOCALDIR, 'PublisherRevenueWS.wsdl'), faults=False)
        criteria = client.create('PublisherRevenueCriteria')
        criteria.publisherid = 1234
        criteria.adspaceid = 1234
        criteria.startdate = 12345
        criteria.enddate = 12345
        rev = client.GetPublisherRevenueCSV(name='', pwd='', operatorId='', criteria=criteria)

    @httprettified
    def testObjectListWithObjectAsChild(self):
        self.setupDefaultSchemas()
        with open(os.path.join(LOCALDIR, 'getFlightList.wsdl')) as fp:
            body = fp.read()
        HTTPretty.register_uri(
            HTTPretty.POST,
            'http://localhost/campaign',
            body=body,
            status=200,
        )
        client = ResudsClient('file://' + os.path.join(LOCALDIR, 'CampaignWS.wsdl'))
        l = client.GetFlightList(name='', pwd='', operatorId='')

    @httprettified
    def testResponseErrorOnCreate(self):
        self.setupHttpPretty('responseError', status_code=500)
        client = ResudsClient(ResudsClientTestCase.wsdl_file, faults=True)
        adspace = client.create('Adspace')
        adspace.externalid = '1' * 200
        adspace.name = 'adspaceName'
        adspace.longtail = True
        adspace.mediachannelid = 2
        adspace.publisherid = ''
        frt = self.client.create('FormatResourceType')
        frt.formatid = 300
        adspace.formatresourcetypelist = [frt, ]

        try:
            res = self.client.CreateAdspace(name='', pwd='', operatorId='', Adspace=adspace)
            self.fail('Expect failing on create a adspace with too long externalid')
        except SoapException, e:
            self.assertEquals(e.message, u'EXTERNAL_ID_TOO_LONG [50]')

    def setupHttpPretty(self, name, method=HTTPretty.POST, status_code=200):
        self.setupDefaultSchemas()
        with open(os.path.join(LOCALDIR, name + '.wsdl')) as fp:
            body = fp.read()
        HTTPretty.register_uri(
            method,
            'http://localhost/invetory',
            body=body,
            status=status_code,
        )

    def setupDefaultSchemas(self):
        with open(os.path.join(LOCALDIR, 'XMLSchema.xsd')) as fp:
            body = fp.read()
        HTTPretty.register_uri(HTTPretty.GET, 'http://www.w3.org/2001/XMLSchema.xsd', body=body)

        with open(os.path.join(LOCALDIR, 'xml.xsd')) as fp:
            body = fp.read()
        HTTPretty.register_uri(HTTPretty.GET, 'http://www.w3.org/2001/xml.xsd', body=body)
