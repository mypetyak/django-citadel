django-citadel
==============
This is a small Django application that provides a field type that stores data under AES encryption. It is useful
for the Django developer that needs to store sensitive data in an untrusted location (such as a database that could
be compromised, a third-party server, an external message queue, etc). It is an application-level alternative to
database-level encryption, such as PostgreSQL's `pgcrypto` module.

##Features:
- Each secret receives a unique salt value and initialization vector
- Password hashing is performed using PBKDF2 hash function in order to combat dictionary attacks
- Hydrated fields remain encrypted in memory until explicitly decrypted, limiting unnecessary performance
overhead and plaintext leakage
- Each SecretField can be decrypted individually
- Each secret can have its own unique key, ideal for encryption using user-provided key

##Requirements:
- Encryption relies on PyCrypto toolkit (`pip install pycrypto`)
- Currently only PostgreSQL is supported

