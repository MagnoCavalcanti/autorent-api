-- ==========================================================
-- Tabela: Empresa
-- ==========================================================
CREATE TABLE empresa (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cnpj VARCHAR(18) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    telefone VARCHAR(15) UNIQUE NOT NULL,
    cep VARCHAR(9) NOT NULL
);

-- ==========================================================
-- Tabela: Carro
-- ==========================================================
CREATE TABLE carro (
    id SERIAL PRIMARY KEY,
    placa VARCHAR(10) UNIQUE NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    marca VARCHAR(50) NOT NULL,
    ano INTEGER NOT NULL CHECK (ano >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'disponivel'
        CHECK (status IN ('disponivel', 'indisponivel', 'manutencao'))
);

-- ==========================================================
-- Tabela: Cliente
-- ==========================================================
CREATE TABLE cliente (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    telefone VARCHAR(15) UNIQUE NOT NULL,
    cep VARCHAR(9) NOT NULL
);

-- ==========================================================
-- Tabela: Usuario
-- ==========================================================
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    nome_usuario VARCHAR(50) UNIQUE NOT NULL,
    senha VARCHAR(128) NOT NULL,
    empresa_id INTEGER NOT NULL,
    FOREIGN KEY (empresa_id) REFERENCES empresa(id) ON DELETE CASCADE
);

-- ==========================================================
-- Tabela: Vendedor
-- ==========================================================
CREATE TABLE vendedor (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    telefone VARCHAR(15) UNIQUE NOT NULL
);

-- ==========================================================
-- Tabela: Aluguel
-- ==========================================================
CREATE TABLE aluguel (
    id SERIAL PRIMARY KEY,
    data_aluguel DATE NOT NULL,
    data_devolucao_prevista DATE NOT NULL,
    data_devolucao_real DATE NULL,
    valor_total NUMERIC(10,2) NOT NULL,
    carro_id INTEGER NOT NULL,
    cliente_id INTEGER NOT NULL,
    vendedor_id INTEGER NOT NULL,
    empresa_id INTEGER NOT NULL,

    FOREIGN KEY (carro_id) REFERENCES carro(id) ON DELETE CASCADE,
    FOREIGN KEY (cliente_id) REFERENCES cliente(id) ON DELETE CASCADE,
    FOREIGN KEY (vendedor_id) REFERENCES vendedor(id) ON DELETE CASCADE,
    FOREIGN KEY (empresa_id) REFERENCES empresa(id) ON DELETE CASCADE
);
