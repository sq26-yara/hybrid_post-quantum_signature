"""
ML-DSA (Dilithium): Постквантовий цифровий підпис
Wrapper для liboqs-python
"""

from typing import Tuple
import oqs
import time


class MLDSA44:
    """
    ML-DSA-44 (FIPS 204) цифровий підпис
    """
    
    # Назва алгоритму в liboqs
    ALGORITHM = "ML-DSA-44"
    
    def __init__(self):
        """Ініціалізація ML-DSA-44"""
        # Перевірка доступності алгоритму
        if self.ALGORITHM not in oqs.get_enabled_sig_mechanisms():
            # Спроба альтернативних назв
            alternatives = ["Dilithium2", "ML-DSA-44-ipd"]
            for alt in alternatives:
                if alt in oqs.get_enabled_sig_mechanisms():
                    self.ALGORITHM = alt
                    break
            else:
                raise RuntimeError(
                    f"ML-DSA-44 не доступний. "
                    f"Доступні алгоритми: {oqs.get_enabled_sig_mechanisms()}"
                )
        
        print(f"    ML-DSA ініціалізовано (використовується {self.ALGORITHM})")
    
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """
        Генерація пари ключів ML-DSA-44
        
        Returns:
            (private_key, public_key) у вигляді байтів
        """
        start_time = time.time()
        
        with oqs.Signature(self.ALGORITHM) as signer:
            public_key = signer.generate_keypair()
            private_key = signer.export_secret_key()
            
        keygen_time = time.time() - start_time
        print(f"     Час генерації ключів ML-DSA-44: {keygen_time:.4f} сек")
        
        return private_key, public_key
    
    def sign(self, data: bytes, private_key: bytes) -> bytes:
        """
        Створення підпису ML-DSA-44
        
        Args:
            data: Дані для підпису
            private_key: Приватний ключ
            
        Returns:
            Підпис
        """

        start_time = time.time()
        
        with oqs.Signature(self.ALGORITHM, private_key) as signer:
            signature = signer.sign(data)

        sign_time = time.time() - start_time
        print(f"     Час підпису за допомогою ML-DSA-44: {sign_time:.4f} сек")
        
        return signature
    
    def verify(self, data: bytes, signature: bytes, public_key: bytes) -> bool:
        """
        Перевірка підпису ML-DSA-44
        
        Args:
            data: Підписані дані
            signature: Підпис
            public_key: Публічний ключ
            
        Returns:
            True якщо підпис валідний, False інакше
        """
                
        try:
            with oqs.Signature(self.ALGORITHM) as verifier:
                start_time = time.time()
                is_valid = verifier.verify(data, signature, public_key)
                verify_time = time.time() - start_time
                print(f"     Час перевірки підпису ML-DSA-44: {verify_time:.4f} сек")
            return is_valid
        except Exception:
            return False
    
    @property
    def public_key_length(self) -> int:
        """Довжина публічного ключа в байтах"""
        with oqs.Signature(self.ALGORITHM) as sig:
            return sig.length_public_key
    
    @property
    def private_key_length(self) -> int:
        """Довжина приватного ключа в байтах"""
        with oqs.Signature(self.ALGORITHM) as sig:
            return sig.length_secret_key
    
    @property
    def signature_length(self) -> int:
        """Довжина підпису в байтах"""
        with oqs.Signature(self.ALGORITHM) as sig:
            return sig.length_signature


def create_mldsa44() -> MLDSA44:
    """
    Створення екземпляра ML-DSA-44
    
    Returns:
        Об'єкт MLDSA44
    """
    return MLDSA44()
