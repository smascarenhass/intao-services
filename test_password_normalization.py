#!/usr/bin/env python3
"""
Script de teste para verificar a normalização de prefixos de senha WordPress.
"""

import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
sys.path.append(project_root)

from api.services.membership_pro import MembershipProService
from routines.services.sparks_app import SparksAppService

def test_password_normalization():
    """
    Testa a normalização de prefixos de senha WordPress.
    """
    print("🧪 TESTE DE NORMALIZAÇÃO DE PREFIXOS DE SENHA")
    print("=" * 60)
    
    # Senhas de teste
    test_passwords = [
        "$wp$2y$10$nkxwsP56M59zO53iIljLdueH662FSrvgG9Od5LQNx/ZmSgcimee3u",
        "$P$HgecMJsd15ENCZ6i6YxUyZuswlK1wh0",
        "senha123",  # Senha em texto plano
        "$wp$2y$10$outroSalt$hashDiferente",
        "$P$outroSalt$hashDiferente",
        "outra_senha_em_texto"
    ]
    
    print("\n📋 SENHAS DE TESTE:")
    for i, password in enumerate(test_passwords, 1):
        print(f"{i}. {password}")
    
    print("\n🔧 TESTANDO NORMALIZAÇÃO DO MEMBERSHIP PRO SERVICE:")
    print("-" * 50)
    
    for i, password in enumerate(test_passwords, 1):
        normalized = MembershipProService._normalize_password_prefix(password)
        ensured = MembershipProService._ensure_wp_prefix(password)
        
        print(f"\nTeste {i}:")
        print(f"  Original: {password}")
        print(f"  Normalizada: {normalized}")
        print(f"  Garantida ($wp$): {ensured}")
        
        # Verifica se a normalização funcionou
        if password.startswith('$P$') and normalized.startswith('$wp$'):
            print(f"  ✅ Prefixo $P$ convertido para $wp$")
        elif password.startswith('$wp$') and normalized == password:
            print(f"  ✅ Prefixo $wp$ mantido")
        elif not password.startswith('$') and ensured.startswith('$wp$'):
            print(f"  ✅ Senha em texto plano convertida para $wp$")
        else:
            print(f"  ⚠️  Comportamento inesperado")
    
    print("\n🔧 TESTANDO NORMALIZAÇÃO DO SPARKS APP SERVICE:")
    print("-" * 50)
    
    sparks_service = SparksAppService()
    
    for i, password in enumerate(test_passwords, 1):
        normalized = sparks_service._normalize_password_prefix(password)
        final = sparks_service._normalize_password(password)
        
        print(f"\nTeste {i}:")
        print(f"  Original: {password}")
        print(f"  Prefixo normalizado: {normalized}")
        print(f"  Final (truncada): {final}")
    
    print("\n🔍 TESTANDO COMPARAÇÃO DE SENHAS:")
    print("-" * 50)
    
    # Testa comparação entre senhas com prefixos diferentes
    test_cases = [
        ("$wp$2y$10$nkxwsP56M59zO53iIljLdueH662FSrvgG9Od5LQNx/ZmSgcimee3u", 
         "$P$nkxwsP56M59zO53iIljLdueH662FSrvgG9Od5LQNx/ZmSgcimee3u"),
        ("$wp$2y$10$outroSalt$hashDiferente", 
         "$P$outroSalt$hashDiferente"),
        ("$wp$2y$10$mesmoSalt$mesmoHash", 
         "$wp$2y$10$mesmoSalt$mesmoHash")
    ]
    
    for i, (pass1, pass2) in enumerate(test_cases, 1):
        match = sparks_service._passwords_match(pass1, pass2)
        print(f"\nComparação {i}:")
        print(f"  Senha 1: {pass1[:20]}...")
        print(f"  Senha 2: {pass2[:20]}...")
        print(f"  Correspondem: {'✅ SIM' if match else '❌ NÃO'}")
    
    print("\n" + "=" * 60)
    print("✅ TESTE CONCLUÍDO")

if __name__ == "__main__":
    test_password_normalization() 