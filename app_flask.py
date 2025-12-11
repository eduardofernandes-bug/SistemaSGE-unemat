import os
import secrets
from datetime import datetime
from functools import wraps
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_file, session
from aluno import Aluno
from empresa import Empresa
from estagio import Estagio
from localidades import Localidades
from estatisticas import Estatisticas
from usuario import Usuario, NIVEL_ADMIN, NIVEL_COORDENADOR, NIVEL_VISUALIZADOR
from documento import GeradorDocumentos


load_dotenv()

app = Flask(__name__)

@app.context_processor
def inject_access_info():
    from usuario import NIVEL_VISUALIZADOR, NIVEL_COORDENADOR, NIVEL_ADMIN, NIVEIS_ACESSO
    return {
        'NIVEL_VISUALIZADOR': NIVEL_VISUALIZADOR,
        'NIVEL_COORDENADOR': NIVEL_COORDENADOR,
        'NIVEL_ADMIN': NIVEL_ADMIN,
        'NIVEIS_ACESSO': NIVEIS_ACESSO,
        'usuario_nivel': session.get('usuario_nivel', NIVEL_VISUALIZADOR)
    }

app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800

if os.getenv('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False


def login_required(f):
    """Decorator para proteger rotas que requerem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def nivel_required(nivel_minimo):
    """
    Decorator para rotas que requerem nível mínimo de acesso
    Uso: @nivel_required(NIVEL_COORDENADOR)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'usuario_id' not in session:
                flash('Você precisa estar logado.', 'warning')
                return redirect(url_for('login'))
            
            nivel_usuario = session.get('usuario_nivel', NIVEL_VISUALIZADOR)
            
            if nivel_usuario < nivel_minimo:
                flash('Você não tem permissão para acessar esta página.', 'danger')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator para rotas que requerem privilégio de admin"""
    return nivel_required(NIVEL_ADMIN)(f)

def coordenador_required(f):
    """Decorator para rotas que requerem no mínimo coordenador"""
    return nivel_required(NIVEL_COORDENADOR)(f)

@app.route("/login", methods=["GET", "POST"])
def login():
    if 'usuario_id' in session:
        return redirect(url_for('index'))
    
    try:
        usuarios = Usuario.listar()
        if not usuarios:
            flash('Nenhum usuário cadastrado. Crie o primeiro administrador.', 'info')
            return redirect(url_for('primeiro_acesso'))
    except Exception as e:
        app.logger.error(f"Erro ao verificar usuários: {e}")
    
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "")
        
        sucesso, resultado = Usuario.autenticar(email, senha)
        
        if sucesso:
            session['usuario_id'] = resultado['idUsuario']
            session['usuario_nome'] = resultado['nome']
            session['usuario_email'] = resultado['email']
            session['usuario_tipo'] = resultado['tipo']
            session['usuario_nivel'] = resultado['nivel']
            session['usuario_aluno_id'] = resultado.get('idAluno')
            session.permanent = True

            nivel_info = Usuario.get_nivel_info(resultado['nivel'])
            flash(f'Bem-vindo, {resultado["nome"]}! ({nivel_info["nome"]})', 'success')
            app.logger.info("Sessão criada: %s", {k: session.get(k) for k in ('usuario_id','usuario_nivel','usuario_aluno_id')})

            if session.get('usuario_nivel') == NIVEL_VISUALIZADOR:
                aluno_id = session.get('usuario_aluno_id')
                if aluno_id:
                    return redirect(url_for('meus_estagios'))
                else:
                    flash("Seu usuário não está associado a um aluno. Contate o administrador.", "warning")
                    return redirect(url_for('index'))

            return redirect(url_for('index'))

        else:
            flash(resultado, 'danger')

    return render_template("login.html")

@app.route("/logout")
def logout():
    """Faz logout do usuário"""
    nome = session.get('usuario_nome', 'Usuário')
    session.clear()
    flash(f'Até logo, {nome}!', 'info')
    return redirect(url_for('login'))

@app.route("/primeiro-acesso", methods=["GET", "POST"])
def primeiro_acesso():
    """Cria o primeiro usuário admin (apenas se não existir nenhum)"""
    try:
        usuarios = Usuario.listar()
        if usuarios:
            flash('Já existem usuários cadastrados no sistema.', 'warning')
            return redirect(url_for('login'))
    except Exception as e:
        app.logger.error(f"Erro ao verificar usuários: {e}")
        flash('Erro ao acessar o banco de dados.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "")
        confirma_senha = request.form.get("confirma_senha", "")
        
        if not nome or not email or not senha:
            flash('Todos os campos são obrigatórios.', 'warning')
            return render_template("primeiro_acesso.html")
        
        if senha != confirma_senha:
            flash('As senhas não coincidem.', 'danger')
            return render_template("primeiro_acesso.html")
        
        usuario = Usuario(email=email, senha=senha, nome=nome, nivel=NIVEL_ADMIN)
        sucesso, mensagem = usuario.salvar()
        
        if sucesso:
            flash('Primeiro usuário administrador criado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('login'))
        else:
            flash(mensagem, 'danger')
    
    return render_template("primeiro_acesso.html")

@app.route("/usuarios")
@admin_required
def usuarios():
    """Lista todos os usuários"""
    try:
        from usuario import NIVEIS_ACESSO
        lista_usuarios = Usuario.listar()
        return render_template("usuarios.html", usuarios=lista_usuarios, niveis=NIVEIS_ACESSO)
    except Exception as e:
        flash("Erro ao carregar usuários.", "danger")
        app.logger.error(f"Erro em /usuarios: {e}")
        return redirect(url_for("index"))

@app.route("/usuario/novo", methods=["GET", "POST"])
@admin_required
def usuario_novo():
    from usuario import NIVEIS_ACESSO, NIVEL_VISUALIZADOR, NIVEL_COORDENADOR, NIVEL_ADMIN

    alunos = Aluno.listar()

    if request.method == "POST":
        try:
            nome = request.form.get("nome", "").strip()
            email = request.form.get("email", "").strip()
            senha = request.form.get("senha", "")
            nivel = int(request.form.get("nivel", NIVEL_VISUALIZADOR))
            id_aluno = request.form.get("id_aluno") or None
            id_aluno = int(id_aluno) if id_aluno else None

            if not nome or not email or not senha:
                flash("Todos os campos são obrigatórios.", "warning")
                return render_template("usuario_form.html", usuario=None, niveis=NIVEIS_ACESSO, alunos=alunos)

            usuario = Usuario(email=email, senha=senha, nome=nome, nivel=nivel, idAluno=id_aluno)
            sucesso, mensagem = usuario.salvar()

            if sucesso:
                flash(f"Usuário '{nome}' criado com sucesso!", "success")
                return redirect(url_for("usuarios"))
            else:
                flash(mensagem, "danger")
        except Exception as e:
            flash("Erro ao criar usuário.", "danger")
            app.logger.error(f"Erro em usuario_novo: {e}")

    return render_template("usuario_form.html", usuario=None, niveis=NIVEIS_ACESSO, alunos=alunos)

@app.route("/usuario/<int:id>/editar", methods=["GET", "POST"])
@admin_required
def usuario_editar(id):
    from usuario import NIVEIS_ACESSO, NIVEL_VISUALIZADOR

    alunos = Aluno.listar()

    if request.method == "POST":
        try:
            nome = request.form.get("nome", "").strip()
            email = request.form.get("email", "").strip()
            senha = request.form.get("senha", "") 
            nivel = int(request.form.get("nivel", NIVEL_VISUALIZADOR))
            id_aluno = request.form.get("id_aluno") or None
            id_aluno = int(id_aluno) if id_aluno else None

            if not nome or not email:
                flash("Nome e email são obrigatórios.", "warning")
                usuario_data = Usuario.buscar_por_id(id)
                return render_template("usuario_form.html", usuario=usuario_data, niveis=NIVEIS_ACESSO, alunos=alunos)

            usuario = Usuario(email=email, senha=senha if senha else None, nome=nome, nivel=nivel, idUsuario=id, idAluno=id_aluno)
            sucesso, mensagem = usuario.editar()

            if sucesso:
                flash("Usuário atualizado com sucesso!", "success")
                return redirect(url_for("usuarios"))
            else:
                flash(mensagem, "danger")
        except Exception as e:
            flash("Erro ao atualizar usuário.", "danger")
            app.logger.error(f"Erro em usuario_editar: {e}")

    usuario = Usuario.buscar_por_id(id)
    if not usuario:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("usuarios"))

    return render_template("usuario_form.html", usuario=usuario, niveis=NIVEIS_ACESSO, alunos=alunos)

@app.route("/usuario/<int:id>/desativar", methods=["POST"])
@admin_required
def usuario_desativar(id):

    if id == session.get('usuario_id'):
        flash("Você não pode desativar seu próprio usuário!", "danger")
        return redirect(url_for("usuarios"))
    
    try:
        usuario = Usuario(idUsuario=id)
        if usuario.desativar():
            flash("Usuário desativado com sucesso.", "info")
        else:
            flash("Erro ao desativar usuário.", "danger")
    except Exception as e:
        flash("Erro ao processar desativação.", "danger")
        app.logger.error(f"Erro em usuario_desativar: {e}")
    return redirect(url_for("usuarios"))

@app.route("/usuario/<int:id>/toggle", methods=["POST"])
@admin_required
def usuario_toggle(id):
    usuario = Usuario.buscar_por_id(id)
    if not usuario:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("usuarios"))

    novo_estado = 0 if usuario.get('ativo') in (1, '1', True) else 1
    sucesso = Usuario.definir_ativo(id, novo_estado)
    if sucesso:
        flash("Status do usuário atualizado.", "success")
    else:
        flash("Falha ao atualizar status.", "danger")
    return redirect(url_for("usuarios"))

@app.route('/')
@login_required
def index():
    """Página inicial com estatísticas do sistema"""
    try:
        stats = Estatisticas.obter_todas_estatisticas()
        
        # Dados para gráficos
        estagios_situacao = Estatisticas.estagios_por_situacao()
        alunos_status = Estatisticas.alunos_por_status()
        estagios_meses = Estatisticas.estagios_ultimos_6_meses()
        
        return render_template('index.html', 
                             stats=stats,
                             estagios_situacao=estagios_situacao,
                             alunos_status=alunos_status,
                             estagios_meses=estagios_meses)
    except Exception as e:
        app.logger.error(f"Erro ao carregar estatísticas: {e}")
        stats = {
            'total_alunos': 0,
            'total_empresas': 0,
            'estagios_ativos': 0,
            'estagios_concluidos_mes': 0
        }
        flash("Erro ao carregar estatísticas do sistema.", "warning")
        return render_template('index.html', 
                             stats=stats,
                             estagios_situacao=[],
                             alunos_status=[],
                             estagios_meses=[])


@app.route("/alunos")
@login_required
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

# Em app_flask.py - SUBSTITUA a rota /aluno/novo

@app.route("/aluno/novo", methods=["GET", "POST"])
@login_required
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
            
            if not nome or not matricula or not cpf:
                flash("Nome, matrícula e CPF são obrigatórios.", "warning")
                return render_template("aluno_form.html", estados=estados, aluno=None)
            
            aluno = Aluno(nome, matricula, cpf, nome_inst, telefone, endereco, bairro,
                         periodo, status, idCidade, idEstado)
            
            # ← MUDANÇA: agora recebe tupla
            sucesso, mensagem = aluno.salvar()
            
            if sucesso:
                flash(mensagem, "success")  # ← Usa mensagem do retorno
                return redirect(url_for("alunos"))
            else:
                flash(mensagem, "danger")  # ← Usa mensagem de erro
                
        except Exception as e:
            flash(f"Erro ao processar cadastro: {str(e)}", "danger")
            app.logger.error(f"Erro em aluno_novo: {e}")
    
    return render_template("aluno_form.html", estados=estados, aluno=None)


# Em app_flask.py - SUBSTITUA a rota /aluno/<id>/editar

@app.route("/aluno/<int:id>/editar", methods=["GET", "POST"])
@login_required
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
            
            # ← MUDANÇA: agora recebe tupla
            sucesso, mensagem = aluno.editar()
            
            if sucesso:
                flash(mensagem, "success")
                return redirect(url_for("alunos"))
            else:
                flash(mensagem, "danger")
                
        except Exception as e:
            flash(f"Erro ao processar atualização: {str(e)}", "danger")
            app.logger.error(f"Erro em aluno_editar: {e}")
    
    aluno = Aluno.buscar_por_id(id)
    if not aluno:
        flash("Aluno não encontrado.", "danger")
        return redirect(url_for("alunos"))
    
    return render_template("aluno_form.html", estados=estados, aluno=aluno)


@app.route("/aluno/<int:id>/desativar", methods=["POST"])
@login_required
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

@app.route("/aluno/<int:id>/toggle", methods=["POST"])
@login_required
def aluno_toggle(id):
    aluno = Aluno.buscar_por_id(id)
    if not aluno:
        flash("Aluno não encontrado.", "danger")
        return redirect(url_for("alunos"))

    novo_estado = 0 if aluno.get('ativo') in (1, '1', True) else 1
    sucesso = Aluno.definir_ativo(id, novo_estado)
    if sucesso:
        flash("Status do aluno atualizado.", "success")
    else:
        flash("Falha ao atualizar status.", "danger")
    return redirect(url_for("alunos"))


@app.route("/empresas")
@login_required
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

# Em app_flask.py - SUBSTITUA a rota /empresa/novo

@app.route("/empresa/novo", methods=["GET", "POST"])
@login_required
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
            
            # ← MUDANÇA: agora recebe tupla
            sucesso, mensagem = emp.salvar()
            
            if sucesso:
                flash(mensagem, "success")
                return redirect(url_for("empresas"))
            else:
                flash(mensagem, "danger")
                
        except Exception as e:
            flash(f"Erro ao processar cadastro: {str(e)}", "danger")
            app.logger.error(f"Erro em empresa_nova: {e}")
    
    return render_template("empresa_form.html", estados=estados, empresa=None)


# Em app_flask.py - SUBSTITUA a rota /empresa/<id>/editar

@app.route("/empresa/<int:id>/editar", methods=["GET", "POST"])
@login_required
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
            
            # ← MUDANÇA: agora recebe tupla
            sucesso, mensagem = emp.editar()
            
            if sucesso:
                flash(mensagem, "success")
                return redirect(url_for("empresas"))
            else:
                flash(mensagem, "danger")
                
        except Exception as e:
            flash(f"Erro ao processar atualização: {str(e)}", "danger")
            app.logger.error(f"Erro em empresa_editar: {e}")
    
    empresa = Empresa.buscar_por_id(id)
    if not empresa:
        flash("Empresa não encontrada.", "danger")
        return redirect(url_for("empresas"))
    
    return render_template("empresa_form.html", estados=estados, empresa=empresa)


@app.route("/empresa/<int:id>/desativar", methods=["POST"])
@login_required
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

@app.route("/empresa/<int:id>/toggle", methods=["POST"])
@login_required
def empresa_toggle(id):
    empresa = Empresa.buscar_por_id(id)
    if not empresa:
        flash("Empresa não encontrado.", "danger")
        return redirect(url_for("empresas"))

    novo_estado = 0 if empresa.get('ativo') in (1, '1', True) else 1
    sucesso = Empresa.definir_ativo(id, novo_estado)
    if sucesso:
        flash("Status da empresa atualizado.", "success")
    else:
        flash("Falha ao atualizar status.", "danger")
    return redirect(url_for("empresas"))

@app.route("/estagios")
@login_required
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

# Em app_flask.py - SUBSTITUA a rota /estagio/novo

@app.route("/estagio/novo", methods=["GET", "POST"])
@login_required
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
            
            # ← MUDANÇA: agora recebe tupla
            sucesso, mensagem = est.salvar()
            
            if sucesso:
                flash(mensagem, "success")
                return redirect(url_for("estagios"))
            else:
                flash(mensagem, "danger")
                
        except Exception as e:
            flash(f"Erro ao processar cadastro: {str(e)}", "danger")
            app.logger.error(f"Erro em estagio_novo: {e}")
    
    return render_template("estagio_form.html", estados=estados, alunos=alunos,
                          empresas=empresas, estagio=None)


# Em app_flask.py - SUBSTITUA a rota /estagio/<id>/editar

@app.route("/estagio/<int:id>/editar", methods=["GET", "POST"])
@login_required
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
            
            # ← MUDANÇA: agora recebe tupla
            sucesso, mensagem = est.editar()
            
            if sucesso:
                flash(mensagem, "success")
                return redirect(url_for("estagios"))
            else:
                flash(mensagem, "danger")
                
        except Exception as e:
            flash(f"Erro ao processar atualização: {str(e)}", "danger")
            app.logger.error(f"Erro em estagio_editar: {e}")
    
    estagio = Estagio.buscar_por_id(id)
    if not estagio:
        flash("Estágio não encontrado.", "danger")
        return redirect(url_for("estagios"))
    
    return render_template("estagio_form.html", estados=estados, alunos=alunos,
                          empresas=empresas, estagio=estagio)


@app.route("/estagio/<int:id>/desativar", methods=["POST"])
@login_required
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

@app.route("/estagio/<int:id>/toggle", methods=["POST"])
@login_required
def estagio_toggle(id):
    estagio = Estagio.buscar_por_id(id)
    if not estagio:
        flash("Estágio não encontrado.", "danger")
        return redirect(url_for("estagios"))

    novo_estado = 0 if estagio.get('ativo') in (1, '1', True) else 1
    sucesso = Estagio.definir_ativo(id, novo_estado)
    if sucesso:
        flash("Status do estágio atualizado.", "success")
    else:
        flash("Falha ao atualizar status.", "danger")
    return redirect(url_for("estagios"))

@app.route("/api/cidades")
@login_required
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
@login_required
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
@login_required
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
@login_required
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

@app.route("/meus-estagios")
@login_required
def meus_estagios():

    from usuario import NIVEL_VISUALIZADOR
    usuario_nivel = session.get('usuario_nivel', NIVEL_VISUALIZADOR)
    usuario_aluno_id = session.get('usuario_aluno_id')

    if usuario_nivel == NIVEL_VISUALIZADOR:
        if not usuario_aluno_id:
            flash("Nenhum aluno associado ao seu usuário. Contate o administrador.", "warning")
            return redirect(url_for("index"))
        estagios = Estagio.listar_por_aluno(usuario_aluno_id)
        aluno = Aluno.buscar_por_id(usuario_aluno_id)
        return render_template("meus_estagios.html", estagios=estagios, aluno=aluno)

    aluno_id = request.args.get("aluno_id")
    if aluno_id:
        try:
            aid = int(aluno_id)
            estagios = Estagio.listar_por_aluno(aid)
            aluno = Aluno.buscar_por_id(aid)
            return render_template("meus_estagios.html", estagios=estagios, aluno=aluno)
        except Exception:
            flash("ID de aluno inválido.", "warning")
            return redirect(url_for("index"))

    return redirect(url_for('estagios'))

@app.route("/documentos")
@login_required
def documentos():
    """Lista documentos gerados"""
    try:
        gerador = GeradorDocumentos()
        documentos_gerados = gerador.listar_documentos_gerados()
        templates_ok = gerador.verificar_templates()
        
        return render_template("documentos.html", 
                             documentos=documentos_gerados,
                             templates=templates_ok)
    except Exception as e:
        flash("Erro ao carregar documentos.", "danger")
        app.logger.error(f"Erro em /documentos: {e}")
        return redirect(url_for("index"))

@app.route("/documento/plano/<int:estagio_id>", methods=["GET", "POST"])
@login_required
def gerar_plano_atividades(estagio_id):
    """Gera Plano de Atividades para um estágio"""
    try:
        estagio = Estagio.buscar_por_id(estagio_id)
        if not estagio:
            flash("Estágio não encontrado.", "danger")
            return redirect(url_for("estagios"))
        
        aluno_data = Aluno.buscar_por_id(estagio['idAlunoA'])
        empresa_data = Empresa.buscar_por_id(estagio['idEmpresaE'])
        
        if request.method == "POST":
            dados_estagiario = {
                'nome': aluno_data['nome'],
                'telefone': aluno_data.get('telefone', ''),
                'email': request.form.get('email_aluno', '')
            }
            
            dados_empresa = {
                'nome': empresa_data['razaoSocial'],
                'telefone': empresa_data.get('telefone', ''),
                'email': request.form.get('email_empresa', ''),
                'supervisor': estagio.get('supervisor', '')
            }
            
            cronograma = []
            periodos = request.form.getlist('periodo[]')
            atividades = request.form.getlist('atividade[]')
            
            for periodo, atividade in zip(periodos, atividades):
                if periodo and atividade:
                    cronograma.append({
                        'periodo': periodo,
                        'atividades': atividade
                    })
            
            cidade = request.form.get('cidade', aluno_data.get('cidade', ''))
            
            gerador = GeradorDocumentos()
            caminho = gerador.gerar_plano_atividades(
                dados_estagiario, dados_empresa, cronograma, cidade
            )
            
            flash("Plano de Atividades gerado com sucesso!", "success")
            return send_file(caminho, as_attachment=True)
        
        return render_template("gerar_plano.html", 
                             estagio=estagio,
                             aluno=aluno_data,
                             empresa=empresa_data)
                             
    except Exception as e:
        flash(f"Erro ao gerar documento: {str(e)}", "danger")
        app.logger.error(f"Erro em gerar_plano_atividades: {e}")
        return redirect(url_for("estagios"))

@app.route("/documento/ficha/<int:estagio_id>", methods=["GET", "POST"])
@login_required
def gerar_ficha_atividades(estagio_id):
    """Gera Ficha de Atividades para um estágio"""
    try:
        estagio = Estagio.buscar_por_id(estagio_id)
        if not estagio:
            flash("Estágio não encontrado.", "danger")
            return redirect(url_for("estagios"))
        
        aluno_data = Aluno.buscar_por_id(estagio['idAlunoA'])
        empresa_data = Empresa.buscar_por_id(estagio['idEmpresaE'])
        
        if request.method == "POST":
            dados_estagiario = {
                'nome': aluno_data['nome']
            }
            
            dados_empresa = {
                'nome': empresa_data['razaoSocial'],
                'supervisor': estagio.get('supervisor', '')
            }
            
            mes = request.form.get('mes')
            ano = int(request.form.get('ano'))
            
            atividades_diarias = []
            dias = request.form.getlist('dia[]')
            inicios = request.form.getlist('inicio[]')
            terminos = request.form.getlist('termino[]')
            descricoes = request.form.getlist('descricao[]')
            
            dia_contador = 1
            for dia, inicio, termino, descricao in zip(dias, inicios, terminos, descricoes):
                if inicio or termino or descricao:
                    dia_real = int(dia) if dia and dia.strip() else dia_contador
        
            atividades_diarias.append({
            'dia': dia_real,
            'inicio': inicio,
            'termino': termino,
            'descricao': descricao
            })
        
            dia_contador += 1

            gerador = GeradorDocumentos()
            caminho = gerador.gerar_ficha_atividades(
                dados_estagiario, dados_empresa, mes, ano, atividades_diarias
            )
            
            flash("Ficha de Atividades gerada com sucesso!", "success")
            return send_file(caminho, as_attachment=True)
        
        meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        
        return render_template("gerar_ficha.html",
                             estagio=estagio,
                             aluno=aluno_data,
                             empresa=empresa_data,
                             meses=meses)
                             
    except Exception as e:
        flash(f"Erro ao gerar documento: {str(e)}", "danger")
        app.logger.error(f"Erro em gerar_ficha_atividades: {e}")
        return redirect(url_for("estagios"))

@app.template_global()
def calcular_progresso(data_inicio, data_fim):
    try:
        if not data_inicio:
            return 0
        di = datetime.strptime(str(data_inicio), "%Y-%m-%d").date()
        if not data_fim:
            return 0
        df = datetime.strptime(str(data_fim), "%Y-%m-%d").date()
        hoje = datetime.now().date()
        total = (df - di).days
        if total <= 0:
            return 0
        decorrido = (min(hoje, df) - di).days
        pct = int((decorrido / total) * 100)
        if pct < 0: pct = 0
        if pct > 100: pct = 100
        return pct
    except Exception:
        return 0

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"Erro 500: {e}")
    flash("Erro interno do servidor. Tente novamente.", "danger")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'True') == 'True',
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000))
    )