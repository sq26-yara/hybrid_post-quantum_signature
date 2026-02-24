#!/usr/bin/env python3
"""
Швидкий тест Hybrid Signature
"""

import sys
from pathlib import Path

# Додаємо поточну директорію
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Тест імпортів"""
    print("=" * 70)
    print("ТЕСТ ІМПОРТІВ")
    print("=" * 70)
    
    try:
        import numpy as np
        print(" numpy")
    except ImportError as e:
        print(f" numpy: {e}")
        return False
    
    try:
        import oqs
        print(" liboqs-python")
    except ImportError as e:
        print(f" liboqs-python: {e}")
        return False
    
    try:
        from hybrid import create_hybrid_scheme
        print(" pure_hybrid")
    except ImportError as e:
        print(f" pure_hybrid: {e}")
        return False
    
    return True


def test_basic_workflow():
    """Тест базового workflow"""
    print("\n" + "=" * 70)
    print("ТЕСТ БАЗОВОГО WORKFLOW")
    print("=" * 70)
    
    try:
        from hybrid import create_hybrid_scheme
        
        # Ініціалізація
        print("\n1. Ініціалізація...")
        scheme = create_hybrid_scheme()
        
        # Генерація ключів
        print("\n2. Генерація ключів...")
        keypair = scheme.generate_keypair(key_id="test-001")
        
        # Підпис
        print("\n3. Підпис...")
        data = b"Test data for pure hybrid signature"
        signature = scheme.sign(data, keypair)
        
        # Верифікація
        print("\n4. Верифікація...")
        results = scheme.verify(data, signature, keypair)
        
        if results['valid']:
            print("\n ВСІ ТЕСТИ ПРОЙШЛИ УСПІШНО!")
            return True
        else:
            print("\n ТЕСТ НЕ ПРОЙШОВ: підпис невалідний")
            return False
            
    except Exception as e:
        print(f"\n ПОМИЛКА: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Головна функція"""
    print("\n" + "=" * 70)
    print("PURE HYBRID SIGNATURE - ШВИДКИЙ ТЕСТ")
    print("=" * 70 + "\n")
    
    # Тест імпортів
    if not test_imports():
        print("\n Тести не пройшли: проблеми з імпортами")
        print("\nВстановіть залежності:")
        print("  pip install -r requirements.txt")
        return 1
    
    # Тест workflow
    if not test_basic_workflow():
        print("\n Тести не пройшли")
        return 1
    
    print("\n" + "=" * 70)
    print(" ВСІ ТЕСТИ УСПІШНО ПРОЙДЕНІ!")
    print("=" * 70)
    print("\nТепер можете:")
    print("  1. Запустити Jupyter: jupyter notebook demo.ipynb")
    print("  2. Використати в Python: from hybrid import create_hybrid_scheme")
    print("=" * 70 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
