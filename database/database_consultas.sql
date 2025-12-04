-- 1) Consulta retornando todos os dados de uma tabela (clientes)
SELECT *
FROM cliente;

-- 2) Consulta usando COUNT() com GROUP BY (quantidade de aluguéis por cliente)
SELECT c.nome AS cliente, COUNT(a.id) AS quantidade_alugueis
FROM cliente c
LEFT JOIN aluguel a ON a.cliente_id = c.id
GROUP BY c.id, c.nome
ORDER BY quantidade_alugueis DESC;

-- 3) Consulta usando AVG() (média de faturamento por aluguel)
SELECT AVG(valor_total) AS media_faturamento_aluguel
FROM aluguel;

-- 4) Consulta usando AVG() (média de carros por empresa)
SELECT AVG(total_carros) AS media_carros_por_empresa
FROM (
    SELECT e.id, e.nome, COUNT(c.id) AS total_carros
    FROM empresa e
    LEFT JOIN carro c ON c.empresa_id = e.id
    GROUP BY e.id, e.nome
) AS carros_empresa;

-- 5) Consulta usando JOIN (alugueis com cliente e carro)
SELECT a.id AS aluguel_id,
	   c.nome AS cliente,
	   ca.modelo AS modelo_carro,
	   ca.marca AS marca_carro,
	   a.data_aluguel,
	   a.data_devolucao_prevista,
	   a.data_devolucao_real,
	   a.valor_total
FROM aluguel a
JOIN cliente c ON c.id = a.cliente_id
JOIN carro ca ON ca.id = a.carro_id
ORDER BY a.data_aluguel DESC;

-- 6) Consulta usando JOIN (alugueis com vendedor e empresa)
SELECT a.id AS aluguel_id,
	   v.nome AS vendedor,
	   e.nome AS empresa,
	   a.valor_total,
	   a.data_aluguel
FROM aluguel a
JOIN vendedor v ON v.id = a.vendedor_id
JOIN empresa e ON e.id = a.empresa_id
ORDER BY a.valor_total DESC;
