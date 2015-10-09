from citadel.types import Secret
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from myapp.models import BuriedTreasure


class BlackbeardTestCase(TestCase):
    def setUp(self):
        self.blackbeard = User.objects.create(username='Blackbeard', email='blackbeard@example.org')
        self.password = "Queen Anne's Revenge"
        self.trove_coords = '30 meters north of the tall coconut tree'

        # create object and save to database
        BuriedTreasure.objects.create(
            user=self.blackbeard,
            location=Secret.from_plaintext(plaintext=self.trove_coords,
                                           password=self.password))

    def test_blackbeard(self):
        # retrieve object from database
        bt = BuriedTreasure.objects.get(user=self.blackbeard)

        # decrypt secret
        jackpot = bt.location.get_plaintext(password=self.password)

        self.assertEqual(jackpot, self.trove_coords)

    def test_upgrade(self):
        """
        Confirm that a SecretField, originally stored with obsolete work
        factor, is automatically upgraded when decrypted.
        """
        # artificially simulate a low, obsolete PBKDF2 work factor
        django_wf = PBKDF2PasswordHasher.iterations
        PBKDF2PasswordHasher.iterations = django_wf//2

        # create object with low work factor
        bt = BuriedTreasure.objects.create(
                user=self.blackbeard,
                location=Secret.from_plaintext(plaintext=self.trove_coords,
                                               password=self.password))

        location_pre = bt.location
        self.assertEqual(location_pre.get_workfactor(), django_wf//2)

        # reset workfactor and retrieve bt from database to simulate a fresh read
        PBKDF2PasswordHasher.iterations = django_wf
        bt = BuriedTreasure.objects.get(pk=bt.pk)

        # confirm a bad password has no affect on workfactor
        with self.assertRaises(ValidationError):
            garbage = bt.location.get_plaintext(password='wrong password')
        self.assertEqual(bt.location.get_workfactor(), django_wf//2)

        # now decrypt the secret, and expect it to be automatically upgraded
        jackpot = bt.location.get_plaintext(password=self.password)
        location_post = bt.location

        # bt.location should now be upgraded to use current workfactor
        self.assertNotEqual(location_pre, location_post)
        self.assertEqual(location_post.get_workfactor(), django_wf)
