from citadel.models import Secret
from django.db import models
from django.utils.six import with_metaclass

     
class SecretField(with_metaclass(models.SubfieldBase, models.Field)):
    LEGACY_PBKDF2_WORK_FACTOR = 12000 # used circa Django 1.6

    def __init__(self, *args, **kwargs):
        super(SecretField, self).__init__(*args, **kwargs)    
    
    def db_type(self, connection):
        # @TODO: add test for database type, return 'blob' if MySQL
        return 'bytea'
    
    def to_python(self, value):
        if isinstance(value, Secret):
            return value
        #@todo: perform some validations here

        if value:
	    # we need to stringify 'value' in case we're handed
	    # a buffer object, as in the case of postgresql
            try:
                [salt, work_factor, ciphertext] = str(value).split('$')
            except ValueError:
                # legacy support for prior citadel versions
                [salt, ciphertext] = str(value).split('$')
                work_factor = LEGACY_PBKDF2_WORK_FACTOR

            return Secret.from_ciphertext(ciphertext.decode('hex'), salt, work_factor)

    def get_prep_value(self, value):
        """
        Prepare Python attribute for storage in database.
        :param value: python attribute
        :return: format for use in database query
        """
        if not value:
            return None
        ciphertext = value.get_ciphertext().encode('hex')
        salt = value.get_salt()

        return str(salt) + '$' + str(value.get_work_factor()) + '$' + str(ciphertext)
        
    def value_to_string(self, obj): 
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)
        
