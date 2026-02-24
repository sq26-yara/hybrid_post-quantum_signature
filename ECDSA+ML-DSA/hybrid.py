"""
Гібридний цифровий підпис: ECDSA P-256 + ML-DSA-44 + SHA-256

Комбінація класичного (ECDSA) та постквантового (ML-DSA) алгоритмів
для забезпечення безпеки як від класичних, так і від квантових атак.
"""

import sys
from pathlib import Path
from typing import Tuple, Optional
from dataclasses import dataclass
import json
from datetime import datetime
import hashlib
import time

sys.path.insert(0, str(Path(__file__).parent))

try:
    from ecdsa_wrapper import create_ecdsa_p256
    from mldsa.wrapper import MLDSA44
except ImportError:
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from ecdsa_wrapper import create_ecdsa_p256
    from mldsa.wrapper import MLDSA44


@dataclass
class HybridKeyPair:
    """
    Пара ключів для гібридного підпису ECDSA + ML-DSA
    """
    ecdsa_private_key: any  # SigningKey
    ecdsa_public_key: any   # VerifyingKey
    mldsa_private_key: bytes
    mldsa_public_key: bytes


@dataclass
class HybridSignature:
    """
    Гібридний підпис ECDSA + ML-DSA
    """
    ecdsa_signature: bytes  # 64 байти (r || s)
    mldsa_signature: bytes  # ~2420 байт
    data_hash_sha256: str
    timestamp: str
    algorithm: str = "ECDSA-P256 + ML-DSA-44 + SHA-256"


class HybridECDSA_MLDSA:
    """
    Гібридна схема цифрового підпису: ECDSA P-256 + ML-DSA-44
    
    Використовує:
    - ECDSA з кривою NIST P-256 для класичної безпеки (~128 біт)
    - ML-DSA-44 (FIPS 204) для постквантової безпеки (128 біт)
    - SHA-256 для хешування даних
    
    Верифікація вимагає, щоб обидва підписи були валідними (AND).
    """
    
    def __init__(self):
        """
        Ініціалізація гібридної схеми підпису
        """
        # ECDSA P-256
        self.ecdsa = create_ecdsa_p256()
        
        # ML-DSA-44
        self.mldsa = MLDSA44()
    
    def generate_keypair(self) -> HybridKeyPair:
        """
        Генерація пари ключів для гібридного підпису
        
        Returns:
            HybridKeyPair з ключами ECDSA та ML-DSA
        """
        # Генерація ключів ECDSA
        ecdsa_private, ecdsa_public = self.ecdsa.generate_keypair()
        
        # Генерація ключів ML-DSA
        mldsa_private, mldsa_public = self.mldsa.generate_keypair()
        
        return HybridKeyPair(
            ecdsa_private_key=ecdsa_private,
            ecdsa_public_key=ecdsa_public,
            mldsa_private_key=mldsa_private,
            mldsa_public_key=mldsa_public
        )
    
    def sign(self, data: bytes, keypair: HybridKeyPair) -> HybridSignature:
        """
        Створення гібридного підпису
        
        Args:
            data: Дані для підпису
            keypair: Пара ключів
            
        Returns:
            HybridSignature з обома підписами
        """
        # Хеш даних (SHA-256)
        data_hash = hashlib.sha256(data).hexdigest()
        
        # Підпис ECDSA
        ecdsa_sig = self.ecdsa.sign(data, keypair.ecdsa_private_key)
        
        # Підпис ML-DSA
        mldsa_sig = self.mldsa.sign(data, keypair.mldsa_private_key)
        
        return HybridSignature(
            ecdsa_signature=ecdsa_sig,
            mldsa_signature=mldsa_sig,
            data_hash_sha256=data_hash,
            timestamp=datetime.now().isoformat()
        )
    
    def verify(self, data: bytes, signature: HybridSignature, 
               keypair: HybridKeyPair) -> bool:
        """
        Верифікація гібридного підпису
        
        Args:
            data: Дані
            signature: Гібридний підпис
            keypair: Пара ключів (публічні)
            
        Returns:
            True якщо обидва підписи валідні
        """
        start_time = time.time()
        print("="*70)
        print(f"    Час верифікації гібридного підпису:")

        # Верифікація ECDSA
        ecdsa_valid = self.ecdsa.verify(
            data,
            signature.ecdsa_signature,
            keypair.ecdsa_public_key
        )
        
        # Верифікація ML-DSA
        mldsa_valid = self.mldsa.verify(
            data,
            signature.mldsa_signature,
            keypair.mldsa_public_key
        )
        
        verify_time = time.time() - start_time
        print(f"     Час перевірки гібридного підпису: {verify_time*1000:.2f} мсек")
        print("="*70)
        # Обидва мають бути валідними
        return ecdsa_valid and mldsa_valid
    
    def export_signature(self, signature: HybridSignature) -> str:
        """
        Експорт підпису у JSON формат
        
        Args:
            signature: Гібридний підпис
            
        Returns:
            JSON строка з підписом
        """
        return json.dumps({
            "algorithm": signature.algorithm,
            "timestamp": signature.timestamp,
            "data_hash_sha256": signature.data_hash_sha256,
            "ecdsa_p256": {
                "signature": signature.ecdsa_signature.hex()
            },
            "mldsa44": {
                "signature": signature.mldsa_signature.hex()
            }
        }, indent=2)
    
    def import_signature(self, json_str: str) -> HybridSignature:
        """
        Імпорт підпису з JSON формату
        
        Args:
            json_str: JSON строка
            
        Returns:
            HybridSignature
        """
        data = json.loads(json_str)
        
        return HybridSignature(
            ecdsa_signature=bytes.fromhex(data["ecdsa_p256"]["signature"]),
            mldsa_signature=bytes.fromhex(data["mldsa44"]["signature"]),
            data_hash_sha256=data["data_hash_sha256"],
            timestamp=data["timestamp"],
            algorithm=data["algorithm"]
        )


# Для зручності
def create_hybrid() -> HybridECDSA_MLDSA:
    """
    Створення екземпляру гібридної схеми
    
    Returns:
        HybridECDSA_MLDSA екземпляр
    """
    return HybridECDSA_MLDSA()


if __name__ == "__main__":
    # Демонстрація використання
    print("=" * 70)
    print("Гібридний цифровий підпис: ECDSA P-256 + ML-DSA-44")
    print("=" * 70)
    
    # Ініціалізація
    print("\n1. Ініціалізація...")
    hybrid = create_hybrid()
    print("   ✓ ECDSA P-256 (NIST)")
    print("   ✓ ML-DSA-44 (FIPS 204)")
    
    # Генерація ключів
    print("\n2. Генерація ключів...")
    keypair = hybrid.generate_keypair()
    print("   ✓ Ключі згенеровано")
    
    # Дані для підпису
    test_data = b"Test message for hybrid signature"
    print(f"\n3. Дані: {test_data.decode()}")
    
    # Підпис
    print("\n4. Створення підпису...")
    signature = hybrid.sign(test_data, keypair)
    print("   ✓ Підпис створено")
    print(f"   ECDSA: {len(signature.ecdsa_signature)} байт")
    print(f"   ML-DSA: {len(signature.mldsa_signature)} байт")
    print(f"   Загалом: {len(signature.ecdsa_signature) + len(signature.mldsa_signature)} байт")
    
    # Верифікація
    print("\n5. Верифікація підпису...")
    valid = hybrid.verify(test_data, signature, keypair)
    print(f"   {'✓' if valid else '✗'} Підпис {'валідний' if valid else 'НЕВАЛІДНИЙ'}")
    
    # Експорт
    print("\n6. Експорт підпису...")
    json_sig = hybrid.export_signature(signature)
    print("   ✓ Підпис експортовано в JSON")
    
    print("\n" + "=" * 70)
    print("✅ Демонстрація завершена успішно!")
    print("=" * 70)
