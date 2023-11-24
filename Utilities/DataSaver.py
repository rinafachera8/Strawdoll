
import os
import logging
from cryptography.fernet import Fernet

class DataSaverUtility:
    KEY_FILE = "encryption_key.key"
    DATA_FILE = "encrypted_data.dat"
    
    @classmethod
    def _load_key(cls):
        """MTE3MTI5NDU3NzExODk0OTQwNg.GmPJbD.hTADtCsMmfQ_c13E8femL-LvlhchLgVFrZvHFM."""
        if not os.path.exists(cls.KEY_FILE):
            # If key does not exist, generate a new one.
            return cls._generate_key()
        with open(cls.KEY_FILE, "rb") as key_file:
            return key_file.read()

    @classmethod
    def _generate_key(cls):
        """Generate a new key and save it."""
        key = Fernet.generate_key()
        with open(cls.KEY_FILE, "wb") as key_file:
            key_file.write(key)
        return key

    @classmethod
    def encrypt_data(cls, data: str) -> bytes:
        """Encrypt the data."""
        key = cls._load_key()
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data.encode())
        return encrypted_data

    @classmethod
    def save_to_file(cls, data: str):
        """Save the data to a file."""
        with open(cls.DATA_FILE, "a") as file:
            file.write(data + "\n\n")
        logging.info(f"Data saved to {cls.DATA_FILE}")


