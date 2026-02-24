"""
ДСТУ 4145-2002: Операції в полі GF(2^m)
Реалізація арифметики у скінченних полях характеристики 2
"""

import numpy as np
from typing import Tuple, Optional


class GF2mField:
    """
    Скінченне поле GF(2^m) з поліноміальним базисом
    
    Базис задається примітивним многочленом f(t) степеня m:
    - Тричлен: f(t) = t^m + t^k + 1
    - П'ятичлен: f(t) = t^m + t^k + t^j + t^l + 1
    """
    
    def __init__(self, m: int, polynomial: Tuple[int, ...]):
        """
        Ініціалізація поля GF(2^m)
        
        Args:
            m: Степінь поля (163 <= m <= 509, непарне просте)
            polynomial: Примітивний многочлен у вигляді (m, k) або (m, k, j, l)
                       Для тричлена: (m, k) означає t^m + t^k + 1
                       Для п'ятичлена: (m, k, j, l) означає t^m + t^k + t^j + t^l + 1
        """
        self.m = m
        self.polynomial = polynomial
        
        # Перевірка параметрів
        if m < 163 or m > 509:
            raise ValueError(f"Степінь поля m={m} поза допустимим діапазоном [163, 509]")
        
        if m % 2 == 0:
            raise ValueError(f"Степінь поля m={m} має бути непарним")
        
        # Визначення типу базису
        if len(polynomial) == 2:
            self.basis_type = "trinomial"
            self.k = polynomial[1]
        elif len(polynomial) == 4:
            self.basis_type = "pentanomial"
            self.k, self.j, self.l = polynomial[1], polynomial[2], polynomial[3]
        else:
            raise ValueError("Поліном має бути тричленом (m, k) або п'ятичленом (m, k, j, l)")
    
    def __repr__(self) -> str:
        if self.basis_type == "trinomial":
            return f"GF(2^{self.m}) з базисом t^{self.m} + t^{self.k} + 1"
        else:
            return f"GF(2^{self.m}) з базисом t^{self.m} + t^{self.k} + t^{self.j} + t^{self.l} + 1"
    
    def element_from_int(self, value: int) -> np.ndarray:
        """
        Створити елемент поля з цілого числа
        
        Args:
            value: Ціле число
            
        Returns:
            Елемент поля у вигляді бітового масиву довжини m
        """
        bits = np.zeros(self.m, dtype=np.uint8)
        for i in range(min(self.m, value.bit_length())):
            if value & (1 << i):
                bits[i] = 1
        return bits
    
    def element_from_bytes(self, data: bytes) -> np.ndarray:
        """
        Створити елемент поля з байтів
        
        Args:
            data: Байтові дані
            
        Returns:
            Елемент поля
        """
        # Конвертуємо байти в біти
        bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))
        
        # Обрізаємо або доповнюємо до m біт
        if len(bits) > self.m:
            bits = bits[:self.m]
        elif len(bits) < self.m:
            bits = np.pad(bits, (0, self.m - len(bits)), 'constant')
        
        return bits[::-1]  # Зворотній порядок (LSB перший)
    
    def element_to_int(self, element: np.ndarray) -> int:
        """
        Конвертувати елемент поля в ціле число
        
        Args:
            element: Елемент поля
            
        Returns:
            Ціле число
        """
        result = 0
        for i in range(self.m):
            if element[i]:
                result |= (1 << i)
        return result
    
    def element_to_bytes(self, element: np.ndarray) -> bytes:
        """
        Конвертувати елемент поля в байти
        
        Args:
            element: Елемент поля
            
        Returns:
            Байти
        """
        # Доповнюємо до кратності 8
        padded_len = ((self.m + 7) // 8) * 8
        padded = np.pad(element[::-1], (padded_len - self.m, 0), 'constant')
        return np.packbits(padded).tobytes()
    
    def add(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Додавання в GF(2^m): a + b = a XOR b
        
        Args:
            a, b: Елементи поля
            
        Returns:
            Сума a + b
        """
        return np.bitwise_xor(a, b)
    
    def multiply(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Множення в GF(2^m) за модулем примітивного многочлена
        
        Args:
            a, b: Елементи поля
            
        Returns:
            Добуток a * b
        """
        # Результат
        result = np.zeros(self.m, dtype=np.uint8)
        
        # Копія b для накопичення
        temp_b = b.copy()
        
        # Множення зсувом і додаванням
        for i in range(self.m):
            if a[i]:
                result = self.add(result, temp_b)
            
            # Зсув temp_b вліво на 1
            high_bit = temp_b[-1]
            temp_b = np.roll(temp_b, 1)
            temp_b[0] = 0
            
            # Якщо вийшли за межі, віднімаємо многочлен
            if high_bit:
                # Застосовуємо редукцію за модулем примітивного многочлена
                if self.basis_type == "trinomial":
                    temp_b[0] = 1 - temp_b[0]  # +1
                    temp_b[self.k] = 1 - temp_b[self.k]  # +t^k
                else:  # pentanomial
                    temp_b[0] = 1 - temp_b[0]  # +1
                    temp_b[self.l] = 1 - temp_b[self.l]  # +t^l
                    temp_b[self.j] = 1 - temp_b[self.j]  # +t^j
                    temp_b[self.k] = 1 - temp_b[self.k]  # +t^k
        
        return result
    
    def square(self, a: np.ndarray) -> np.ndarray:
        """
        Піднесення до квадрату в GF(2^m)
        В полях характеристики 2: a^2 = a * a
        
        Args:
            a: Елемент поля
            
        Returns:
            Квадрат a^2
        """
        return self.multiply(a, a)
    
    def power(self, a: np.ndarray, n: int) -> np.ndarray:
        """
        Піднесення до степеня a^n в GF(2^m)
        
        Args:
            a: Елемент поля
            n: Степінь
            
        Returns:
            Результат a^n
        """
        if n == 0:
            return self.element_from_int(1)  # Одиниця поля
        
        if n == 1:
            return a.copy()
        
        # Метод бінарного піднесення до степеня
        result = self.element_from_int(1)
        base = a.copy()
        
        while n > 0:
            if n & 1:
                result = self.multiply(result, base)
            base = self.square(base)
            n >>= 1
        
        return result
    
    def inverse(self, a: np.ndarray) -> Optional[np.ndarray]:
        """
        Обчислення оберненого елемента a^(-1) в GF(2^m)
        Використовуємо малу теорему Ферма: a^(-1) = a^(2^m - 2)
        
        Args:
            a: Елемент поля (не нуль)
            
        Returns:
            Обернений елемент або None якщо a = 0
        """
        if not np.any(a):  # Якщо a = 0
            return None
        
        # a^(-1) = a^(2^m - 2)
        exponent = (1 << self.m) - 2
        return self.power(a, exponent)
    
    def trace(self, a: np.ndarray) -> int:
        """
        Обчислення сліду елемента (ДСТУ 4145, згідно розділу 6.5)
        tr(a) = a + a^2 + a^4 + ... + a^(2^(m-1))
        
        Args:
            a: Елемент поля
            
        Returns:
            Слід (0 або 1)
        """
        result = a.copy()
        temp = a.copy()
        
        for _ in range(self.m - 1):
            temp = self.square(temp)
            result = self.add(result, temp)
        
        # Слід завжди 0 або 1
        return int(result[0])
    
    def half_trace(self, a: np.ndarray) -> np.ndarray:
        """
        Обчислення напівсліду елемента (ДСТУ 4145, згідно розділу 6.6)
        htr(a) = a + a^4 + a^16 + ... + a^(2^(2*((m-1)//2)))
        Тільки для непарних m
        
        Args:
            a: Елемент поля
            
        Returns:
            Напівслід
        """
        if self.m % 2 == 0:
            raise ValueError("Напівслід визначений тільки для непарного m")
        
        result = a.copy()
        temp = a.copy()
        
        for _ in range((self.m - 1) // 2):
            temp = self.square(self.square(temp))  # a^4
            result = self.add(result, temp)
        
        return result
    
    def solve_quadratic(self, u: np.ndarray, w: np.ndarray) -> Tuple[int, Optional[np.ndarray]]:
        """
        Розв'язання квадратного рівняння z^2 + uz + w = 0 в GF(2^m)
        (ДСТУ 4145, розділ 6.7)
        
        Args:
            u, w: Коефіцієнти рівняння
            
        Returns:
            (count, solution) де:
            - count: кількість розв'язків (0, 1, або 2)
            - solution: один з розв'язків якщо count > 0
        """
        # Випадок u = 0
        if not np.any(u):
            if not np.any(w):
                return (2, np.zeros(self.m, dtype=np.uint8))  # z = 0
            else:
                # z = w^(1/2) = w^(2^(m-1))
                sqrt_w = self.power(w, 1 << (self.m - 1))
                return (1, sqrt_w)
        
        # Випадок w = 0
        if not np.any(w):
            return (2, np.zeros(self.m, dtype=np.uint8))  # z = 0
        
        # Загальний випадок
        # v = w / u^2
        u_squared = self.square(u)
        u_inv = self.inverse(u_squared)
        if u_inv is None:
            return (0, None)
        
        v = self.multiply(w, u_inv)
        
        # Перевірка розв'язності: tr(v) має бути 0
        if self.trace(v) != 0:
            return (0, None)
        
        # z = htr(v) * u
        htr_v = self.half_trace(v)
        z = self.multiply(htr_v, u)
        
        return (2, z)
    
    def is_zero(self, a: np.ndarray) -> bool:
        """Перевірка чи елемент дорівнює нулю"""
        return not np.any(a)
    
    def is_one(self, a: np.ndarray) -> bool:
        """Перевірка чи елемент дорівнює одиниці"""
        one = self.element_from_int(1)
        return np.array_equal(a, one)
    
    def zero(self) -> np.ndarray:
        """Нульовий елемент поля"""
        return np.zeros(self.m, dtype=np.uint8)
    
    def one(self) -> np.ndarray:
        """Одиничний елемент поля"""
        return self.element_from_int(1)
    
    def random_element(self) -> np.ndarray:
        """Генерація випадкового елемента поля"""
        return np.random.randint(0, 2, self.m, dtype=np.uint8)


# Задамо три поля з поліноміальним базисом згідно табл. 1 ДСТУ 4145 
DSTU_FIELDS = {
    163: GF2mField(163, (163, 7, 6, 3)),  # t^163 + t^7 + t^6 + t^3 + 1
    173: GF2mField(173, (173, 10, 2, 1)),  # t^173 + t^10 + t^2 + t + 1
    257: GF2mField(257, (257, 12)),        # t^257 + t^12 + 1 (тричлен)
}
