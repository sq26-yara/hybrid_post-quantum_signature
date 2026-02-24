"""
ECDSA (Elliptic Curve Digital Signature Algorithm)
Wrapper для бібліотеки ecdsa з підтримкою NIST P-256

Цифровий підпис на еліптичних кривих над простим полем GF(p)
"""

import ecdsa
from ecdsa import SigningKey, VerifyingKey, NIST256p
from ecdsa.util import sigencode_string, sigdecode_string
import hashlib
import time
from typing import Tuple


class ECDSA_P256:
    """
    ECDSA з кривою NIST P-256 (secp256r1)
    
    Параметри:
    - Крива: NIST P-256 (secp256r1)
    - Поле: GF(p) де p = 2^256 - 2^224 + 2^192 + 2^96 - 1
    - Порядок: n ≈ 2^256
    - Хеш-функція: SHA-256
    - Розмір ключа: 256 біт
    - Розмір підпису: 64 байти (r: 32 байти, s: 32 байти)

    """
    
    def __init__(self):
        """
        Ініціалізація ECDSA з кривою P-256
        """
        self.curve = NIST256p
        self.hash_func = hashlib.sha256
    
    def generate_keypair(self) -> Tuple[SigningKey, VerifyingKey]:
        """
        Генерація пари ключів ECDSA
        
        Returns:
            (private_key, public_key)
        """
        start_time = time.time()
        private_key = SigningKey.generate(curve=self.curve, hashfunc=self.hash_func)
        public_key = private_key.get_verifying_key()

        keygen_time = time.time() - start_time
        print(f"     Час генерації ключів ECDSA: {keygen_time*1000:.2f} мсек")
        
        return private_key, public_key
    
    def sign(self, data: bytes, private_key: SigningKey) -> bytes:
        """
        Створення цифрового підпису ECDSA
        
        Args:
            data: Дані для підпису
            private_key: Приватний ключ
            
        Returns:
            Підпис (64 байти: r || s)
        """
        
        start_time = time.time()
        
        # Підпис з детермінованим k (RFC 6979)
        signature = private_key.sign_digest_deterministic(
            self.hash_func(data).digest(),
            hashfunc=self.hash_func,
            sigencode=sigencode_string
        )
        
        sign_time = time.time() - start_time
        print(f"     Час підпису за допомогою ECDSA: {sign_time*1000:.2f} мсек")
        
        return signature
    
    def verify(self, data: bytes, signature: bytes, public_key: VerifyingKey) -> bool:
        """
        Верифікація цифрового підпису ECDSA
        
        Args:
            data: Дані
            signature: Підпис (64 байти)
            public_key: Публічний ключ
            
        Returns:
            True якщо підпис валідний
        """
        
        start_time = time.time()
        
        try:
            public_key.verify_digest(
                signature,
                self.hash_func(data).digest(),
                sigdecode=sigdecode_string,

            )
            verify_time = time.time() - start_time
            print(f"     Час перевірки підпису ECDSA: {verify_time*1000:.2f} мсек")
            return True
        except:
            return False
    
    def private_key_to_bytes(self, private_key: SigningKey) -> bytes:
        """
        Серіалізація приватного ключа
        
        Args:
            private_key: Приватний ключ
            
        Returns:
            32 байти приватного ключа
        """
        return private_key.to_string()
    
    def public_key_to_bytes(self, public_key: VerifyingKey) -> bytes:
        """
        Серіалізація публічного ключа
        
        Args:
            public_key: Публічний ключ
            
        Returns:
            64 байти публічного ключа (x || y)
        """
        return public_key.to_string()
    
    def private_key_from_bytes(self, key_bytes: bytes) -> SigningKey:
        """
        Десеріалізація приватного ключа
        
        Args:
            key_bytes: 32 байти приватного ключа
            
        Returns:
            Приватний ключ
        """
        return SigningKey.from_string(key_bytes, curve=self.curve, hashfunc=self.hash_func)
    
    def public_key_from_bytes(self, key_bytes: bytes) -> VerifyingKey:
        """
        Десеріалізація публічного ключа
        
        Args:
            key_bytes: 64 байти публічного ключа
            
        Returns:
            Публічний ключ
        """
        return VerifyingKey.from_string(key_bytes, curve=self.curve, hashfunc=self.hash_func)


# Фабрика для зручності
def create_ecdsa_p256() -> ECDSA_P256:
    """
    Створення екземпляру ECDSA P-256
    
    Returns:
        ECDSA_P256 екземпляр
    """
    return ECDSA_P256()


__all__ = ['ECDSA_P256', 'create_ecdsa_p256']
