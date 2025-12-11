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


class Empresa(BaseModel):
    def __init__(self, razao_social=None, nome_fantasia=None, cnpj=None, cep=None,
                 endereco=None, bairro=None, idCidade=None, idEstado=None, idEmpresa=None):


        super().__init__(id_value=idEmpresa)
        
        self._razao_social = razao_social
        self._nome_fantasia = nome_fantasia
        self._cnpj = cnpj
        self._cep = cep
        self._endereco = endereco
        self._bairro = bairro
        self._idCidade = idCidade
        self._idEstado = idEstado
    
    
    @property
    def idEmpresa(self):
        return self._id
    
    @property
    def razao_social(self):
        return self._razao_social
    
    @razao_social.setter
    def razao_social(self, valor):
        if valor and not isinstance(valor, str):
            raise ValueError("Razão social deve ser uma string")
        self._razao_social = valor
    
    @property
    def nome_fantasia(self):
        return self._nome_fantasia
    
    @nome_fantasia.setter
    def nome_fantasia(self, valor):
        self._nome_fantasia = valor
    
    @property
    def cnpj(self):
        """Retorna CNPJ apenas com dígitos"""
        return only_digits(self._cnpj) if self._cnpj else None
    
    @cnpj.setter
    def cnpj(self, valor):
        """Valida CNPJ ao atribuir"""
        if valor:
            cnpj_digits = only_digits(valor)
            if len(cnpj_digits) != 14:
                raise ValueError("CNPJ deve conter 14 dígitos")
            self._cnpj = valor
        else:
            self._cnpj = None
    
    @property
    def cep(self):
        return self._cep
    
    @cep.setter
    def cep(self, valor):
        self._cep = valor
    
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
    def idCidade(self):
        return self._idCidade
    
    @idCidade.setter
    def idCidade(self, valor):
        self._idCidade = valor
    
    @property
    def idEstado(self):
        return self._idEstado
    
    @idEstado.setter
    def idEstado(self, valor):
        self._idEstado = valor
    
    
    def __str__(self):
        nome = self._nome_fantasia or self._razao_social or "Sem nome"
        return f"Empresa: {nome}"
    
    def __repr__(self):
        return f"<Empresa id={self._id} razao='{self._razao_social}' fantasia='{self._nome_fantasia}'>"
    
    
    def _get_table_name(self):
        return "empresa"
    
    def _get_id_column_name(self):
        return "idEmpresa"
    
    def _validar(self):
        if self._cnpj:
            try:
                cnpj_digits = self.cnpj
                if not cnpj_digits:
                    return False, "CNPJ inválido"
            except ValueError as e:
                return False, str(e)
        
        return True, None
    
    def _get_insert_data(self):
        colunas = [
            'razaoSocial', 'nomeFantasia', 'cnpj', 'cep',
            'endereco', 'bairro', 'idCidade_Cidades', 'idEstadoE_Cidades'
        ]
        
        valores = [
            self._razao_social,
            self._nome_fantasia,
            self.cnpj,
            self._cep,
            self._endereco,
            self._bairro,
            self._idCidade,
            self._idEstado
        ]
        
        return (colunas, valores)
    
    def _get_update_data(self):
        colunas = [
            'razaoSocial', 'nomeFantasia', 'cnpj', 'cep',
            'endereco', 'bairro', 'idCidade_Cidades', 'idEstadoE_Cidades'
        ]
        
        valores = [
            self._razao_social,
            self._nome_fantasia,
            self.cnpj,
            self._cep,
            self._endereco,
            self._bairro,
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
                SELECT e.idEmpresa, e.razaoSocial, e.nomeFantasia, e.cnpj, e.cep,
                       e.endereco, e.bairro,
                       c.nome AS cidade, est.uf AS estado,
                       e.ativo,
                       e.idCidade_Cidades, e.idEstadoE_Cidades
                FROM empresa e
                LEFT JOIN cidades c ON e.idCidade_Cidades = c.idCidade
                LEFT JOIN estados est ON c.idEstadoE = est.idEstado
                WHERE e.ativo IS NULL OR e.ativo = 0
                ORDER BY e.nomeFantasia
            """
        else:
            sql = """
                SELECT e.idEmpresa, e.razaoSocial, e.nomeFantasia, e.cnpj, e.cep,
                       e.endereco, e.bairro,
                       c.nome AS cidade, est.uf AS estado,
                       e.ativo,
                       e.idCidade_Cidades, e.idEstadoE_Cidades
                FROM empresa e
                LEFT JOIN cidades c ON e.idCidade_Cidades = c.idCidade
                LEFT JOIN estados est ON c.idEstadoE = est.idEstado
                WHERE e.ativo IS NULL OR e.ativo = 1
                ORDER BY e.nomeFantasia
            """
        
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        con.close()
        
        return rows
    
    @staticmethod
    def buscar_por_id(idEmpresa):
        con = conectar()
        cursor = con.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT e.idEmpresa, e.razaoSocial, e.nomeFantasia, e.cnpj, e.cep,
                   e.endereco, e.bairro,
                   c.idCidade, c.nome AS cidade, est.idEstado, est.nome AS estado, est.uf,
                   e.idCidade_Cidades, e.idEstadoE_Cidades, e.ativo
            FROM empresa e
            LEFT JOIN cidades c ON e.idCidade_Cidades = c.idCidade
            LEFT JOIN estados est ON e.idEstadoE_Cidades = est.idEstado
            WHERE e.idEmpresa = %s
        """, (idEmpresa,))
        
        row = cursor.fetchone()
        cursor.close()
        con.close()
        
        return row
    
    @classmethod
    def buscar_por_id_objeto(cls, idEmpresa):
        data = cls.buscar_por_id(idEmpresa)
        
        if not data:
            return None
        
        empresa = cls(
            razao_social=data['razaoSocial'],
            nome_fantasia=data['nomeFantasia'],
            cnpj=data['cnpj'],
            cep=data['cep'],
            endereco=data['endereco'],
            bairro=data['bairro'],
            idCidade=data.get('idCidade_Cidades'),
            idEstado=data.get('idEstadoE_Cidades'),
            idEmpresa=data['idEmpresa']
        )
        empresa._ativo = bool(data.get('ativo', 1))
        
        return empresa
    
    @staticmethod
    def listar_por_cidade(idCidade, mostrar_inativos=False):
        con = conectar()
        cursor = con.cursor(dictionary=True)
        
        if mostrar_inativos:
            sql = """
                SELECT e.idEmpresa, e.razaoSocial, e.nomeFantasia, e.cnpj, e.cep,
                       e.endereco, e.bairro,
                       c.nome AS cidade, est.uf AS estado,
                       e.ativo
                FROM empresa e
                LEFT JOIN cidades c ON e.idCidade_Cidades = c.idCidade
                LEFT JOIN estados est ON c.idEstadoE = est.idEstado
                WHERE e.idCidade_Cidades = %s
                ORDER BY e.nomeFantasia
            """
        else:
            sql = """
                SELECT e.idEmpresa, e.razaoSocial, e.nomeFantasia, e.cnpj, e.cep,
                       e.endereco, e.bairro,
                       c.nome AS cidade, est.uf AS estado,
                       e.ativo
                FROM empresa e
                LEFT JOIN cidades c ON e.idCidade_Cidades = c.idCidade
                LEFT JOIN estados est ON c.idEstadoE = est.idEstado
                WHERE (e.ativo IS NULL OR e.ativo = 1) AND e.idCidade_Cidades = %s
                ORDER BY e.nomeFantasia
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
                SELECT e.idEmpresa, e.razaoSocial, e.nomeFantasia, e.cnpj, e.cep,
                       e.endereco, e.bairro,
                       c.nome AS cidade, est.uf AS estado,
                       e.ativo
                FROM empresa e
                LEFT JOIN cidades c ON e.idCidade_Cidades = c.idCidade
                LEFT JOIN estados est ON c.idEstadoE = est.idEstado
                WHERE c.idEstadoE = %s
                ORDER BY e.nomeFantasia
            """
        else:
            sql = """
                SELECT e.idEmpresa, e.razaoSocial, e.nomeFantasia, e.cnpj, e.cep,
                       e.endereco, e.bairro,
                       c.nome AS cidade, est.uf AS estado,
                       e.ativo
                FROM empresa e
                LEFT JOIN cidades c ON e.idCidade_Cidades = c.idCidade
                LEFT JOIN estados est ON c.idEstadoE = est.idEstado
                WHERE (e.ativo IS NULL OR e.ativo = 1) AND c.idEstadoE = %s
                ORDER BY e.nomeFantasia
            """
        
        cursor.execute(sql, (idEstado,))
        rows = cursor.fetchall()
        cursor.close()
        con.close()
        
        return rows
