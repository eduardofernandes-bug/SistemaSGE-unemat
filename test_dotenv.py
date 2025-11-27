from dotenv import load_dotenv
import os

load_dotenv()

print("✅ python-dotenv instalado com sucesso!")
print(f"DB_HOST: {os.getenv('DB_HOST', 'não encontrado')}")