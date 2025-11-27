# -*- coding: utf-8 -*-
import mysql.connector
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def conectar():
    """
    Estabelece conexão com o banco de dados MySQL usando credenciais
    armazenadas em variáveis de ambiente para maior segurança.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME', 'sge'),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        raise