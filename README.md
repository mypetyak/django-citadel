django-citadel
==============
[![Build Status](https://travis-ci.org/mypetyak/django-citadel.svg?branch=master)](https://travis-ci.org/mypetyak/django-citadel)

This Django application provides a field type that stores data under AES encryption at rest. It is useful
for the Django developer that needs to store sensitive data in an untrusted location (a database that could
be compromised, a third-party external message queue, etc). It is an application-level alternative to
database-level encryption, such as PostgreSQL's `pgcrypto` module.

##Disclaimer:
Encryption is hard to get right. For now, `django-citadel` is still a work in progress, and should be treated as such. Please don't deploy this package to highly sensitive data without thorough review of the underlying encryption system by a cryptographic professional. Feedback is, of course, welcome!

##Features:
- Each secret receives a unique salt value and initialization vector
- Password hashing is performed using PBKDF2 hash function in order to combat dictionary attacks
- PBKDF2 work factor adjustments, due to Django upgrades, are applied to stored secrets upon the next decryption
- Hydrated fields remain encrypted in memory until explicitly decrypted, limiting unnecessary performance
overhead and plaintext leakage
- Each SecretField can be decrypted individually, providing granular control
- Each secret can be encrypted with a unique unique key, ideal for encryption using user-provided key

##Requirements:
- Encryption relies on PyCrypto toolkit (`pip install pycrypto`)
- Currently only PostgreSQL is supported

##Usage:
To store sensitive data, add a SecretField to your model. This field represents a Secret, which can be
encrypted or decrypted on an as-needed basis.

To provide the developer ultimate control over each Secret, 
the encryption key is required when the Secret is created. In the following example,
a BuriedTreasure model is used to protect the location of Blackbeard's loot. 

Example model:
Each model that uses a SecretField type should inherit from SecretiveModel. This enables automatic upgrading of PBKDF2 hash work factors during Django upgrades.

```
from citadel.models import SecretiveModel

class BuriedTreasure(SecretiveModel):
    user = models.ForeignKey(User)
    location = SecretField()
```

Example usage:

```
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
jackpot_directions = bt.location.get_plaintext(password=password)
```

Printing `jackpot_directions` now outputs the text "30 meters north of the tall coconut tree"

##Installation:
The app is available through Pypi:
`pip install django-citadel`

Add support to your Django project by adding `citadel` to your list of `INSTALLED_APPS`. 

In installations where Secrets have been stored with legacy versions of `django-citadel`, set a default `CITADEL_DEFAULT_WF` value. See [changelog](https://github.com/mypetyak/django-citadel/blob/feature/workfactor-tracking/CHANGELOG.md#preparing-for-upgrade) for details.
