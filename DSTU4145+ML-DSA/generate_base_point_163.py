#!/usr/bin/env python3
"""
Генерація базової точки для ДСТУ 4145 GF(2^163)
Згідно п. 6.8 та п. 7.3 ДСТУ 4145-2002
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dstu4145.curve import get_dstu_curve_163

print("=" * 70)
print("ГЕНЕРАЦІЯ БАЗОВОЇ ТОЧКИ ДЛЯ GF(2^163)")
print("Згідно п. 6.8 ДСТУ 4145-2002")
print("=" * 70)

# Варіант 1: Офіційна базова точка з Додатку Б
print("\n1⃣  Офіційна базова точка (з Додатку Б ДСТУ 4145-2002):")
print("-" * 70)

field, curve, base_point, n = get_dstu_curve_163(use_official_base_point=True)

xP = field.element_to_int(base_point.x)
yP = field.element_to_int(base_point.y)

print(f"Поле: GF(2^{field.m})")
print(f"Коефіцієнти кривої: A = {curve.A}")
print(f"Порядок n: {hex(n)}")
print(f"\nБазова точка P:")
print(f"  xP = {hex(xP)}")
print(f"  yP = {hex(yP)}")

# Перевірка: точка на кривій?
on_curve = curve.is_on_curve(base_point)
print(f"\nПеревірка:")
print(f"   P на кривій: {on_curve}")


# Варіант 2: Згенерована базова точка
print("\n" + "=" * 70)
print("2⃣  Згенерована базова точка (п. 6.8 ДСТУ 4145-2002):")
print("-" * 70)
print("⏳ Генеруємо нову базову точку...\n")

import time
start = time.time()
field, curve, base_point_new, n = get_dstu_curve_163(use_official_base_point=False)
elapsed = time.time() - start

xP_new = field.element_to_int(base_point_new.x)
yP_new = field.element_to_int(base_point_new.y)

print(f" Базову точку згенеровано за {elapsed:.2f}с")
print(f"\nНова базова точка P:")
print(f"  xP = {hex(xP_new)}")
print(f"  yP = {hex(yP_new)}")

# Перевірка
on_curve_new = curve.is_on_curve(base_point_new)
print(f"\nПеревірка:")
print(f"   P на кривій: {on_curve_new}")

# Опціонально: перевірка n·P = O (повільно!)
print(f"\n  УВАГА: Перевірка n·P = O займе ~60 секунд")
verify = input("Виконати перевірку n·P = O для НОВОЇ точки? (y/N): ").lower().strip()

if verify == 'y':
    print(f"⏳ Обчислюємо n·P...")
    start = time.time()
    nP_new = curve.multiply(n, base_point_new)
    elapsed = time.time() - start
    print(f" n·P = O: {nP_new.is_infinity} (час: {elapsed:.1f}с)")
else:
    print("ℹ  Перевірка пропущена. Для кривих ДСТУ 4145, де n - великий")
    print("   простий дільник, майже всі точки мають правильний порядок.")


# Порівняння
print("\n" + "=" * 70)
print("ПОРІВНЯННЯ:")
print("=" * 70)
print(f"Офіційна xP:    {hex(xP)}")
print(f"Згенерована xP: {hex(xP_new)}")
print(f"\nТочки різні: {xP != xP_new}")
print(f"Обидві на кривій: {on_curve and on_curve_new}")

print("\n" + "=" * 70)
print(" ГОТОВО!")
print("=" * 70)
print("\nВисновок:")
print("• Офіційна базова точка з Додатку Б ДСТУ 4145-2002 ")
print("• Згенерована точка валідна (на кривій) ")
print("• Для перевірки порядку n·P = O запустіть з опцією 'y'")
print("• Для сумісності рекомендується офіційна точка")
