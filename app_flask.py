# -*- coding: utf-8 -*-
import os
import secrets
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from aluno import Aluno
from empresa import Empresa
from estagio import Estagio
from localidades import Localidades
from estatisticas import Estatisticas

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Configuração segura da secret key
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Configurações de segurança
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'  # HTTPS em produção
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Previne acesso via JavaScript
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Proteção contra CSRF
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutos de sessão

# Desabilita debug em produção
if os.getenv('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False

# Página inicial
@app.route("/")
def index():
    """Página inicial com estatísticas do sistema"""
    try:
        # Busca todas as estatísticas do banco de dados
        stats = Estatisticas.obter_todas_estatisticas()
        return render_template("index.html", stats=stats)
    except Exception as e:
        app.logger.error(f"Erro ao carregar estatísticas: {e}")
        # Em caso de erro, passa valores zerados
        stats = {
            'total_alunos': 0,
            'total_empresas': 0,
            'estagios_ativos': 0,
            'estagios_concluidos_mes': 0
        }
        flash("Erro ao carregar estatísticas do sistema.", "warning")
        return render_template("index.html", stats=stats)

# ---------------------------
# ALUNOS - views (HTML)
# ---------------------------
@app.route("/alunos")
def alunos():
    try:
        idCidade = request.args.get("cidade")
        idEstado = request.args.get("estado")
        mostrar_inativos = request.args.get("mostrar_inativos") == "1"
        
        if idCidade:
            lista = Aluno.listar_por_cidade(int(idCidade), mostrar_inativos)
        elif idEstado:
            lista = Aluno.listar_por_estado(int(idEstado), mostrar_inativos)
        else:
            lista = Aluno.listar(mostrar_inativos)
        
        estados = Localidades.listar_estados()
        return render_template("alunos.html", alunos=lista, estados=estados)
    except Exception as e:
        flash("Erro ao carregar lista de alunos.", "danger")
        app.logger.error(f"Erro em /alunos: {e}")
        return redirect(url_for("index"))

@app.route("/aluno/novo", methods=["GET", "POST"])
def aluno_novo():
    estados = Localidades.listar_estados()
    if request.method == "POST":
        try:
            nome = request.form.get("nome", "").strip()
            matricula = request.form.get("matricula", "").strip()
            cpf = request.form.get("cpf", "").strip()
            nome_inst = request.form.get("nome_institucional", "").strip()
            telefone = request.form.get("telefone", "").strip()
            endereco = request.form.get("endereco", "").strip()
            bairro = request.form.get("bairro", "").strip()
            periodo = request.form.get("periodo", "").strip()
            status = request.form.get("status", "").strip()
            idCidade = request.form.get("cidade_id")
            idEstado = request.form.get("estado_id")

            # Validações básicas
            if not nome or not matricula or not cpf:
                flash("Nome, matrícula e CPF são obrigatórios.", "warning")
                return render_template("aluno_form.html", estados=estados, aluno=None)

            aluno = Aluno(nome, matricula, cpf, nome_inst, telefone, endereco, bairro, 
                         periodo, status, idCidade, idEstado)
            if aluno.salvar():
                flash("Aluno cadastrado com sucesso!", "success")
                return redirect(url_for("alunos"))
            else:
                flash("Erro ao cadastrar aluno. Verifique os dados.", "danger")
        except Exception as e:
            flash("Erro ao processar cadastro.", "danger")
            app.logger.error(f"Erro em aluno_novo: {e}")
    
    return render_template("aluno_form.html", estados=estados, aluno=None)

@app.route("/aluno/<int:id>/editar", methods=["GET", "POST"])
def aluno_editar(id):
    estados = Localidades.listar_estados()
    if request.method == "POST":
        try:
            nome = request.form.get("nome", "").strip()
            matricula = request.form.get("matricula", "").strip()
            cpf = request.form.get("cpf", "").strip()
            nome_inst = request.form.get("nome_institucional", "").strip()
            telefone = request.form.get("telefone", "").strip()
            endereco = request.form.get("endereco", "").strip()
            bairro = request.form.get("bairro", "").strip()
            periodo = request.form.get("periodo", "").strip()
            status = request.form.get("status", "").strip()
            idCidade = request.form.get("cidade_id")
            idEstado = request.form.get("estado_id")

            aluno = Aluno(nome, matricula, cpf, nome_inst, telefone, endereco, bairro, 
                         periodo, status, idCidade, idEstado, idAluno=id)
            if aluno.editar():
                flash("Aluno atualizado com sucesso!", "success")
                return redirect(url_for("alunos"))
            else:
                flash("Erro ao atualizar aluno.", "danger")
        except Exception as e:
            flash("Erro ao processar atualização.", "danger")
            app.logger.error(f"Erro em aluno_editar: {e}")

    aluno = Aluno.buscar_por_id(id)
    if not aluno:
        flash("Aluno não encontrado.", "danger")
        return redirect(url_for("alunos"))
    return render_template("aluno_form.html", estados=estados, aluno=aluno)

@app.route("/aluno/<int:id>/desativar", methods=["POST"])
def aluno_desativar(id):
    try:
        aluno = Aluno(None, None, None, None, None, None, None, None, None, None, None, idAluno=id)
        if aluno.desativar():
            flash("Aluno desativado com sucesso.", "info")
        else:
            flash("Erro ao desativar aluno.", "danger")
    except Exception as e:
        flash("Erro ao processar desativação.", "danger")
        app.logger.error(f"Erro em aluno_desativar: {e}")
    return redirect(url_for("alunos"))

# ---------------------------
# EMPRESAS - views (HTML)
# ---------------------------
@app.route("/empresas")
def empresas():
    try:
        idCidade = request.args.get("cidade")
        idEstado = request.args.get("estado")
        mostrar_inativos = request.args.get("mostrar_inativos") == "1"
        
        if idCidade:
            lista = Empresa.listar_por_cidade(int(idCidade), mostrar_inativos)
        elif idEstado:
            lista = Empresa.listar_por_estado(int(idEstado), mostrar_inativos)
        else:
            lista = Empresa.listar(mostrar_inativos)
        
        estados = Localidades.listar_estados()
        return render_template("empresas.html", empresas=lista, estados=estados)
    except Exception as e:
        flash("Erro ao carregar lista de empresas.", "danger")
        app.logger.error(f"Erro em /empresas: {e}")
        return redirect(url_for("index"))

@app.route("/empresa/novo", methods=["GET", "POST"])
def empresa_nova():
    estados = Localidades.listar_estados()
    if request.method == "POST":
        try:
            razao = request.form.get("razao_social", "").strip()
            fantasia = request.form.get("nome_fantasia", "").strip()
            cnpj = request.form.get("cnpj", "").strip()
            cep = request.form.get("cep", "").strip()
            endereco = request.form.get("endereco", "").strip()
            bairro = request.form.get("bairro", "").strip()
            idCidade = request.form.get("cidade_id")
            idEstado = request.form.get("estado_id")

            if not razao:
                flash("Razão Social é obrigatória.", "warning")
                return render_template("empresa_form.html", estados=estados, empresa=None)

            emp = Empresa(razao, fantasia, cnpj, cep, endereco, bairro, idCidade, idEstado)
            if emp.salvar():
                flash("Empresa cadastrada com sucesso!", "success")
                return redirect(url_for("empresas"))
            else:
                flash("Erro ao cadastrar empresa.", "danger")
        except Exception as e:
            flash("Erro ao processar cadastro.", "danger")
            app.logger.error(f"Erro em empresa_nova: {e}")
    
    return render_template("empresa_form.html", estados=estados, empresa=None)

@app.route("/empresa/<int:id>/editar", methods=["GET", "POST"])
def empresa_editar(id):
    estados = Localidades.listar_estados()
    if request.method == "POST":
        try:
            razao = request.form.get("razao_social", "").strip()
            fantasia = request.form.get("nome_fantasia", "").strip()
            cnpj = request.form.get("cnpj", "").strip()
            cep = request.form.get("cep", "").strip()
            endereco = request.form.get("endereco", "").strip()
            bairro = request.form.get("bairro", "").strip()
            idCidade = request.form.get("cidade_id")
            idEstado = request.form.get("estado_id")

            emp = Empresa(razao, fantasia, cnpj, cep, endereco, bairro, idCidade, idEstado, idEmpresa=id)
            if emp.editar():
                flash("Empresa atualizada com sucesso!", "success")
                return redirect(url_for("empresas"))
            else:
                flash("Erro ao atualizar empresa.", "danger")
        except Exception as e:
            flash("Erro ao processar atualização.", "danger")
            app.logger.error(f"Erro em empresa_editar: {e}")

    empresa = Empresa.buscar_por_id(id)
    if not empresa:
        flash("Empresa não encontrada.", "danger")
        return redirect(url_for("empresas"))
    return render_template("empresa_form.html", estados=estados, empresa=empresa)

@app.route("/empresa/<int:id>/desativar", methods=["POST"])
def empresa_desativar(id):
    try:
        emp = Empresa(None, None, None, None, None, None, None, None, idEmpresa=id)
        if emp.desativar():
            flash("Empresa desativada com sucesso.", "info")
        else:
            flash("Erro ao desativar empresa.", "danger")
    except Exception as e:
        flash("Erro ao processar desativação.", "danger")
        app.logger.error(f"Erro em empresa_desativar: {e}")
    return redirect(url_for("empresas"))

# ---------------------------
# ESTÁGIOS - views (HTML)
# ---------------------------
@app.route("/estagios")
def estagios():
    try:
        idCidade = request.args.get("cidade")
        idEstado = request.args.get("estado")
        mostrar_inativos = request.args.get("mostrar_inativos") == "1"
        
        if idCidade:
            lista = Estagio.listar_por_cidade(int(idCidade), mostrar_inativos)
        elif idEstado:
            lista = Estagio.listar_por_estado(int(idEstado), mostrar_inativos)
        else:
            lista = Estagio.listar(mostrar_inativos)
        
        estados = Localidades.listar_estados()
        return render_template("estagios.html", estagios=lista, estados=estados)
    except Exception as e:
        flash("Erro ao carregar lista de estágios.", "danger")
        app.logger.error(f"Erro em /estagios: {e}")
        return redirect(url_for("index"))

@app.route("/estagio/novo", methods=["GET", "POST"])
def estagio_novo():
    estados = Localidades.listar_estados()
    alunos = Aluno.listar()
    empresas = Empresa.listar()
    if request.method == "POST":
        try:
            idAluno = request.form.get("aluno_id")
            idEmpresa = request.form.get("empresa_id")
            data_inicio = request.form.get("data_inicio")
            data_fim = request.form.get("data_fim")
            carga = request.form.get("carga_horaria")
            situacao = request.form.get("situacao")
            supervisor = request.form.get("supervisor", "").strip()
            orientador = request.form.get("orientador", "").strip()
            setor = request.form.get("setor", "").strip()
            documentacao = request.form.get("documentacao", "").strip()
            status = request.form.get("status")

            if not idAluno or not idEmpresa:
                flash("Aluno e Empresa são obrigatórios.", "warning")
                return render_template("estagio_form.html", estados=estados, alunos=alunos, 
                                      empresas=empresas, estagio=None)

            est = Estagio(idAluno, idEmpresa, data_inicio, data_fim, carga, situacao, 
                         supervisor, orientador, setor, documentacao, status)
            if est.salvar():
                flash("Estágio cadastrado com sucesso!", "success")
                return redirect(url_for("estagios"))
            else:
                flash("Erro ao cadastrar estágio.", "danger")
        except Exception as e:
            flash("Erro ao processar cadastro.", "danger")
            app.logger.error(f"Erro em estagio_novo: {e}")
    
    return render_template("estagio_form.html", estados=estados, alunos=alunos, 
                          empresas=empresas, estagio=None)

@app.route("/estagio/<int:id>/editar", methods=["GET", "POST"])
def estagio_editar(id):
    estados = Localidades.listar_estados()
    alunos = Aluno.listar()
    empresas = Empresa.listar()
    
    if request.method == "POST":
        try:
            idAluno = request.form.get("aluno_id")
            idEmpresa = request.form.get("empresa_id")
            data_inicio = request.form.get("data_inicio")
            data_fim = request.form.get("data_fim")
            carga = request.form.get("carga_horaria")
            situacao = request.form.get("situacao")
            supervisor = request.form.get("supervisor", "").strip()
            orientador = request.form.get("orientador", "").strip()
            setor = request.form.get("setor", "").strip()
            documentacao = request.form.get("documentacao", "").strip()
            status = request.form.get("status")

            est = Estagio(idAluno, idEmpresa, data_inicio, data_fim, carga, situacao, 
                         supervisor, orientador, setor, documentacao, status, idEstagio=id)
            if est.editar():
                flash("Estágio atualizado com sucesso!", "success")
                return redirect(url_for("estagios"))
            else:
                flash("Erro ao atualizar estágio.", "danger")
        except Exception as e:
            flash("Erro ao processar atualização.", "danger")
            app.logger.error(f"Erro em estagio_editar: {e}")

    estagio = Estagio.buscar_por_id(id)
    if not estagio:
        flash("Estágio não encontrado.", "danger")
        return redirect(url_for("estagios"))
    
    return render_template("estagio_form.html", estados=estados, alunos=alunos, 
                          empresas=empresas, estagio=estagio)

@app.route("/estagio/<int:id>/desativar", methods=["POST"])
def estagio_desativar(id):
    try:
        est = Estagio(None, None, None, None, None, None, None, None, None, None, None, idEstagio=id)
        if est.desativar():
            flash("Estágio desativado com sucesso.", "info")
        else:
            flash("Erro ao desativar estágio.", "danger")
    except Exception as e:
        flash("Erro ao processar desativação.", "danger")
        app.logger.error(f"Erro em estagio_desativar: {e}")
    return redirect(url_for("estagios"))

# ---------------------------
# API endpoints (JSON)
# ---------------------------
@app.route("/api/cidades")
def api_cidades():
    try:
        estado = request.args.get("estado")
        if not estado:
            return jsonify([])
        cidades = Localidades.listar_cidades_por_estado(int(estado))
        return jsonify(cidades)
    except Exception as e:
        app.logger.error(f"Erro em api_cidades: {e}")
        return jsonify({"error": "Erro ao carregar cidades"}), 500

@app.route("/api/alunos")
def api_alunos():
    try:
        idCidade = request.args.get("cidade")
        idEstado = request.args.get("estado")
        if idCidade:
            res = Aluno.listar_por_cidade(int(idCidade))
        elif idEstado:
            res = Aluno.listar_por_estado(int(idEstado))
        else:
            res = Aluno.listar()
        return jsonify(res)
    except Exception as e:
        app.logger.error(f"Erro em api_alunos: {e}")
        return jsonify({"error": "Erro ao carregar alunos"}), 500

@app.route("/api/empresas")
def api_empresas():
    try:
        idCidade = request.args.get("cidade")
        idEstado = request.args.get("estado")
        if idCidade:
            res = Empresa.listar_por_cidade(int(idCidade))
        elif idEstado:
            res = Empresa.listar_por_estado(int(idEstado))
        else:
            res = Empresa.listar()
        return jsonify(res)
    except Exception as e:
        app.logger.error(f"Erro em api_empresas: {e}")
        return jsonify({"error": "Erro ao carregar empresas"}), 500

@app.route("/api/estagios")
def api_estagios():
    try:
        idCidade = request.args.get("cidade")
        idEstado = request.args.get("estado")
        if idCidade:
            res = Estagio.listar_por_cidade(int(idCidade))
        elif idEstado:
            res = Estagio.listar_por_estado(int(idEstado))
        else:
            res = Estagio.listar()
        return jsonify(res)
    except Exception as e:
        app.logger.error(f"Erro em api_estagios: {e}")
        return jsonify({"error": "Erro ao carregar estágios"}), 500

# ---------------------------
# Tratamento de erros
# ---------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"Erro 500: {e}")
    flash("Erro interno do servidor. Tente novamente.", "danger")
    return redirect(url_for("index"))

if __name__ == "__main__":
    # Em produção, use um servidor WSGI como Gunicorn
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'True') == 'True',
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000))
    )