#!/usr/bin/env python3
"""
Демонстрація гібридного цифрового підпису ECDSA + ML-DSA
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from hybrid import create_hybrid
import time


def main():
    print("=" * 80)
    print("ДЕМОНСТРАЦІЯ: Гібридний цифровий підпис ECDSA P-256 + ML-DSA-44")
    print("=" * 80)
    
    # Ініціалізація
    print("\n📋 Крок 1: Ініціалізація")
    print("-" * 80)
    hybrid = create_hybrid()
    print("✓ ECDSA P-256 (NIST)")
    print("  • Крива: NIST P-256 (secp256r1)")
    print("  • Поле: GF(p) де p ≈ 2^256")
    print("  • Класична безпека: ~128 біт")
    print()
    print("✓ ML-DSA-44 (FIPS 204)")
    print("  • Lattice-based криптографія")
    print("  • Постквантова безпека: 128 біт")
    print("  • NIST Level 2")
    
    # Генерація ключів
    print("\n📋 Крок 2: Генерація ключів")
    print("-" * 80)
    start = time.time()
    keypair = hybrid.generate_keypair()
    keygen_time = time.time() - start
    
    print(f"✓ Ключі згенеровано за {keygen_time:.4f} сек")
    
    # Розміри ключів
    ecdsa_priv = hybrid.ecdsa.private_key_to_bytes(keypair.ecdsa_private_key)
    ecdsa_pub = hybrid.ecdsa.public_key_to_bytes(keypair.ecdsa_public_key)
    
    print(f"\nРозміри:")
    print(f"  • ECDSA приватний ключ: {len(ecdsa_priv)} байт")
    print(f"  • ECDSA публічний ключ: {len(ecdsa_pub)} байт")
    print(f"  • ML-DSA приватний ключ: {len(keypair.mldsa_private_key)} байт")
    print(f"  • ML-DSA публічний ключ: {len(keypair.mldsa_public_key)} байт")
    
    # Тестові дані
    print("\n📋 Крок 3: Дані для підпису")
    print("-" * 80)
    test_data = b"Важливий документ для підпису гібридною схемою ECDSA + ML-DSA"
    print(f"Дані: {test_data.decode()}")
    print(f"Розмір: {len(test_data)} байт")
    
    # Підпис
    print("\n📋 Крок 4: Створення підпису")
    print("-" * 80)
    start = time.time()
    signature = hybrid.sign(test_data, keypair)
    sign_time = time.time() - start
    
    print(f"✓ Підпис створено за {sign_time:.4f} сек")
    print(f"\nРозміри підпису:")
    print(f"  • ECDSA підпис: {len(signature.ecdsa_signature)} байт")
    print(f"  • ML-DSA підпис: {len(signature.mldsa_signature)} байт")
    print(f"  • Загальний розмір: {len(signature.ecdsa_signature) + len(signature.mldsa_signature)} байт")
    print(f"\nМетадані:")
    print(f"  • SHA-256 хеш: {signature.data_hash_sha256[:32]}...")
    print(f"  • Timestamp: {signature.timestamp}")
    print(f"  • Алгоритм: {signature.algorithm}")
    
    # Верифікація
    print("\n📋 Крок 5: Верифікація підпису")
    print("-" * 80)
    start = time.time()
    valid = hybrid.verify(test_data, signature, keypair)
    verify_time = time.time() - start
    
    print(f"{'✓' if valid else '✗'} Підпис {'валідний' if valid else 'НЕВАЛІДНИЙ'}")
    print(f"Час верифікації: {verify_time:.4f} сек")
    
    if not valid:
        print("\n❌ ПОМИЛКА: Підпис має бути валідним!")
        return False
    
    # Тест з підробленими даними
    print("\n📋 Крок 6: Тест з підробленими даними")
    print("-" * 80)
    fake_data = b"Підроблені дані"
    valid_fake = hybrid.verify(fake_data, signature, keypair)
    print(f"Підроблені дані: {fake_data.decode()}")
    print(f"{'✗' if not valid_fake else '✓'} Підпис {'НЕВАЛІДНИЙ' if not valid_fake else 'валідний'} (очікується НЕВАЛІДНИЙ)")
    
    if valid_fake:
        print("\n❌ ПОМИЛКА: Підпис НЕ має бути валідним для підроблених даних!")
        return False
    
    # Експорт
    print("\n📋 Крок 7: Експорт підпису")
    print("-" * 80)
    json_sig = hybrid.export_signature(signature)
    print(f"✓ Підпис експортовано в JSON")
    print(f"Розмір JSON: {len(json_sig)} символів")
    print(f"\nПриклад JSON (скорочено):")
    print(json_sig[:200] + "...")
    
    # Імпорт
    print("\n📋 Крок 8: Імпорт підпису")
    print("-" * 80)
    signature_imported = hybrid.import_signature(json_sig)
    print("✓ Підпис імпортовано з JSON")
    
    valid_imported = hybrid.verify(test_data, signature_imported, keypair)
    print(f"{'✓' if valid_imported else '✗'} Імпортований підпис {'валідний' if valid_imported else 'НЕВАЛІДНИЙ'}")
    
    # Підсумок
    print("\n" + "=" * 80)
    print("✅ ДЕМОНСТРАЦІЯ ЗАВЕРШЕНА УСПІШНО!")
    print("=" * 80)
    
    print("\nПідсумок продуктивності:")
    print(f"  • Генерація ключів: {keygen_time:.4f} сек")
    print(f"  • Створення підпису: {sign_time:.4f} сек")
    print(f"  • Верифікація: {verify_time:.4f} сек")
    
    print("\nПідсумок розмірів:")
    total_sig_size = len(signature.ecdsa_signature) + len(signature.mldsa_signature)
    total_key_size = len(ecdsa_pub) + len(keypair.mldsa_public_key)
    print(f"  • Загальний підпис: {total_sig_size} байт")
    print(f"  • Загальний публічний ключ: {total_key_size} байт")
    
    print("\nБезпека:")
    print("  • ECDSA: ~128 біт класичної безпеки")
    print("  • ML-DSA: 128 біт постквантової безпеки")
    print("  • Гібрид: захист від класичних та квантових атак")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ПОМИЛКА: {e}")
        import traceback
        traceback.print_exc()
        print("\nПеревірте, що встановлені всі залежності:")
        print("  pip install ecdsa liboqs-python --break-system-packages")
        sys.exit(1)
