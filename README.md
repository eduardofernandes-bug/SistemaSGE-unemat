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
- 🧑‍💼 **Gestão de Usuários** - Níveis de acesso: Visualizador, Coordenador e Administrador
- 📊 **Dashboard com Gráficos** - Visualizações interativas com Chart.js
- 📄 **Geração de Documentos** - Planos e Fichas de Atividades automatizados
- 🔍 **Filtros Avançados** - Busca por estado, cidade e status
- 🎨 **Tema Claro/Escuro** - Interface personalizável
- 📱 **Design Responsivo** - Compatível com dispositivos móveis
- 🔐 **Segurança** - Boas práticas implementadas

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
```
Execute os scripts da pasta /Scripts BD na ordem:

SCRIPT DB

INSERT ESTADOS

INSERT CIDADES

INSERT DADOS (opcional para popular o sistema e testar) 
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
├── usuario.py                # Model de Usuários
├── estatisticas.py           # Cálculos e métricas + dados para gráficos
├── documento.py              # Geração de documentos .docx e .xlsx
├── generate_secret_key.py    # Gerador de chave secreta
├── requirements.txt          # Dependências Python
├── .env.example              # Template de configuração
├── .gitignore                # Arquivos ignorados
├── README.md                 # Este arquivo
│
└── templates/                # Templates Jinja2
    ├── base.html             # Layout base
    ├── index.html            # Dashboard principal com gráficos
    ├── login.html            # Tela de login
    ├── alunos.html           # Lista de alunos
    ├── aluno_form.html       # Formulário de aluno
    ├── empresas.html         # Lista de empresas
    ├── empresa_form.html     # Formulário de empresa
    ├── estagios.html         # Lista de estágios
    ├── estagio_form.html     # Formulário de estágio
    ├── usuarios.html         # Lista de usuários
    ├── usuario_form.html     # Formulário de usuários
    ├── primeiro_acesso.html  # Cadastro inicial do usuário administrador
    ├── meus_estagios.html    # Visualização dos estágios do aluno
    ├── gerar_plano.html      # Interface para gerar Plano de Atividades
    └── gerar_ficha.html      # Interface para gerar Ficha de Atividades
```

---

## 🎯 Funcionalidades Detalhadas

### 👨‍🎓 Módulo de Alunos
- Dados completos (nome, matrícula, CPF, telefone, nome institucional, endereço, bairro)
- Máscaras automáticas (CPF, telefone)
- Filtros por estado/cidade
- Ativar/Desativar aluno (com botão alternável)
- Edição estruturada com layout moderno

### 🏢 Módulo de Empresas
- Cadastro com CNPJ + máscara
- CEP, endereço, bairro, cidade, estado
- Filtro por UF e cidade
- Botão ativar/desativar

### 📋 Módulo de Estágios
- Vínculo aluno/empresa
- Controle de situação (Aguardando, Ativo, Trancado, Concluído, Cancelado)
- Carga horária, datas com validação
- Supervisor, orientador e setor
- Filtros avançados

### 🧑‍🚀 Módulo de Usuários
- Níveis completos:
  - Visualizador (apenas Meus Estágios)
  - Coordenador (Alunos, Empresas e Estágios)
  - Administrador (tudo)
- Usuário não pode desativar a si mesmo
- Associação opcional de aluno → libera tela Meus Estágios

### 📌 Módulo "Meus Estágios"
- Exibe dados do estágio do aluno
- Barra de progresso automática
- Situação atual

### 📊 Dashboard com Gráficos Interativos
- **Cards Informativos:**
  - Total de alunos ativos
  - Total de empresas parceiras
  - Estágios ativos no momento
  - Estágios concluídos no mês atual

- **Visualizações Gráficas (Chart.js 4.4.1):**
  - 📊 **Gráfico de Pizza**: Distribuição de Estágios por Situação
  - 👨‍🎓 **Gráfico de Pizza**: Distribuição de Alunos por Status
  - 📈 **Gráfico de Linha**: Evolução de Novos Estágios (últimos 6 meses)

- **Características:**
  - Responsivos e interativos
  - Atualização em tempo real
  - Cores intuitivas e consistentes
  - Animações suaves

### 📄 Geração Automatizada de Documentos
- **Anexo VI - Plano de Atividades (.docx)**
  - Preenchimento automático de dados do aluno, empresa e estágio
  - Formatação padronizada institucional
  - Download direto pelo navegador

- **Anexo VII - Ficha de Atividades (.xlsx)**
  - Planilha mensal com dias do mês
  - Cabeçalho com dados do estagiário
  - Formatação profissional (bordas, cores, alinhamento)
  - Nome de arquivo automático: `Ficha_Atividades_{ALUNO}_{MES}_{ANO}.xlsx`

- **Tecnologias:**
  - `python-docx` para documentos Word
  - `openpyxl` para planilhas Excel
  - Validações de data e existência de estágio

---

## 🔐 Segurança

### ✅ Implementado
- ✅ SECRET_KEY gerada automaticamente
- ✅ Prepared Statements (sem SQL injection)
- ✅ Sessões com expiração
- ✅ Usuário não pode se autodesativar
- ✅ .env fora do versionamento
- ✅ Hash de senhas com Werkzeug

---

## 🛠️ Tecnologias

### Backend
| Tecnologia | Versão | Uso |
|------------|--------|-----|
| Python | 3.8+ | Linguagem principal |
| Flask | 3.0.0 | Framework web |
| MySQL | 5.7+ | Banco de dados |
| python-docx | 1.1.0 | Geração de documentos Word |
| openpyxl | 3.1.2 | Geração de planilhas Excel |
| Werkzeug | 3.0.1 | Segurança e hash |
| python-dotenv | 1.0.0 | Variáveis de ambiente |

### Frontend
| Tecnologia | Versão | Uso |
|------------|--------|-----|
| Bootstrap | 5.3.0 | Framework CSS |
| Bootstrap Icons | 1.11.0 | Ícones |
| Chart.js | 4.4.1 | Gráficos interativos |
| Jinja2 | 3.1+ | Template engine |
| JavaScript | ES6+ | Interatividade |


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

---

## 📖 API Endpoints

### Estatísticas para Dashboard
```http
GET /api/estatisticas
```

**Resposta:**
```json
{
  "total_alunos": 150,
  "total_empresas": 45,
  "estagios_ativos": 89,
  "estagios_concluidos_mes": 12,
  "estagios_por_situacao": [
    {"situacao": "Ativo", "total": 89},
    {"situacao": "Concluído", "total": 34}
  ],
  "alunos_por_status": [
    {"status": "Ativo", "total": 120},
    {"status": "Inativo", "total": 30}
  ],
  "estagios_ultimos_6_meses": [
    {"mes": "2025-06", "total": 15},
    {"mes": "2025-07", "total": 22}
  ]
}
```

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

### Gerar Plano de Atividades
```http
POST /documentos/plano/<id_estagio>
```

### Gerar Ficha de Atividades
```http
POST /documentos/ficha/<id_estagio>?mes=12&ano=2025
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

### Gráficos não aparecem
- Verifique a conexão com CDN do Chart.js
- Abra o console (F12) e procure por erros JavaScript
- Confirme que `/api/estatisticas` retorna dados válidos
- Limpe o cache do navegador (Ctrl+Shift+Delete)

### Erro ao gerar documentos
```bash
# Verifique se as bibliotecas estão instaladas
pip install python-docx openpyxl

# Confirme permissões de escrita na pasta do projeto
```

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
- Validações nos models
- Tratamento de erros

---

## 📄 Licença

Este projeto foi desenvolvido para fins **educacionais** no **Laboratório de Programação Orientada a Objetos - UNEMAT**.

---

## 👥 Autores

**Desenvolvido por:** Eduardo Fernandes, João Victor e Leonardo Miranda  
**Instituição:** UNEMAT - Universidade do Estado de Mato Grosso  
**Disciplina:** Laboratório de Programação Orientada a Objetos - LPOO  
**Professor:** Carlos Alex Sander Juvencio Gulo  
**Período:** 2025/2 - 5º Semestre | Ciência da Computação

---

## 🙏 Agradecimentos

- Equipe UNEMAT
- Comunidade Flask
- Bootstrap Team
- Chart.js Contributors
- Todos os contribuidores


---

## 🔄 Changelog

### v1.2.0 - Dezembro 2025 (Atual) 🎉
- ✨ **Dashboard com Gráficos Interativos (Chart.js)**
  - Gráfico de pizza: Estágios por Situação
  - Gráfico de pizza: Alunos por Status
  - Gráfico de linha: Evolução de Estágios (6 meses)
- 📄 **Geração Automatizada de Documentos**
  - Anexo VI: Plano de Atividades (.docx)
  - Anexo VII: Ficha de Atividades (.xlsx)
  - Preenchimento automático de dados
- 📊 **Novas APIs de Estatísticas**
  - `/api/estatisticas` com dados completos
  - Endpoints para gráficos
- 🎨 **Melhorias de UI/UX**
  - Cards responsivos no dashboard
  - Animações suaves
  - Layout modernizado
- 🔧 **Novos Módulos**
  - `documento.py` para geração de arquivos
  - Métodos expandidos em `estatisticas.py`

### v1.1.0 - Novembro 2025
- ✅ Tema escuro/claro completo
- ✅ Novo layout moderno em todas as telas
- ✅ Tela de Primeiro Acesso
- ✅ Botão ativar/desativar para todos os módulos
- ✅ Melhoria nos formulários (validações e máscaras)
- ✅ Novo módulo Meus Estágios
- ✅ Dashboard remodelado
- ✅ Filtros avançados por estado/cidade
- ✅ Ajustes na segurança
- ✅ Melhorias de UI/UX

### v1.0.0 - Outubro 2025
- ✅ Estrutura básica com CRUDs
- ✅ Dashboard simples
- ✅ Temas e filtros iniciais

---

<div align="center">

**⭐ Se este projeto foi útil, considere dar uma estrela!**

Desenvolvido com ❤️ por Eduardo, João e Leonardo - UNEMAT

[⬆ Voltar ao topo](#-sge---sistema-de-gerenciamento-de-estágios)

</div>
