#1.0.1.dev0 Release Notes

##Incompatabilities:
Backwards incompatible with Django < 1.8 due to the use of `models.fields.from_db_value()`.  See [Django 1.8 docs](https://docs.djangoproject.com/en/1.8/howto/custom-model-fields/#converting-values-to-python-objects).

Before upgrading Django, 'Preparing for Upgrade' section below.

##Preparing for Upgrade: 
Previous releases did not account for Django upgrades that incurred a PBKDF2 hash [work factor increase](https://docs.djangoproject.com/en/1.8/topics/auth/passwords/#increasing-the-work-factor). This release introduces database storage of the work factor for each Secret and upgrades Secrets automatically upon decryption.  However, Secrets stored using previous versions of `django-citadel` require a default workfactor to be properly decrypted.  Prior to upgrading Django, follow the below process:

####Step 1: Determine your pre-upgrade PBKDF2 work factor:

    $ python manage.py shell
    >>> from django.contrib.auth.hashers import PBKDF2PasswordHasher
    >>> print PBKDF2PasswordHasher.iterations
    
This value can also be found via code inspection. For example, Django 1.6.5 deploys a work factor of 12000, found in [django.contrib.auth.hashers](https://github.com/django/django/blob/b5bacdea00c8ca980ff5885e15f7cd7b26b4dbb9/django/contrib/auth/hashers.py#L230).
####Step 2: Set the pre-upgrade work factor as a default in your django settings.

    CITADEL_DEFAULT_WF = 12000 #value depends on version
    
####Step 3: Upgrade Django to version > 1.8
####Step 4: Upgrade django-citadel
####Step 5: Ensure that all models with Secret attributes now extend `citadel.models.SecretiveModel`:
This allows for automatic PBKDF2 work factor upgrade for each secret decrypted after any future Django upgrades.  Example:

    class BuriedTreasure(SecretiveModel):
        user = models.ForeignKey(User)
        location = SecretField()    

##What's new:  
- Attempts to decrypt a secret with a bad password now raise a ValidationError.  
- Persistent model now stores PBKDF2 work factor and checksum for validation of decryption.  
- New SecretiveModel tracks its Secret attributes and allows for automatic PBKDF2 work factor upgrades any time Django's default work factor changes.  


