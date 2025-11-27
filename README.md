# 📚 SGE - Sistema de Gerenciamento de Estágios

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-5.7%2B-orange.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-Educational-yellow.svg)](LICENSE)

Sistema web moderno e completo para gerenciamento de estágios em instituições de ensino. Desenvolvido com Python/Flask, oferece interface intuitiva para cadastro e acompanhamento de alunos, empresas parceiras e contratos de estágio.


---

## ✨ Características Principais

- 🎓 **Gerenciamento de Alunos** - Cadastro completo com validações automáticas
- 🏢 **Empresas Parceiras** - Controle de empresas conveniadas
- 📋 **Controle de Estágios** - Acompanhamento detalhado de contratos
- 📊 **Dashboard Intuitivo** - Estatísticas em tempo real
- 🔍 **Filtros Avançados** - Busca por estado, cidade e status
- 🎨 **Tema Claro/Escuro** - Interface personalizável
- 📱 **Design Responsivo** - Compatível com dispositivos móveis
- 🔐 **Segurança** - Boas práticas implementadas
- 🚀 **API REST** - Endpoints para integração

---

## 🚀 Início Rápido

### Pré-requisitos

```bash
Python 3.8+
MySQL 5.7+
pip
```

### Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/eduardofernandes-bug/SistemaSGE-unemat
cd sge
```

2. **Crie e ative o ambiente virtual**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure o banco de dados**
```sql
CREATE DATABASE sge CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

5. **Configure as variáveis de ambiente**
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Gere uma SECRET_KEY segura
python generate_secret_key.py

# Edite o arquivo .env com suas configurações
```

6. **Execute a aplicação**
```bash
python app_flask.py
```

7. **Acesse no navegador**
```
http://localhost:5000
```

---

## 📁 Estrutura do Projeto

```
sge/
├── app_flask.py              # Aplicação principal Flask
├── db.py                     # Configuração do banco de dados
├── aluno.py                  # Model de Aluno
├── empresa.py                # Model de Empresa
├── estagio.py                # Model de Estágio
├── localidades.py            # Model de Estados/Cidades
├── estatisticas.py           # Cálculos e métricas
├── generate_secret_key.py    # Gerador de chave secreta
├── requirements.txt          # Dependências Python
├── .env.example              # Template de configuração
├── .gitignore                # Arquivos ignorados
├── README.md                 # Este arquivo
│
└── templates/                # Templates Jinja2
    ├── base.html             # Layout base
    ├── index.html            # Dashboard principal
    ├── alunos.html           # Lista de alunos
    ├── aluno_form.html       # Formulário de aluno
    ├── empresas.html         # Lista de empresas
    ├── empresa_form.html     # Formulário de empresa
    ├── estagios.html         # Lista de estágios
    └── estagio_form.html     # Formulário de estágio
```

---

## 🎯 Funcionalidades Detalhadas

### 👨‍🎓 Módulo de Alunos
- Cadastro com validação de CPF (11 dígitos)
- Máscaras automáticas para CPF e telefone
- Campos: nome, matrícula, CPF, telefone, endereço, período, status
- Filtros por estado, cidade e status (ativo/inativo)
- Soft delete (desativação sem remoção)

### 🏢 Módulo de Empresas
- Cadastro com validação opcional de CNPJ (14 dígitos)
- Máscara automática para CNPJ
- Campos: razão social, nome fantasia, CNPJ, CEP, endereço
- Vinculação com localização (estado/cidade)
- Filtros e sistema de desativação

### 📋 Módulo de Estágios
- Vinculação aluno-empresa
- Controle de datas (início/fim com validação)
- Carga horária semanal
- Status detalhado (Aguardando, Ativo, Trancado, Concluído, Cancelado)
- Informações complementares: supervisor, orientador, setor, documentação
- Filtros por localização do aluno ou empresa

### 📊 Dashboard
- Total de alunos ativos
- Total de empresas parceiras
- Estágios ativos no momento
- Estágios concluídos no mês atual
- Cards informativos com ícones

---

## 🔐 Segurança

### ✅ Implementado
- ✅ Variáveis de ambiente para credenciais sensíveis
- ✅ SECRET_KEY aleatória gerada com `secrets.token_hex(32)`
- ✅ Cookies seguros: HttpOnly, SameSite
- ✅ Prepared statements (previne SQL Injection)
- ✅ Validação e sanitização de entrada
- ✅ Sessões com timeout de 30 minutos
- ✅ Logging de erros
- ✅ Arquivo `.env` no `.gitignore`

### ⚠️ Recomendações para Produção
- [ ] Implementar sistema de autenticação/autorização
- [ ] Configurar HTTPS com certificado SSL
- [ ] Adicionar rate limiting
- [ ] Implementar CSRF protection
- [ ] Sistema de auditoria de ações

---

## 🛠️ Tecnologias

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| Python | 3.8+ | Backend |
| Flask | 3.0.0 | Framework web |
| MySQL | 5.7+ | Banco de dados |
| Bootstrap | 5.3.0 | Framework CSS |
| JavaScript | ES6+ | Interatividade |
| Jinja2 | 3.1+ | Templates |
| Gunicorn | 21.2.0 | Servidor WSGI |

---

## 📝 Configuração do `.env`

```env
# === BANCO DE DADOS ===
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=sge

# === SEGURANÇA ===
SECRET_KEY=gere_com_generate_secret_key.py

# === AMBIENTE ===
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
```

**⚠️ IMPORTANTE:**
- **NUNCA** commite o arquivo `.env`
- **SEMPRE** use uma SECRET_KEY diferente em produção
- Em produção: `FLASK_ENV=production` e `FLASK_DEBUG=False`

---

## 🚀 Deploy em Produção

### Com Gunicorn (Recomendado)

```bash
# Instale o Gunicorn
pip install gunicorn

# Execute com 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app_flask:app
```

### Configuração Nginx (Proxy Reverso)

```nginx
server {
    listen 80;
    server_name seu_dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## 📖 API Endpoints

### Cidades por Estado
```http
GET /api/cidades?estado=1
```

**Resposta:**
```json
[
  {"idCidade": 1, "cidade": "Rondonópolis"},
  {"idCidade": 2, "cidade": "Cuiabá"}
]
```

### Listar Alunos
```http
GET /api/alunos?estado=1&cidade=5
```

### Listar Empresas
```http
GET /api/empresas?estado=1
```

### Listar Estágios
```http
GET /api/estagios?cidade=5
```

---

## 🐛 Solução de Problemas

### Erro de Conexão MySQL
```bash
# Verifique se o MySQL está rodando
sudo systemctl status mysql

# Teste a conexão
mysql -u root -p
```

### SECRET_KEY não encontrada
```bash
# Gere uma nova chave
python generate_secret_key.py

# Copie para o .env
# SECRET_KEY=chave_gerada_aqui
```

### Cidades não carregam
- Verifique o console do navegador (F12)
- Confirme que `/api/cidades` está funcionando
- Verifique se existem dados na tabela `cidades`

---

## 📚 Documentação Completa

Para documentação detalhada com guias passo-a-passo, consulte:
- [DOCUMENTATION.md](DOCUMENTATION.md) - Documentação completa do sistema

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'Adiciona nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

### Padrões de Código
- Siga PEP 8 para Python
- Docstrings em português
- Comentários explicativos
- Validações nos models
- Tratamento de erros

---

## 📄 Licença

Este projeto foi desenvolvido para fins **educacionais** no **Laboratório de Programação Orientada a Objetos - UNEMAT**.

---

## 👥 Autores

**Desenvolvido por:** [Seu Nome/Equipe]  
**Instituição:** UNEMAT - Universidade do Estado de Mato Grosso  
**Disciplina:** Laboratório de Programação Orientada a Objetos  
**Professor:** [Nome do Professor]  
**Período:** 2024/2025

---

## 🙏 Agradecimentos

- Equipe UNEMAT
- Comunidade Flask
- Bootstrap Team
- Todos os contribuidores

---

## 📞 Contato e Suporte

- **Email**: seu_email@exemplo.com
- **GitHub Issues**: [Link do repositório]
- **Documentação**: [Link da documentação]

---

## 🔄 Changelog

### v1.0.0 - Inicial (2024/2025)
- ✅ Sistema completo de gerenciamento
- ✅ CRUD de alunos, empresas e estágios
- ✅ Dashboard com estatísticas
- ✅ Filtros por localização
- ✅ Tema claro/escuro com persistência
- ✅ Design responsivo
- ✅ Validações e máscaras
- ✅ Soft delete
- ✅ API REST

### Próximas Versões
- [ ] Sistema de autenticação
- [ ] Relatórios em PDF
- [ ] Gráficos avançados
- [ ] Notificações por email
- [ ] Upload de documentos

---

<div align="center">

**⭐ Se este projeto foi útil, considere dar uma estrela!**

Desenvolvido com ❤️ por [Sua Equipe] - UNEMAT

[⬆ Voltar ao topo](#-sge---sistema-de-gerenciamento-de-estágios)

</div>