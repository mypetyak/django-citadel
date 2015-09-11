"""
Unit tests for the Citadel application
"""

from citadel.fields import SecretField
from citadel.types import Secret
from django.test import TestCase

class EncryptionTestCase(TestCase):

    def test_secretmodel(self):
        """
        Confirm that basic Secret and SecretField behavior
        """
        key = 'abcdefabcdefabcd'
        plaintext = 'We build too many walls and not enough bridges.'
        
        # create python object from plaintext
        s1 = Secret.from_plaintext(plaintext, 'abcdefabcdefabcd')
        
        sf = SecretField()
        
        # simulate save to DB
        db_value = sf.get_prep_value(s1)

        # simulate retrieval from DB
        py_obj = sf.from_db_value(db_value, expression=None, connection=None, context=None)

        self.assertEqual(py_obj.get_plaintext(key), s1.get_plaintext(key))
        self.assertEqual(py_obj.get_plaintext(key), plaintext)
