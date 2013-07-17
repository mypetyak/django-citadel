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
        return 'blob'
    
    def to_python(self, value):
        if isinstance(value, Secret):
            return value
        #@todo: perform some validations here
        return Secret.from_ciphertext(value.decode('hex'))

    def get_prep_value(self, value):
        return value.get_ciphertext().encode('hex')
        