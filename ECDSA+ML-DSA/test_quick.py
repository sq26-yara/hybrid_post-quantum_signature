#!/usr/bin/env python3
"""
Швидкий тест гібридного підпису ECDSA + ML-DSA
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from hybrid import create_hybrid


def main():
    print("=" * 70)
    print("ШВИДКИЙ ТЕСТ: ECDSA P-256 + ML-DSA-44")
    print("=" * 70)
    
    # Ініціалізація
    print("\n1. Ініціалізація гібридної схеми...")
    hybrid = create_hybrid()
    print("   ✓ ECDSA P-256")
    print("   ✓ ML-DSA-44")
    
    # Генерація ключів
    print("\n2. Генерація ключів...")
    keypair = hybrid.generate_keypair()
    print("   ✓ Ключі згенеровано")
    
    # Тестові дані
    test_data = b"Тестові дані для гібридного підпису ECDSA + ML-DSA"
    print(f"\n3. Тестові дані ({len(test_data)} байт):")
    print(f"   {test_data.decode()}")
    
    # Підпис
    print("\n4. Створення підпису...")
    signature = hybrid.sign(test_data, keypair)
    print("   ✓ Підпис створено")
    print(f"   • ECDSA підпис: {len(signature.ecdsa_signature)} байт")
    print(f"   • ML-DSA підпис: {len(signature.mldsa_signature)} байт")
    print(f"   • Загальний розмір: {len(signature.ecdsa_signature) + len(signature.mldsa_signature)} байт")
    print(f"   • SHA-256 хеш: {signature.data_hash_sha256[:16]}...")
    print(f"   • Timestamp: {signature.timestamp}")
    
    # Верифікація (коректні дані)
    print("\n5. Верифікація підпису...")
    valid = hybrid.verify(test_data, signature, keypair)
    print(f"   {'✓' if valid else '✗'} Підпис {'валідний' if valid else 'НЕВАЛІДНИЙ'}")
    
    if not valid:
        print("   ❌ ПОМИЛКА: Підпис має бути валідним!")
        return False
    
    # Верифікація (підроблені дані)
    print("\n6. Тест з підробленими даними...")
    fake_data = b"Підроблені дані"
    valid_fake = hybrid.verify(fake_data, signature, keypair)
    print(f"   {'✗' if not valid_fake else '✓'} Підпис {'НЕВАЛІДНИЙ' if not valid_fake else 'валідний'} (очікується НЕВАЛІДНИЙ)")
    
    if valid_fake:
        print("   ❌ ПОМИЛКА: Підпис НЕ має бути валідним для підроблених даних!")
        return False
    
    # Експорт/імпорт
    print("\n7. Тест експорт/імпорт...")
    json_sig = hybrid.export_signature(signature)
    print(f"   ✓ Експортовано в JSON ({len(json_sig)} символів)")
    
    signature_imported = hybrid.import_signature(json_sig)
    print("   ✓ Імпортовано з JSON")
    
    # Верифікація імпортованого
    valid_imported = hybrid.verify(test_data, signature_imported, keypair)
    print(f"   {'✓' if valid_imported else '✗'} Імпортований підпис {'валідний' if valid_imported else 'НЕВАЛІДНИЙ'}")
    
    if not valid_imported:
        print("   ❌ ПОМИЛКА: Імпортований підпис має бути валідним!")
        return False
    
    # Підсумок
    print("\n" + "=" * 70)
    print("✅ ВСІ ТЕСТИ ПРОЙШЛИ УСПІШНО!")
    print("=" * 70)
    
    print("\nПідсумок:")
    print("• Гібридна схема ECDSA + ML-DSA працює коректно")
    print("• ECDSA забезпечує класичну безпеку (~128 біт)")
    print("• ML-DSA забезпечує постквантову безпеку (128 біт)")
    print("• Верифікація вимагає валідності обох підписів")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ПОМИЛКА: {e}")
        print("\nПеревірте, що встановлені всі залежності:")
        print("  pip install numpy ecdsa liboqs-python --break-system-packages")
        sys.exit(1)
