from Crypto import Random
from Crypto.Cipher import AES
from django.contrib.auth.hashers import PBKDF2PasswordHasher

class Secret(object):
    def __init__(self, plaintext=None, password=None, 
                 ciphertext=None, salt=None, work_factor=None,
                 checksum=None):
        self.model_ref = None
        if(plaintext and password):
            # Secret begins life unencrypted, keep it that way
            self.plaintext = plaintext
            encoded = self._encode(password)

            [alg, iterations, self.salt, hash]  = encoded.split('$')

            [_, _, _, self.checksum] = self._encode(plaintext, self.salt).split('$')
            self.work_factor = int(iterations)

            # generate a unique initialization vector
            iv = Random.new().read(AES.block_size)
            cipher = AES.new(hash[0:32], AES.MODE_CFB, iv)

            # store ciphertext alongside plaintext
            self.ciphertext = (iv + cipher.encrypt(plaintext))
        elif(ciphertext and salt and work_factor):
            # Secret begins life encrypted, keep it that way
            self.salt = salt
            self.ciphertext = ciphertext
            self.work_factor = int(work_factor)
            self.checksum = checksum
        else:
            raise ValueError("Insufficient arguments to initialize Secret")

    def _encode(self, password, salt=None, work_factor=None):
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
        if work_factor:
            encoded = hasher.encode(password, salt, iterations=self.work_factor)
        else:
            # if work_factor isn't specified, use Django's default value
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
    def from_ciphertext(cls, ciphertext, salt, work_factor, checksum):
        """
        Generate a Secret object from ciphertext and salt

        :param ciphertext: initialization vector + encrypted plaintext
        :param salt: AES salt value
        :param work_factor: PBKDF2 hash work factor
        :param checksum: PBKDF2 hash checksum of secret
        :return: Secret object (encrypted)
        """
        return cls(ciphertext=ciphertext, 
                   salt=salt, 
                   work_factor=work_factor, 
                   checksum=checksum)
    
    def recrypt(self, old_pw, new_pw):
        """
        Change the Secret password

        :param old_pw: current password
        :param new_pw: desired password
        :return: None
        """
        plaintext = self.get_plaintext(old_pw)
        encoded = self._encode(new_pw, self.work_factor)

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
    
    def get_work_factor(self):
        """
        Return PBKDF2 hash work factor

        :return: PBKDF2 work factor
        """
        return self.work_factor

    def get_ciphertext(self):
        """
        Return IV concatenated with encrypted plaintext

        :return: initialization vector + encrypted plaintext
        """
        return self.ciphertext
        
    def get_checksum(self):
        return self.checksum

    def get_plaintext(self, password=None):
        """
        Return the secret in plaintext.

        Assumptions: salt and work_factor attributes are already populated.

        :param password: Password to try in decryption
        :return: string plaintext
        """
        try:
            return self.plaintext
        except AttributeError:
            if (password and self.salt and self.work_factor):
                # nobody has assigned plaintext yet
            
                encoded = self._encode(password, self.salt, self.work_factor)

                # retrieve the pw hash, used as decryption key
                [alg, iterations, self.salt, key] = encoded.split('$')            

                iv = self.ciphertext[0:AES.block_size]
                cipher = AES.new(key[0:32], AES.MODE_CFB, iv)
            
                plaintext = cipher.decrypt(self.ciphertext[AES.block_size:])

                checksum_encoded = self._encode(plaintext, self.salt, self.work_factor)
                [_, _, _, checksum] = checksum_encoded.split('$')

                # self.checksum could be None in legacy cases!
                if not self.checksum or checksum == self.checksum:
                    self.plaintext = plaintext

                    # if upgrade needed, send signal to Model instances to update their SecretFields
                    if self.work_factor != PBKDF2PasswordHasher.iterations:
                        (model, field_name) = self.model_ref
                        model.upgrade_secret(field_name, self.plaintext, password)

                    return self.plaintext
                else:
                    #@TODO: raise exception here
                    return None

    def create_model_reference(self, (instance, field_name)):
        """Keep track of the Django models to which this Secret belongs."""
        self.model_ref = (instance, field_name)

    def destroy_model_reference(self, (instance, field_name)):
        self.model_ref = None
