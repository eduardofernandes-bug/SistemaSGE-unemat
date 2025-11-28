# -*- coding: utf-8 -*-
"""
usuario.py - Model para gerenciamento de usuários com níveis de acesso
"""
import re
import mysql.connector
import logging
from db import conectar
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Constantes de níveis de acesso
NIVEL_VISUALIZADOR = 1
NIVEL_COORDENADOR = 2
NIVEL_ADMIN = 3

NIVEIS_ACESSO = {
    NIVEL_VISUALIZADOR: {
        'nome': 'Visualizador',
        'descricao': 'Apenas leitura',
        'cor': 'info'
    },
    NIVEL_COORDENADOR: {
        'nome': 'Coordenador',
        'descricao': 'Gerenciar alunos, empresas e estágios',
        'cor': 'warning'
    },
    NIVEL_ADMIN: {
        'nome': 'Administrador',
        'descricao': 'Acesso total ao sistema',
        'cor': 'danger'
    }
}

class Usuario:
    def __init__(self, email=None, senha=None, nome=None, tipo='usuario', nivel=NIVEL_VISUALIZADOR, idUsuario=None, idAluno=None):
        self.idUsuario = idUsuario
        self.email = email
        self.senha = senha
        self.nome = nome
        self.tipo = tipo  # Mantido por compatibilidade
        self.nivel = nivel  # 1=Visualizador, 2=Coordenador, 3=Admin
        self.ativo = True
        self.idAluno = idAluno 

    def _validar_email(self):
        """Valida formato do email"""
        if not self.email:
            return False, "Email é obrigatório."
        
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(padrao, self.email):
            return False, "Email inválido."
        
        return True, None

    def _validar_senha(self):
        """Valida força da senha"""
        if not self.senha:
            return False, "Senha é obrigatória."
        
        if len(self.senha) < 6:
            return False, "Senha deve ter no mínimo 6 caracteres."
        
        return True, None

    def salvar(self):
        """Cria novo usuário com senha criptografada"""
        ok, msg = self._validar_email()
        if not ok:
            logger.warning(f"Validação de email falhou: {msg}")
            return False, msg
        
        ok, msg = self._validar_senha()
        if not ok:
            logger.warning(f"Validação de senha falhou: {msg}")
            return False, msg

        con = None
        cursor = None
        try:
            con = conectar()
            cursor = con.cursor()
            
            # Verifica se email já existe
            cursor.execute("SELECT idUsuario FROM usuarios WHERE email = %s", (self.email,))
            if cursor.fetchone():
                logger.warning(f"Email já cadastrado: {self.email}")
                return False, "Email já está cadastrado."
            
            # Hash da senha
            senha_hash = generate_password_hash(self.senha)
            
            # Atualiza tipo baseado no nível
            if self.nivel == NIVEL_ADMIN:
                self.tipo = 'admin'
            else:
                self.tipo = 'usuario'
            
            sql = """
            INSERT INTO usuarios (email, senha, nome, tipo, nivel, ativo, idAluno)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (self.email, senha_hash, self.nome, self.tipo, self.nivel, 1, self.idAluno))
            con.commit()
            
            logger.info(f"Usuário '{self.email}' criado com sucesso (nível {self.nivel}).")
            return True, "Usuário criado com sucesso!"
            
        except Exception as e:
            logger.exception(f"Erro ao criar usuário: {e}")
            return False, "Erro ao criar usuário."
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()

    def editar(self):
        """Atualiza dados do usuário"""
        if not self.idUsuario:
            return False, "ID de usuário não informado."
        
        ok, msg = self._validar_email()
        if not ok:
            return False, msg

        con = None
        cursor = None
        try:
            con = conectar()
            cursor = con.cursor()
            
            # Verifica se email já existe em outro usuário
            cursor.execute(
                "SELECT idUsuario FROM usuarios WHERE email = %s AND idUsuario != %s", 
                (self.email, self.idUsuario)
            )
            if cursor.fetchone():
                return False, "Email já está cadastrado por outro usuário."
            
            # Atualiza tipo baseado no nível
            if self.nivel == NIVEL_ADMIN:
                self.tipo = 'admin'
            else:
                self.tipo = 'usuario'
            
            # Se senha foi fornecida, atualiza também
            if self.senha:
                ok, msg = self._validar_senha()
                if not ok:
                    return False, msg
                senha_hash = generate_password_hash(self.senha)
                sql = """
                UPDATE usuarios 
                SET email = %s, senha = %s, nome = %s, tipo = %s, nivel = %s
                WHERE idUsuario = %s
                """
                cursor.execute(sql, (self.email, senha_hash, self.nome, self.tipo, self.nivel, self.idUsuario, self.idAluno,))
            else:
                sql = """
                UPDATE usuarios 
                SET email = %s, nome = %s, tipo = %s, nivel = %s
                WHERE idUsuario = %s
                """
                cursor.execute(sql, (self.email, self.nome, self.tipo, self.nivel, self.idUsuario, self.idAluno,))
            
            con.commit()
            logger.info(f"Usuário ID {self.idUsuario} atualizado com sucesso.")
            return True, "Usuário atualizado com sucesso!"
            
        except Exception as e:
            logger.exception(f"Erro ao editar usuário: {e}")
            return False, "Erro ao editar usuário."
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()

    @staticmethod
    def autenticar(email, senha):
        """Autentica usuário verificando email e senha"""
        if not email or not senha:
            return False, "Email e senha são obrigatórios."

        con = None
        cursor = None
        try:
            con = conectar()
            cursor = con.cursor(dictionary=True)
            
            sql = """
            SELECT idUsuario, email, senha, nome, tipo, nivel, ativo, idAluno
            FROM usuarios
            WHERE email = %s
            """

            cursor.execute(sql, (email,))
            usuario = cursor.fetchone()
            
            if not usuario:
                logger.warning(f"Tentativa de login com email não cadastrado: {email}")
                return False, "Email ou senha incorretos."
            
            if not usuario['ativo']:
                logger.warning(f"Tentativa de login de usuário inativo: {email}")
                return False, "Usuário desativado."
            
            # Verifica senha
            if check_password_hash(usuario['senha'], senha):
                logger.info(f"Login bem-sucedido: {email} (nível {usuario['nivel']})")
                del usuario['senha']
                return True, usuario
            else:
                logger.warning(f"Senha incorreta para: {email}")
                return False, "Email ou senha incorretos."
                
        except Exception as e:
            logger.exception(f"Erro na autenticação: {e}")
            return False, "Erro ao processar login."
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()

    @staticmethod
    def buscar_por_id(idUsuario):
        """Busca usuário por ID"""
        con = conectar()
        cursor = con.cursor(dictionary=True)
        cursor.execute("""
            SELECT idUsuario, email, nome, tipo, nivel, ativo
            FROM usuarios
            WHERE idUsuario = %s
        """, (idUsuario,))
        usuario = cursor.fetchone()
        cursor.close()
        con.close()
        return usuario

    @staticmethod
    def listar():
        """Lista todos os usuários (sem senhas)"""
        con = conectar()
        cursor = con.cursor(dictionary=True)
        cursor.execute("""
            SELECT idUsuario, email, nome, tipo, nivel, ativo
            FROM usuarios
            ORDER BY nivel DESC, nome
        """)
        usuarios = cursor.fetchall()
        cursor.close()
        con.close()
        return usuarios

    @staticmethod
    def get_nivel_info(nivel):
        """Retorna informações sobre um nível de acesso"""
        return NIVEIS_ACESSO.get(nivel, NIVEIS_ACESSO[NIVEL_VISUALIZADOR])

    def alterar_senha(self, senha_nova):
        """Altera senha do usuário"""
        if not self.idUsuario:
            return False, "ID de usuário não informado."
        
        if len(senha_nova) < 6:
            return False, "Senha deve ter no mínimo 6 caracteres."

        con = None
        cursor = None
        try:
            con = conectar()
            cursor = con.cursor()
            
            senha_hash = generate_password_hash(senha_nova)
            cursor.execute("""
                UPDATE usuarios 
                SET senha = %s
                WHERE idUsuario = %s
            """, (senha_hash, self.idUsuario))
            
            con.commit()
            logger.info(f"Senha alterada para usuário ID: {self.idUsuario}")
            return True, "Senha alterada com sucesso!"
            
        except Exception as e:
            logger.exception(f"Erro ao alterar senha: {e}")
            return False, "Erro ao alterar senha."
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()

    def desativar(self):
        """Desativa usuário"""
        if not self.idUsuario:
            return False
        
        con = None
        cursor = None
        try:
            con = conectar()
            cursor = con.cursor()
            cursor.execute("UPDATE usuarios SET ativo = 0 WHERE idUsuario = %s", (self.idUsuario,))
            con.commit()
            logger.info(f"Usuário ID {self.idUsuario} desativado.")
            return True
        except Exception as e:
            logger.exception(f"Erro ao desativar usuário: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()

    def definir_ativo(idUsuario, ativo):
        con = conectar()
        cursor = con.cursor()
        try:
            cursor.execute("UPDATE usuarios SET ativo = %s WHERE idUsuario = %s", (1 if ativo else 0, idUsuario))
            con.commit()
            return cursor.rowcount > 0
        except Exception as e:
            return False
        finally:
            cursor.close()
            con.close()