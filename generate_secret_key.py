#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para gerar uma SECRET_KEY segura para o Flask.
Execute: python generate_secret_key.py
"""

import secrets

if __name__ == "__main__":
    secret_key = secrets.token_hex(32)
    print("=" * 80)
    print("CHAVE SECRETA GERADA COM SUCESSO!")
    print("=" * 80)
    print(f"\nSECRET_KEY={secret_key}")
    print("\n⚠️  IMPORTANTE:")
    print("1. Copie esta chave e cole no arquivo .env")
    print("2. NUNCA compartilhe esta chave publicamente")
    print("3. NUNCA faça commit desta chave no Git")
    print("4. Gere uma nova chave diferente para produção")
    print("=" * 80)