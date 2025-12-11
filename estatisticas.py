from db import conectar
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Estatisticas:
    
    @staticmethod
    def total_alunos():
        try:
            con = conectar()
            cursor = con.cursor()
            cursor.execute("SELECT COUNT(*) FROM aluno WHERE ativo IS NULL OR ativo = 1")
            total = cursor.fetchone()[0]
            cursor.close()
            con.close()
            return total
        except Exception as e:
            logger.error(f"Erro ao buscar total de alunos: {e}")
            return 0
    
    @staticmethod
    def total_empresas():
        try:
            con = conectar()
            cursor = con.cursor()
            cursor.execute("SELECT COUNT(*) FROM empresa WHERE ativo IS NULL OR ativo = 1")
            total = cursor.fetchone()[0]
            cursor.close()
            con.close()
            return total
        except Exception as e:
            logger.error(f"Erro ao buscar total de empresas: {e}")
            return 0
    
    @staticmethod
    def estagios_ativos():
        try:
            con = conectar()
            cursor = con.cursor()
            cursor.execute("SELECT COUNT(*) FROM estagio WHERE (ativo IS NULL OR ativo = 1) AND situacao = 'Ativo'")
            total = cursor.fetchone()[0]
            cursor.close()
            con.close()
            return total
        except Exception as e:
            logger.error(f"Erro ao buscar estágios ativos: {e}")
            return 0
    
    @staticmethod
    def estagios_concluidos_mes():
        try:
            con = conectar()
            cursor = con.cursor()
            hoje = datetime.now()
            primeiro_dia = hoje.replace(day=1)
            
            if hoje.month == 12:
                proximo_mes = hoje.replace(year=hoje.year + 1, month=1, day=1)
            else:
                proximo_mes = hoje.replace(month=hoje.month + 1, day=1)
            
            cursor.execute("""
                SELECT COUNT(*) FROM estagio 
                WHERE (ativo IS NULL OR ativo = 1) 
                AND situacao = 'Concluído'
                AND dataFim >= %s AND dataFim < %s
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
        return {
            'total_alunos': Estatisticas.total_alunos(),
            'total_empresas': Estatisticas.total_empresas(),
            'estagios_ativos': Estatisticas.estagios_ativos(),
            'estagios_concluidos_mes': Estatisticas.estagios_concluidos_mes()
        }
    
    # ========== NOVOS MÉTODOS PARA GRÁFICOS ==========
    
    @staticmethod
    def estagios_por_situacao():
        """Retorna quantidade de estágios por situação"""
        try:
            con = conectar()
            cursor = con.cursor(dictionary=True)
            cursor.execute("""
                SELECT situacao, COUNT(*) as total 
                FROM estagio 
                WHERE (ativo IS NULL OR ativo = 1)
                GROUP BY situacao
            """)
            resultado = cursor.fetchall()
            cursor.close()
            con.close()
            return resultado
        except Exception as e:
            logger.error(f"Erro ao buscar estágios por situação: {e}")
            return []
    
    @staticmethod
    def alunos_por_status():
        """Retorna quantidade de alunos por status"""
        try:
            con = conectar()
            cursor = con.cursor(dictionary=True)
            cursor.execute("""
                SELECT statusAluno, COUNT(*) as total 
                FROM aluno 
                WHERE (ativo IS NULL OR ativo = 1)
                GROUP BY statusAluno
            """)
            resultado = cursor.fetchall()
            cursor.close()
            con.close()
            return resultado
        except Exception as e:
            logger.error(f"Erro ao buscar alunos por status: {e}")
            return []
    
    @staticmethod
    def estagios_ultimos_6_meses():
        """Retorna estágios iniciados nos últimos 6 meses"""
        try:
            con = conectar()
            cursor = con.cursor(dictionary=True)
            
            hoje = datetime.now()
            resultado = []
            
            for i in range(5, -1, -1):
                mes_atual = hoje.month - i
                ano_atual = hoje.year
                
                while mes_atual <= 0:
                    mes_atual += 12
                    ano_atual -= 1
                
                primeiro_dia = datetime(ano_atual, mes_atual, 1).date()
                
                if mes_atual == 12:
                    ultimo_dia = datetime(ano_atual, 12, 31).date()
                else:
                    ultimo_dia = (datetime(ano_atual, mes_atual + 1, 1) - timedelta(days=1)).date()
                
                meses_pt = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                           'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                nome_mes = f"{meses_pt[mes_atual-1]}/{str(ano_atual)[2:]}"
                
                cursor.execute("""
                    SELECT COUNT(*) as total 
                    FROM estagio 
                    WHERE (ativo IS NULL OR ativo = 1)
                    AND dataInicio BETWEEN %s AND %s
                """, (primeiro_dia, ultimo_dia))
                
                total = cursor.fetchone()['total']
                resultado.append({'mes': nome_mes, 'total': total})
            
            cursor.close()
            con.close()
            return resultado
        except Exception as e:
            logger.error(f"Erro ao buscar estágios dos últimos meses: {e}")
            return []
