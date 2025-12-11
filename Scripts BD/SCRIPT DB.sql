
SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

CREATE SCHEMA IF NOT EXISTS `sge` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci ;
USE `sge` ;

CREATE TABLE IF NOT EXISTS `sge`.`estados` (
  `idEstado` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(75) NULL DEFAULT NULL,
  `uf` CHAR(2) NULL DEFAULT NULL,
  PRIMARY KEY (`idEstado`))
ENGINE = InnoDB
AUTO_INCREMENT = 28
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `sge`.`cidades` (
  `idCidade` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(120) NULL DEFAULT NULL,
  `idEstadoE` INT NOT NULL,
  PRIMARY KEY (`idCidade`),
  INDEX `fk_cidades_estado` (`idEstadoE` ASC) VISIBLE,
  CONSTRAINT `fk_cidades_estado`
    FOREIGN KEY (`idEstadoE`)
    REFERENCES `sge`.`estados` (`idEstado`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 5565
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `sge`.`aluno` (
  `idAluno` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NULL DEFAULT NULL,
  `matricula` VARCHAR(50) NULL DEFAULT NULL,
  `CPF` CHAR(11) NULL DEFAULT NULL,
  `nomeInstitucional` VARCHAR(80) NULL DEFAULT NULL,
  `telefone` VARCHAR(20) NULL DEFAULT NULL,
  `periodo` ENUM('Matutino', 'Vespertino', 'Noturno', 'Integral') NOT NULL,
  `statusAluno` ENUM('Ativo', 'Inativo', 'Trancado', 'Concluído') NOT NULL,
  `endereco` VARCHAR(150) NULL DEFAULT NULL,
  `bairro` VARCHAR(80) NULL DEFAULT NULL,
  `idCidade_Cidades` INT NULL DEFAULT NULL,
  `idEstadoE_Cidades` INT NULL DEFAULT NULL,
  `ativo` TINYINT NULL DEFAULT '1',
  PRIMARY KEY (`idAluno`),
  UNIQUE INDEX `matricula` (`matricula` ASC) VISIBLE,
  UNIQUE INDEX `CPF` (`CPF` ASC) VISIBLE,
  INDEX `idx_aluno_cidade` (`idCidade_Cidades` ASC) VISIBLE,
  INDEX `idx_aluno_estado` (`idEstadoE_Cidades` ASC) VISIBLE,
  CONSTRAINT `fk_aluno_cidade`
    FOREIGN KEY (`idCidade_Cidades`)
    REFERENCES `sge`.`cidades` (`idCidade`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT `fk_aluno_estado`
    FOREIGN KEY (`idEstadoE_Cidades`)
    REFERENCES `sge`.`estados` (`idEstado`)
    ON DELETE SET NULL
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 32
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `sge`.`empresa` (
  `idEmpresa` INT NOT NULL AUTO_INCREMENT,
  `razaoSocial` VARCHAR(130) NULL DEFAULT NULL,
  `nomeFantasia` VARCHAR(80) NULL DEFAULT NULL,
  `cnpj` CHAR(14) NULL DEFAULT NULL,
  `cep` CHAR(8) NULL DEFAULT NULL,
  `endereco` VARCHAR(150) NULL DEFAULT NULL,
  `bairro` VARCHAR(80) NULL DEFAULT NULL,
  `idCidade_Cidades` INT NULL DEFAULT NULL,
  `idEstadoE_Cidades` INT NULL DEFAULT NULL,
  `ativo` TINYINT NULL DEFAULT '1',
  PRIMARY KEY (`idEmpresa`),
  UNIQUE INDEX `cnpj` (`cnpj` ASC) VISIBLE,
  INDEX `idx_empresa_cidade` (`idCidade_Cidades` ASC) VISIBLE,
  INDEX `idx_empresa_estado` (`idEstadoE_Cidades` ASC) VISIBLE,
  CONSTRAINT `fk_empresa_cidade`
    FOREIGN KEY (`idCidade_Cidades`)
    REFERENCES `sge`.`cidades` (`idCidade`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT `fk_empresa_estado`
    FOREIGN KEY (`idEstadoE_Cidades`)
    REFERENCES `sge`.`estados` (`idEstado`)
    ON DELETE SET NULL
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 21
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `sge`.`estagio` (
  `idEstagio` INT NOT NULL AUTO_INCREMENT,
  `idAlunoA` INT NOT NULL,
  `idEmpresaE` INT NOT NULL,
  `dataInicio` DATE NULL DEFAULT NULL,
  `dataFim` DATE NULL DEFAULT NULL,
  `cargaHorariaSemanal` SMALLINT NULL DEFAULT NULL,
  `situacao` ENUM('Aguardando', 'Ativo', 'Trancado', 'Concluido', 'Cancelado') NULL DEFAULT 'Aguardando',
  `supervisor` VARCHAR(90) NULL DEFAULT NULL,
  `orientadorAcademico` VARCHAR(40) NULL DEFAULT NULL,
  `setor` VARCHAR(50) NULL DEFAULT NULL,
  `documentacao` VARCHAR(50) NULL DEFAULT NULL,
  `statusEstagio` ENUM('Pendente', 'EmAnalise', 'Aprovado', 'Reprovado') NULL DEFAULT 'Pendente',
  `ativo` TINYINT NULL DEFAULT '1',
  PRIMARY KEY (`idEstagio`),
  INDEX `idx_estagio_aluno` (`idAlunoA` ASC) VISIBLE,
  INDEX `idx_estagio_empresa` (`idEmpresaE` ASC) VISIBLE,
  CONSTRAINT `fk_estagio_aluno`
    FOREIGN KEY (`idAlunoA`)
    REFERENCES `sge`.`aluno` (`idAluno`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `fk_estagio_empresa`
    FOREIGN KEY (`idEmpresaE`)
    REFERENCES `sge`.`empresa` (`idEmpresa`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 79
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `sge`.`usuarios` (
  `idUsuario` INT NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(255) NOT NULL,
  `senha` VARCHAR(255) NOT NULL,
  `nome` VARCHAR(255) NOT NULL,
  `tipo` ENUM('admin', 'usuario') NULL DEFAULT 'usuario',
  `ativo` TINYINT(1) NULL DEFAULT '1',
  `data_criacao` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `data_atualizacao` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `nivel` INT NULL DEFAULT '1' COMMENT '1=Visualizador, 2=Coordenador, 3=Admin',
  `idAluno` INT NULL DEFAULT NULL,
  PRIMARY KEY (`idUsuario`),
  UNIQUE INDEX `email` (`email` ASC) VISIBLE,
  INDEX `idx_email` (`email` ASC) VISIBLE,
  INDEX `idx_ativo` (`ativo` ASC) VISIBLE,
  INDEX `idx_usuarios_nivel` (`nivel` ASC) VISIBLE,
  INDEX `fk_usuarios_aluno` (`idAluno` ASC) VISIBLE,
  CONSTRAINT `fk_usuarios_aluno`
    FOREIGN KEY (`idAluno`)
    REFERENCES `sge`.`aluno` (`idAluno`))
ENGINE = InnoDB
AUTO_INCREMENT = 6
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;

TRUNCATE TABLE aluno;
TRUNCATE TABLE empresa;
TRUNCATE TABLE estagio;
TRUNCATE TABLE usuarios;
