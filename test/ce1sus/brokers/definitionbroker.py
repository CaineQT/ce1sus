'''
Created on Jul 4, 2013

@author: jhemp
'''
import unittest
from ce1sus.db.session import SessionManager
from ce1sus.brokers.definitionbroker import DEF_AttributeBroker, DEF_ObjectBroker
from ce1sus.brokers.classes.definitions import DEF_Attribute, DEF_Object
from ce1sus import helpers

class TestDefinitionBrokers(unittest.TestCase):

  # The following test have to be ordered



  def setUp(self):

    self.sessionManager = SessionManager('../ce1sus.cfg')
    self.attributebroker = self.sessionManager.brokerFactory(DEF_AttributeBroker)



    self.attribute = DEF_Attribute()
    self.attribute.description = 'Description'
    self.attribute.identifier = 1
    self.attribute.name = 'Name'
    self.attribute.regex = 'Regex'
    self.attribute.valuetable = 1

    self.objectbroker = self.sessionManager.brokerFactory(DEF_ObjectBroker)

    self.object = DEF_Object()
    self.object.name = 'Name'
    self.object.identifier = 1
    self.object.description = 'A description'
    # self.object.addAttribute(self.attribute)
  def tearDown(self):
    pass

  def test_A_InsertAttribute(self):

    self.attributebroker.insert(self.attribute)
    assert True

  def testNothingFound(self):
    try:
      user = self.attributebroker.getUserByID('test')
      # just to prevent the warning
      print user
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

    # get actual attribute
    attribute = self.attributebroker.getByID(self.attribute.identifier)

    # attach group to user
    self.object.addAttribute(attribute)

    self.objectbroker.insert(self.object)
    assert True


# Test if the user is setup correctly if found
  def test_D_GetObjectByID(self):

    obj = self.objectbroker.getByID(self.object.identifier)
    assert True


    assert helpers.objects.compareObjects(obj, self.object)



  def test_E_DeleteObject(self):

      self.objectbroker.removeByID(self.object.identifier)
      # Check if attribute is still existing
      attribute = self.attributebroker.getByID(self.attribute.identifier)

      if helpers.objects.compareObjects(attribute, self.attribute):
        assert True
      else:
        assert False


  def test_F_DeleteGroup(self):
    self.attributebroker.removeByID(self.attribute.identifier)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
