import re
import mysql.connector
import logging
from db import conectar

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def only_digits(s):
    return re.sub(r'\D', '', s or '')

class Aluno:
    def __init__(self, nome=None, matricula=None, cpf=None, nomeInstitucional=None, telefone=None,
                 endereco=None, bairro=None, periodo=None, statusAluno=None, idCidade=None, idEstado=None,
                 idAluno=None):
        self.idAluno = idAluno
        self.nome = nome
        self.matricula = matricula
        self.cpf = cpf
        self.nomeInstitucional = nomeInstitucional
        self.telefone = telefone
        self.endereco = endereco
        self.bairro = bairro
        self.periodo = periodo
        self.statusAluno = statusAluno
        self.idcidade = idCidade
        self.idEstado = idEstado

    def _validar(self):
        """Validações mínimas de formato (CPF e telefone). Retorna (True, None) se ok ou (False, msg)."""
        cpf_digits = only_digits(self.cpf)
        if not cpf_digits or len(cpf_digits) != 11:
            return False, "CPF inválido: deve conter 11 dígitos."
        if self.telefone:
            tel_digits = only_digits(self.telefone)
            if len(tel_digits) not in (10, 11):
                return False, "Telefone inválido: informe 10 ou 11 dígitos."
        return True, None

    def salvar(self):
        """Insere um novo aluno. Retorna True em sucesso, False caso contrário."""
        ok, msg = self._validar()
        if not ok:
            logger.warning("Validação falhou ao inserir aluno: %s", msg)
            return False

        con = None
        cursor = None
        try:
            con = conectar()
            cursor = con.cursor()
            sql = """
            INSERT INTO aluno (
                nome, matricula, CPF, nomeInstitucional, telefone,
                endereco, bairro, periodo, statusAluno,
                idCidade_Cidades, idEstadoE_Cidades, ativo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (
                self.nome, self.matricula, only_digits(self.cpf), self.nomeInstitucional,
                only_digits(self.telefone) if self.telefone else None, self.endereco, self.bairro,
                self.periodo, self.statusAluno, self.idcidade, self.idEstado, 1
            )
            cursor.execute(sql, valores)
            con.commit()
            logger.info("Aluno '%s' inserido com sucesso (matrícula: %s).", self.nome, self.matricula)
            return True
        except mysql.connector.IntegrityError as e:
            msg_text = str(e).lower()
            if "matricula" in msg_text:
                logger.warning("Matrícula já cadastrada: %s", self.matricula)
            elif "cpf" in msg_text or "cpf" in msg_text:
                logger.warning("CPF já cadastrado.")
            else:
                logger.exception("Erro de integridade ao inserir aluno: %s", e)
            return False
        except Exception as e:
            logger.exception("Erro inesperado ao inserir aluno: %s", e)
            return False
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()

    def editar(self):
        """Atualiza um aluno existente. Usa self.idAluno para localizar o registro."""
        if not self.idAluno:
            logger.error("idAluno não informado para edição.")
            return False

        ok, msg = self._validar()
        if not ok:
            logger.warning("Validação falhou ao editar aluno: %s", msg)
            return False

        con = None
        cursor = None
        try:
            con = conectar()
            cursor = con.cursor()
            sql = """
            UPDATE aluno SET
                nome = %s,
                matricula = %s,
                CPF = %s,
                nomeInstitucional = %s,
                telefone = %s,
                endereco = %s,
                bairro = %s,
                periodo = %s,
                statusAluno = %s,
                idCidade_Cidades = %s,
                idEstadoE_Cidades = %s
            WHERE idAluno = %s
            """
            valores = (
                self.nome, self.matricula, only_digits(self.cpf), self.nomeInstitucional,
                only_digits(self.telefone) if self.telefone else None, self.endereco, self.bairro,
                self.periodo, self.statusAluno, self.idcidade, self.idEstado, self.idAluno
            )
            cursor.execute(sql, valores)
            con.commit()
            logger.info("Aluno id=%s atualizado com sucesso.", self.idAluno)
            return True
        except mysql.connector.IntegrityError as e:
            logger.exception("Erro de integridade ao editar aluno: %s", e)
            return False
        except Exception as e:
            logger.exception("Erro inesperado ao editar aluno: %s", e)
            return False
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()

    @staticmethod
    def listar(mostrar_inativos=False):
        """Retorna lista de alunos com cidade e estado (dictionary list)."""
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

    def desativar(self):
        """Marca o registro como inativo (ativo = 0)."""
        if not self.idAluno:
            logger.error("idAluno não informado para desativação.")
            return False
        con = None
        cursor = None
        try:
            con = conectar()
            cursor = con.cursor()
            cursor.execute("UPDATE aluno SET ativo = 0 WHERE idAluno = %s", (self.idAluno,))
            con.commit()
            logger.info("Aluno id=%s desativado.", self.idAluno)
            return True
        except Exception as e:
            logger.exception("Erro ao desativar: %s", e)
            return False
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
