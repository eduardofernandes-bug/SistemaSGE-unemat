import re
import mysql.connector
import logging
from db import conectar

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def only_digits(s):
    return re.sub(r'\D', '', s or '')

class Empresa:
    def __init__(self, razao_social=None, nome_fantasia=None, cnpj=None, cep=None,
                 endereco=None, bairro=None, idCidade=None, idEstado=None, idEmpresa=None):
        self.idEmpresa = idEmpresa
        self.razao_social = razao_social
        self.nome_fantasia = nome_fantasia
        self.cnpj = cnpj
        self.cep = cep
        self.endereco = endereco
        self.bairro = bairro
        self.idCidade = idCidade
        self.idEstado = idEstado

    def _validar(self):
        cnpj_digits = only_digits(self.cnpj)
        if self.cnpj and len(cnpj_digits) != 14:
            return False, "CNPJ inválido: deve conter 14 dígitos."
        return True, None

    def salvar(self):
        """Insere nova empresa"""
        ok, msg = self._validar()
        if not ok:
            logger.warning("Validação falhou ao inserir empresa: %s", msg)
            return False

        con = None
        cursor = None
        try:
            con = conectar()
            cursor = con.cursor()
            sql = """
            INSERT INTO empresa (
                razaoSocial, nomeFantasia, cnpj, cep, endereco, bairro,
                idCidade_Cidades, idEstadoE_Cidades, ativo
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            valores = (
                self.razao_social, self.nome_fantasia, only_digits(self.cnpj) if self.cnpj else None,
                self.cep, self.endereco, self.bairro,
                self.idCidade, self.idEstado, 1
            )
            cursor.execute(sql, valores)
            con.commit()
            logger.info("Empresa '%s' inserida com sucesso.", self.nome_fantasia)
            return True
        except mysql.connector.IntegrityError as e:
            msg = str(e).lower()
            if "cnpj" in msg:
                logger.warning("CNPJ já cadastrado: %s", self.cnpj)
            else:
                logger.exception("Erro de integridade ao inserir empresa: %s", e)
            return False
        except Exception as e:
            logger.exception("Erro inesperado ao inserir empresa: %s", e)
            return False
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()

    def editar(self):
        """Atualiza empresa existente identificada por self.idEmpresa"""
        if not self.idEmpresa:
            logger.error("idEmpresa não informado para edição.")
            return False

        ok, msg = self._validar()
        if not ok:
            logger.warning("Validação falhou ao editar empresa: %s", msg)
            return False

        con = None
        cursor = None
        try:
            con = conectar()
            cursor = con.cursor()
            sql = """
            UPDATE empresa SET
                razaoSocial = %s,
                nomeFantasia = %s,
                cnpj = %s,
                cep = %s,
                endereco = %s,
                bairro = %s,
                idCidade_Cidades = %s,
                idEstadoE_Cidades = %s
            WHERE idEmpresa = %s
            """
            valores = (
                self.razao_social, self.nome_fantasia, only_digits(self.cnpj) if self.cnpj else None,
                self.cep, self.endereco, self.bairro,
                self.idCidade, self.idEstado, self.idEmpresa
            )
            cursor.execute(sql, valores)
            con.commit()
            logger.info("Empresa id=%s atualizada com sucesso.", self.idEmpresa)
            return True
        except mysql.connector.IntegrityError as e:
            logger.exception("Erro de integridade ao editar empresa: %s", e)
            return False
        except Exception as e:
            logger.exception("Erro inesperado ao editar empresa: %s", e)
            return False
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()

    @staticmethod
    def listar(mostrar_inativos=False):
        """Lista empresas com cidade e estado (dictionary list)."""
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

    @staticmethod
    def listar_por_cidade(idCidade, mostrar_inativos=False):
        """Lista empresas filtradas por cidade."""
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
            params = (idCidade,)
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
            params = (idCidade,)

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()
        con.close()
        return rows

    @staticmethod
    def listar_por_estado(idEstado, mostrar_inativos=False):
        """Lista empresas filtradas por estado."""
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
            params = (idEstado,)
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
            params = (idEstado,)

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()
        con.close()
        return rows

    def desativar(self):
        """Marca a empresa como inativa (ativo = 0)"""
        if not self.idEmpresa:
            logger.error("idEmpresa não informado para desativação.")
            return False
        con = None
        cursor = None
        try:
            con = conectar()
            cursor = con.cursor()
            cursor.execute("UPDATE empresa SET ativo = 0 WHERE idEmpresa = %s", (self.idEmpresa,))
            con.commit()
            logger.info("Empresa id=%s desativada.", self.idEmpresa)
            return True
        except Exception as e:
            logger.exception("Erro ao desativar empresa: %s", e)
            return False
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
