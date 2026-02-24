"""
ДСТУ 4145-2002: Цифровий підпис
Формування та перевірка підпису
"""

import secrets
import sys
import time
from pathlib import Path
from typing import Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from kupyna import KUPYNA256
    from dstu4145.field import GF2mField
    from dstu4145.curve import EllipticCurve, Point
except ImportError:
    from kupyna import KUPYNA256
    from field import GF2mField
    from curve import EllipticCurve, Point


class DSTU4145:
    """
    Схема цифрового підпису ДСТУ 4145-2002
    """
    
    def __init__(self, field: GF2mField, curve: EllipticCurve, base_point: Point, n: int):
        """
        Args:
            field: Скінченне поле GF(2^m)
            curve: Еліптична крива
            base_point: Базова точка P
            n: Порядок базової точки
        """
        self.field = field
        self.curve = curve
        self.P = base_point
        self.n = n
        
        # Перевірка параметрів
        if not curve.is_on_curve(base_point):
            raise ValueError("Базова точка не належить кривій")
    
    def hash_data(self, data: bytes) -> bytes:
        """
        Хешування даних за допомогою геш-функції Купина (256 біт)
        
        Args:
            data: Дані для хешування
            
        Returns:
            Хеш (256 біт)
        """
        hasher = KUPYNA256()
        hasher.update(data)
        return hasher.digest()
    
    def hash_to_field_element(self, h: bytes):
        """
        Перетворення хешу на елемент поля (ДСТУ 4145, розділ 5.9)
        
        Args:
            h: Хеш (байти)
            
        Returns:
            Елемент поля
        """
        element = self.field.element_from_bytes(h)
        
        # Якщо h = 0, приймаємо h = 1
        if self.field.is_zero(element):
            element = self.field.one()
        
        return element
    
    def field_element_to_int(self, x) -> int:
        """
        Перетворення елемента поля на ціле число (ДСТУ 4145, розділ 5.8)
        
        Args:
            x: Елемент поля
            
        Returns:
            Ціле число, обрізане до довжини L(n)
        """
        # Конвертуємо елемент поля в ціле число
        value = self.field.element_to_int(x)
        
        # Обрізаємо до довжини L(n) - 1 біт
        n_bit_length = self.n.bit_length()
        mask = (1 << (n_bit_length - 1)) - 1
        
        return value & mask
    
    def generate_keypair(self) -> Tuple[int, Point]:
        """
        Генерація пари ключів (ДСТУ 4145, розділ 9)
        
        Returns:
            (d, Q) де:
            - d: особистий ключ (ціле число)
            - Q: відкритий ключ (точка кривої)
        """
        start_time = time.time()
        # Генеруємо випадковий особистий ключ d, 0 < d < n
        while True:
            d = secrets.randbelow(self.n)
            if d > 0:
                break
        
        # Обчислюємо відкритий ключ Q = dP
        Q = self.curve.multiply(d, self.P)
        keygen_time = time.time() - start_time
        print(f"     Час генерації ключів ДСТУ 4145: {keygen_time:.4f} сек")
        return d, Q
    
    def sign(self, data: bytes, private_key: int) -> Tuple[int, int]:
        """
        Створення цифрового підпису (ДСТУ 4145, розділ 12)
        
        Args:
            data: Дані для підпису
            private_key: Особистий ключ d
            
        Returns:
            (r, s) - цифровий підпис
        """
        # Перевірка особистого ключа
        if not (0 < private_key < self.n):
            raise ValueError("Невірний особистий ключ")

        
        # Крок 6: Обчислити геш
        hash_bytes = self.hash_data(data)
        
        # Крок 7: Перетворити на елемент поля
        h = self.hash_to_field_element(hash_bytes)
        
        # Кроки 8-13: Генерація підпису
        max_attempts = 1000
        for _ in range(max_attempts):
            start_time = time.time()
            # Крок 8: Генеруємо випадкове e, 0 < e < n
            e = secrets.randbelow(self.n)
            if e == 0:
                continue
            
            # Обчислюємо R = eP
            R = self.curve.multiply(e, self.P)
            
            if R.is_infinity:
                continue
            
            # Крок 9: y = h * Fe, де Fe = xR
            Fe = R.x
            y = self.field.multiply(h, Fe)
            
            # Крок 10: Перетворюємо y на ціле число r
            r = self.field_element_to_int(y)
            
            # Крок 11: Перевірка r ≠ 0
            if r == 0:
                continue
            
            # Крок 12: s = (e - dr) mod n
            s = (e - private_key * r) % self.n
            
            # Крок 13: Перевірка s ≠ 0
            if s == 0:
                continue
                
            sign_time = time.time() - start_time
            print(f"     Час підпису за допомогою ДСТУ 4145: {sign_time:.4f} сек")
            # Успішно згенерували підпис
            return (r, s)
        
        raise RuntimeError("Не вдалося створити підпис за 1000 спроб")
    
    def verify(self, data: bytes, signature: Tuple[int, int], public_key: Point) -> bool:
        """
        Перевірка цифрового підпису (ДСТУ 4145, розділ 13)
        
        Args:
            data: Підписані дані
            signature: Цифровий підпис (r, s)
            public_key: Відкритий ключ Q
            
        Returns:
            True - якщо підпис валідний, False - якщо ні
        """

        start_time = time.time()
        r, s = signature
        
        # Крок 10: Перевірка 0 < r < n
        if not (0 < r < self.n):
            return False
        
        # Крок 11: Перевірка 0 < s < n
        if not (0 < s < self.n):
            return False
        
        # Перевірка відкритого ключа
        if not self.curve.is_on_curve(public_key):
            return False
        
        if public_key.is_infinity:
            return False
        
        # Крок 7: Обчислити геш
        hash_bytes = self.hash_data(data)
        
        # Крок 8: Перетворити на елемент поля
        h = self.hash_to_field_element(hash_bytes)
        
        # Крок 12: Обчислити R = sP + rQ
        sP = self.curve.multiply(s, self.P)
        rQ = self.curve.multiply(r, public_key)
        R = self.curve.add(sP, rQ)
        
        if R.is_infinity:
            return False
        
        # Крок 13: y = h * xR
        y = self.field.multiply(h, R.x)
        
        # Крок 14: Перетворити y на ціле число r'
        r_prime = self.field_element_to_int(y)
                
        verify_time = time.time() - start_time
        print(f"     Час перевірки підпису ДСТУ 4145: {verify_time:.4f} сек")
        
        # Крок 15: Перевірка r' == r
        return r_prime == r
    
    def export_signature(self, signature: Tuple[int, int]) -> bytes:
        """
        Експорт підпису в байти
        
        Args:
            signature: (r, s)
            
        Returns:
            Байтове зображення підпису
        """
        r, s = signature
        
        # Довжина кожного компонента (в байтах)
        n_bytes = (self.n.bit_length() + 7) // 8
        
        # Конвертуємо в байти
        r_bytes = r.to_bytes(n_bytes, byteorder='big')
        s_bytes = s.to_bytes(n_bytes, byteorder='big')
        
        return r_bytes + s_bytes
    
    def import_signature(self, signature_bytes: bytes) -> Tuple[int, int]:
        """
        Імпорт підпису з байтів
        
        Args:
            signature_bytes: Байтове зображення підпису
            
        Returns:
            (r, s)
        """
        # Довжина кожного компонента
        n_bytes = (self.n.bit_length() + 7) // 8
        
        if len(signature_bytes) != 2 * n_bytes:
            raise ValueError(f"Невірна довжина підпису: очікується {2 * n_bytes}, отримано {len(signature_bytes)}")
        
        # Витягуємо компоненти
        r = int.from_bytes(signature_bytes[:n_bytes], byteorder='big')
        s = int.from_bytes(signature_bytes[n_bytes:], byteorder='big')
        
        return (r, s)
    
    def export_public_key(self, public_key: Point) -> bytes:
        """Експорт відкритого ключа"""
        if public_key.is_infinity:
            raise ValueError("Не можна експортувати точку O")
        
        # Конвертуємо координати в числа
        x_int = self.field.element_to_int(public_key.x)
        y_int = self.field.element_to_int(public_key.y)
        
        # Довжина в байтах
        byte_len = (self.field.m + 7) // 8
        
        # Конвертуємо в байти
        x_bytes = x_int.to_bytes(byte_len, byteorder='big')
        y_bytes = y_int.to_bytes(byte_len, byteorder='big')
        
        return x_bytes + y_bytes
    
    def import_public_key(self, key_bytes: bytes) -> Point:
        """Імпорт відкритого ключа"""
        byte_len = (self.field.m + 7) // 8
        
        if len(key_bytes) != 2 * byte_len:
            raise ValueError(f"Невірна довжина ключа: очікується {2 * byte_len}, отримано {len(key_bytes)}")
        
        # Відновлюємо координати
        x_int = int.from_bytes(key_bytes[:byte_len], byteorder='big')
        y_int = int.from_bytes(key_bytes[byte_len:], byteorder='big')
        
        x = self.field.element_from_int(x_int)
        y = self.field.element_from_int(y_int)
        
        point = Point(x, y)
        
        if not self.curve.is_on_curve(point):
            raise ValueError("Точка не належить кривій")
        
        return point


def create_dstu4145_163():
    """
    Створення екземпляра ДСТУ 4145 з рекомендованими параметрами для GF(2^163)
    
    Returns:
        Об'єкт DSTU4145
    """
    try:
        from dstu4145.curve import get_dstu_curve_163
    except ImportError:
        from curve import get_dstu_curve_163
    
    field, curve, base_point, n = get_dstu_curve_163()
    return DSTU4145(field, curve, base_point, n)


def create_dstu4145_257():
    """
    Створення екземпляра ДСТУ 4145 з параметрами для GF(2^257)
    Підвищена безпека (~128 біт)
    
    Returns:
        Об'єкт DSTU4145
    """
    try:
        from dstu4145.curve import get_dstu_curve_257
    except ImportError:
        from curve import get_dstu_curve_257
    
    field, curve, base_point, n = get_dstu_curve_257()
    return DSTU4145(field, curve, base_point, n)
