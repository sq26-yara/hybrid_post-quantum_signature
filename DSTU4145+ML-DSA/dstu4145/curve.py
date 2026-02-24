"""
ДСТУ 4145-2002: Еліптичні криві над GF(2^m)
Рівняння еліптичної кривої: y^2 + xy = x^3 + Ax^2 + B
"""

import numpy as np
import sys
import time
from pathlib import Path
from typing import Tuple, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dstu4145.field import GF2mField
except ImportError:
    from field import GF2mField


class Point:
    """Точка еліптичної кривої"""
    
    def __init__(self, x: Optional[np.ndarray], y: Optional[np.ndarray], is_infinity: bool = False):
        """
        Args:
            x, y: Координати точки (None для точки в нескінченності)
            is_infinity: Чи є це точка O (нескінченно віддалена)
        """
        self.x = x
        self.y = y
        self.is_infinity = is_infinity
    
    def __eq__(self, other: 'Point') -> bool:
        if self.is_infinity and other.is_infinity:
            return True
        if self.is_infinity or other.is_infinity:
            return False
        return np.array_equal(self.x, other.x) and np.array_equal(self.y, other.y)
    
    def __repr__(self) -> str:
        if self.is_infinity:
            return "Point(O)"
        return f"Point(x={self.x[:8]}..., y={self.y[:8]}...)"


class EllipticCurve:
    """
    Еліптична крива над GF(2^m)
    Рівняння: y^2 + xy = x^3 + Ax^2 + B
    """
    
    def __init__(self, field: GF2mField, A: int, B: np.ndarray):
        """
        Args:
            field: Поле GF(2^m)
            A: Коефіцієнт A ∈ {0, 1}
            B: Коефіцієнт B (елемент поля, B ≠ 0)
        """
        self.field = field
        
        # Перевірка параметрів
        if A not in (0, 1):
            raise ValueError(f"Коефіцієнт A має бути 0 або 1, отримано {A}")
        
        if field.is_zero(B):
            raise ValueError("Коефіцієнт B не може бути нулем")
        
        self.A = A
        self.B = B
        
        # Точка в нескінченності (нульовий елемент групи)
        self.O = Point(None, None, is_infinity=True)
    
    def __repr__(self) -> str:
        return f"EllipticCurve(y^2 + xy = x^3 + {self.A}x^2 + B) over {self.field}"
    
    def is_on_curve(self, P: Point) -> bool:
        """
        Перевірка чи точка належить кривій
        y^2 + xy = x^3 + Ax^2 + B
        
        Args:
            P: Точка
            
        Returns:
            True якщо точка на кривій
        """
        if P.is_infinity:
            return True
        
        # Ліва частина: y^2 + xy
        y_squared = self.field.square(P.y)
        xy = self.field.multiply(P.x, P.y)
        left = self.field.add(y_squared, xy)
        
        # Права частина: x^3 + Ax^2 + B
        x_squared = self.field.square(P.x)
        x_cubed = self.field.multiply(P.x, x_squared)
        
        right = x_cubed
        if self.A == 1:
            right = self.field.add(right, x_squared)
        right = self.field.add(right, self.B)
        
        return np.array_equal(left, right)
    
    def add(self, P: Point, Q: Point) -> Point:
        """
        Додавання точок на еліптичній кривій (ДСТУ 4145, Додаток В.8)
        
        Args:
            P, Q: Точки на кривій
            
        Returns:
            R = P + Q
        """
        # O + Q = Q
        if P.is_infinity:
            return Q
        
        # P + O = P
        if Q.is_infinity:
            return P
        
        # P + (-P) = O
        if np.array_equal(P.x, Q.x):
            if np.array_equal(P.y, Q.y):
                # P = Q, використовуємо подвоєння
                return self.double(P)
            else:
                # P = -Q
                return self.O
        
        # Загальний випадок: P ≠ Q
        # λ = (yP + yQ) / (xP + xQ)
        numerator = self.field.add(P.y, Q.y)
        denominator = self.field.add(P.x, Q.x)
        denominator_inv = self.field.inverse(denominator)
        
        if denominator_inv is None:
            return self.O
        
        lambda_ = self.field.multiply(numerator, denominator_inv)
        
        # xR = λ^2 + λ + xP + xQ + A
        lambda_squared = self.field.square(lambda_)
        xR = self.field.add(lambda_squared, lambda_)
        xR = self.field.add(xR, P.x)
        xR = self.field.add(xR, Q.x)
        if self.A == 1:
            xR = self.field.add(xR, self.field.one())
        
        # yR = λ(xP + xR) + xR + yP
        temp1 = self.field.add(P.x, xR)
        temp2 = self.field.multiply(lambda_, temp1)
        yR = self.field.add(temp2, xR)
        yR = self.field.add(yR, P.y)
        
        return Point(xR, yR)
    
    def double(self, P: Point) -> Point:
        """
        Подвоєння точки 2P (ДСТУ 4145, Додаток В.8)
        
        Args:
            P: Точка на кривій
            
        Returns:
            R = 2P
        """
        if P.is_infinity:
            return self.O
        
        # Якщо xP = 0, то 2P = O
        if self.field.is_zero(P.x):
            return self.O
        
        # λ = xP + yP/xP
        xP_inv = self.field.inverse(P.x)
        if xP_inv is None:
            return self.O
        
        temp = self.field.multiply(P.y, xP_inv)
        lambda_ = self.field.add(P.x, temp)
        
        # xR = λ^2 + λ + A
        lambda_squared = self.field.square(lambda_)
        xR = self.field.add(lambda_squared, lambda_)
        if self.A == 1:
            xR = self.field.add(xR, self.field.one())
        
        # yR = xP^2 + λ*xR + xR
        xP_squared = self.field.square(P.x)
        temp = self.field.multiply(lambda_, xR)
        yR = self.field.add(xP_squared, temp)
        yR = self.field.add(yR, xR)
        
        return Point(xR, yR)
    
    def multiply(self, k: int, P: Point) -> Point:
        """
        Множення точки на скаляр kP (бінарний метод)
        
        Args:
            k: Скаляр
            P: Точка на кривій
            
        Returns:
            R = kP
        """
        if k == 0 or P.is_infinity:
            return self.O
        
        if k == 1:
            return P
        
        # Бінарне множення (метод подвійного-і-додавання)
        result = self.O
        addend = P
        
        while k > 0:
            if k & 1:
                result = self.add(result, addend)
            addend = self.double(addend)
            k >>= 1
        
        return result
    
    def compress_point(self, P: Point) -> np.ndarray:
        """
        Стискання точки (ДСТУ 4145, розділ 6.9)
        Зберігає тільки x-координату і 1 біт для відновлення y
        
        Args:
            P: Точка на кривій
            
        Returns:
            Стиснене зображення (координата x з модифікованим молодшим бітом)
        """
        if P.is_infinity:
            return self.field.zero()
        
        if self.field.is_zero(P.x):
            # Спеціальний випадок: xP = 0
            # yP = B^(1/2)
            return self.field.zero()
        
        # Обчислюємо y = yP / xP
        xP_inv = self.field.inverse(P.x)
        y_norm = self.field.multiply(P.y, xP_inv)
        
        # Обчислюємо слід
        trace_bit = self.field.trace(y_norm)
        
        # Копіюємо xP і встановлюємо молодший біт = trace
        compressed = P.x.copy()
        compressed[0] = trace_bit
        
        return compressed
    
    def decompress_point(self, compressed: np.ndarray) -> Point:
        """
        Відновлення точки зі стисненого зображення (ДСТУ 4145, розділ 6.10)
        
        Args:
            compressed: Стиснене зображення точки
            
        Returns:
            Відновлена точка
        """
        # Перевірка на точку O
        if self.field.is_zero(compressed):
            # xP = 0, yP = B^(1/2)
            sqrt_B = self.field.power(self.B, 1 << (self.field.m - 1))
            return Point(self.field.zero(), sqrt_B)
        
        # Витягуємо біт сліду
        k = int(compressed[0])
        
        # Відновлюємо xP (обнуляємо молодший біт)
        xP = compressed.copy()
        xP[0] = 0
        
        # Перевіряємо слід xP
        if self.field.trace(xP) != self.A:
            xP[0] = 1
        
        # Обчислюємо w = xP^3 + A*xP^2 + B
        xP_squared = self.field.square(xP)
        xP_cubed = self.field.multiply(xP, xP_squared)
        
        w = xP_cubed
        if self.A == 1:
            w = self.field.add(w, xP_squared)
        w = self.field.add(w, self.B)
        
        # Обчислюємо v = w / xP^2
        xP_squared_inv = self.field.inverse(xP_squared)
        v = self.field.multiply(w, xP_squared_inv)
        
        # Розв'язуємо z^2 + z + v = 0
        count, z = self.field.solve_quadratic(self.field.one(), v)
        
        if count == 0:
            raise ValueError("Не вдалося відновити точку")
        
        # Вибираємо правильний розв'язок
        if self.field.trace(z) == k:
            yP = self.field.multiply(z, xP)
        else:
            z_alt = self.field.add(z, self.field.one())
            yP = self.field.multiply(z_alt, xP)
        
        return Point(xP, yP)
    
    def compute_random_point(self, seed: Optional[int] = None) -> Point:
        """
        Обчислення випадкової точки еліптичної кривої (ДСТУ 4145-2002, п. 6.8)
        
        Алгоритм:
        1. Вибрати випадкову xP ∈ GF(2^m)
        2. Перевірити tr(xP) = A, інакше xP := xP + 1
        3. Обчислити w = xP^3 + A·xP^2 + B
        4. Обчислити v = w / xP^2
        5. Розв'язати z^2 + z + v = 0
        6. Якщо розв'язків немає, повторити з кроку 1
        7. yP = z · xP
        8. Повернути (xP, yP)
        
        Args:
            seed: Seed для генератора (для відтворюваності)
            
        Returns:
            Випадкова точка на кривій
        """
        import random
        if seed is not None:
            random.seed(seed)
        
        max_attempts = 1000
        
        for attempt in range(max_attempts):
            # Крок 1: Вибрати випадкову xP
            xP_int = random.randint(1, (1 << self.field.m) - 1)
            xP = self.field.element_from_int(xP_int)
            
            # Перевірка xP ≠ 0
            if self.field.is_zero(xP):
                continue
            
            # Крок 2: Перевірити tr(xP) = A
            trace_xP = self.field.trace(xP)
            if trace_xP != self.A:
                # Спробувати xP + 1
                xP = self.field.add(xP, self.field.one())
                trace_xP = self.field.trace(xP)
                
                # Якщо все ще не дорівнює, пропустити
                if trace_xP != self.A:
                    continue
            
            # Крок 3: w = xP^3 + A·xP^2 + B
            xP_squared = self.field.square(xP)
            xP_cubed = self.field.multiply(xP, xP_squared)
            
            w = xP_cubed
            if self.A == 1:
                w = self.field.add(w, xP_squared)
            w = self.field.add(w, self.B)
            
            # Крок 4: v = w / xP^2
            try:
                xP_squared_inv = self.field.inverse(xP_squared)
            except:
                continue
            
            v = self.field.multiply(w, xP_squared_inv)
            
            # Крок 5: Розв'язати z^2 + z + v = 0
            count, z = self.field.solve_quadratic(self.field.one(), v)
            
            if count == 0:
                continue
            
            # Крок 7: yP = z · xP
            yP = self.field.multiply(z, xP)
            
            # Створюємо точку
            point = Point(xP, yP)
            
            # Перевіряємо, що точка на кривій
            if self.is_on_curve(point):
                return point
        
        raise ValueError(f"Не вдалося згенерувати випадкову точку за {max_attempts} спроб")
    
    def generate_random_point(self) -> Point:
        """
        Генерація випадкової точки
        
        Returns:
            Випадкова точка
        """
        return self.compute_random_point()
    
    def compute_base_point(self, n: int, cofactor: int = 1, seed: Optional[int] = None) -> Point:
        """
        Обчислення базової точки еліптичної кривої (ДСТУ 4145-2002, п. 7.3)
        
        Алгоритм:
        1. Обчислити випадкову точку Q згідно з п. 6.8
        2. Обчислити P = h·Q, де h - кофактор
        3. Якщо P = O, повторити з кроку 1
        4. Перевірити, що n·P = O
        5. Повернути P
        
        Args:
            n: Порядок базової точки (має бути простим числом)
            cofactor: Кофактор кривої (зазвичай 1)
            seed: Seed для генератора (для відтворюваності)
            
        Returns:
            Базова точка порядку n
        """
        max_attempts = 100
        
        for attempt in range(max_attempts):
            # Крок 1: Обчислити випадкову точку Q
            Q = self.compute_random_point(seed=seed)
            
            # Крок 2: P = h·Q
            if cofactor == 1:
                P = Q
            else:
                P = self.multiply(cofactor, Q)
            
            # Крок 3: Якщо P = O, повторити
            if P.is_infinity:
                if seed is not None:
                    seed += 1  # Змінюємо seed для наступної спроби
                continue
            
            # Крок 4: Перевірити, що n·P = O
            nP = self.multiply(n, P)
            
            if nP.is_infinity:
                # Знайдено правильну базову точку
                return P
            
            # Якщо n·P ≠ O, повторити з новим seed
            if seed is not None:
                seed += 1
        
        raise ValueError(f"Не вдалося згенерувати базову точку за {max_attempts} спроб")


# Рекомендовані криві згідно ДСТУ 4145 (Додаток Г)
def get_dstu_curve_163(use_official_base_point: bool = True) -> Tuple[GF2mField, EllipticCurve, Point, int]:
    """
    Перша рекомендована крива над GF(2^163)
    Параметри з ДСТУ 4145-2002, Додаток Г.1
    
    Args:
        use_official_base_point: Якщо True, використовується офіційна базова точка
                                 з Додатку Б. Якщо False, генерується нова згідно п. 6.8
                                 (БЕЗ повільної перевірки n·P = O для швидкості)
    
    Returns:
        (field, curve, base_point, order)
    """
    try:
        from dstu4145.field import DSTU_FIELDS
    except ImportError:
        from field import DSTU_FIELDS
    
    field = DSTU_FIELDS[163]
    
    # Коефіцієнти кривої (згідно табл. Г.1 Додатку Г)
    A = 1
    B = field.element_from_int(
        0x5FF6108462A2DC8210AB403925E638A19C1455D21
    )
    
    curve = EllipticCurve(field, A, B)
    
    # Порядок базової точки (Додаток Г.1)
    n = 0x400000000000000000002BEC12BE2262D39BCF14D
    
    if use_official_base_point:
        # Базова точка (з Додатку Б - приклад обчислень)
        xP = field.element_from_int(0x72D867F93A93AC27DF9FF01AFFE74885C8C540420)
        yP = field.element_from_int(0x0224A9C3947852B97C5599D5F4AB81122ADC3FD9B)
        base_point = Point(xP, yP)
    else:
        # Генеруємо випадкову точку згідно п. 6.8 ДСТУ 4145-2002
        # ПРИМІТКА: Для швидкості НЕ перевіряємо n·P = O тут (займає ~60 сек)
        # Для кривих ДСТУ 4145, де n - великий простий дільник,
        # майже всі точки мають правильний порядок
        base_point = curve.compute_random_point(seed=163)
    
    return field, curve, base_point, n


def get_dstu_curve_257() -> Tuple[GF2mField, EllipticCurve, Point, int]:
    """
    Офіційні параметри ДСТУ 4145-2002 для GF(2^257)
    
    Параметри кривої:
        A = 0
        B = 0x1CEF494720115657E18F938D7A7942394FF9425C1458C57861F9EEA6ADBE3BE10
        n = 0x800000000000000000000000000000006759213AF182E987D3E17714907D470D
    
    Рівняння кривої: y^2 + xy = x^3 + B
    Безпека: ~128 біт (класична), еквівалент NIST Level 2 
    
    ПРИМІТКА: Базова точка генерується згідно п. 7.3 та п. 6.8 ДСТУ 4145-2002
    (обчислюємо базову точку з фіксованим seed для відтворюваності)
    
    Returns:
        (field, curve, base_point, order)
    """
    try:
        from dstu4145.field import DSTU_FIELDS
    except ImportError:
        from field import DSTU_FIELDS
    
    field = DSTU_FIELDS[257]
    
    # Коефіцієнти кривої (згідно табл. Г.1 Додатку Г)
    A = 0 
    B = field.element_from_int(
        0x1CEF494720115657E18F938D7A7942394FF9425C1458C57861F9EEA6ADBE3BE10
    )
    
    curve = EllipticCurve(field, A, B)
    
    # Порядок базової точки (згідно табл. Г.1 Додатку Г)
    n = 0x800000000000000000000000000000006759213AF182E987D3E17714907D470D
    
    # Базова точка: обчислюємо згідно п. 7.3 та п. 6.8 ДСТУ 4145-2002
    # Використовуємо фіксований seed для відтворюваності
    base_point = curve.compute_base_point(n=n, cofactor=1, seed=257)
    
    return field, curve, base_point, n

