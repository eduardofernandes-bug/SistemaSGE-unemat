# -*- coding: utf-8 -*-

import logging
import mysql.connector
from abc import ABC, abstractmethod
from db import conectar

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BaseModel(ABC):
    def __init__(self, id_value=None):
        self._id = id_value
        self._ativo = True
    
    
    @property
    def id(self):
        return self._id
    
    @property
    def ativo(self):
        return self._ativo
    
    @ativo.setter
    def ativo(self, valor):
        if not isinstance(valor, (bool, int)):
            raise ValueError("Ativo deve ser booleano ou 0/1")
        self._ativo = bool(valor)
    
    
    @abstractmethod
    def _get_table_name(self):
        pass
    
    @abstractmethod
    def _get_id_column_name(self):
        pass
    
    @abstractmethod
    def _validar(self):
        pass
    
    @abstractmethod
    def _get_insert_data(self):
        pass
    
    @abstractmethod
    def _get_update_data(self):
        pass

    def __str__(self):
        return f"{self.__class__.__name__}(id={self._id})"
    
    def __repr__(self):
        return f"<{self.__class__.__name__} id={self._id} ativo={self._ativo}>"
    
    def salvar(self):
        ok, msg = self._validar()
        if not ok:
            logger.warning(f"Validação falhou ao inserir {self.__class__.__name__}: {msg}")
            return False, msg
        
        con = None
        cursor = None
        
        try:
            con = conectar()
            cursor = con.cursor()
            
            colunas, valores = self._get_insert_data()
            
            colunas.append('ativo')
            valores.append(1)
        
            placeholders = ', '.join(['%s'] * len(valores))
            colunas_str = ', '.join(colunas)
            
            sql = f"""
                INSERT INTO {self._get_table_name()} ({colunas_str})
                VALUES ({placeholders})
            """
            
            cursor.execute(sql, valores)
            con.commit()
        
            self._id = cursor.lastrowid
        
            logger.info(f"{self.__class__.__name__} inserido com sucesso (ID: {self._id})")
            return True, f"{self.__class__.__name__} cadastrado com sucesso!"
            
        except mysql.connector.IntegrityError as e:
            logger.exception(f"Erro de integridade ao inserir {self.__class__.__name__}: {e}")
            return False, "Erro de integridade ao cadastrar. Verifique dados duplicados."
            
        except Exception as e:
            logger.exception(f"Erro inesperado ao inserir {self.__class__.__name__}: {e}")
            return False, "Erro ao cadastrar. Tente novamente."
        
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
            return False, f"ID não informado para edição."
    
        ok, msg = self._validar()
        if not ok:
            logger.warning(f"Validação falhou ao editar {self.__class__.__name__}: {msg}")
            return False, msg
    
        con = None
        cursor = None
    
        try:
            con = conectar()
            cursor = con.cursor()
        
            colunas, valores = self._get_update_data()
        
            set_clause = ', '.join([f"{col} = %s" for col in colunas])
            valores.append(self._id)
            sql = f"""
                UPDATE {self._get_table_name()}
                SET {set_clause}
                WHERE {self._get_id_column_name()} = %s
            """
        
            cursor.execute(sql, valores)
            con.commit()
        
            logger.info(f"{self.__class__.__name__} id={self._id} atualizado com sucesso.")
            return True, f"{self.__class__.__name__} atualizado com sucesso!"
            
        except mysql.connector.IntegrityError as e:
            logger.exception(f"Erro de integridade ao editar {self.__class__.__name__}: {e}")
            return False, "Erro de integridade ao atualizar. Verifique dados duplicados."
            
        except Exception as e:
            logger.exception(f"Erro inesperado ao editar {self.__class__.__name__}: {e}")
            return False, "Erro ao atualizar. Tente novamente."
        
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()

    
    def desativar(self):
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
        con = conectar()
        cursor = con.cursor()
        
        try:
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
