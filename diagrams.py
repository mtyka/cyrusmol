#!/usr/bin/env python
#
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
import hashlib
import urllib 
import httplib
import json
import webapp2
import common

from google.appengine.api import users
from google.appengine.ext import db


diagram_list_name = 'db_diagrams'


class Diagram(db.Model):
  """Models a molecular structure or system.

    _id: id of the diagram
    user_id: the user that the diagram belongs to
    created_time: self explainatory
    elements: a list of ids of all the diagram elements in that diagram.
    parent_element: id of the parent element of the diagram (null if its the root diagram)
    
  """
  _id = db.Key()
  user_id = db.StringProperty()
  created_time = db.DateTimeProperty(auto_now_add=True)
  elements = db.StringListProperty()
  parent_element = db.StringProperty()
  
  @classmethod
  def Key(cls, diagram_name):
    """Constructs a Datastore key for a diagram entity with diagram_name."""
    return db.Key.from_path('Diagram', diagram_name)

  def AsDict(self):
    """Returns data in dictionary form."""
    dform = {
        '_id': str(self.key()),
        'created_time': str(self.created_time),
        'user_id': str(self.user_id),
        'elements': str(self.elements),
    }

    return dform


class List(common.RequestHandler):
  ROUTE = '/diagrams/list'

  @classmethod
  def Routes(cls):
    return [webapp2.Route(cls.ROUTE, cls, methods=['GET'])]

  @common.RequestHandler.LoginRequired
  def get(self):   # pylint: disable=g-bad-name
    """Obtain a list of diagrams."""
    user = users.get_current_user()
    diagrams = Diagram.query(user_id=user.user_id).fetch()

    self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
    self.response.headers['Content-Disposition'] = 'attachment'
    self.response.out.write(json.dumps(diagrams))


class Get(common.RequestHandler):
  ROUTE = '/diagrams/get'

  @classmethod
  def Routes(cls):
    return [webapp2.Route(cls.ROUTE, cls, methods=['GET'])]

  @common.RequestHandler.LoginRequired
  def get(self):   # pylint: disable=g-bad-name
    """Obtain a particular diagram based on a key."""

    id = self.request.get('_id')
    diagram = db.get(id)
    
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
    return



class Put(common.RequestHandler):
  ROUTE = '/diagrams/put'

  @classmethod
  def Routes(cls):
    return [webapp2.Route(cls.ROUTE, cls, methods=['POST'])]

  def put(self):   # pylint: disable=g-bad-name
    """Add a diagram to the database. This is called by the workers"""
    
    new_diagram = Diagram(Diagram.Key(diagram_list_name))
    user = users.get_current_user()
    
    new_diagram.user_id = user.user_id

    new_diagram.put()
    
    new_diagram_dict = new_diagram.AsDict()
    
    self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
    self.response.headers['Content-Disposition'] = 'attachment'
    self.response.out.write(json.dumps(new_diagram_dict))

class Delete(common.RequestHandler):
  ROUTE = '/diagrams/delete'

  @classmethod
  def Routes(cls):
    return [webapp2.Route(cls.ROUTE, cls, methods=['POST'])]

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
    

all_routes = [List.Routes(), Get.Routes(), Put.Routes(), Delete.Routes()]


def Routes():
  return sum(all_routes, [])

