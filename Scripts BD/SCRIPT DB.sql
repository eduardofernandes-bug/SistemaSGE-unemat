-- RECRIAR BANCO SGE (ATENÇÃO: vai apagar dados se já existe)
DROP DATABASE IF EXISTS sge;
CREATE DATABASE sge CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sge;

-- Tabela estados
CREATE TABLE estados (
  idEstado INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(75) DEFAULT NULL,
  uf CHAR(2) DEFAULT NULL
) ENGINE=InnoDB;

-- Tabela cidades
CREATE TABLE cidades (
  idCidade INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(120) DEFAULT NULL,
  idEstadoE INT NOT NULL,
  CONSTRAINT fk_cidades_estado FOREIGN KEY (idEstadoE) REFERENCES estados(idEstado)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Tabela aluno
CREATE TABLE aluno (
  idAluno INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100),
  matricula VARCHAR(50) UNIQUE,
  CPF CHAR(11) UNIQUE,
  nomeInstitucional VARCHAR(80),
  telefone VARCHAR(20),
  periodo ENUM('Matutino','Vespertino','Noturno','Integral') NOT NULL,
  statusAluno ENUM('Ativo','Inativo','Trancado','Concluído') NOT NULL,
  endereco VARCHAR(150),
  bairro VARCHAR(80),
  idCidade_Cidades INT NULL,
  idEstadoE_Cidades INT NULL,
  ativo TINYINT DEFAULT 1,
  CONSTRAINT fk_aluno_cidade FOREIGN KEY (idCidade_Cidades) REFERENCES cidades(idCidade)
    ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT fk_aluno_estado FOREIGN KEY (idEstadoE_Cidades) REFERENCES estados(idEstado)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;

-- Tabela empresa
CREATE TABLE empresa (
  idEmpresa INT AUTO_INCREMENT PRIMARY KEY,
  razaoSocial VARCHAR(130),
  nomeFantasia VARCHAR(80),
  cnpj CHAR(14) UNIQUE,
  cep CHAR(8),
  endereco VARCHAR(150),
  bairro VARCHAR(80),
  idCidade_Cidades INT NULL,
  idEstadoE_Cidades INT NULL,
  ativo TINYINT DEFAULT 1,
  CONSTRAINT fk_empresa_cidade FOREIGN KEY (idCidade_Cidades) REFERENCES cidades(idCidade)
    ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT fk_empresa_estado FOREIGN KEY (idEstadoE_Cidades) REFERENCES estados(idEstado)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;

-- Tabela estagio
CREATE TABLE estagio (
  idEstagio INT AUTO_INCREMENT PRIMARY KEY,
  idAlunoA INT NOT NULL,
  idEmpresaE INT NOT NULL,
  dataInicio DATE,
  dataFim DATE,
  cargaHorariaSemanal SMALLINT,
  situacao ENUM('Aguardando','Ativo','Trancado','Concluido','Cancelado') DEFAULT 'Aguardando',
  supervisor VARCHAR(90),
  orientadorAcademico VARCHAR(40),
  setor VARCHAR(50),
  documentacao VARCHAR(50),
  statusEstagio ENUM('Pendente','EmAnalise','Aprovado','Reprovado') DEFAULT 'Pendente',
  ativo TINYINT DEFAULT 1,
  CONSTRAINT fk_estagio_aluno FOREIGN KEY (idAlunoA) REFERENCES aluno(idAluno)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_estagio_empresa FOREIGN KEY (idEmpresaE) REFERENCES empresa(idEmpresa)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Índices utilitários
CREATE INDEX idx_aluno_cidade ON aluno(idCidade_Cidades);
CREATE INDEX idx_aluno_estado ON aluno(idEstadoE_Cidades);
CREATE INDEX idx_empresa_cidade ON empresa(idCidade_Cidades);
CREATE INDEX idx_empresa_estado ON empresa(idEstadoE_Cidades);
CREATE INDEX idx_estagio_aluno ON estagio(idAlunoA);
CREATE INDEX idx_estagio_empresa ON estagio(idEmpresaE);
