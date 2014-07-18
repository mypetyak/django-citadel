from Crypto import Random
from Crypto.Cipher import AES
from django.contrib.auth.hashers import PBKDF2PasswordHasher

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^citadel\.fields\.SecretField"])
except ImportError:
    # South isn't used
    pass

class Secret(object):
    def __init__(self, plaintext=None, password=None, ciphertext=None, salt=None):
        if(plaintext and password):
            # Secret begins life unencrypted, keep it that way
            self.plaintext = plaintext
            encoded = self._encode(password)

            [alg, iterations, self.salt, hash]  = encoded.split('$')

            # generate a unique initialization vector
            iv = Random.new().read(AES.block_size)
            cipher = AES.new(hash[0:32], AES.MODE_CFB, iv)

            # store ciphertext alongside plaintext
            self.ciphertext = (iv + cipher.encrypt(plaintext))

        elif(ciphertext and salt):
            # Secret begins life encrypted, keep it that way
            self.salt = salt
            self.ciphertext = ciphertext

        else:
            raise ValueError("Insufficient arguments to initialize Secret")

    def _encode(self, password, salt=None):
        """
        Generate hash using PBKDF2 function.

        :param password: text password
        :param salt: AES salt. If not provided, one is generated
        :return: string with [alg, iterations, salt, hash] separated by '$'
        """
        hasher = PBKDF2PasswordHasher()
        if not salt:
            salt = hasher.salt()
            self.salt = salt
        encoded = hasher.encode(password, salt)
        return encoded

    @classmethod
    def from_plaintext(cls, plaintext, password):
        """
        Generate a Secret object from plaintext and password.

        Note that password is not encryption key, but is used
        to generate a key.

        :param plaintext: free text secret to encrypt
        :param password: free text password used to generate encryption key
        :return: Secret object (unencrypted)
        """
        return cls(plaintext=plaintext, password=password)
    
    @classmethod
    def from_ciphertext(cls, ciphertext, salt):
        """
        Generate a Secret object from ciphertext and salt

        :param ciphertext: initialization vector + encrypted plaintext
        :param salt: AES salt value
        :return: Secret object (encrypted)
        """
        return cls(ciphertext=ciphertext, salt=salt)    
    
    def recrypt(self, old_pw, new_pw):
        """
        Change the Secret password

        :param old_pw: current password
        :param new_pw: desired password
        :return: None
        """
        plaintext = self.get_plaintext(old_pw)
        encoded = self._encode(new_pw)

        [alg, iterations, self.salt, hash]  = encoded.split('$')
        
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(hash[0:32], AES.MODE_CFB, iv)
        self.ciphertext = (iv + cipher.encrypt(plaintext))
       
    def get_salt(self):
        """
        Return AES encryption salt

        :return: AES salt
        """
        return self.salt

    def get_ciphertext(self):
        """
        Return IV concatenated with encrypted plaintext

        :return: initialization vector + encrypted plaintext
        """
        return self.ciphertext
        
    def get_plaintext(self, password=None):
        """
        Return the secret in plaintext.

        :param password: Password to try in decryption
        :return: string plaintext
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
        
