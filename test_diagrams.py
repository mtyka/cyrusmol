#!/usr/bin/env python
#
# Written by mtyka@google.com (Mike Tyka)
# Written by lior.zimmerman@mail.huji.ac.il (Lior Zimmerman)
#
# Copyright 2012-2013 Google Inc.
#
# Dual license of MIT license or LGPL3 (the "Licenses")
# MIT license: http://opensource.org/licenses/MIT
# LGPL3: www.gnu.org/licences/lgpl.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Licenses is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the Licenses for the specific language governing permissions and
# limitations under the Licenses.
#

import unittest
import os
from google.appengine.ext import testbed
import webapp2
import webtest
import json
from cyrusmol import MainPageHandler
from diagrams import List
from diagrams import New
from diagrams import GetDiagram
from google.appengine.api import apiproxy_stub_map,datastore_file_stub

class DiagramTestCase(unittest.TestCase):

    def setUp(self):
        # Create a WSGI application.
        app = webapp2.WSGIApplication([('/', MainPageHandler),
                                       ('/diagram/new', New),
                                       ('/diagram/list', List),
				       ('/diagram/(\w+)'. GetDiagram)
                                       ('/_ah/login',MainPageHandler)],debug=True)
        app_name = 'diagrams_test'
        os.environ['APPLICATION_ID'] = app_name
        self.testapp = webtest.TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_user_stub()
        self.testbed.setup_env(
            USER_EMAIL = 'test@example.com',
            USER_ID = '123',
            USER_IS_ADMIN = '0',
            overwrite = True)
        datastore_file = '/dev/null'
        apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap() 
        stub = datastore_file_stub.DatastoreFileStub(app_name, datastore_file, '/')
        apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)

	def new_diagram(self):
		response = self.testapp.post('/diagram/new')
		self.assertEqual(response.status_int,200)
		diagram_json = json.loads(response.body)
		return diagram_json
	
    	
	def testNewDiagrams(self):
		#Trying to create a new empty diagram on the server
		response = self.testapp.post('/diagram/new')
		self.assertEqual(response.status_int, 200)
		json_arr = []
		json_arr.append(json.loads(response.body))
		response = self.testapp.post('/diagram/new')
		self.assertEqual(response.status_int, 200)
		

		self.assertEqual(response.status_int,200)
		json_arr.append(json.loads(response.body))	
		self.assertEqual(len(json_arr),2)
		first_d = json_arr[0]
		self.assertEqual("123", first_d['user_id'] )
		print first_d['elements']
		self.assertEqual(0,len(json.loads(first_d['elements'])))

	def testGetDiagram(self): 
		
		diagram_json = self.new_diagram()
		response = self.testapp.get('/diagram/'+diagram_json)
		self.assertEqual(200, response.status_int)


if __name__ == '__main__':
    unittest.main()
