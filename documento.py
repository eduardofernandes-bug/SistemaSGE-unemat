# -*- coding: utf-8 -*-

import os
import logging
import openpyxl
import openpyxl.utils
from datetime import datetime
from docx import Document
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from openpyxl.cell.cell import MergedCell

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GeradorDocumentos:
    TEMPLATES_DIR = 'documentos_templates'
    OUTPUT_DIR = 'documentos_gerados'
    
    TEMPLATE_PLANO = os.path.join(TEMPLATES_DIR, 'anexo_VI_Plano_de_Atividades.docx')
    TEMPLATE_FICHA = os.path.join(TEMPLATES_DIR, 'Anexo_VII_Ficha_Atividades.xlsx')
    
    def __init__(self):
        """Inicializa o gerador e cria pasta de saída se não existir"""
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        os.makedirs(self.TEMPLATES_DIR, exist_ok=True)
    
    @classmethod
    def gerar_plano_atividades(cls, dados_estagiario, dados_empresa, cronograma, cidade=""):
        try:
            doc = Document(cls.TEMPLATE_PLANO)
            
            for table in doc.tables:
                if len(table.rows) >= 3:
                    cls._substituir_texto_celula(table.rows[1].cells[0], 
                                                  'Digite seu nome aqui', 
                                                  dados_estagiario['nome'])
                    cls._substituir_texto_celula(table.rows[2].cells[0], 
                                                  'Digite o número de contato aqui', 
                                                  dados_estagiario['telefone'])
                    cls._substituir_texto_celula(table.rows[3].cells[0], 
                                                  'Digite seu e-mail aqui', 
                                                  dados_estagiario['email'])
                    
                    cls._substituir_texto_celula(table.rows[1].cells[1], 
                                                  'Digite o nome aqui', 
                                                  dados_empresa['nome'])
                    cls._substituir_texto_celula(table.rows[2].cells[1], 
                                                  'Digite o número de contato aqui', 
                                                  dados_empresa['telefone'])
                    cls._substituir_texto_celula(table.rows[3].cells[1], 
                                                  'Digite o e-mail aqui', 
                                                  dados_empresa['email'])
                
                if 'PERÍODO' in table.rows[0].cells[0].text:
                    for _ in range(len(table.rows) - 1):
                        if len(table.rows) > 1:
                            table._element.remove(table.rows[-1]._element)
                    
                    for item in cronograma:
                        row = table.add_row()
                        row.cells[0].text = item['periodo']
                        row.cells[1].text = item['atividades']
                
                if 'Acadêmico(a)/Estagiário(a)' in table.rows[-1].cells[0].text:
                    cls._substituir_texto_celula(table.rows[-2].cells[0], 
                                                  'Digite o nome aqui', 
                                                  dados_estagiario['nome'])
                    cls._substituir_texto_celula(table.rows[-2].cells[1], 
                                                  'Digite o nome aqui', 
                                                  dados_empresa.get('supervisor', ''))
            
            data_atual = datetime.now().strftime('%d/%m/%Y')
            for paragraph in doc.paragraphs:
                if 'Digite a cidade' in paragraph.text:
                    paragraph.text = f"{cidade}, {data_atual}"
            
            nome_arquivo = f"Plano_Atividades_{dados_estagiario['nome'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            caminho_saida = os.path.join(cls.OUTPUT_DIR, nome_arquivo)
            doc.save(caminho_saida)
            
            logger.info(f"Plano de Atividades gerado: {caminho_saida}")
            return caminho_saida
            
        except Exception as e:
            logger.exception(f"Erro ao gerar Plano de Atividades: {e}")
            raise
    
    @staticmethod
    def _substituir_texto_celula(celula, texto_antigo, texto_novo):
        for paragraph in celula.paragraphs:
            if texto_antigo in paragraph.text:
                paragraph.text = paragraph.text.replace(texto_antigo, texto_novo)
    
    @classmethod
    def gerar_ficha_atividades(cls, dados_estagiario, dados_empresa, mes, ano, atividades_diarias):
        try:
            wb = load_workbook(cls.TEMPLATE_FICHA)
            ws = wb.active
            
            imagens_originais = []
            if hasattr(ws, '_images'):
                for img in ws._images:
                    imagens_originais.append(img)
            
            ws['D13'] = dados_estagiario['nome']
            
            ws['D14'] = dados_empresa['nome']
            
            ws['C17'] = mes
            
            ws['E17'] = ano
            
            for atividade in atividades_diarias:
                dia = atividade['dia']
                

                if 1 <= dia <= 31:
                    linha = 19 + dia
                    
                    if atividade.get('inicio'):
                        ws[f'B{linha}'] = atividade['inicio']
                    
                    if atividade.get('termino'):
                        ws[f'C{linha}'] = atividade['termino']
                    
                    if atividade.get('descricao'):
                        ws[f'D{linha}'] = atividade['descricao']
                    
            ws._images = imagens_originais
            
            nome_arquivo = f"Ficha_Atividades_{dados_estagiario['nome'].replace(' ', '_')}_{mes}_{ano}.xlsx"
            caminho_saida = os.path.join(cls.OUTPUT_DIR, nome_arquivo)
            wb.save(caminho_saida)
            
            logger.info(f"Ficha de Atividades gerada com sucesso: {caminho_saida}")
            return caminho_saida
            
        except Exception as e:
            logger.exception(f"Erro ao gerar Ficha de Atividades: {e}")
            raise

    
    @staticmethod
    def _calcular_horas(hora_inicio, hora_termino):
        try:
            fmt = '%H:%M:%S' if ':' in hora_inicio and hora_inicio.count(':') == 2 else '%H:%M'
            
            inicio = datetime.strptime(hora_inicio, fmt)
            termino = datetime.strptime(hora_termino, fmt)
            
            diferenca = termino - inicio
            horas = diferenca.total_seconds() / 3600
            
            return round(horas, 2)
            
        except Exception as e:
            logger.warning(f"Erro ao calcular horas: {e}")
            return 0
    
    @classmethod
    def verificar_templates(cls):
        return {
            'plano': os.path.exists(cls.TEMPLATE_PLANO),
            'ficha': os.path.exists(cls.TEMPLATE_FICHA)
        }
    
    @classmethod
    def listar_documentos_gerados(cls):
        if not os.path.exists(cls.OUTPUT_DIR):
            return []
        
        documentos = []
        for arquivo in os.listdir(cls.OUTPUT_DIR):
            caminho_completo = os.path.join(cls.OUTPUT_DIR, arquivo)
            if os.path.isfile(caminho_completo):
                info = {
                    'nome': arquivo,
                    'caminho': caminho_completo,
                    'tamanho': os.path.getsize(caminho_completo),
                    'data_criacao': datetime.fromtimestamp(os.path.getctime(caminho_completo))
                }
                documentos.append(info)
        
        return sorted(documentos, key=lambda x: x['data_criacao'], reverse=True)
