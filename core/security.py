import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class JarvisSecurity:
    """
    Sistema de Criptografia Stark Mark III.
    Protege memórias e chaves de API com criptografia AES-256.
    """
    def __init__(self, password="stark_industries_legacy"):
        self.key = self._generate_key(password)
        self.cipher = Fernet(self.key)

    def _generate_key(self, password):
        salt = b'stark_salt_legacy'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt(self, data):
        if not data: return data
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data):
        if not encrypted_data: return encrypted_data
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except:
            return "ERR_DECRYPT"
