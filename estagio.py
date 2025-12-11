# -*- coding: utf-8 -*-

import re
import mysql.connector
import logging
from datetime import datetime
from db import conectar
from base_model import BaseModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def only_digits(s):
    return re.sub(r'\D', '', s or '')


class Estagio(BaseModel):
    def __init__(self, idAluno=None, idEmpresa=None, data_inicio=None, data_fim=None,
                 carga_horaria=None, situacao=None, supervisor=None, orientador=None,
                 setor=None, documentacao=None, status=None, idEstagio=None):

        super().__init__(id_value=idEstagio)
        
        self._idAluno = idAluno
        self._idEmpresa = idEmpresa
        self._data_inicio = data_inicio
        self._data_fim = data_fim
        self._carga_horaria = carga_horaria
        self._situacao = situacao
        self._supervisor = supervisor
        self._orientador = orientador
        self._setor = setor
        self._documentacao = documentacao
        self._status = status
    
    @property
    def idEstagio(self):
        return self._id
    
    @property
    def idAluno(self):
        return self._idAluno
    
    @idAluno.setter
    def idAluno(self, valor):
        if valor is not None and not isinstance(valor, int):
            raise ValueError("idAluno deve ser um inteiro")
        self._idAluno = valor
    
    @property
    def idEmpresa(self):
        return self._idEmpresa
    
    @idEmpresa.setter
    def idEmpresa(self, valor):
        if valor is not None and not isinstance(valor, int):
            raise ValueError("idEmpresa deve ser um inteiro")
        self._idEmpresa = valor
    
    @property
    def data_inicio(self):
        if self._data_inicio:
            if isinstance(self._data_inicio, str):
                return self._data_inicio
            return self._data_inicio.strftime('%Y-%m-%d')
        return None
    
    @data_inicio.setter
    def data_inicio(self, valor):
        if valor:
            if isinstance(valor, str):
                try:
                    datetime.strptime(valor, "%Y-%m-%d")
                    self._data_inicio = valor
                except ValueError:
                    raise ValueError("Data de início inválida. Use formato YYYY-MM-DD")
            else:
                self._data_inicio = valor
        else:
            self._data_inicio = None
    
    @property
    def data_fim(self):
        if self._data_fim:
            if isinstance(self._data_fim, str):
                return self._data_fim
            return self._data_fim.strftime('%Y-%m-%d')
        return None
    
    @data_fim.setter
    def data_fim(self, valor):
        if valor:
            if isinstance(valor, str):
                try:
                    datetime.strptime(valor, "%Y-%m-%d")
                    self._data_fim = valor
                except ValueError:
                    raise ValueError("Data de fim inválida. Use formato YYYY-MM-DD")
            else:
                self._data_fim = valor
        else:
            self._data_fim = None
    
    @property
    def carga_horaria(self):
        return self._carga_horaria
    
    @carga_horaria.setter
    def carga_horaria(self, valor):
        self._carga_horaria = valor
    
    @property
    def situacao(self):
        return self._situacao
    
    @situacao.setter
    def situacao(self, valor):
        situacoes_validas = ['Aguardando', 'Ativo', 'Trancado', 'Concluído', 'Cancelado']
        if valor and valor not in situacoes_validas:
            logger.warning(f"Situação '{valor}' não está na lista padrão: {situacoes_validas}")
        self._situacao = valor
    
    @property
    def supervisor(self):
        return self._supervisor
    
    @supervisor.setter
    def supervisor(self, valor):
        self._supervisor = valor
    
    @property
    def orientador(self):
        return self._orientador
    
    @orientador.setter
    def orientador(self, valor):
        self._orientador = valor
    
    @property
    def setor(self):
        return self._setor
    
    @setor.setter
    def setor(self, valor):
        self._setor = valor
    
    @property
    def documentacao(self):
        return self._documentacao
    
    @documentacao.setter
    def documentacao(self, valor):
        self._documentacao = valor
    
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, valor):
        self._status = valor
    
    
    def __str__(self):
        return f"Estágio #{self._id} - Aluno ID: {self._idAluno}, Empresa ID: {self._idEmpresa}"
    
    def __repr__(self):
        return f"<Estagio id={self._id} aluno={self._idAluno} empresa={self._idEmpresa} situacao='{self._situacao}'>"
    
    def calcular_progresso(self):
        try:
            if not self._data_inicio or not self._data_fim:
                return 0
            
            if isinstance(self._data_inicio, str):
                di = datetime.strptime(self._data_inicio, "%Y-%m-%d").date()
            else:
                di = self._data_inicio
            
            if isinstance(self._data_fim, str):
                df = datetime.strptime(self._data_fim, "%Y-%m-%d").date()
            else:
                df = self._data_fim
            
            hoje = datetime.now().date()
            
            total = (df - di).days
            if total <= 0:
                return 0
            
            decorrido = (min(hoje, df) - di).days
            pct = int((decorrido / total) * 100)
            
            return max(0, min(100, pct))
            
        except Exception as e:
            logger.error(f"Erro ao calcular progresso: {e}")
            return 0
    
    def dias_restantes(self):
        try:
            if not self._data_fim:
                return None
            
            if isinstance(self._data_fim, str):
                df = datetime.strptime(self._data_fim, "%Y-%m-%d").date()
            else:
                df = self._data_fim
            
            hoje = datetime.now().date()
            return (df - hoje).days
            
        except Exception:
            return None
    
    def _get_table_name(self):
        return "estagio"
    
    def _get_id_column_name(self):
        return "idEstagio"
    
    def _validar(self):
        if self._data_inicio:
            try:
                if isinstance(self._data_inicio, str):
                    di = datetime.strptime(self._data_inicio, "%Y-%m-%d").date()
                else:
                    di = self._data_inicio
            except Exception:
                return False, "Data de início inválida. Use formato YYYY-MM-DD."
            
            if self._data_fim:
                try:
                    if isinstance(self._data_fim, str):
                        df = datetime.strptime(self._data_fim, "%Y-%m-%d").date()
                    else:
                        df = self._data_fim
                    
                    if df < di:
                        return False, "Data de fim não pode ser anterior à data de início."
                        
                except Exception:
                    return False, "Data de fim inválida. Use formato YYYY-MM-DD."
        
        return True, None
    
    def _get_insert_data(self):
        colunas = [
            'idAlunoA', 'idEmpresaE', 'dataInicio', 'dataFim',
            'cargaHorariaSemanal', 'situacao', 'supervisor',
            'orientadorAcademico', 'setor', 'documentacao', 'statusEstagio'
        ]
        
        valores = [
            self._idAluno,
            self._idEmpresa,
            self.data_inicio,
            self.data_fim,
            self._carga_horaria,
            self._situacao,
            self._supervisor,
            self._orientador,
            self._setor,
            self._documentacao,
            self._status
        ]
        
        return (colunas, valores)
    
    def _get_update_data(self):
        colunas = [
            'idAlunoA', 'idEmpresaE', 'dataInicio', 'dataFim',
            'cargaHorariaSemanal', 'situacao', 'supervisor',
            'orientadorAcademico', 'setor', 'documentacao', 'statusEstagio'
        ]
        
        valores = [
            self._idAluno,
            self._idEmpresa,
            self.data_inicio,
            self.data_fim,
            self._carga_horaria,
            self._situacao,
            self._supervisor,
            self._orientador,
            self._setor,
            self._documentacao,
            self._status
        ]
        
        return (colunas, valores)
    
    @staticmethod
    def listar(mostrar_inativos=False):
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
        
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        con.close()
        
        return rows
    
    @staticmethod
    def buscar_por_id(idEstagio):
        con = conectar()
        cursor = con.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT e.idEstagio, e.idAlunoA, e.idEmpresaE, e.dataInicio, e.dataFim, 
                   e.cargaHorariaSemanal, e.situacao, e.supervisor, e.orientadorAcademico,
                   e.setor, e.documentacao, e.statusEstagio, e.ativo, 
                   a.nome AS aluno, emp.nomeFantasia AS empresa
            FROM estagio e
            LEFT JOIN aluno a ON e.idAlunoA = a.idAluno
            LEFT JOIN empresa emp ON e.idEmpresaE = emp.idEmpresa
            WHERE e.idEstagio = %s
        """, (idEstagio,))
        
        row = cursor.fetchone()
        cursor.close()
        con.close()
        
        return row
    
    @classmethod
    def buscar_por_id_objeto(cls, idEstagio):
        data = cls.buscar_por_id(idEstagio)
        
        if not data:
            return None
        
        estagio = cls(
            idAluno=data['idAlunoA'],
            idEmpresa=data['idEmpresaE'],
            data_inicio=data['dataInicio'],
            data_fim=data['dataFim'],
            carga_horaria=data['cargaHorariaSemanal'],
            situacao=data['situacao'],
            supervisor=data['supervisor'],
            orientador=data['orientadorAcademico'],
            setor=data['setor'],
            documentacao=data['documentacao'],
            status=data['statusEstagio'],
            idEstagio=data['idEstagio']
        )
        estagio._ativo = bool(data.get('ativo', 1))
        
        return estagio
    
    @staticmethod
    def listar_por_estado(idEstado, mostrar_inativos=False):
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
        
        cursor.execute(sql, (idEstado, idEstado))
        rows = cursor.fetchall()
        cursor.close()
        con.close()
        
        return rows
    
    @staticmethod
    def listar_por_cidade(idCidade, mostrar_inativos=False):
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
        
        cursor.execute(sql, (idCidade, idCidade))
        rows = cursor.fetchall()
        cursor.close()
        con.close()
        
        return rows
    
    @staticmethod
    def listar_por_aluno(idAluno, mostrar_inativos=False):
        con = conectar()
        cursor = con.cursor(dictionary=True)
        
        if mostrar_inativos:
            sql = """
                SELECT e.idEstagio,
                       a.idAluno, a.nome AS aluno,
                       emp.idEmpresa, emp.nomeFantasia AS empresa,
                       e.idEmpresaE, e.dataInicio, e.dataFim, e.cargaHorariaSemanal,
                       e.situacao, e.statusEstagio, e.ativo, e.supervisor, e.orientadorAcademico
                FROM estagio e
                LEFT JOIN aluno a ON e.idAlunoA = a.idAluno
                LEFT JOIN empresa emp ON e.idEmpresaE = emp.idEmpresa
                WHERE e.idAlunoA = %s
                ORDER BY e.dataInicio DESC
            """
        else:
            sql = """
                SELECT e.idEstagio,
                       a.idAluno, a.nome AS aluno,
                       emp.idEmpresa, emp.nomeFantasia AS empresa,
                       e.idEmpresaE, e.dataInicio, e.dataFim, e.cargaHorariaSemanal,
                       e.situacao, e.statusEstagio, e.ativo, e.supervisor, e.orientadorAcademico
                FROM estagio e
                LEFT JOIN aluno a ON e.idAlunoA = a.idAluno
                LEFT JOIN empresa emp ON e.idEmpresaE = emp.idEmpresa
                WHERE (e.ativo IS NULL OR e.ativo = 1) AND e.idAlunoA = %s
                ORDER BY e.dataInicio DESC
            """
        
        cursor.execute(sql, (idAluno,))
        rows = cursor.fetchall()
        cursor.close()
        con.close()
        
        return rows
