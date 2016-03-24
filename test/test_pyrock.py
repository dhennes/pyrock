import unittest

import pyrock


import omniORB
import omniORB.any


class TestTypes(unittest.TestCase):

    def test_default_constructor_message_driver_Message(self):
        C = pyrock.message_driver.Message
        obj = C()
        self.assertTrue(hasattr(obj, 'content'))
        self.assertTrue(hasattr(obj, 'time'))

    def test_default_constructor_all_basetypes(self):
        for _, C in pyrock.base.__dict__.iteritems():
            if hasattr(C, '_NP_RepositoryId'):
                obj = C()
                omniORB.any.to_any(obj)

if __name__ == '__main__':
    unittest.main(verbosity=2)
