"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Unit tests for the Citadel application
"""

from apps.citadel.fields import SecretField
from apps.citadel.models import Secret
from django.test import TestCase

class EncryptionTestCase(TestCase):

    def test_secretmodel(self):                          
        key = 'abcdefabcdefabcd'
        plaintext = "Study hard what interests you the most in the most undisciplined, irreverent and original manner possible."
        
        # create python object from plaintext
        s1 = Secret.from_plaintext(plaintext, 'abcdefabcdefabcd')
        
        sf = SecretField()
        
        # reconstruct python object from ciphertext
        s2 = sf.to_python(s1.get_ciphertext())
        self.assertEqual(s2.get_plaintext(key), s1.get_plaintext(key))        
        


