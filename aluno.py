# -*- coding: utf-8 -*-

import re
import mysql.connector
import logging
from db import conectar
from base_model import BaseModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def only_digits(s):
    return re.sub(r'\D', '', s or '')


class Aluno(BaseModel):
    
    def __init__(self, nome=None, matricula=None, cpf=None, nomeInstitucional=None,
                 telefone=None, endereco=None, bairro=None, periodo=None,
                 statusAluno=None, idCidade=None, idEstado=None, idAluno=None):

        super().__init__(id_value=idAluno)
        
        self._nome = nome
        self._matricula = matricula
        self._cpf = cpf
        self._nomeInstitucional = nomeInstitucional
        self._telefone = telefone
        self._endereco = endereco
        self._bairro = bairro
        self._periodo = periodo
        self._statusAluno = statusAluno
        self._idCidade = idCidade
        self._idEstado = idEstado
    
    @property
    def idAluno(self):
        """Getter para ID (compatibilidade com código antigo)"""
        return self._id
    
    @property
    def nome(self):
        return self._nome
    
    @nome.setter
    def nome(self, valor):
        if valor and not isinstance(valor, str):
            raise ValueError("Nome deve ser uma string")
        self._nome = valor
    
    @property
    def matricula(self):
        return self._matricula
    
    @matricula.setter
    def matricula(self, valor):
        self._matricula = valor
    
    @property
    def cpf(self):
        """Retorna CPF apenas com dígitos"""
        return only_digits(self._cpf) if self._cpf else None
    
    @cpf.setter
    def cpf(self, valor):
        """Valida CPF ao atribuir"""
        if valor:
            cpf_digits = only_digits(valor)
            if len(cpf_digits) != 11:
                raise ValueError("CPF deve conter 11 dígitos")
            self._cpf = valor
        else:
            self._cpf = None
    
    @property
    def nomeInstitucional(self):
        return self._nomeInstitucional
    
    @nomeInstitucional.setter
    def nomeInstitucional(self, valor):
        self._nomeInstitucional = valor
    
    @property
    def telefone(self):
        """Retorna telefone apenas com dígitos"""
        return only_digits(self._telefone) if self._telefone else None
    
    @telefone.setter
    def telefone(self, valor):
        """Valida telefone ao atribuir"""
        if valor:
            tel_digits = only_digits(valor)
            if len(tel_digits) not in (10, 11):
                raise ValueError("Telefone deve ter 10 ou 11 dígitos")
            self._telefone = valor
        else:
            self._telefone = None
    
    @property
    def endereco(self):
        return self._endereco
    
    @endereco.setter
    def endereco(self, valor):
        self._endereco = valor
    
    @property
    def bairro(self):
        return self._bairro
    
    @bairro.setter
    def bairro(self, valor):
        self._bairro = valor
    
    @property
    def periodo(self):
        return self._periodo
    
    @periodo.setter
    def periodo(self, valor):
        self._periodo = valor
    
    @property
    def statusAluno(self):
        return self._statusAluno
    
    @statusAluno.setter
    def statusAluno(self, valor):
        self._statusAluno = valor
    
    @property
    def idcidade(self):
        """Compatibilidade com código antigo"""
        return self._idCidade
    
    @property
    def idEstado(self):
        return self._idEstado
    
    
    def __str__(self):
        """Representação em string legível"""
        return f"Aluno: {self._nome} - Matrícula: {self._matricula}"
    
    def __repr__(self):
        """Representação para debug"""
        return f"<Aluno id={self._id} nome='{self._nome}' matricula='{self._matricula}'>"
    
    def _get_table_name(self):
        """Retorna nome da tabela"""
        return "aluno"
    
    def _get_id_column_name(self):
        """Retorna nome da coluna ID"""
        return "idAluno"
    
    def _validar(self):
        """
        Validações específicas de Aluno.
        
        Returns:
            tuple: (bool_sucesso, str_mensagem_erro)
        """
        try:
            cpf_digits = self.cpf
            if not cpf_digits:
                return False, "CPF é obrigatório"
        except ValueError as e:
            return False, str(e)
        
        if self._telefone:
            try:
                tel_digits = self.telefone
            except ValueError as e:
                return False, str(e)
        
        return True, None
    
    def _get_insert_data(self):
        colunas = [
            'nome', 'matricula', 'CPF', 'nomeInstitucional', 'telefone',
            'endereco', 'bairro', 'periodo', 'statusAluno',
            'idCidade_Cidades', 'idEstadoE_Cidades'
        ]
        
        valores = [
            self._nome,
            self._matricula,
            self.cpf,
            self._nomeInstitucional,
            self.telefone,
            self._endereco,
            self._bairro,
            self._periodo,
            self._statusAluno,
            self._idCidade,
            self._idEstado
        ]
        
        return (colunas, valores)
    
    def _get_update_data(self):
        colunas = [
            'nome', 'matricula', 'CPF', 'nomeInstitucional', 'telefone',
            'endereco', 'bairro', 'periodo', 'statusAluno',
            'idCidade_Cidades', 'idEstadoE_Cidades'
        ]
        
        valores = [
            self._nome,
            self._matricula,
            self.cpf,
            self._nomeInstitucional,
            self.telefone,
            self._endereco,
            self._bairro,
            self._periodo,
            self._statusAluno,
            self._idCidade,
            self._idEstado
        ]
        
        return (colunas, valores)
    
    @staticmethod
    def listar(mostrar_inativos=False):
        con = conectar()
        cursor = con.cursor(dictionary=True)
        
        if mostrar_inativos:
            sql = """
                SELECT a.idAluno, a.nome, a.matricula, a.CPF, a.nomeInstitucional, a.telefone,
                       a.endereco, a.bairro, a.periodo, a.statusAluno,
                       c.nome AS cidade, est.uf AS estado, a.ativo,
                       a.idCidade_Cidades, a.idEstadoE_Cidades
                FROM aluno a
                LEFT JOIN cidades c ON a.idCidade_Cidades = c.idCidade
                LEFT JOIN estados est ON a.idEstadoE_Cidades = est.idEstado
                WHERE a.ativo IS NULL OR a.ativo = 0
                ORDER BY a.nome
            """
        else:
            sql = """
                SELECT a.idAluno, a.nome, a.matricula, a.CPF, a.nomeInstitucional, a.telefone,
                       a.endereco, a.bairro, a.periodo, a.statusAluno,
                       c.nome AS cidade, est.uf AS estado, a.ativo,
                       a.idCidade_Cidades, a.idEstadoE_Cidades
                FROM aluno a
                LEFT JOIN cidades c ON a.idCidade_Cidades = c.idCidade
                LEFT JOIN estados est ON a.idEstadoE_Cidades = est.idEstado
                WHERE a.ativo IS NULL OR a.ativo = 1
                ORDER BY a.nome
            """
        
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        con.close()
        
        return results
    
    @staticmethod
    def buscar_por_id(idAluno):
        con = conectar()
        cursor = con.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT a.idAluno, a.nome, a.matricula, a.CPF, a.nomeInstitucional, a.telefone,
                   a.endereco, a.bairro, a.periodo, a.statusAluno,
                   c.idCidade, c.nome AS cidade, est.idEstado, est.nome AS estado, est.uf,
                   a.idCidade_Cidades, a.idEstadoE_Cidades, a.ativo
            FROM aluno a
            LEFT JOIN cidades c ON a.idCidade_Cidades = c.idCidade
            LEFT JOIN estados est ON a.idEstadoE_Cidades = est.idEstado
            WHERE a.idAluno = %s
        """, (idAluno,))
        
        row = cursor.fetchone()
        cursor.close()
        con.close()
        
        return row
    
    @classmethod
    def buscar_por_id_objeto(cls, idAluno):
        data = cls.buscar_por_id(idAluno)
        
        if not data:
            return None
        

        aluno = cls(
            nome=data['nome'],
            matricula=data['matricula'],
            cpf=data['CPF'],
            nomeInstitucional=data['nomeInstitucional'],
            telefone=data['telefone'],
            endereco=data['endereco'],
            bairro=data['bairro'],
            periodo=data['periodo'],
            statusAluno=data['statusAluno'],
            idCidade=data.get('idCidade_Cidades'),
            idEstado=data.get('idEstadoE_Cidades'),
            idAluno=data['idAluno']
        )
        aluno._ativo = bool(data.get('ativo', 1))
        
        return aluno
    
    @staticmethod
    def listar_por_cidade(idCidade, mostrar_inativos=False):
        con = conectar()
        cursor = con.cursor(dictionary=True)
        
        if mostrar_inativos:
            sql = """
                SELECT a.idAluno, a.nome, a.matricula, a.CPF, c.nome AS cidade, est.uf AS estado, a.ativo
                FROM aluno a
                LEFT JOIN cidades c ON a.idCidade_Cidades = c.idCidade
                LEFT JOIN estados est ON a.idEstadoE_Cidades = est.idEstado
                WHERE a.idCidade_Cidades = %s
                ORDER BY a.nome
            """
        else:
            sql = """
                SELECT a.idAluno, a.nome, a.matricula, a.CPF, c.nome AS cidade, est.uf AS estado, a.ativo
                FROM aluno a
                LEFT JOIN cidades c ON a.idCidade_Cidades = c.idCidade
                LEFT JOIN estados est ON a.idEstadoE_Cidades = est.idEstado
                WHERE (a.ativo IS NULL OR a.ativo = 1) AND a.idCidade_Cidades = %s
                ORDER BY a.nome
            """
        
        cursor.execute(sql, (idCidade,))
        rows = cursor.fetchall()
        cursor.close()
        con.close()
        
        return rows
    
    @staticmethod
    def listar_por_estado(idEstado, mostrar_inativos=False):
        con = conectar()
        cursor = con.cursor(dictionary=True)
        
        if mostrar_inativos:
            sql = """
                SELECT a.idAluno, a.nome, a.matricula, a.CPF, c.nome AS cidade, est.uf AS estado, a.ativo
                FROM aluno a
                LEFT JOIN cidades c ON a.idCidade_Cidades = c.idCidade
                LEFT JOIN estados est ON a.idEstadoE_Cidades = est.idEstado
                WHERE a.idEstadoE_Cidades = %s
                ORDER BY a.nome
            """
        else:
            sql = """
                SELECT a.idAluno, a.nome, a.matricula, a.CPF, c.nome AS cidade, est.uf AS estado, a.ativo
                FROM aluno a
                LEFT JOIN cidades c ON a.idCidade_Cidades = c.idCidade
                LEFT JOIN estados est ON a.idEstadoE_Cidades = est.idEstado
                WHERE (a.ativo IS NULL OR a.ativo = 1) AND a.idEstadoE_Cidades = %s
                ORDER BY a.nome
            """
        
        cursor.execute(sql, (idEstado,))
        rows = cursor.fetchall()
        cursor.close()
        con.close()
        
        return rows
