# -*- coding: utf-8 -*-
"""
base_model.py - Classe base abstrata para todos os models do SGE
Implementa: Herança, Polimorfismo, Abstração e parte do Encapsulamento
"""

import logging
import mysql.connector
from abc import ABC, abstractmethod
from db import conectar

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BaseModel(ABC):
    """
    Classe abstrata base para todos os models.
    Implementa operações comuns de CRUD e validação.
    
    Conceitos POO aplicados:
    - Abstração: Define interface comum para subclasses
    - Herança: Classes filhas herdam comportamento comum
    - Polimorfismo: Métodos abstratos sobrescritos nas subclasses
    - Encapsulamento: Atributos protegidos (_ativo, _id)
    """
    
    def __init__(self, id_value=None):
        """
        Inicializa o model base.
        
        Args:
            id_value: ID do registro no banco de dados
        """
        self._id = id_value  # Atributo protegido (encapsulamento)
        self._ativo = True
    
    # ==================== PROPERTIES (Encapsulamento) ====================
    
    @property
    def id(self):
        """Getter para ID (somente leitura após criação)"""
        return self._id
    
    @property
    def ativo(self):
        """Getter para status ativo"""
        return self._ativo
    
    @ativo.setter
    def ativo(self, valor):
        """Setter para status ativo com validação"""
        if not isinstance(valor, (bool, int)):
            raise ValueError("Ativo deve ser booleano ou 0/1")
        self._ativo = bool(valor)
    
    # ==================== MÉTODOS ABSTRATOS (Polimorfismo) ====================
    
    @abstractmethod
    def _get_table_name(self):
        """
        Retorna o nome da tabela no banco.
        Deve ser implementado pelas subclasses.
        """
        pass
    
    @abstractmethod
    def _get_id_column_name(self):
        """
        Retorna o nome da coluna ID (ex: 'idAluno', 'idEmpresa').
        Deve ser implementado pelas subclasses.
        """
        pass
    
    @abstractmethod
    def _validar(self):
        """
        Valida os dados específicos da entidade.
        Deve retornar (True, None) se válido ou (False, mensagem_erro).
        Deve ser implementado pelas subclasses.
        """
        pass
    
    @abstractmethod
    def _get_insert_data(self):
        """
        Retorna tupla (colunas, valores) para INSERT.
        Deve ser implementado pelas subclasses.
        
        Returns:
            tuple: (lista_de_colunas, lista_de_valores)
        """
        pass
    
    @abstractmethod
    def _get_update_data(self):
        """
        Retorna tupla (colunas, valores) para UPDATE.
        Deve ser implementado pelas subclasses.
        
        Returns:
            tuple: (lista_de_colunas, lista_de_valores)
        """
        pass
    
    # ==================== MÉTODOS MÁGICOS ====================
    
    def __str__(self):
        """Representação em string do objeto"""
        return f"{self.__class__.__name__}(id={self._id})"
    
    def __repr__(self):
        """Representação para debug"""
        return f"<{self.__class__.__name__} id={self._id} ativo={self._ativo}>"
    
    # ==================== MÉTODOS CRUD GENÉRICOS (Herança) ====================
    
    def salvar(self):
        """
        Insere novo registro no banco.
        Template Method Pattern: usa métodos abstratos das subclasses.
        
        Returns:
           tuple: (bool_sucesso, str_mensagem)
        """
        # Validação (polimorfismo - cada classe implementa)
        ok, msg = self._validar()
        if not ok:
            logger.warning(f"Validação falhou ao inserir {self.__class__.__name__}: {msg}")
            return False, msg  # ← MUDANÇA AQUI
        
        con = None
        cursor = None
        
        try:
            con = conectar()
            cursor = con.cursor()
            
            # Obtém dados específicos da subclasse
            colunas, valores = self._get_insert_data()
            
            # Adiciona campo 'ativo'
            colunas.append('ativo')
            valores.append(1)
        
            # Monta SQL dinamicamente
            placeholders = ', '.join(['%s'] * len(valores))
            colunas_str = ', '.join(colunas)
            
            sql = f"""
                INSERT INTO {self._get_table_name()} ({colunas_str})
                VALUES ({placeholders})
            """
            
            cursor.execute(sql, valores)
            con.commit()
        
            # Captura o ID gerado
            self._id = cursor.lastrowid
        
            logger.info(f"{self.__class__.__name__} inserido com sucesso (ID: {self._id})")
            return True, f"{self.__class__.__name__} cadastrado com sucesso!"  # ← MUDANÇA AQUI
            
        except mysql.connector.IntegrityError as e:
            logger.exception(f"Erro de integridade ao inserir {self.__class__.__name__}: {e}")
            return False, "Erro de integridade ao cadastrar. Verifique dados duplicados."  # ← MUDANÇA AQUI
            
        except Exception as e:
            logger.exception(f"Erro inesperado ao inserir {self.__class__.__name__}: {e}")
            return False, "Erro ao cadastrar. Tente novamente."  # ← MUDANÇA AQUI
        
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()

    def editar(self):
        """
        Atualiza registro existente no banco.
        
        Returns:
            tuple: (bool_sucesso, str_mensagem)
        """
        if not self._id:
            logger.error(f"{self._get_id_column_name()} não informado para edição.")
            return False, f"ID não informado para edição."  # ← MUDANÇA AQUI
    
        # Validação
        ok, msg = self._validar()
        if not ok:
            logger.warning(f"Validação falhou ao editar {self.__class__.__name__}: {msg}")
            return False, msg  # ← MUDANÇA AQUI
    
        con = None
        cursor = None
    
        try:
            con = conectar()
            cursor = con.cursor()
        
            # Obtém dados específicos da subclasse
            colunas, valores = self._get_update_data()
        
            # Monta SQL dinamicamente
            set_clause = ', '.join([f"{col} = %s" for col in colunas])
            valores.append(self._id)  # Adiciona ID no final
        
            sql = f"""
                UPDATE {self._get_table_name()}
                SET {set_clause}
                WHERE {self._get_id_column_name()} = %s
            """
        
            cursor.execute(sql, valores)
            con.commit()
        
            logger.info(f"{self.__class__.__name__} id={self._id} atualizado com sucesso.")
            return True, f"{self.__class__.__name__} atualizado com sucesso!"  # ← MUDANÇA AQUI
            
        except mysql.connector.IntegrityError as e:
            logger.exception(f"Erro de integridade ao editar {self.__class__.__name__}: {e}")
            return False, "Erro de integridade ao atualizar. Verifique dados duplicados."  # ← MUDANÇA AQUI
            
        except Exception as e:
            logger.exception(f"Erro inesperado ao editar {self.__class__.__name__}: {e}")
            return False, "Erro ao atualizar. Tente novamente."  # ← MUDANÇA AQUI
        
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()

    
    def desativar(self):
        """
        Marca o registro como inativo (soft delete).
        
        Returns:
            bool: True se sucesso, False caso contrário
        """
        if not self._id:
            logger.error(f"{self._get_id_column_name()} não informado para desativação.")
            return False
        
        con = None
        cursor = None
        
        try:
            con = conectar()
            cursor = con.cursor()
            
            sql = f"""
                UPDATE {self._get_table_name()}
                SET ativo = 0
                WHERE {self._get_id_column_name()} = %s
            """
            
            cursor.execute(sql, (self._id,))
            con.commit()
            
            self._ativo = False
            logger.info(f"{self.__class__.__name__} id={self._id} desativado.")
            return True
            
        except Exception as e:
            logger.exception(f"Erro ao desativar {self.__class__.__name__}: {e}")
            return False
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    @classmethod
    def definir_ativo(cls, id_value, ativo):
        """
        Método de classe para alternar status ativo/inativo.
        
        Args:
            id_value: ID do registro
            ativo: True/1 para ativar, False/0 para desativar
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        # Cria instância temporária para acessar métodos abstratos
        # (Workaround - idealmente seria static com nome de tabela fixo)
        con = conectar()
        cursor = con.cursor()
        
        try:
            # Precisamos do nome da tabela - usa reflexão
            temp_instance = cls.__new__(cls)
            table_name = temp_instance._get_table_name()
            id_column = temp_instance._get_id_column_name()
            
            sql = f"UPDATE {table_name} SET ativo = %s WHERE {id_column} = %s"
            cursor.execute(sql, (1 if ativo else 0, id_value))
            con.commit()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            logger.exception(f"Erro ao definir ativo: {e}")
            return False
            
        finally:
            cursor.close()
            con.close()
