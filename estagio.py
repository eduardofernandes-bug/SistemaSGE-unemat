import re
import mysql.connector
import logging
from db import conectar
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def only_digits(s):
    return re.sub(r'\D', '', s or '')

class Estagio:
    def __init__(self, idAluno=None, idEmpresa=None, data_inicio=None, data_fim=None,
                 carga_horaria=None, situacao=None, supervisor=None, orientador=None,
                 setor=None, documentacao=None, status=None, idEstagio=None):
        self.idEstagio = idEstagio
        self.idAluno = idAluno
        self.idEmpresa = idEmpresa
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.carga_horaria = carga_horaria
        self.situacao = situacao
        self.supervisor = supervisor
        self.orientador = orientador
        self.setor = setor
        self.documentacao = documentacao
        self.status = status

    def _validar_datas(self):
        if not self.data_inicio:
            return True, None
        try:
            di = datetime.strptime(self.data_inicio, "%Y-%m-%d").date()
        except Exception:
            return False, "Data de início inválida. Use AAAA-MM-DD."
        if self.data_fim:
            try:
                df = datetime.strptime(self.data_fim, "%Y-%m-%d").date()
            except Exception:
                return False, "Data de fim inválida. Use AAAA-MM-DD."
            if df < di:
                return False, "Data de fim não pode ser anterior à data de início."
        return True, None

    def salvar(self):
        ok, msg = self._validar_datas()
        if not ok:
            logger.warning("Validação de datas falhou ao inserir estagio: %s", msg)
            return False

        con = None
        cursor = None
        try:
            con = conectar()
            cursor = con.cursor()
            sql = """INSERT INTO estagio
                     (idAlunoA, idEmpresaE, dataInicio, dataFim, cargaHorariaSemanal, situacao,
                      supervisor, orientadorAcademico, setor, documentacao, statusEstagio, ativo)
                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            valores = (self.idAluno, self.idEmpresa, self.data_inicio, self.data_fim,
                       self.carga_horaria, self.situacao, self.supervisor, self.orientador,
                       self.setor, self.documentacao, self.status, 1)
            cursor.execute(sql, valores)
            con.commit()
            logger.info("Estágio inserido com sucesso: aluno=%s empresa=%s", self.idAluno, self.idEmpresa)
            return True
        except mysql.connector.IntegrityError as e:
            logger.exception("Erro de integridade ao inserir estagio: %s", e)
            return False
        except Exception as e:
            logger.exception("Erro inesperado ao inserir estagio: %s", e)
            return False
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()

    def editar(self):
        if not self.idEstagio:
            logger.error("idEstagio não informado para edição.")
            return False

        ok, msg = self._validar_datas()
        if not ok:
            logger.warning("Validação de datas falhou ao editar estagio: %s", msg)
            return False

        con = None
        cursor = None
        try:
            con = conectar()
            cursor = con.cursor()
            sql = """UPDATE estagio SET
                        idAlunoA = %s,
                        idEmpresaE = %s,
                        dataInicio = %s,
                        dataFim = %s,
                        cargaHorariaSemanal = %s,
                        situacao = %s,
                        supervisor = %s,
                        orientadorAcademico = %s,
                        setor = %s,
                        documentacao = %s,
                        statusEstagio = %s
                     WHERE idEstagio = %s"""
            valores = (self.idAluno, self.idEmpresa, self.data_inicio, self.data_fim,
                       self.carga_horaria, self.situacao, self.supervisor, self.orientador,
                       self.setor, self.documentacao, self.status, self.idEstagio)
            cursor.execute(sql, valores)
            con.commit()
            logger.info("Estágio id=%s atualizado com sucesso.", self.idEstagio)
            return True
        except mysql.connector.IntegrityError as e:
            logger.exception("Erro de integridade ao editar estagio: %s", e)
            return False
        except Exception as e:
            logger.exception("Erro inesperado ao editar estagio: %s", e)
            return False
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()

    @staticmethod
    def listar(mostrar_inativos=False):
        """Lista estágios (apenas ativos por padrão) com aluno e empresa."""
        con = conectar()
        cursor = con.cursor(dictionary=True)

        if mostrar_inativos:
            sql = """
            SELECT e.idEstagio,
                   a.idAluno, a.nome AS aluno, a.idCidade_Cidades AS aluno_idCidade, ac.nome AS aluno_cidade, a.idEstadoE_Cidades AS aluno_idEstado, aest.uf AS aluno_estado,
                   emp.idEmpresa, emp.nomeFantasia AS empresa, emp.idCidade_Cidades AS empresa_idCidade, ec.nome AS empresa_cidade, emp.idEstadoE_Cidades AS empresa_idEstado, eest.uf AS empresa_estado,
                   e.dataInicio, e.dataFim, e.cargaHorariaSemanal, e.situacao, e.statusEstagio, e.ativo
            FROM estagio e
            JOIN aluno a ON e.idAlunoA = a.idAluno
            LEFT JOIN cidades ac ON a.idCidade_Cidades = ac.idCidade
            LEFT JOIN estados aest ON ac.idEstadoE = aest.idEstado
            JOIN empresa emp ON e.idEmpresaE = emp.idEmpresa
            LEFT JOIN cidades ec ON emp.idCidade_Cidades = ec.idCidade
            LEFT JOIN estados eest ON ec.idEstadoE = eest.idEstado
            WHERE e.ativo IS NULL OR e.ativo = 0
            ORDER BY e.dataInicio DESC
            """
            params = ()
        else:
            sql = """
            SELECT e.idEstagio,
                   a.idAluno, a.nome AS aluno, a.idCidade_Cidades AS aluno_idCidade, ac.nome AS aluno_cidade, a.idEstadoE_Cidades AS aluno_idEstado, aest.uf AS aluno_estado,
                   emp.idEmpresa, emp.nomeFantasia AS empresa, emp.idCidade_Cidades AS empresa_idCidade, ec.nome AS empresa_cidade, emp.idEstadoE_Cidades AS empresa_idEstado, eest.uf AS empresa_estado,
                   e.dataInicio, e.dataFim, e.cargaHorariaSemanal, e.situacao, e.statusEstagio, e.ativo
            FROM estagio e
            JOIN aluno a ON e.idAlunoA = a.idAluno
            LEFT JOIN cidades ac ON a.idCidade_Cidades = ac.idCidade
            LEFT JOIN estados aest ON ac.idEstadoE = aest.idEstado
            JOIN empresa emp ON e.idEmpresaE = emp.idEmpresa
            LEFT JOIN cidades ec ON emp.idCidade_Cidades = ec.idCidade
            LEFT JOIN estados eest ON ec.idEstadoE = eest.idEstado
            WHERE e.ativo IS NULL OR e.ativo = 1
            ORDER BY e.dataInicio DESC
            """
            params = ()

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()
        con.close()
        return rows

    
    # Substitua o método buscar_por_id na classe Estagio (estagio.py)

    @staticmethod
    def buscar_por_id(idEstagio):
        con = conectar()
        cursor = con.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.idEstagio, e.idAlunoA, e.idEmpresaE, e.dataInicio, e.dataFim, e.cargaHorariaSemanal, e.situacao, e.supervisor, e.orientadorAcademico,
                   e.setor, e.documentacao, e.statusEstagio, e.ativo, a.nome AS aluno, emp.nomeFantasia AS empresa
            FROM estagio e
            LEFT JOIN aluno a ON e.idAlunoA = a.idAluno
            LEFT JOIN empresa emp ON e.idEmpresaE = emp.idEmpresa
            WHERE e.idEstagio = %s
        """, (idEstagio,))
        row = cursor.fetchone()
        cursor.close()
        con.close()
        return row
    
    @staticmethod
    def listar_por_estado(idEstado, mostrar_inativos=False):
        """Lista estágios onde aluno OU empresa pertence ao estado informado."""
        con = conectar()
        cursor = con.cursor(dictionary=True)

        if mostrar_inativos:
            sql = """
            SELECT e.idEstagio,
                   a.idAluno, a.nome AS aluno, aest.uf AS aluno_estado,
                   emp.idEmpresa, emp.nomeFantasia AS empresa, eest.uf AS empresa_estado,
                   e.dataInicio, e.dataFim, e.cargaHorariaSemanal, e.situacao, e.statusEstagio, e.ativo
            FROM estagio e
            JOIN aluno a ON e.idAlunoA = a.idAluno
            LEFT JOIN cidades ac ON a.idCidade_Cidades = ac.idCidade
            LEFT JOIN estados aest ON ac.idEstadoE = aest.idEstado
            JOIN empresa emp ON e.idEmpresaE = emp.idEmpresa
            LEFT JOIN cidades ec ON emp.idCidade_Cidades = ec.idCidade
            LEFT JOIN estados eest ON ec.idEstadoE = eest.idEstado
            WHERE (a.idEstadoE_Cidades = %s OR emp.idEstadoE_Cidades = %s)
            ORDER BY e.dataInicio DESC
            """
            params = (idEstado, idEstado)
        else:
            sql = """
            SELECT e.idEstagio,
                   a.idAluno, a.nome AS aluno, aest.uf AS aluno_estado,
                   emp.idEmpresa, emp.nomeFantasia AS empresa, eest.uf AS empresa_estado,
                   e.dataInicio, e.dataFim, e.cargaHorariaSemanal, e.situacao, e.statusEstagio, e.ativo
            FROM estagio e
            JOIN aluno a ON e.idAlunoA = a.idAluno
            LEFT JOIN cidades ac ON a.idCidade_Cidades = ac.idCidade
            LEFT JOIN estados aest ON ac.idEstadoE = aest.idEstado
            JOIN empresa emp ON e.idEmpresaE = emp.idEmpresa
            LEFT JOIN cidades ec ON emp.idCidade_Cidades = ec.idCidade
            LEFT JOIN estados eest ON ec.idEstadoE = eest.idEstado
            WHERE (e.ativo IS NULL OR e.ativo = 1)
              AND (a.idEstadoE_Cidades = %s OR emp.idEstadoE_Cidades = %s)
            ORDER BY e.dataInicio DESC
            """
            params = (idEstado, idEstado)

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()
        con.close()
        return rows

    @staticmethod
    def listar_por_cidade(idCidade, mostrar_inativos=False):
        """Lista estágios onde aluno OU empresa pertence à cidade informada."""
        con = conectar()
        cursor = con.cursor(dictionary=True)

        if mostrar_inativos:
            sql = """
            SELECT e.idEstagio,
                   a.idAluno, a.nome AS aluno, ac.nome AS aluno_cidade,
                   emp.idEmpresa, emp.nomeFantasia AS empresa, ec.nome AS empresa_cidade,
                   e.dataInicio, e.dataFim, e.cargaHorariaSemanal, e.situacao, e.statusEstagio, e.ativo
            FROM estagio e
            JOIN aluno a ON e.idAlunoA = a.idAluno
            LEFT JOIN cidades ac ON a.idCidade_Cidades = ac.idCidade
            JOIN empresa emp ON e.idEmpresaE = emp.idEmpresa
            LEFT JOIN cidades ec ON emp.idCidade_Cidades = ec.idCidade
            WHERE (a.idCidade_Cidades = %s OR emp.idCidade_Cidades = %s)
            ORDER BY e.dataInicio DESC
            """
            params = (idCidade, idCidade)
        else:
            sql = """
            SELECT e.idEstagio,
                   a.idAluno, a.nome AS aluno, ac.nome AS aluno_cidade,
                   emp.idEmpresa, emp.nomeFantasia AS empresa, ec.nome AS empresa_cidade,
                   e.dataInicio, e.dataFim, e.cargaHorariaSemanal, e.situacao, e.statusEstagio, e.ativo
            FROM estagio e
            JOIN aluno a ON e.idAlunoA = a.idAluno
            LEFT JOIN cidades ac ON a.idCidade_Cidades = ac.idCidade
            JOIN empresa emp ON e.idEmpresaE = emp.idEmpresa
            LEFT JOIN cidades ec ON emp.idCidade_Cidades = ec.idCidade
            WHERE (e.ativo IS NULL OR e.ativo = 1)
              AND (a.idCidade_Cidades = %s OR emp.idCidade_Cidades = %s)
            ORDER BY e.dataInicio DESC
            """
            params = (idCidade, idCidade)

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()
        con.close()
        return rows


    def desativar(self):
        if not self.idEstagio:
            logger.error("idEstagio não informado para desativação.")
            return False
        con = None
        cursor = None
        try:
            con = conectar()
            cursor = con.cursor()
            cursor.execute("UPDATE estagio SET ativo = 0 WHERE idEstagio = %s", (self.idEstagio,))
            con.commit()
            logger.info("Estágio id=%s desativado.", self.idEstagio)
            return True
        except Exception as e:
            logger.exception("Erro ao desativar estagio: %s", e)
            return False
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
