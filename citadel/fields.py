from citadel.types import Secret
from django.conf import settings
from django.db import models
from django.utils.six import with_metaclass

     
class SecretField(with_metaclass(models.SubfieldBase, models.Field)):
    def __init__(self, *args, **kwargs):
        super(SecretField, self).__init__(*args, **kwargs)    
    
    def db_type(self, connection):
        # @TODO: add test for database type, return 'blob' if MySQL
        return 'bytea'
    
    def from_db_value(self, value, expression, connection, context):
        """
        Convert a value as returned by the database to a Python object.
        """
        if value is None:
            return value
        else:
            workfactor = None
            # we need to stringify 'value' in case we're handed
            # a buffer object, as in the case of postgresql
            try:
                [salt, workfactor, ciphertext, checksum] = str(value).split('$')
                secret = Secret.from_ciphertext(ciphertext.decode('hex'), 
                                                salt, 
                                                workfactor, 
                                                checksum)
            except ValueError:
                # maintain support for Citadel versions <= 0.2
                [salt, ciphertext] = str(value).split('$')
                workfactor = int(getattr(settings, 'CITADEL_DEFAULT_WF', 20000))
                
                secret = Secret.from_ciphertext(ciphertext.decode('hex'), salt, workfactor, checksum=None)

            return secret

    def get_prep_value(self, value):
        """
        Prepare Python attribute for storage in database.
        :param value: python attribute
        :return: format for use in database query
        """
        if not value:
            return None
        elif isinstance(value, basestring):
            # When loading a fixture, get_prep_value
            # is executed on a prepared string
            return value

        ciphertext = value.get_ciphertext().encode('hex')
        salt = value.get_salt()
        checksum = value.get_checksum()

        prep = str(salt) + '$' + str(value.get_workfactor()) + '$' + str(ciphertext) + '$' + str(checksum)
        return prep
        
    def value_to_string(self, obj): 
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)
