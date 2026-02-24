"""
ML-DSA-44: Постквантовий цифровий підпис (FIPS 204)
Wrapper для liboqs
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from mldsa.wrapper import MLDSA44, create_mldsa44
except ImportError:
    from wrapper import MLDSA44, create_mldsa44

__all__ = [
    'MLDSA44',
    'create_mldsa44',
]

__version__ = '1.0.0'
