1.0.1.dev0  
BACKWARDS INCOMPATIBLE WITH DJANGO < 1.8

Also:
- Attempts to decrypt a secret with a bad password now raise a ValidationError
- Persistent model now stores PBKDF2 work factor and checksum for validation of decryption 

