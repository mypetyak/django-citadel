from Crypto import Random
from Crypto.Cipher import AES
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.core.exceptions import ValidationError

class Secret(object):
    @classmethod
    def gen_hash_params(cls, message, salt=None, workfactor=None):
        """
        Generate hash and accompanying parameters using PBKDF2 function.

        :param password: text password
        :param salt: AES salt. If not provided, one is generated
        :return: string with [alg, iterations, salt, hash] separated by '$'
        """
        hasher = PBKDF2PasswordHasher()
        if not salt:
            salt = hasher.salt()
        if workfactor:
            hash_params = hasher.encode(message, salt, iterations=workfactor)
        else:
            # if workfactor isn't specified, use Django's default value
            hash_params = hasher.encode(message, salt)
        return hash_params

    @classmethod
    def from_plaintext(cls, plaintext, password):
        """
        Generate a Secret object from plaintext and password.

        Note that password is not encryption key, but is run through
        PBKDF2 hashing function to generate the key.

        :param plaintext: free text secret to encrypt
        :param password: free text password used to generate encryption key
        :return: Secret object (unencrypted)
        """
        if(not plaintext or not password):
            raise ValueError("Insufficient arguments to initialize Secret")

        secret = cls()

        hash_params = cls.gen_hash_params(password)
        [alg, iterations, secret.salt, key]  = hash_params.split('$')

        # we must persist the workfactor since it can change over time,
        # and decryption will break through a Django upgrade that increases it
        secret.workfactor = int(iterations)

        # generate a PBKDF2 hash of plaintext, stored and used as a checksum.
        # note that the fresh salt, generated above, is reused in this hashing so that
        # only one salt is stored with each Secret
        [_, _, _, secret.checksum] = cls.gen_hash_params(plaintext, secret.salt).split('$')

        # generate a unique initialization vector to prepend on the plaintext
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key[0:32], AES.MODE_CFB, iv)

        # store ciphertext alongside plaintext
        secret.ciphertext = (iv + cipher.encrypt(plaintext))
        return secret

    @classmethod
    def from_ciphertext(cls, ciphertext, salt, workfactor, checksum):
        """
        Generate a Secret object from ciphertext and salt

        :param ciphertext: initialization vector + encrypted plaintext
        :param salt: AES salt value
        :param workfactor: PBKDF2 hash work factor
        :param checksum: PBKDF2 hash checksum of secret
        :return: Secret object (encrypted)
        """
        secret = cls()
        secret.salt = salt
        secret.ciphertext = ciphertext
        secret.workfactor = int(workfactor)
        secret.checksum = checksum
        return secret
    
    def recrypt(self, old_pw, new_pw):
        """
        Change the Secret password.

        Raises a ValidationError if the old_pw is incorrect.

        :param old_pw: current password
        :param new_pw: desired password
        :return: None
        """
        plaintext = self.get_plaintext(old_pw)
        hash_params = Secret.gen_hash_params(new_pw, workfactor=self.workfactor)

        [alg, iterations, self.salt, hash]  = hash_params.split('$')
        
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(hash[0:32], AES.MODE_CFB, iv)
        self.ciphertext = (iv + cipher.encrypt(plaintext))
        self.workfactor = int(iterations)
        [_, _, _, self.checksum] = Secret.gen_hash_params(plaintext, self.salt, self.workfactor).split('$')
       
    def get_salt(self):
        """
        Return AES encryption salt

        :return: AES salt
        """
        return self.salt
    
    def get_workfactor(self):
        """
        Return PBKDF2 hash work factor

        :return: PBKDF2 work factor
        """
        return self.workfactor

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

        Assumptions: salt and workfactor attributes are already populated.

        :param password: Password to try in decryption
        :return: string plaintext
        """
        if (password and self.salt and self.workfactor):
            # nobody has assigned plaintext yet
        
            hash_params = Secret.gen_hash_params(password, self.salt, self.workfactor)

            # retrieve the pw hash, used as decryption key
            [alg, iterations, self.salt, key] = hash_params.split('$')            

            iv = self.ciphertext[0:AES.block_size]
            cipher = AES.new(key[0:32], AES.MODE_CFB, iv)
        
            plaintext = cipher.decrypt(self.ciphertext[AES.block_size:])

            checksum_hash_params = Secret.gen_hash_params(plaintext, self.salt, self.workfactor)
            [_, _, _, checksum] = checksum_hash_params.split('$')

            # self.checksum could be None in legacy cases, so we must
            # assume decryption was successful :( !!
            if not self.checksum or checksum == self.checksum:
                self.plaintext = plaintext

                # if upgrade needed, send signal to Model instances to update their SecretFields
                if self.workfactor != PBKDF2PasswordHasher.iterations:
                    try:
                        (model, field_name) = self.model_ref
                        model.upgrade_secret(field_name, self.plaintext, password)
                    except TypeError:
                        # No model_ref is assigned
                        pass

                return self.plaintext
            else:
                #@TODO: raise exception here
                raise ValidationError('Incorrect password')

    def create_model_reference(self, (instance, field_name)):
        """Keep track of the Django models to which this Secret belongs."""
        self.model_ref = (instance, field_name)

    def destroy_model_reference(self, (instance, field_name)):
        self.model_ref = None
