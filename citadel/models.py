from Crypto import Random
from Crypto.Cipher import AES
from south.modelsinspector import add_introspection_rules

# add_introspection_rules([], ["^apps\.citadel\.fields\.SecretField"])     
add_introspection_rules([], ["^citadel\.fields\.SecretField"])

class Secret(object):
    def __init__(self, plaintext=None, key=None, ciphertext=None):
    
        if(plaintext and key):
            self.plaintext = plaintext
            
            iv = Random.new().read(AES.block_size)
            cipher = AES.new(key, AES.MODE_CFB, iv)
            self.ciphertext = (iv + cipher.encrypt(plaintext))
        elif ciphertext:
            self.ciphertext = ciphertext
            
    @classmethod
    def from_plaintext(cls, plaintext, key):
        return cls(plaintext=plaintext, key=key)
    
    @classmethod
    def from_ciphertext(cls, ciphertext):
        return cls(ciphertext=ciphertext)    
        
    def get_ciphertext(self):
        return self.ciphertext
        
    def get_plaintext(self, key=None):
        """Return the secret in plaintext.
        
        Keyword Arguments:
        key -- the cipher key used for decryption (default None)
        """
        try:
            return self.plaintext
        except AttributeError:
            # nobody has assigned plaintext yet
            iv = self.ciphertext[0:AES.block_size]
            cipher = AES.new(key, AES.MODE_CFB, iv)
            
            self.plaintext = cipher.decrypt(self.ciphertext[AES.block_size:])
            return self.plaintext
        