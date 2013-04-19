import os
from unittest import TestCase
from httpretty import HTTPretty, httprettified
from resuds.api import SoapException
from resuds.amobee import AmobeeClient
from resuds.tests import LOCALDIR


class AmobeeClientTestCase(TestCase):
    wsdl_file = 'file://' + os.path.join(LOCALDIR, 'inventory_service.wsdl')

    @httprettified
    def testCredential(self):
        self.setupDefaultSchemas()
        client = AmobeeClient(AmobeeClientTestCase.wsdl_file, 'user', 'password', 'operator_id', nosend=True)
        req = client.GetAdSpaceById(adSpaceId=1234567)
        xml = req.envelope
        self.assertTrue('user' in xml)
        self.assertTrue('password' in xml)
        self.assertTrue('operator_id' in xml)
        self.assertTrue('1234567' in xml)

    @httprettified
    def testFaultRequest(self):
        self.setupHttpPretty('GetAdSpaceById')
        client = AmobeeClient(AmobeeClientTestCase.wsdl_file, 'user', 'password', 'operator_id', faults=True)
        adspace_id = 32645
        res = client.GetAdSpaceById(name='', pwd='', operatorId='', adSpaceId=adspace_id)
        self.assertEquals(res.cls_name, 'Adspace')

    @httprettified
    def testWebFaultExceptionOnHttpError(self):
        self.setupHttpPretty('InvalidGetAdSpaceById', status_code=500)
        client = AmobeeClient(AmobeeClientTestCase.wsdl_file, 'user', 'password', 'operator_id')
        adspace_id = 1234567890
        self.assertRaises(SoapException, client.GetAdSpaceById, name='', pwd='', operatorId='', adSpaceId=adspace_id)

    @httprettified
    def testGetObject(self):
        self.setupHttpPretty('GetAdSpaceById')
        client = AmobeeClient(AmobeeClientTestCase.wsdl_file, 'user', 'password', 'operator_id', faults=False)
        adspace_id = 32645
        adspace = client.GetAdSpaceById(adSpaceId=adspace_id)
        self.assertEquals(adspace.id, adspace_id)

    def setupHttpPretty(self, name, method=HTTPretty.POST, status_code=200):
        with open(os.path.join(LOCALDIR, name + '.wsdl')) as fp:
            body = fp.read()
        HTTPretty.register_uri(
            method,
            'https://localhost/invetory',
            body=body,
            status=status_code,
        )
        self.setupDefaultSchemas()

    def setupDefaultSchemas(self):
        with open(os.path.join(LOCALDIR, 'XMLSchema.xsd')) as fp:
            body = fp.read()
        HTTPretty.register_uri(HTTPretty.GET, 'http://www.w3.org/2001/XMLSchema.xsd', body=body)

        with open(os.path.join(LOCALDIR, 'xml.xsd')) as fp:
            body = fp.read()
        HTTPretty.register_uri(HTTPretty.GET, 'http://www.w3.org/2001/xml.xsd', body=body)
