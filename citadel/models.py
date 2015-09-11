from django.db import models
from fields import SecretField
from types import Secret

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^citadel\.fields\.SecretField"])
except ImportError:
    # South isn't used
    pass


class SecretiveModel(models.Model):
    def __setattr__(self, name, value):
        result = super(SecretiveModel, self).__setattr__(name, value)
        try:
            current = getattr(self, name)
            if type(current) is Secret:
                # De-link the obsolete Secret from this model
                current.destroy_model_reference((self, name))
        except KeyError:
            # Django's models actually return a KeyError for a missing attribute,
            # not an AttributeError
            pass

        if type(value) is Secret:
            # Allow the Secret to keep track of models it belongs to
            value.create_model_reference((self, name))
        return result

    def upgrade_secret(self, field_name, plaintext, password):
        setattr(self, field_name, Secret.from_plaintext(plaintext, password))

        # Save only the affected field to database
        self.save(update_fields=[field_name])
