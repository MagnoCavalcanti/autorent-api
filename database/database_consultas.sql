-- 1) Consulta retornando todos os dados de uma tabela (clientes)
SELECT *
FROM cliente;

-- 2) Consulta usando COUNT() com GROUP BY (quantidade de carros por status)
SELECT status, COUNT(*) AS quantidade
FROM carro
GROUP BY status
ORDER BY quantidade DESC;

-- 3) Consulta usando AVG() (média de ano dos carros)
SELECT AVG(ano) AS media_ano_carros
FROM carro;

-- 4) Consulta usando AVG() (média de valor dos aluguéis por empresa)
SELECT e.nome AS empresa, AVG(a.valor_total) AS media_valor_alugueis
FROM aluguel a
JOIN empresa e ON e.id = a.empresa_id
GROUP BY e.nome
ORDER BY media_valor_alugueis DESC;

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
