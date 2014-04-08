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
from elements import NewElement
from elements import DeleteElement
from elements import PutElement
from elements import ElementsInDiagram
from elements import NewAttribute
from elements import GetElement
from elements import UpdateAttribute
from elements import DeleteAttribute

from google.appengine.api import apiproxy_stub_map,datastore_file_stub


class DiagramTestCase(unittest.TestCase):


	diagram_id = "DFD"

	def setUp(self):
		   # Create a WSGI application.
		   app = webapp2.WSGIApplication([('/', MainPageHandler),
										  ('/diagram/new', New),
										  ('/element/get/(\w+)',GetElement),
										  ('/diagram/list', List),
						  ('/diagram/(\w+)',GetDiagram),
										  ('/element/new', NewElement),
										  ('/attribute/id/(\w+)',UpdateAttribute),
						  ('/element/(\w+)/delete',DeleteElement),
										  ('/diagram/(\w+)/elements', ElementsInDiagram),
						  ('/element/update',PutElement),('/attribute/new', NewAttribute),
						  ("/attribute/id/(\w+)",DeleteAttribute),
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
		   
		   #Constructing url for new element:
		   diagram_obj = {
				'name': "Some diagram"
			}
		   response = self.testapp.post('/diagram/new', json.dumps(diagram_obj))
		   self.assertEqual(response.status_int, 200)
		   diagram_json = json.loads(response.body)
		   self.diagram_id = diagram_json['_id'] 
	
	def new_diagram(self):
		response = self.testapp.post('/diagram/new')
		self.assertEqual(response.status_int,200)
		diagram_json = json.loads(response.body)
		return diagram_json

	def testB_GetElementsFromDiagram(self):
		#Testing the ability to retrieve element from a diagram
		
		print self.diagram_id;
		self.assertEqual(1, 1)
 		self.testA_NewElement()
# 		self.testA_NewElement()
# 
# 		url = '/diagram/' + self.diagram_id + '/elements'
# 		response = self.testapp.get(url)
# 		elements_json = json.loads(response.body)
# 		self.assertEquals(2,len(elements_json))

  	def testA_NewElement(self):
  		   	#Trying to create a new empty diagram on the server
  					
  		url = '/element/new'
  		new_element = {
  			'diagram': self.diagram_id,
  			'connections': [],
  			'attributes': [],
  			'width': 140,
  			'height': 80,
  			'show_in_protocols': True,
  			'x' : 10,
  			'y': 20,
  			'name': "DockingMover"
  		}
  		response = self.testapp.post(url,json.dumps(new_element))
  		element_json = json.loads(response.body)
  		self.assertEquals(element_json['diagram'],self.diagram_id)
  		self.assertEquals(element_json['x'],new_element['x'])
  		
		
	def testElementWithAttributes(self):
		url = '/element/new'
  		new_element = {
  			'diagram': self.diagram_id,
  			'connections': [],
  			'width': 140,
  			'height': 80,
  			'show_in_protocols': True,
  			'x' : 10,
  			'y': 20,
  			'name': "DockingMover",
  			'attributes':[{'key':'googie','value':'Shmoogi'}]
  		}
  		response = self.testapp.post(url,json.dumps(new_element))
  		element_json = json.loads(response.body)
  		self.assertEquals(element_json['diagram'],self.diagram_id)
  		self.assertEquals(element_json['x'],new_element['x'])
  		
  		#Trying new attribute:
		new_attribute = {
						'key':'googi',
						'value': 'hamoogi',
						'element':element_json['_id']
   		}
		response = self.testapp.post('/attribute/new',json.dumps(new_attribute))
		attribute_json = json.loads(response.body)
		self.assertEqual(attribute_json['key'], new_attribute['key'])
		
		response = self.testapp.get('/element/get/' + element_json['_id'])
		element_json = json.loads(response.body)
		self.assertEqual(len(element_json["attributes"]), 2, "Attribute length increased by 1")
		
		#Trying updating attribute:
		attribute_json["key"] = "BooBoo"
		response = self.testapp.put('/attribute/id/'+attribute_json["_id"],json.dumps(attribute_json))
		attribute_json = json.loads(response.body)
		self.assertEqual(attribute_json["key"],"BooBoo")
  
  	def testC_DeleteElement(self):
  		#Trying to delete an element from the diagram
  		self.testA_NewElement()
  		response = self.testapp.get('/diagram/'+ self.diagram_id + '/elements')
  		elements_json = json.loads(response.body)	
  		self.assertEquals(len(elements_json),1)
  		element_to_del_id = elements_json[0]['_id']
  		self.assertNotEqual(None,element_to_del_id);
  		self.assertNotEqual('',element_to_del_id);
  
  		response = self.testapp.delete('/element/' + element_to_del_id + '/delete')
  		self.assertEquals(response.status_int,200)
  
  		#Verifying there are no more element
  		response = self.testapp.get('/diagram/'+ self.diagram_id + '/elements')
  
  		self.assertEquals(len(json.loads(response.body)),0)
  
  	def testD_UpdateElement(self):
  		self.testA_NewElement()
  		
  		response = self.testapp.get('/diagram/'+ self.diagram_id + '/elements')
  		elements_json = json.loads(response.body)	
  		self.assertEquals(len(elements_json),1)
  		element = elements_json[0]
  		self.testapp.put('/element/update',json.dumps(element))
  
  	
  	def testGetDiagram(self): 
  		
  		response = self.testapp.get('/diagram/'+self.diagram_id)
  		self.assertEqual(200, response.status_int)

		
		
if __name__ == '__main__':
	   unittest.main()
