import unittest

import pyrock


class TestTypes(unittest.TestCase):

    def test_default_constructor_message_driver_Message(self):
        obj = pyrock.message_driver.Message()
        self.assertTrue(hasattr(obj, 'content'))
        self.assertTrue(hasattr(obj, 'time'))

    def test_default_constructor_all_basetypes(self):
        for _, c in pyrock.base.__dict__.iteritems():
            if hasattr(c, '_NP_RepositoryId'):
                obj = c()


if __name__ == '__main__':
    unittest.main(verbosity=2)
