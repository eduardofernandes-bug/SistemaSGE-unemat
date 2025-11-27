from db import conectar
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Estatisticas:
    """Classe para calcular estatísticas do sistema"""
    
    @staticmethod
    def total_alunos():
        """Retorna o total de alunos ativos no sistema"""
        try:
            con = conectar()
            cursor = con.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM aluno 
                WHERE ativo IS NULL OR ativo = 1
            """)
            total = cursor.fetchone()[0]
            cursor.close()
            con.close()
            return total
        except Exception as e:
            logger.error(f"Erro ao buscar total de alunos: {e}")
            return 0
    
    @staticmethod
    def total_empresas():
        """Retorna o total de empresas ativas no sistema"""
        try:
            con = conectar()
            cursor = con.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM empresa 
                WHERE ativo IS NULL OR ativo = 1
            """)
            total = cursor.fetchone()[0]
            cursor.close()
            con.close()
            return total
        except Exception as e:
            logger.error(f"Erro ao buscar total de empresas: {e}")
            return 0
    
    @staticmethod
    def estagios_ativos():
        """Retorna o total de estágios com situação 'Ativo'"""
        try:
            con = conectar()
            cursor = con.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM estagio 
                WHERE (ativo IS NULL OR ativo = 1) 
                AND situacao = 'Ativo'
            """)
            total = cursor.fetchone()[0]
            cursor.close()
            con.close()
            return total
        except Exception as e:
            logger.error(f"Erro ao buscar estágios ativos: {e}")
            return 0
    
    @staticmethod
    def estagios_concluidos_mes():
        """Retorna o total de estágios concluídos no mês atual"""
        try:
            con = conectar()
            cursor = con.cursor()
            
            # Primeiro e último dia do mês atual
            hoje = datetime.now()
            primeiro_dia = hoje.replace(day=1)
            if hoje.month == 12:
                proximo_mes = hoje.replace(year=hoje.year + 1, month=1, day=1)
            else:
                proximo_mes = hoje.replace(month=hoje.month + 1, day=1)
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM estagio 
                WHERE (ativo IS NULL OR ativo = 1) 
                AND situacao = 'Concluido'
                AND dataFim >= %s 
                AND dataFim < %s
            """, (primeiro_dia.date(), proximo_mes.date()))
            
            total = cursor.fetchone()[0]
            cursor.close()
            con.close()
            return total
        except Exception as e:
            logger.error(f"Erro ao buscar estágios concluídos no mês: {e}")
            return 0
    
    @staticmethod
    def obter_todas_estatisticas():
        """Retorna um dicionário com todas as estatísticas"""
        return {
            'total_alunos': Estatisticas.total_alunos(),
            'total_empresas': Estatisticas.total_empresas(),
            'estagios_ativos': Estatisticas.estagios_ativos(),
            'estagios_concluidos_mes': Estatisticas.estagios_concluidos_mes()
        }
    
    @staticmethod
    def estatisticas_por_periodo(dias=30):
        """
        Retorna estatísticas detalhadas dos últimos X dias
        Útil para gráficos e dashboards
        """
        try:
            con = conectar()
            cursor = con.cursor(dictionary=True)
            
            data_limite = datetime.now() - timedelta(days=dias)
            
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM estagio 
                WHERE dataInicio >= %s
                AND (ativo IS NULL OR ativo = 1)
            """, (data_limite.date(),))
            estagios_iniciados = cursor.fetchone()['total']
            
            cursor.execute("""
                SELECT statusAluno, COUNT(*) as total
                FROM aluno 
                WHERE ativo IS NULL OR ativo = 1
                GROUP BY statusAluno
            """)
            alunos_por_status = cursor.fetchall()
            
            cursor.execute("""
                SELECT situacao, COUNT(*) as total
                FROM estagio 
                WHERE ativo IS NULL OR ativo = 1
                GROUP BY situacao
            """)
            estagios_por_situacao = cursor.fetchall()
            
            cursor.close()
            con.close()
            
            return {
                'estagios_iniciados_periodo': estagios_iniciados,
                'alunos_por_status': alunos_por_status,
                'estagios_por_situacao': estagios_por_situacao
            }
        except Exception as e:
            logger.error(f"Erro ao buscar estatísticas por período: {e}")
            return {
                'estagios_iniciados_periodo': 0,
                'alunos_por_status': [],
                'estagios_por_situacao': []
            }