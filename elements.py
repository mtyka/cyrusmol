# LGPL3: www.gnu.org/licences/lgpl.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Licenses is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the Licenses for the specific language governing permissions and
# limitations under the Licenses.
#

"""Defines data models needed for RosettaDiagrams

"""
import json
import webapp2
import common
import diagrams
from google.appengine.ext import db
from google.appengine.api import users

element_list_name = 'db_elements'

class Element(db.Model):
  """Models a Diagram Element

	_id: id of the element
	user_id: the user that the element belongs to
	created_time: self explanatory
	connections: a list of ids of all the connections to other elements.
	subdiagarm: id of the contained subdiagram (if exists) 
	diagram: id of the containing diagram
  """

  created_time = db.DateTimeProperty(auto_now_add=True)
  subdiagram = db.ReferenceProperty(diagrams.Diagram)
  diagram = db.StringProperty()
  name = db.StringProperty()
  width = db.IntegerProperty(default=0)
  height = db.IntegerProperty(default=0)
  show_in_protocols = db.BooleanProperty(default=True)
  x = db.IntegerProperty(default=0)
  y = db.IntegerProperty(default=0)
  type = db.StringProperty(default='mover')
  
  @classmethod
  def Key(cls, element_name):
	"""Constructs a Datastore key for an element entity with element_name."""
	return db.Key.from_path('Element', element_name)

  def AsDict(self):
    """Returns data in dictionary form."""
    dform = {
        '_id': str(self.key()),
        'created_time': str(self.created_time),
        'subdiagram': self.subdiagram.AsDict(),
        'diagram': str(self.diagram),
        'width': long(self.width),
        'height': long(self.height),
        'attributes': [a.AsDict() for a in self.attributes.run()],
        'connections': [c.AsDict() for c in self.connections.run()],
        'pointed_by': [p.AsDict() for p in self.pointed_by.run()],
        'show_in_protocols':self.show_in_protocols,
        'x':long(self.x),
        'y':long(self.y),
        'type': str(self.type),
        'name': str(self.name)
    }

    return dform    

    
class Attribute (db.Model): 
	
	attrkey = db.StringProperty()
	value = db.StringProperty()
	element = db.ReferenceProperty(Element,collection_name='attributes')
	
	@classmethod
	def Key(cls, element_name):
		return db.Key.from_path('Attribute', element_name)
	
	def AsDict(self):
		dform = {
				 '_id': str(self.key()),
				 'key' : self.attrkey,
				 'value': self.value,
				 'element':str(self.element.key())
				 }

		return dform


class Connection(db.Model):
    
    source = db.ReferenceProperty(Element,collection_name='connections')
    target = db.ReferenceProperty(Element,collection_name='pointed_by')
    type = db.StringProperty()
    
    @classmethod
    def Key(cls, element_name):
        return db.Key.from_path('Connection', element_name)
    
    def AsDict(self):
        dform = {
                 'source' : str(self.source.key()),
                 'target': str(self.target.key()),
                 '_id': str(self.key()),
                 'type' : self.type
                 }

        return dform

class NewConnection(common.RequestHandler):
    ROUTE = '/connection/new'
    
    @classmethod
    def Routes(cls):
        return [webapp2.Route(cls.ROUTE, cls, methods=['POST'])]
    
    def post(self):
        
        connection_json = json.loads(self.request.body)
        print "Connection JSON:"
        source = db.get(connection_json['source'])
        target = db.get(connection_json['target'])
        
        obj = Connection(source=source,target=target, type=connection_json['type'])
        obj.put()
        
        connection_json = json.dumps(obj.AsDict())
        
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        self.response.headers['Content-Disposition'] = 'attachment'
        self.response.out.write(connection_json)
        
    
class UpdateConnection(common.RequestHandler):
    ROUTE = '/connection/id/<:([\w\-]+)?>'
    
    @classmethod
    def Routes(cls):
        return [webapp2.Route(cls.ROUTE, cls, methods=['PUT'])]
    
    def put(self,con_id):
        con_json = json.loads(self.request.body)
        print con_json;
        obj = db.get(con_id)
        
        obj.source = db.get(con_json['source'])
        obj.target = db.get(con_json['target'])
        obj.put()

        self.response.set_status(200)


class DeleteConnection(common.RequestHandler):
    ROUTE = '/connection/id/<:([\w\-]+)?>'

    @classmethod
    def Routes(cls):
        return [webapp2.Route(cls.ROUTE, cls, methods=['DELETE'])]
    
    def delete(self,con_id):
        obj = db.get(con_id)
        obj.delete()
        
        self.response.set_status(200)

class NewAttribute(common.RequestHandler):
	ROUTE = '/attribute/new'
	
	@classmethod
	def Routes(cls):
		return [webapp2.Route(cls.ROUTE, cls, methods=['POST'])]
	
	
	def post(self):   # pylint: disable=g-bad-name
		"""Add a diagram to the database. This is called by the workers"""
		attribute_json = json.loads(self.request.body)
		print "ATTRIBUTE: "
	        print attribute_json
		attribute = Attribute()
		attribute.attrkey = attribute_json['key']
		attribute.value = attribute_json['value']
		
		element_id = attribute_json['element']
		element = db.get(element_id)
		
		attribute.element = element
		
		attribute.put()
		
		self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
		self.response.headers['Content-Disposition'] = 'attachment'
		self.response.out.write(json.dumps(attribute.AsDict()))
	


class UpdateAttribute(common.RequestHandler):
    ROUTE = '/attribute/id/<:([\w\-]+)?>'
    
    @classmethod
    def Routes(cls):
        return [webapp2.Route(cls.ROUTE, cls, methods=['PUT'])]
    
    def put(self,attribute_id):
        
        attribute_json = json.loads(self.request.body)
        
        attribute_obj = db.get(attribute_id)
        attribute_obj.attrkey = str(attribute_json["key"])
        attribute_obj.value = str(attribute_json["value"])
        attribute_obj.put()
        
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        self.response.headers['Content-Disposition'] = 'attachment'
        self.response.out.write(json.dumps(attribute_obj.AsDict()))
        
class DeleteAttribute(common.RequestHandler):
    ROUTE = '/attribute/id/<:([\w\-]+)?>'
    
    def Routes(cls,attribute_id):
        return [webapp2.Route(cls.ROUTE, cls, methods=['PUT'])]
    
    def delete(self,attribute_id):
        
        print attribute_id
        attribute_obj = db.get(attribute_id)
        attribute_obj.delete()
        
        self.response.set_status(200)
    
	

#TODO [LiorZ]: Check that the diagram indeed belongs to the user requesting it .. 
class ElementsInDiagram(common.RequestHandler):
  ROUTE = '/diagram/<:([\w\-]+)?>/elements'

  @classmethod
  def Routes(cls):
	return [webapp2.Route(cls.ROUTE, cls, methods=['GET'])]

  @common.RequestHandler.LoginRequired
  def get(self,diagram_id):   # pylint: disable=g-bad-name

	"""Obtain a list of elements in diagram."""
	
        print "Requesting all elements!"
        all_elements = Element.all()
        print "Looking for elements with diagram id " + diagram_id
        filtered_elements = all_elements.filter('diagram = ',diagram_id).run()
        dict_elements = [e.AsDict() for e in filtered_elements]
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        self.response.headers['Content-Disposition'] = 'attachment'
        self.response.out.write(json.dumps(dict_elements))


class GetElement(common.RequestHandler):
  ROUTE = '/element/id/<:([\w\-]+)?>'

  @classmethod
  def Routes(cls):
	return [webapp2.Route(cls.ROUTE, cls, methods=['GET'])]

  @common.RequestHandler.LoginRequired
  def get(self,element_id):   # pylint: disable=g-bad-name
	"""Obtain a particular element in a particular diagram based on a key."""
	my_elem = db.get(element_id)
    
        my_elem_dict = my_elem.AsDict()
        
    
	# reply with JSON object
	self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
	self.response.headers['Content-Disposition'] = 'attachment'
	self.response.out.write(json.dumps())
	return


class PutElement(common.RequestHandler):
  ROUTE = '/element/id/<:([\w\-]+)?>'

  @classmethod
  def Routes(cls):
	return [webapp2.Route(cls.ROUTE, cls, methods=['PUT'])]

  def put(self,element_id):   # pylint: disable=g-bad-name
	"""Add a diagram to the database. This is called by the workers"""

	element_json = json.loads(self.request.body)
	
	new_element = db.get(element_id)

	new_element.diagram = element_json['diagram']
	new_element.width = element_json['width']
	new_element.height = element_json['height']
	new_element.show_in_protocols = bool(element_json['show_in_protocols'] or True) 
	new_element.x = int(element_json['x'] or 1)
	new_element.y = int(element_json['y'] or 1)
	new_element.name = element_json['name']
	new_element.put()
    
	new_element_dict = new_element.AsDict()

	self.response.set_status(200)




class NewElement(common.RequestHandler):
  ROUTE = '/element/new'

  @classmethod
  def Routes(cls):
	return [webapp2.Route(cls.ROUTE, cls, methods=['POST'])]

  def post(self):   # pylint: disable=g-bad-name
	"""Add a diagram to the database. This is called by the workers"""
        element_json = json.loads(self.request.body)
	
        new_element = Element()
        user = users.get_current_user()
        print "Saving new element with diagram id " + element_json['diagram']
        new_element.diagram = element_json['diagram'] 
        new_element.width = int(element_json['width'] or 1)
        new_element.height = int(element_json['height'] or 1)
        new_element.show_in_protocols = bool(element_json['show_in_protocols'] or True) 
        new_element.x = int(element_json['x'] or 1)
        new_element.y = int(element_json['y'] or 1)
        new_element.name = element_json['name']
        new_element.type = element_json['type']
        
        subdiagram = diagrams.Diagram()
        subdiagram.user_id = user.user_id()
        subdiagram.name = new_element.name + "_Subdiagram"
        subdiagram.put()
        new_element.subdiagram = subdiagram
        new_element.put()
        
        subdiagram.parent_element = str(new_element.key())
        subdiagram.put()
        
        elem_id = str(new_element.key())
        #Ugly workaround ahead:
        
        attribute_arr = []
        if element_json["attributes"]:
            for attr in element_json["attributes"]:
                attr_obj = Attribute(attrkey=attr['key'],value=attr['value'],element=new_element)
                attr_obj.put()
                attribute_arr.append(attr_obj.AsDict())
        
        
        new_element_dict = new_element.AsDict()
        print "NEW ELEMENT DICT: "
        print new_element_dict
        new_element_dict["attributes"] = attribute_arr
        #new_element_dict["subdiagram"] = subdiagram.AsDict()
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        self.response.headers['Content-Disposition'] = 'attachment'
        self.response.out.write(json.dumps(new_element_dict))

class DeleteElement(common.RequestHandler):
  ROUTE = '/element/id/<:([\w\-]+)?>'

  @classmethod
  def Routes(cls):
	return [webapp2.Route(cls.ROUTE, cls, methods=['DELETE'])]

  @common.RequestHandler.LoginRequired
  def delete(self,element_id):  # pylint: disable=g-bad-name

	element = db.get(element_id)
	element.delete()
	
	self.response.set_status(200)

	

all_routes = [ElementsInDiagram.Routes(), NewElement.Routes(), DeleteElement.Routes(),GetElement.Routes(), PutElement.Routes(), NewAttribute.Routes(), UpdateAttribute.Routes(),
              NewConnection.Routes(),UpdateConnection.Routes(), DeleteConnection.Routes()]

def Routes():
	return sum(all_routes, [])
