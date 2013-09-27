from Crypto import Random
from Crypto.Cipher import AES
from south.modelsinspector import add_introspection_rules
from django.contrib.auth.hashers import PBKDF2PasswordHasher

# add_introspection_rules([], ["^apps\.citadel\.fields\.SecretField"])     
add_introspection_rules([], ["^citadel\.fields\.SecretField"])

class Secret(object):
    def __init__(self, plaintext=None, password=None, ciphertext=None, salt=None):
    
        if(plaintext and password):
            self.plaintext = plaintext
            encoded = self._encode(password)
            
            #self.salt = 
            [alg, iterations, self.salt, hash]  = encoded.split('$')
 
            iv = Random.new().read(AES.block_size)
            cipher = AES.new(hash[0:32], AES.MODE_CFB, iv)
            self.ciphertext = (iv + cipher.encrypt(plaintext))
        elif(ciphertext and salt):
            self.salt = salt
            self.ciphertext = ciphertext
            
    #@todo - implement key storage, retrieval, and generation from
    #        freetext password        
    def _encode(self, password, salt=None):
        hasher = PBKDF2PasswordHasher()
        if not salt:
            salt = hasher.salt()
            self.salt = salt
        encoded = hasher.encode(password, salt)
        return encoded

    @classmethod
    def from_plaintext(cls, plaintext, password):
        return cls(plaintext=plaintext, password=password)
    
    @classmethod
    def from_ciphertext(cls, ciphertext, salt):
        return cls(ciphertext=ciphertext, salt=salt)    
    
    def recrypt(self, old_pw, new_pw):
        plaintext = self.get_plaintext(old_pw)
#         self = Secret.from_plaintext(pt, new_pw)
        encoded = self._encode(new_pw)
        
        #self.salt = 
        [alg, iterations, self.salt, hash]  = encoded.split('$')
        
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(hash[0:32], AES.MODE_CFB, iv)
        self.ciphertext = (iv + cipher.encrypt(plaintext))
       
    def get_salt(self):
        return self.salt

    def get_ciphertext(self):
        return self.ciphertext
        
    def get_plaintext(self, password=None):
        """Return the secret in plaintext.
        
        Keyword Arguments:
        key -- the cipher key used for decryption (default None)
        """
        try:
            return self.plaintext
        except AttributeError:
            if (password and self.salt):
                # nobody has assigned plaintext yet
            
                encoded = self._encode(password, self.salt)
                [alg, iterations, self.salt, hash] = encoded.split('$')            

                iv = self.ciphertext[0:AES.block_size]
                cipher = AES.new(hash[0:32], AES.MODE_CFB, iv)
            
                self.plaintext = cipher.decrypt(self.ciphertext[AES.block_size:])
                return self.plaintext
        
