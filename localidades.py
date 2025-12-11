from db import conectar


class Localidades:
    @staticmethod
    def listar_estados():
        con = conectar()
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM estados ORDER BY nome")
        estados = cursor.fetchall()
        con.close()
        return estados
    
    @staticmethod
    def listar_cidades():
        con = conectar()
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cidades ORDER BY nome")
        cidades = cursor.fetchall()
        con.close()
        return cidades

    @staticmethod
    def listar_cidades_por_estado(id_estado):
        con = conectar()
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT idCidade, nome AS cidade FROM cidades WHERE idEstadoE = %s ORDER BY nome", (id_estado,))
        cidades = cursor.fetchall()
        con.close()
        return cidades

    @staticmethod
    def buscar_cidade_por_id(id_cidade):
        con = conectar()
        cursor = con.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.idCidade, c.nome AS cidade, e.idEstado, e.nome AS estado, e.uf 
            FROM cidades c
            JOIN estados e ON c.idEstadoE = e.idEstado
            WHERE c.idCidade = %s
        """, (id_cidade,))
        cidade = cursor.fetchone()
        con.close()
        return cidade

    @staticmethod
    def pesquisar_cidade_por_nome(nome_parcial):
        con = conectar()
        cursor = con.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.idCidade, c.nome AS cidade, e.idEstado, e.nome AS estado, e.uf
            FROM cidades c
            JOIN estados e ON c.idEstadoE = e.idEstado
            WHERE c.nome LIKE %s
            ORDER BY c.nome
        """, (f"%{nome_parcial}%",))
        resultados = cursor.fetchall()
        con.close()
        return resultados
