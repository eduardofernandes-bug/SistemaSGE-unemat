import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def conectar():
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
        print(f"⚠️ Erro ao conectar ao banco de dados: {err}")
        raise