#!/usr/bin/env python
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

"""Defines data models needed for RosettaDiagrams

"""
import httplib
import json
import webapp2
import common
import functools
from google.appengine.api import users
from google.appengine.ext import db

diagram_list_name = 'db_diagrams'

class Diagram(db.Model):
  """Models a molecular structure or system.

    _id: id of the diagram
    user_id: the user that the diagram belongs to
    created_time: self explanatory
    elements: a list of ids of all the diagram elements in that diagram.
    parent_element: id of the parent element of the diagram (null if its the root diagram)
    
  """
  user_id = db.StringProperty()
  created_time = db.DateTimeProperty(auto_now_add=True)
  elements = db.StringListProperty()
  parent_element = db.StringProperty()
  name = db.StringProperty()

  def AsDict(self):
    """Returns data in dictionary form."""
    dform = {
        '_id': str(self.key()),
        'created_time': str(self.created_time),
        'user_id': str(self.user_id),
        'elements': str(self.elements),
        'name': str(self.name),
        'parent_element':str(self.parent_element)
    }

    return dform


class List(common.RequestHandler):
  ROUTE = '/diagram/list'

  @classmethod
  def Routes(cls):
    return [webapp2.Route(cls.ROUTE, cls, methods=['GET'])]

  @common.RequestHandler.LoginRequired
  def get(self):   # pylint: disable=g-bad-name

    """Obtain a list of diagrams."""
    user = users.get_current_user()
    all_diagrams = Diagram.all()
    diagrams = all_diagrams.filter('user_id =', user.user_id()).filter('parent_element = ', "").run()
    diagrams_dicts = [d.AsDict() for d in diagrams]
    
    self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
    self.response.out.write(json.dumps(diagrams_dicts))

class DiagramBelongsToUser(common.RequestHandler):

	@staticmethod
	def DiagramBelongs(func):
		""" Decorator function - checks if diagram belongs to current user """

		@functools.wraps(func)
		def CheckDiagram(self, *args, **kwargs):
			print args

			return func(self,*args, **kwargs)
		return CheckDiagram


class GetDiagram(common.RequestHandler):
  ROUTE = r'/diagram/<:([\w\-]+)?>'

  @classmethod
  def Routes(cls):
    return [webapp2.Route(cls.ROUTE, cls, methods=['GET'])]

  @common.RequestHandler.LoginRequired
  def get(self,diagram_id):   # pylint: disable=g-bad-name
    """Obtain a particular diagram based on a key."""

    diagram = db.get(diagram_id)
    if not diagram:
      self.abort(httplib.FORBIDDEN)
      return


    # Check that this user matches the owner of the object
    user = users.get_current_user()
    if user.user_id() != diagram.user_id:
      self.abort(httplib.FORBIDDEN)
      return

    diagram_dict = diagram.AsDict()

    # reply with JSON object
    self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
    self.response.headers['Content-Disposition'] = 'attachment'
    self.response.out.write(json.dumps(diagram_dict))


class New(common.RequestHandler):
  ROUTE = '/diagram/new'

  @classmethod
  def Routes(cls):
    return [webapp2.Route(cls.ROUTE, cls, methods=['POST'])]
  
  @common.RequestHandler.LoginRequired
  def post(self):   # pylint: disable=g-bad-name
    """Add a diagram to the database. This is called by the workers"""
    
    print "NAME"
    diagram_json = json.loads(self.request.body)
    print diagram_json['name']
    
    new_diagram = Diagram();
    user = users.get_current_user()
    
    new_diagram.user_id = user.user_id()
    new_diagram.name = diagram_json['name']
    new_diagram.parent_element = diagram_json['parent_element'] or ""
    new_diagram.put()
    
    new_diagram_dict = new_diagram.AsDict()
    
    self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
    self.response.headers['Content-Disposition'] = 'attachment'
    self.response.out.write(json.dumps(new_diagram_dict))

class Delete(common.RequestHandler):
  ROUTE = '/diagram/delete'

  @classmethod
  def Routes(cls):
    return [webapp2.Route(cls.ROUTE, cls, methods=['DELETE'])]

  @common.RequestHandler.LoginRequired
  def delete(self):  # pylint: disable=g-bad-name

    diagram = db.get(self.request.get('_id'))

    # Check that this user matches the owner of the object
    user = users.get_current_user()
    if user.user_id() != diagram.user_id:
      self.abort(httplib.FORBIDDEN)
      return

    # or else continue to deleting this diagram
    diagram.delete()
    self.response.set_status(200)
    

all_routes = [List.Routes(), GetDiagram.Routes(), New.Routes(), Delete.Routes()]

def Routes():
	return sum(all_routes, [])
