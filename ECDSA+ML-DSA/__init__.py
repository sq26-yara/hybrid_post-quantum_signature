"""
ECDSA + ML-DSA Hybrid Signature

Гібридна схема цифрового підпису, що комбінує:
- ECDSA P-256 (NIST) - класичний підпис
- ML-DSA-44 (FIPS 204) - постквантовий підпис
- SHA-256 - хеш-функція
"""

from .hybrid import HybridECDSA_MLDSA, HybridKeyPair, HybridSignature, create_hybrid
from .ecdsa_wrapper import ECDSA_P256, create_ecdsa_p256

__version__ = "1.0.0"
__author__ = "ECDSA+ML-DSA Hybrid Project"

__all__ = [
    'HybridECDSA_MLDSA',
    'HybridKeyPair',
    'HybridSignature',
    'create_hybrid',
    'ECDSA_P256',
    'create_ecdsa_p256',
]
