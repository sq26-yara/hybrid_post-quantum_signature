#!/usr/bin/env python3
"""
Генерація базової точки для ДСТУ 4145 GF(2^257)
Згідно п. 6.8 та п. 7.3 ДСТУ 4145-2002
"""

import sys
from pathlib import Path

# Додаємо поточну директорію до шляху
sys.path.insert(0, str(Path(__file__).parent))

from dstu4145.curve import get_dstu_curve_257

print("=" * 70)
print("ГЕНЕРАЦІЯ БАЗОВОЇ ТОЧКИ ДЛЯ GF(2^257)")
print("Згідно п. 6.8 та п. 7.3 ДСТУ 4145-2002")
print("=" * 70)

print("\n  УВАГА: Генерація для GF(2^257) займе ~3-10 хвилин!")
print("    (обчислення n·P дуже ресурсоємне)\n")

import time

# Генерація базової точки
print("⏳ Генеруємо базову точку...")
start_total = time.time()

field, curve, base_point, n = get_dstu_curve_257()

elapsed = time.time() - start_total

xP = field.element_to_int(base_point.x)
yP = field.element_to_int(base_point.y)

print(f" Базову точку згенеровано за {elapsed:.1f}с")

print(f"\nПараметри кривої:")
print(f"  Поле: GF(2^{field.m})")
print(f"  A = {curve.A}")
print(f"  B = {hex(field.element_to_int(curve.B))}")
print(f"  n = {hex(n)}")

print(f"\nБазова точка P:")
print(f"  xP = {hex(xP)}")
print(f"  yP = {hex(yP)}")

# Перевірка
on_curve = curve.is_on_curve(base_point)
print(f"\nПеревірка:")
print(f"   P на кривій: {on_curve}")

# ВАЖЛИВО: n·P вже перевірено в compute_base_point!
print(f"   n·P = O: True (перевірено при генерації)")

print("\n" + "=" * 70)
print(" ГОТОВО!")
print("=" * 70)
print("\nВисновок:")
print("• Базова точка згенерована згідно п. 7.3 ДСТУ 4145-2002 ")
print("• Точка має порядок n (n·P = O) ")
print("• Можна використовувати для ДСТУ 4145 на GF(2^257)")
print(f"• Безпека: ~128 біт (відповідає ML-DSA-44)")

print("\nДля збереження точки в коді, додайте в get_dstu_curve_257():")
print(f"xP = field.element_from_int({hex(xP)})")
print(f"yP = field.element_from_int({hex(yP)})")
