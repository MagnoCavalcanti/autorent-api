-- Empresa
INSERT INTO empresa (nome, cnpj, email, telefone, cep) VALUES ('AutoRent Centro', '12.345.678/0001-90', 'contato@autorentcentro.com', '(11) 4000-1000', '01001-000');
INSERT INTO empresa (nome, cnpj, email, telefone, cep) VALUES ('AutoRent Norte', '23.456.789/0001-01', 'contato@norte.com', '(11) 4000-1001', '02020-000');
INSERT INTO empresa (nome, cnpj, email, telefone, cep) VALUES ('AutoRent Sul', '34.567.890/0001-12', 'contato@sul.com', '(11) 4000-1002', '03030-000');
INSERT INTO empresa (nome, cnpj, email, telefone, cep) VALUES ('AutoRent Leste', '45.678.901/0001-23', 'contato@leste.com', '(11) 4000-1003', '04040-000');
INSERT INTO empresa (nome, cnpj, email, telefone, cep) VALUES ('AutoRent Oeste', '56.789.012/0001-34', 'contato@oeste.com', '(11) 4000-1004', '05050-000');
INSERT INTO empresa (nome, cnpj, email, telefone, cep) VALUES ('AutoRent Premium', '67.890.123/0001-45', 'premium@autorent.com', '(11) 4000-1005', '06060-000');
INSERT INTO empresa (nome, cnpj, email, telefone, cep) VALUES ('AutoRent Executivo', '78.901.234/0001-56', 'exec@autorent.com', '(11) 4000-1006', '07070-000');
INSERT INTO empresa (nome, cnpj, email, telefone, cep) VALUES ('AutoRent Popular', '89.012.345/0001-67', 'popular@autorent.com', '(11) 4000-1007', '08080-000');
INSERT INTO empresa (nome, cnpj, email, telefone, cep) VALUES ('AutoRent Flex', '90.123.456/0001-78', 'flex@autorent.com', '(11) 4000-1008', '09090-000');
INSERT INTO empresa (nome, cnpj, email, telefone, cep) VALUES ('AutoRent Express', '11.222.333/0001-99', 'express@autorent.com', '(11) 4000-1009', '01111-000');

-- Carro
INSERT INTO carro (placa, modelo, marca, ano, status) VALUES ('ABC-1234', 'Onix', 'Chevrolet', 2020, 'disponivel');
INSERT INTO carro (placa, modelo, marca, ano, status) VALUES ('DEF-5678', 'HB20', 'Hyundai', 2019, 'disponivel');
INSERT INTO carro (placa, modelo, marca, ano, status) VALUES ('GHI-9012', 'Gol', 'Volkswagen', 2018, 'indisponivel');
INSERT INTO carro (placa, modelo, marca, ano, status) VALUES ('JKL-3456', 'Ka', 'Ford', 2017, 'manutencao');
INSERT INTO carro (placa, modelo, marca, ano, status) VALUES ('MNO-7890', 'Corolla', 'Toyota', 2021, 'disponivel');
INSERT INTO carro (placa, modelo, marca, ano, status) VALUES ('PQR-1122', 'Civic', 'Honda', 2022, 'disponivel');
INSERT INTO carro (placa, modelo, marca, ano, status) VALUES ('STU-3344', 'Argo', 'Fiat', 2020, 'disponivel');
INSERT INTO carro (placa, modelo, marca, ano, status) VALUES ('VWX-5566', 'Sandero', 'Renault', 2019, 'indisponivel');
INSERT INTO carro (placa, modelo, marca, ano, status) VALUES ('YZA-7788', 'Compass', 'Jeep', 2023, 'disponivel');
INSERT INTO carro (placa, modelo, marca, ano, status) VALUES ('BCA-9900', 'Tracker', 'Chevrolet', 2022, 'disponivel');

-- Cliente
INSERT INTO cliente (nome, cpf, email, telefone, cep) VALUES ('João Silva', '123.456.789-00', 'joao.silva@example.com', '(11) 91234-0001', '01010-000');
INSERT INTO cliente (nome, cpf, email, telefone, cep) VALUES ('Maria Souza', '234.567.890-11', 'maria.souza@example.com', '(11) 91234-0002', '02020-000');
INSERT INTO cliente (nome, cpf, email, telefone, cep) VALUES ('Pedro Santos', '345.678.901-22', 'pedro.santos@example.com', '(11) 91234-0003', '03030-000');
INSERT INTO cliente (nome, cpf, email, telefone, cep) VALUES ('Ana Paula', '456.789.012-33', 'ana.paula@example.com', '(11) 91234-0004', '04040-000');
INSERT INTO cliente (nome, cpf, email, telefone, cep) VALUES ('Lucas Almeida', '567.890.123-44', 'lucas.almeida@example.com', '(11) 91234-0005', '05050-000');
INSERT INTO cliente (nome, cpf, email, telefone, cep) VALUES ('Carla Pereira', '678.901.234-55', 'carla.pereira@example.com', '(11) 91234-0006', '06060-000');
INSERT INTO cliente (nome, cpf, email, telefone, cep) VALUES ('Rafael Costa', '789.012.345-66', 'rafael.costa@example.com', '(11) 91234-0007', '07070-000');
INSERT INTO cliente (nome, cpf, email, telefone, cep) VALUES ('Bruna Lima', '890.123.456-77', 'bruna.lima@example.com', '(11) 91234-0008', '08080-000');
INSERT INTO cliente (nome, cpf, email, telefone, cep) VALUES ('Felipe Araujo', '901.234.567-88', 'felipe.araujo@example.com', '(11) 91234-0009', '09090-000');
INSERT INTO cliente (nome, cpf, email, telefone, cep) VALUES ('Paula Ribeiro', '012.345.678-99', 'paula.ribeiro@example.com', '(11) 91234-0010', '01111-000');

-- Usuario (empresa_id referenciando 1..10)
INSERT INTO usuario (nome_usuario, senha, empresa_id) VALUES ('admin_centro', 'hash_senha_1', 1);
INSERT INTO usuario (nome_usuario, senha, empresa_id) VALUES ('admin_norte', 'hash_senha_2', 2);
INSERT INTO usuario (nome_usuario, senha, empresa_id) VALUES ('admin_sul', 'hash_senha_3', 3);
INSERT INTO usuario (nome_usuario, senha, empresa_id) VALUES ('admin_leste', 'hash_senha_4', 4);
INSERT INTO usuario (nome_usuario, senha, empresa_id) VALUES ('admin_oeste', 'hash_senha_5', 5);
INSERT INTO usuario (nome_usuario, senha, empresa_id) VALUES ('admin_premium', 'hash_senha_6', 6);
INSERT INTO usuario (nome_usuario, senha, empresa_id) VALUES ('admin_exec', 'hash_senha_7', 7);
INSERT INTO usuario (nome_usuario, senha, empresa_id) VALUES ('admin_popular', 'hash_senha_8', 8);
INSERT INTO usuario (nome_usuario, senha, empresa_id) VALUES ('admin_flex', 'hash_senha_9', 9);
INSERT INTO usuario (nome_usuario, senha, empresa_id) VALUES ('admin_express', 'hash_senha_10', 10);

-- Vendedor
INSERT INTO vendedor (nome, cpf, email, telefone) VALUES ('Carlos Mendes', '111.222.333-44', 'carlos.mendes@autorent.com', '(11) 90001-0001');
INSERT INTO vendedor (nome, cpf, email, telefone) VALUES ('Fernanda Dias', '222.333.444-55', 'fernanda.dias@autorent.com', '(11) 90001-0002');
INSERT INTO vendedor (nome, cpf, email, telefone) VALUES ('Marcos Vinicius', '333.444.555-66', 'marcos.vini@autorent.com', '(11) 90001-0003');
INSERT INTO vendedor (nome, cpf, email, telefone) VALUES ('Aline Rocha', '444.555.666-77', 'aline.rocha@autorent.com', '(11) 90001-0004');
INSERT INTO vendedor (nome, cpf, email, telefone) VALUES ('Tiago Nunes', '555.666.777-88', 'tiago.nunes@autorent.com', '(11) 90001-0005');
INSERT INTO vendedor (nome, cpf, email, telefone) VALUES ('Juliana Prado', '666.777.888-99', 'juliana.prado@autorent.com', '(11) 90001-0006');
INSERT INTO vendedor (nome, cpf, email, telefone) VALUES ('Rodrigo Pires', '777.888.999-00', 'rodrigo.pires@autorent.com', '(11) 90001-0007');
INSERT INTO vendedor (nome, cpf, email, telefone) VALUES ('Patricia Moraes', '888.999.000-11', 'patricia.moraes@autorent.com', '(11) 90001-0008');
INSERT INTO vendedor (nome, cpf, email, telefone) VALUES ('Bruno Martins', '999.000.111-22', 'bruno.martins@autorent.com', '(11) 90001-0009');
INSERT INTO vendedor (nome, cpf, email, telefone) VALUES ('Sofia Teixeira', '000.111.222-33', 'sofia.teixeira@autorent.com', '(11) 90001-0010');

-- Aluguel (FKs: carro_id 1..10, cliente_id 1..10, vendedor_id 1..10, empresa_id 1..10)
INSERT INTO aluguel (data_aluguel, data_devolucao_prevista, data_devolucao_real, valor_total, carro_id, cliente_id, vendedor_id, empresa_id) VALUES ('2025-01-05', '2025-01-10', NULL, 500.00, 1, 1, 1, 1);
INSERT INTO aluguel (data_aluguel, data_devolucao_prevista, data_devolucao_real, valor_total, carro_id, cliente_id, vendedor_id, empresa_id) VALUES ('2025-01-12', '2025-01-15', '2025-01-15', 320.00, 2, 2, 2, 2);
INSERT INTO aluguel (data_aluguel, data_devolucao_prevista, data_devolucao_real, valor_total, carro_id, cliente_id, vendedor_id, empresa_id) VALUES ('2025-02-01', '2025-02-07', '2025-02-06', 780.50, 3, 3, 3, 3);
INSERT INTO aluguel (data_aluguel, data_devolucao_prevista, data_devolucao_real, valor_total, carro_id, cliente_id, vendedor_id, empresa_id) VALUES ('2025-02-10', '2025-02-14', NULL, 420.00, 4, 4, 4, 4);
INSERT INTO aluguel (data_aluguel, data_devolucao_prevista, data_devolucao_real, valor_total, carro_id, cliente_id, vendedor_id, empresa_id) VALUES ('2025-03-03', '2025-03-08', '2025-03-08', 610.00, 5, 5, 5, 5);
INSERT INTO aluguel (data_aluguel, data_devolucao_prevista, data_devolucao_real, valor_total, carro_id, cliente_id, vendedor_id, empresa_id) VALUES ('2025-03-15', '2025-03-20', NULL, 950.00, 6, 6, 6, 6);
INSERT INTO aluguel (data_aluguel, data_devolucao_prevista, data_devolucao_real, valor_total, carro_id, cliente_id, vendedor_id, empresa_id) VALUES ('2025-04-01', '2025-04-05', '2025-04-04', 350.00, 7, 7, 7, 7);
INSERT INTO aluguel (data_aluguel, data_devolucao_prevista, data_devolucao_real, valor_total, carro_id, cliente_id, vendedor_id, empresa_id) VALUES ('2025-04-18', '2025-04-22', NULL, 480.00, 8, 8, 8, 8);
INSERT INTO aluguel (data_aluguel, data_devolucao_prevista, data_devolucao_real, valor_total, carro_id, cliente_id, vendedor_id, empresa_id) VALUES ('2025-05-02', '2025-05-07', '2025-05-07', 820.00, 9, 9, 9, 9);
INSERT INTO aluguel (data_aluguel, data_devolucao_prevista, data_devolucao_real, valor_total, carro_id, cliente_id, vendedor_id, empresa_id) VALUES ('2025-05-20', '2025-05-25', NULL, 630.00, 10, 10, 10, 10);