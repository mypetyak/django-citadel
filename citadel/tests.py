"""
Unit tests for the Citadel application
"""

from citadel.fields import SecretField
from citadel.types import Secret
from django.core.exceptions import ValidationError
from django.test import TestCase

class EncryptionTestCase(TestCase):
    def simulate_db_load(self, secret):
        sf = SecretField()

        # simulate save to DB
        db_value = sf.get_prep_value(secret)

        # simulate retrieval of Secret from DB
        new_secret = sf.from_db_value(db_value, expression=None, connection=None, context=None)
        return new_secret

    def test_db_persistence(self):
        """
        Confirm that saving to database preserves encrypted payload.
        """
        key = 'abcdefabcdefabcd'
        plaintext = 'We build too many walls and not enough bridges.'
        
        # create python object from plaintext
        s1 = Secret.from_plaintext(plaintext, 'abcdefabcdefabcd')
        
        s2 = self.simulate_db_load(s1)

        self.assertEqual(s2.get_plaintext(key), s1.get_plaintext(key))
        self.assertEqual(s2.get_plaintext(key), plaintext)

    def test_badpw(self):
        """
        Confirm that incorrect key returns no false decryption.
        """
        pw_correct = 'goodkey'
        pw_incorrect = 'badkey'
        plaintext = 'Bring me a shrubbery!'

        # test without saving
        s1 = Secret.from_plaintext(plaintext, pw_correct)
        
        self.assertEqual(s1.get_plaintext(pw_correct), plaintext)
        with self.assertRaises(ValidationError):
            s1.get_plaintext(pw_incorrect)

        # simulate retrieval from DB
        s2 = self.simulate_db_load(s1)
        with self.assertRaises(ValidationError):
            s2.get_plaintext(pw_incorrect)

    def test_badpw_recrypt(self):
        """
        Confirm that recryption gracefully handles bad keys.
        """
        pw_correct = 'goodkey'
        pw_incorrect = 'badkey'
        pw_new = 'whocares'
        plaintext = 'Our lives are in your hands and you\'ve got butter fingers!'

        s = Secret.from_plaintext(plaintext, pw_correct)
        with self.assertRaises(ValidationError):
            s.recrypt(old_pw=pw_incorrect, new_pw=pw_new)

        # confirm recryption has not occurred
        self.assertEqual(s.get_plaintext(pw_correct), plaintext)

    def test_recrypt(self):
        """
        Confirm that a recrypted secret decrypts with new password.
        """
        pw_init = 'goodkey'
        pw_new = 'goodnewkey'
        plaintext = 'I always wanted to be a lumberjack.'

        s = Secret.from_plaintext(plaintext, pw_init)
        s.recrypt(old_pw=pw_init, new_pw=pw_new)

        self.assertEqual(s.get_plaintext(pw_new), plaintext)
        with self.assertRaises(ValidationError):
            s.get_plaintext(pw_init)
