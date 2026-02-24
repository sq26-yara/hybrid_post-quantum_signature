"""
Pure Hybrid Signature: ДСТУ 4145 + ML-DSA-44

Верифікація: DSTU4145.verify() AND MLDSA44.verify()
"""

import json
import base64
from kupyna import Kupyna256
import sys
from pathlib import Path
from typing import Tuple, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Додаємо поточну директорію до шляху
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from dstu4145 import DSTU4145, create_dstu4145_257, Point
    from mldsa import MLDSA44, create_mldsa44
except ImportError:
    # Fallback для запуску з різних місць
    sys.path.insert(0, str(current_dir / 'dstu4145'))
    sys.path.insert(0, str(current_dir / 'mldsa'))
    from dstu4145 import DSTU4145, create_dstu4145_257, Point
    from mldsa import MLDSA44, create_mldsa44


@dataclass
class HybridKeyPair:
    """Гібридна пара ключів"""
    # DSTU 4145 ключі
    dstu_private_key: int
    dstu_public_key_bytes: bytes
    
    # ML-DSA-44 ключі
    mldsa_private_key: bytes
    mldsa_public_key: bytes
    
    # Метадані
    created_at: str
    key_id: str


@dataclass
class HybridSignature:
    """Гібридний підпис"""
    # Підписи
    dstu_signature: Tuple[int, int]  # (r, s)
    mldsa_signature: bytes
    
    # Метадані
    algorithm: str = "DSTU-4145 + ML-DSA-44 + Купина-256"
    timestamp: str = ""
    data_hash_kupyna: str = ""


class PureHybridSignature:
    
    def __init__(self):
        """Ініціалізація гібридної схеми"""
        print("=" * 70)
        print("PURE HYBRID SIGNATURE")
        print("=" * 70)
        print("Ініціалізація...")
        
        # Ініціалізуємо ДСТУ 4145 з GF(2^257)
        print("\n1. ДСТУ 4145-2002:")
        self.dstu = create_dstu4145_257()
        print(f"    Поле: GF(2^{self.dstu.field.m})")
        print(f"    Крива: y^2 + xy = x^3 + {self.dstu.curve.A}x^2 + B")
        print(f"    Порядок: {hex(self.dstu.n)[:64]}...")
        print(f"    Хеш: Купина-256 (ДСТУ 7564:2014)")
        
        # Ініціалізуємо ML-DSA-44
        print("\n2. ML-DSA-44:")
        self.mldsa = create_mldsa44()
        print(f"    Публічний ключ: {self.mldsa.public_key_length} байт")
        print(f"    Приватний ключ: {self.mldsa.private_key_length} байт")
        print(f"    Підпис: {self.mldsa.signature_length} байт")
        
        print("\n" + "=" * 70)
        print(" Гібридна схема готова (ДСТУ 4145(2^257) + ML-DSA-44 + Купина-256)")
        print("=" * 70)
    
    def generate_keypair(self, key_id: str = None) -> HybridKeyPair:
        """
        Генерація гібридної пари ключів
        
        Args:
            key_id: Ідентифікатор ключа (опціонально)
            
        Returns:
            Гібридна пара ключів
        """
        print("\n Генерація гібридної пари ключів...")
        
        # Генеруємо ключі ДСТУ 4145
        print("  1. ДСТУ 4145:")
        dstu_priv, dstu_pub = self.dstu.generate_keypair()
        dstu_pub_bytes = self.dstu.export_public_key(dstu_pub)
        print(f"      Приватний ключ: {hex(dstu_priv)[:20]}...")
        print(f"      Публічний ключ: {len(dstu_pub_bytes)} байт")
        
        # Генеруємо ключі ML-DSA-44
        print("  2. ML-DSA-44:")
        mldsa_priv, mldsa_pub = self.mldsa.generate_keypair()
        print(f"      Приватний ключ: {len(mldsa_priv)} байт")
        print(f"      Публічний ключ: {len(mldsa_pub)} байт")
        
        # Створюємо гібридну пару
        keypair = HybridKeyPair(
            dstu_private_key=dstu_priv,
            dstu_public_key_bytes=dstu_pub_bytes,
            mldsa_private_key=mldsa_priv,
            mldsa_public_key=mldsa_pub,
            created_at=datetime.now().isoformat(),
            key_id=key_id or f"hybrid-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        
        print(f"\n Гібридна пара ключів згенерована: {keypair.key_id}")
        return keypair
    
    def sign(self, data: bytes, keypair: HybridKeyPair) -> HybridSignature:
        """
        Створення гібридного підпису
        
        Args:
            data: Дані для підпису
            keypair: Гібридна пара ключів
            
        Returns:
            Гібридний підпис
        """
        print("\n  Створення гібридного підпису...")
        print(f"   Дані: {len(data)} байт")
        
        # Обчислюємо хеш даних за допомогою Купина-256
        kupyna = Kupyna256()
        data_hash = kupyna.hash(data).hex()
        
        # Підпис ДСТУ 4145
        print("   1. ДСТУ 4145...")
        dstu_sig = self.dstu.sign(data, keypair.dstu_private_key)
        print(f"       Підпис: (r={hex(dstu_sig[0])[:20]}..., s={hex(dstu_sig[1])[:20]}...)")
        
        # Підпис ML-DSA-44
        print("   2. ML-DSA-44...")
        mldsa_sig = self.mldsa.sign(data, keypair.mldsa_private_key)
        print(f"       Підпис: {len(mldsa_sig)} байт")
        
        # Створюємо гібридний підпис
        signature = HybridSignature(
            dstu_signature=dstu_sig,
            mldsa_signature=mldsa_sig,
            timestamp=datetime.now().isoformat(),
            data_hash_kupyna=data_hash
        )
        
        total_size = len(self.dstu.export_signature(dstu_sig)) + len(mldsa_sig)
        print(f"\n Гібридний підпис створено ({total_size} байт)")
        
        return signature
    
    def verify(self, data: bytes, signature: HybridSignature, keypair: HybridKeyPair) -> Dict[str, Any]:
        """
        Верифікація гібридного підпису
        
        Args:
            data: Підписані дані
            signature: Гібридний підпис
            keypair: Гібридна пара ключів (публічні ключі)
            
        Returns:
            Словник з результатами верифікації
        """
        print("\n Верифікація гібридного підпису...")
        
        results = {
            'valid': False,
            'dstu_valid': False,
            'mldsa_valid': False,
            'timestamp': signature.timestamp,
            'errors': []
        }
        
        # Верифікація ДСТУ 4145
        print("   1. ДСТУ 4145...")
        try:
            dstu_pub = self.dstu.import_public_key(keypair.dstu_public_key_bytes)
            dstu_valid = self.dstu.verify(data, signature.dstu_signature, dstu_pub)
            results['dstu_valid'] = dstu_valid
            print(f"      {'' if dstu_valid else ''} {'ВАЛІДНИЙ' if dstu_valid else 'НЕВАЛІДНИЙ'}")
        except Exception as e:
            print(f"       Помилка: {e}")
            results['errors'].append(f"DSTU: {e}")
        
        # Верифікація ML-DSA-44
        print("   2. ML-DSA-44...")
        try:
            mldsa_valid = self.mldsa.verify(data, signature.mldsa_signature, keypair.mldsa_public_key)
            results['mldsa_valid'] = mldsa_valid
            print(f"      {'' if mldsa_valid else ''} {'ВАЛІДНИЙ' if mldsa_valid else 'НЕВАЛІДНИЙ'}")
        except Exception as e:
            print(f"       Помилка: {e}")
            results['errors'].append(f"ML-DSA: {e}")
        
        # Гібридна валідність: ОБИДВА мають бути валідні
        results['valid'] = results['dstu_valid'] and results['mldsa_valid']
        
        print(f"\n{'' if results['valid'] else ''} Гібридний підпис: {'ВАЛІДНИЙ' if results['valid'] else 'НЕВАЛІДНИЙ'}")
        
        return results
    
    def export_signature_json(self, signature: HybridSignature) -> str:
        """
        Експорт підпису в JSON
        
        Args:
            signature: Гібридний підпис
            
        Returns:
            JSON рядок
        """
        dstu_r, dstu_s = signature.dstu_signature
        
        data = {
            "algorithm": signature.algorithm,
            "timestamp": signature.timestamp,
            "data_hash_kupyna": signature.data_hash_kupyna,
            "dstu4145": {
                "r": hex(dstu_r),
                "s": hex(dstu_s)
            },
            "mldsa44": {
                "signature": base64.b64encode(signature.mldsa_signature).decode('utf-8')
            }
        }
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def import_signature_json(self, json_str: str) -> HybridSignature:
        """
        Імпорт підпису з JSON
        
        Args:
            json_str: JSON рядок
            
        Returns:
            Гібридний підпис
        """
        data = json.loads(json_str)
        
        dstu_r = int(data["dstu4145"]["r"], 16)
        dstu_s = int(data["dstu4145"]["s"], 16)
        mldsa_sig = base64.b64decode(data["mldsa44"]["signature"])
        
        return HybridSignature(
            dstu_signature=(dstu_r, dstu_s),
            mldsa_signature=mldsa_sig,
            algorithm=data["algorithm"],
            timestamp=data["timestamp"],
            data_hash_kupyna=data["data_hash_kupyna"]
        )
    
    def export_keypair_json(self, keypair: HybridKeyPair, include_private: bool = True) -> str:
        """
        Експорт ключів в JSON
        
        Args:
            keypair: Гібридна пара ключів
            include_private: Чи включати приватні ключі
            
        Returns:
            JSON рядок
        """
        data = {
            "key_id": keypair.key_id,
            "created_at": keypair.created_at,
            "algorithm": "DSTU-4145 + ML-DSA-44",
            "public_keys": {
                "dstu4145": base64.b64encode(keypair.dstu_public_key_bytes).decode('utf-8'),
                "mldsa44": base64.b64encode(keypair.mldsa_public_key).decode('utf-8')
            }
        }
        
        if include_private:
            data["private_keys"] = {
                "dstu4145": hex(keypair.dstu_private_key),
                "mldsa44": base64.b64encode(keypair.mldsa_private_key).decode('utf-8')
            }
        
        return json.dumps(data, indent=2, ensure_ascii=False)


def create_hybrid_scheme() -> PureHybridSignature:
    """
    Створення гібридної схеми підпису
    
    Returns:
        Об'єкт PureHybridSignature
    """
    return PureHybridSignature()
