
from citadel.models import Secret
from django.test import TestCase
from django.contrib.auth.models import User
from example.models import BuriedTreasure


class BlackbeardTestCase(TestCase):

    def test_blackbeard(self):
        blackbeard = User.objects.create(username='Blackbeard', email='blackbeard@example.org')
        password = "Queen Anne's Revenge"
        trove_coords = '30 meters north of the tall coconut tree'

        # create object and save to database
        BuriedTreasure.objects.create(
            user=blackbeard,
            location=Secret.from_plaintext(plaintext=trove_coords,
                                           password=password))

        # retrieve object from database
        bt = BuriedTreasure.objects.get(user=blackbeard)

        # decrypt secret
        jackpot = bt.location.get_plaintext(password=password)

        self.assertEqual(jackpot, trove_coords)