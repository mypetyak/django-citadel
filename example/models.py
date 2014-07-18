from citadel.fields import SecretField
from django.contrib.auth.models import User
from django.db import models

class BuriedTreasure(models.Model):
    """
    Provide a Model as an example with one non-Secret field (user) and
    a Secret field (location)
    """
    user = models.ForeignKey(User)
    location = SecretField()