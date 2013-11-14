from citadel.models import Secret
from django.db import models
from django.utils.six import with_metaclass

     
class SecretField(with_metaclass(models.SubfieldBase, models.Field)):
    
#     description = "A text value that is encrypted via AES-128"       
#     __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        # account for the rounding-up to fit all the AES blocks + iv
#         self.maxlength = AES.block_size * (max_length / AES.block_size + 2)
        super(SecretField, self).__init__(*args, **kwargs)    
    
    def db_type(self, connection):
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
        ciphertext = value.get_ciphertext().encode('hex')
        salt = value.get_salt()
        
        try:
            db_value = str(salt) + '$' + str(ciphertext)
        except e:
            pass

        return str(salt) + '$' + str(ciphertext)
        
    def value_to_string(self, obj): 
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)
        
