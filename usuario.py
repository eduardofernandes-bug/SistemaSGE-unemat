# -*- coding: utf-8 -*-

import re
import mysql.connector
import logging
from db import conectar
from base_model import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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


class Usuario(BaseModel):
    def __init__(self, email=None, senha=None, nome=None, tipo='usuario', 
                 nivel=NIVEL_VISUALIZADOR, idUsuario=None, idAluno=None):

        super().__init__(id_value=idUsuario)
        
        self._email = email
        self._senha = senha
        self._senha_hash = None
        self._nome = nome
        self._tipo = tipo
        self._nivel = nivel
        self._idAluno = idAluno
    
    
    @property
    def idUsuario(self):
        return self._id
    
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, valor):
        if valor:
            padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(padrao, valor):
                raise ValueError("Email inválido")
        self._email = valor
    
    @property
    def senha(self):
        return None
    
    @senha.setter
    def senha(self, valor):
        if valor:
            if len(valor) < 6:
                raise ValueError("Senha deve ter no mínimo 6 caracteres")
            self._senha = valor
        else:
            self._senha = None
    
    @property
    def nome(self):
        return self._nome
    
    @nome.setter
    def nome(self, valor):
        if valor and not isinstance(valor, str):
            raise ValueError("Nome deve ser uma string")
        self._nome = valor
    
    @property
    def tipo(self):
        return self._tipo
    
    @tipo.setter
    def tipo(self, valor):
        if valor not in ('usuario', 'admin'):
            raise ValueError("Tipo deve ser 'usuario' ou 'admin'")
        self._tipo = valor
    
    @property
    def nivel(self):
        return self._nivel
    
    @nivel.setter
    def nivel(self, valor):
        """Valida nível e sincroniza tipo"""
        if valor not in NIVEIS_ACESSO:
            raise ValueError(f"Nível inválido. Use: {list(NIVEIS_ACESSO.keys())}")
        
        self._nivel = valor
        
        if valor == NIVEL_ADMIN:
            self._tipo = 'admin'
        else:
            self._tipo = 'usuario'
    
    @property
    def idAluno(self):
        return self._idAluno
    
    @idAluno.setter
    def idAluno(self, valor):
        if valor is not None and not isinstance(valor, int):
            raise ValueError("idAluno deve ser um inteiro")
        self._idAluno = valor
    
    def __str__(self):
        nivel_info = NIVEIS_ACESSO[self._nivel]['nome']
        return f"Usuário: {self._nome} ({nivel_info}) - {self._email}"
    
    def __repr__(self):
        """Representação para debug"""
        return f"<Usuario id={self._id} email='{self._email}' nivel={self._nivel} ativo={self._ativo}>"
    
    def _gerar_hash_senha(self):
        if self._senha:
            self._senha_hash = generate_password_hash(self._senha)
            self._senha = None
    
    def verificar_senha(self, senha_texto):
        if not self._senha_hash:
            data = Usuario.buscar_por_id(self._id)
            if data and 'senha' in data:
                self._senha_hash = data['senha']
        
        if self._senha_hash:
            return check_password_hash(self._senha_hash, senha_texto)
        return False
    
    def get_nivel_info(self):
        return NIVEIS_ACESSO.get(self._nivel, NIVEIS_ACESSO[NIVEL_VISUALIZADOR])
    
    def eh_admin(self):
        return self._nivel == NIVEL_ADMIN
    
    def eh_coordenador_ou_superior(self):
        return self._nivel >= NIVEL_COORDENADOR
    
    def _get_table_name(self):
        return "usuarios"
    
    def _get_id_column_name(self):
        return "idUsuario"
    
    def _validar(self):
        if not self._email:
            return False, "Email é obrigatório"
        
        try:
            padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(padrao, self._email):
                return False, "Email inválido"
        except ValueError as e:
            return False, str(e)
        
        if not self._id and not self._senha:
            return False, "Senha é obrigatória"
        
        if self._senha and len(self._senha) < 6:
            return False, "Senha deve ter no mínimo 6 caracteres"
        
        return True, None
    
    def _get_insert_data(self):
        self._gerar_hash_senha()
        
        colunas = [
            'email', 'senha', 'nome', 'tipo', 'nivel', 'idAluno'
        ]
        
        valores = [
            self._email,
            self._senha_hash,
            self._nome,
            self._tipo,
            self._nivel,
            self._idAluno
        ]
        
        return (colunas, valores)
    
    def _get_update_data(self):
        colunas = ['email', 'nome', 'tipo', 'nivel', 'idAluno']
        valores = [self._email, self._nome, self._tipo, self._nivel, self._idAluno]
        
        if self._senha:
            self._gerar_hash_senha()
            colunas.append('senha')
            valores.append(self._senha_hash)
        
        return (colunas, valores)
    
    def salvar(self):
        ok, msg = self._validar()
        if not ok:
            logger.warning(f"Validação falhou ao inserir usuário: {msg}")
            return False, msg
        
        con = None
        cursor = None
        
        try:
            con = conectar()
            cursor = con.cursor()
            
            cursor.execute("SELECT idUsuario FROM usuarios WHERE email = %s", (self._email,))
            if cursor.fetchone():
                logger.warning(f"Email já cadastrado: {self._email}")
                return False, "Email já está cadastrado."
            
            self._gerar_hash_senha()
            
            colunas, valores = self._get_insert_data()
            
            colunas.append('ativo')
            valores.append(1)

            placeholders = ', '.join(['%s'] * len(valores))
            colunas_str = ', '.join(colunas)
            
            sql = f"INSERT INTO usuarios ({colunas_str}) VALUES ({placeholders})"
            
            cursor.execute(sql, valores)
            con.commit()

            self._id = cursor.lastrowid
            
            logger.info(f"Usuário '{self._email}' criado com sucesso (ID: {self._id}, nível {self._nivel})")
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
        if not self._id:
            return False, "ID de usuário não informado."
        
        ok, msg = self._validar()
        if not ok:
            return False, msg
        
        con = None
        cursor = None
        
        try:
            con = conectar()
            cursor = con.cursor()
            
            cursor.execute(
                "SELECT idUsuario FROM usuarios WHERE email = %s AND idUsuario != %s",
                (self._email, self._id)
            )
            if cursor.fetchone():
                return False, "Email já está cadastrado por outro usuário."
            
            colunas, valores = self._get_update_data()
            
            set_clause = ', '.join([f"{col} = %s" for col in colunas])
            valores.append(self._id)
            
            sql = f"UPDATE usuarios SET {set_clause} WHERE idUsuario = %s"
            
            cursor.execute(sql, valores)
            con.commit()
            
            logger.info(f"Usuário ID {self._id} atualizado com sucesso.")
            return True, "Usuário atualizado com sucesso!"
            
        except Exception as e:
            logger.exception(f"Erro ao editar usuário: {e}")
            return False, "Erro ao editar usuário."
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    def alterar_senha(self, senha_nova):
        if not self._id:
            return False, "ID de usuário não informado."
        
        if len(senha_nova) < 6:
            return False, "Senha deve ter no mínimo 6 caracteres."
        
        con = None
        cursor = None
        
        try:
            con = conectar()
            cursor = con.cursor()
            
            senha_hash = generate_password_hash(senha_nova)
            
            cursor.execute(
                "UPDATE usuarios SET senha = %s WHERE idUsuario = %s",
                (senha_hash, self._id)
            )
            con.commit()
            
            self._senha_hash = senha_hash
            logger.info(f"Senha alterada para usuário ID: {self._id}")
            return True, "Senha alterada com sucesso!"
            
        except Exception as e:
            logger.exception(f"Erro ao alterar senha: {e}")
            return False, "Erro ao alterar senha."
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()

    @staticmethod
    def autenticar(email, senha):
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
        con = conectar()
        cursor = con.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT idUsuario, email, nome, tipo, nivel, ativo, idAluno
            FROM usuarios
            WHERE idUsuario = %s
        """, (idUsuario,))
        
        usuario = cursor.fetchone()
        cursor.close()
        con.close()
        
        return usuario
    
    @classmethod
    def buscar_por_id_objeto(cls, idUsuario):
        data = cls.buscar_por_id(idUsuario)
        
        if not data:
            return None
        
        usuario = cls(
            email=data['email'],
            senha=None,
            nome=data['nome'],
            tipo=data['tipo'],
            nivel=data['nivel'],
            idUsuario=data['idUsuario'],
            idAluno=data.get('idAluno')
        )
        usuario._ativo = bool(data.get('ativo', 1))
        
        return usuario
    
    @staticmethod
    def listar():
        con = conectar()
        cursor = con.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT idUsuario, email, nome, tipo, nivel, ativo, idAluno
            FROM usuarios
            ORDER BY nivel DESC, nome
        """)
        
        usuarios = cursor.fetchall()
        cursor.close()
        con.close()
        
        return usuarios
    
    @staticmethod
    def get_nivel_info(nivel):
        return NIVEIS_ACESSO.get(nivel, NIVEIS_ACESSO[NIVEL_VISUALIZADOR])
