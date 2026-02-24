"""
ДСТУ 4145-2002: Цифровий підпис на еліптичних кривих
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dstu4145.field import GF2mField, DSTU_FIELDS
    from dstu4145.curve import EllipticCurve, Point, get_dstu_curve_163, get_dstu_curve_257
    from dstu4145.signature import DSTU4145, create_dstu4145_163, create_dstu4145_257
except ImportError:
    from field import GF2mField, DSTU_FIELDS
    from curve import EllipticCurve, Point, get_dstu_curve_163, get_dstu_curve_257
    from signature import DSTU4145, create_dstu4145_163, create_dstu4145_257

__all__ = [
    'GF2mField',
    'DSTU_FIELDS',
    'EllipticCurve',
    'Point',
    'get_dstu_curve_163',
    'get_dstu_curve_257',
    'DSTU4145',
    'create_dstu4145_163',
    'create_dstu4145_257',
]

__version__ = '1.0.0'
