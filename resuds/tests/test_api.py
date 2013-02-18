import os
from unittest import TestCase
from httpretty import HTTPretty, httprettified
from suds.client import RequestContext, WebFault
from resuds.api import ResudsClient
from resuds.tests import LOCALDIR


class ResudsClientTestCase(TestCase):
    wsdl_file = 'file://' + os.path.join(LOCALDIR, 'inventory.wsdl')

    def setUp(self):
        self.client = ResudsClient(ResudsClientTestCase.wsdl_file, faults=False)

    def testCreateAdspaceSoapObject(self):
        adspace = self.client.create('Adspace')
        self.assertEquals(adspace.cls_name, 'Adspace')
        self.assertEquals(
            repr(
                adspace), "Adspace({'estdailyusers': 1, 'minallowedcpm': '', 'description': '', 'placementheight': '', 'allowcompanionflights': '', 'placementwidth': '', 'mediachannelid': '', 'longtail': '', 'estdailyimps': 1, 'test': false, 'externalid': '', 'active': '', 'supportconvtracking': false, 'publisherid': '', 'id': '', 'minallowedcpc': '', 'name': ''}, {'excludedtopicidlist': [], 'formatresourcetypelist': [], 'categoryidlist': []})"
        )

    def testGetUnexistentProperty(self):
        adspace = self.client.create('Adspace')
        self.assertRaises(AttributeError, getattr, adspace, 'dummy')

    def testSetUnexistentProperty(self):
        adspace = self.client.create('Adspace')
        self.assertRaises(AttributeError, setattr, adspace, 'dummy', 'dummyvalue')

    def testChangeObjectProperty(self):
        adspace = self.client.create('Adspace')
        adspace.description = "new Description"
        self.assertEquals(adspace.description, 'new Description')

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

    def testAddListToObject(self):
        adspace = self.client.create('Adspace')
        frt = self.client.create('FormatResourceType', formatid=5, resourcetypeidlist=[5, 6, ])
        frtl = [frt, ]
        adspace.formatresourcetypelist = frtl
        self.assertEquals(
            adspace.formatresourcetypelist[0].formatid, 5
        )
        self.assertEquals(
            adspace.formatresourcetypelist[0].resourcetypeidlist, [5, 6, ]
        )

    def testUnexistentMethod(self):
        self.assertRaises(NotImplementedError, getattr, self.client, 'unexistentMethod')

    def testNoSendRequest(self):
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
        self.assertRaises(WebFault, client.GetAdSpaceById, name='', pwd='', operatorId='', adSpaceId=adspace_id)

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

    def setupHttpPretty(self, name, method=HTTPretty.POST, status_code=200):
        with open(os.path.join(LOCALDIR, name + '.wsdl')) as fp:
            body = fp.read()
        HTTPretty.register_uri(
            method,
            'http://localhost/invetory',
            body=body,
            status=status_code,
        )
