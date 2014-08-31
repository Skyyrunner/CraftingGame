import unittest
import item

class TestItems(unittest.TestCase):
    def setUp(self):
        self.im = item.ItemMaker()

    def test_itemCreation(self):
        i = self.im.getMaterial("iron")

    def test_itemProfilePrint(self):
        i = self.im.getMaterial("iron")
        #print "\n" + i.getProfile() + "\n"

    def test_itemCreationWithValues(self):
        i = self.im.getMaterial("iron", {"hardness":42.0, "malleability":78.0})
        self.assertEqual(i.properties["hardness"], 42.0)
        self.assertEqual(i.properties["malleability"], 78.0)

    def test_itemAffixes(self):
        i = self.im.getMaterial("iron", {"hardness":42.0, "malleability":70.0})
        self.assertEqual(i.getName(), "soft iron")
        i = self.im.getMaterial("feathers", {"hardness":0.3})
        self.assertEqual(i.getName(), "downy feathers")

if __name__=="__main__":
    unittest.main()