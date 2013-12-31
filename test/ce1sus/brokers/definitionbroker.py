'''
Created on Jul 4, 2013

@author: jhemp
'''
import unittest
from dagr.db.session import SessionManager
from ce1sus.brokers.definition.attributedefinitionbroker import \
                                                  AttributeDefinitionBroker
from ce1sus.brokers.definition.definitionclasses import AttributeDefinition, \
                                                        ObjectDefinition
import dagr.helpers.objects as helpers
from ce1sus.brokers.definition.objectdefinitionbroker import ObjectDefinitionBroker

class TestDefinitionBrokers(unittest.TestCase):

  # The following test have to be ordered
  def setUp(self):
    self.object = ObjectDefinition()
    self.object = ObjectDefinition()
    self.object.name = 'Name'
    self.object.identifier = long(666)
    self.object.description = 'A description'
    self.object.share = long(1)

    self.sessionManager = SessionManager('../config/ce1sustest.conf')
    self.attributebroker = self.sessionManager.brokerFactory(
                                                      AttributeDefinitionBroker)
    self.attribute = AttributeDefinition()
    self.attribute.description = 'Description'
    self.attribute.identifier = long(666)
    self.attribute.name = 'Name'
    self.attribute.regex = 'Regex'
    self.attribute.valuetable = long(1)
    self.attribute.share = long(1)
    self.attribute.classIndex = long(0)
    self.attribute.handlerIndex = long(0)
    self.attribute.deletable = long(1)
    self.attribute.relation = long(1)
    self.attribute.objects = list()

    self.objectbroker = self.sessionManager.brokerFactory(
                                                      ObjectDefinitionBroker)


    self.object.attributes.append(self.attribute)

  def tearDown(self):
    pass

  def testNothingFound(self):
    try:
      attribute = self.attributebroker.getUserByID('test')
      # just to prevent the warning
      del attribute
      assert False
    except Exception:
      assert True

  def testNothingFound2(self):
    try:
      user = self.userBroker.getUserByID('test')
      # just to prevent the warning
      print user
      assert False
    except Exception:
      assert True

  def test_C_InsertObject(self):

    self.objectbroker.insert(self.object)
    assert True

# Test if the user is setup correctly if found
  def test_D_GetObjectByID(self):

    obj = self.objectbroker.getByID(self.object.identifier)
    assert True
    obj.attributes[0].objects = list()
    self.object.attributes[0].objects = list()
    assert helpers.compareObjects(obj, self.object)

  def test_E_DeleteObject(self):

    self.objectbroker.removeByID(self.object.identifier)
    assert True


  def test_F_DeleteAttribute(self):
    self.attributebroker.removeByID(self.attribute.identifier)
    assert True

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
