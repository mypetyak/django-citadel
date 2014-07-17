from citadel.models import Secret
from django.db import models
from django.utils.six import with_metaclass

     
class SecretField(with_metaclass(models.SubfieldBase, models.Field)):
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
            [salt, ciphertext] = str(value).split('$')
            return Secret.from_ciphertext(ciphertext.decode('hex'), salt)

    def get_prep_value(self, value):
        """
        Prepare Python attribute for storage in database.
        :param value: python attribute
        :return: format for use in database query
        """
        ciphertext = value.get_ciphertext().encode('hex')
        salt = value.get_salt()

        return str(salt) + '$' + str(ciphertext)
        
    def value_to_string(self, obj): 
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)
        
