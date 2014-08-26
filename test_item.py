import unittest
import item

class TestItems(unittest.TestCase):
    def setUp(self):
        self.im = item.ItemMaker()

    def test_itemCreation(self):
        i = self.im.getMaterial("iron")

    def test_itemProfilePrint(self):
        i = self.im.getMaterial("iron")
        print "\n" + i.getProfile() + "\n"

if __name__=="__main__":
    unittest.main()