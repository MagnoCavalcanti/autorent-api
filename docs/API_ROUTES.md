# Documentação de Rotas - autorent-api

Esta documentação descreve os endpoints expostos pelo projeto `autorent-api`, incluindo os bodies esperados, respostas típicas e permissões.

## Autenticação

### POST /api/v1/auth/login/

- Permissão: `AllowAny`
- Body esperado:
```json
{
  "username": "joao",
  "password": "senha123"
}
```
- Resposta esperada (200):
```json
{
  "refresh": "<token_refresh>",
  "access": "<token_access>"
}
```

### POST /api/v1/auth/token/refresh/

- Permissão: `AllowAny`
- Body esperado:
```json
{
  "refresh": "<token_refresh>"
}
```
- Resposta esperada (200):
```json
{
  "access": "<novo_token_access>"
}
```

### POST /api/v1/auth/registro/

- Permissão: `AllowAny`
- Body esperado:
```json
{
  "username": "joao",
  "password": "senha123",
  "nome_empresa": "AutoRent Brasil"
}
```
- Resposta esperada (201):
```json
{
  "message": "Usuário criado com sucesso!",
  "usuario": {
    "username": "joao",
    "email": ""
  }
}
```
- Observação: o serializer atual registra apenas `username`, `password` e `nome_empresa`. O campo `email` não é aceito no corpo de requisição.

## Rotas de Empresa

### GET /api/v1/empresas/

- Permissão: `AllowAny`
- Retorna lista de empresas.
- Exemplo de resposta (200):
```json
[
  {
    "nome": "AutoRent Brasil",
    "cep": "01234-567",
    "telefone": "(11) 99999-9999",
    "email": "contato@autorent.com",
    "cnpj": "12.345.678/0001-90"
  }
]
```

### POST /api/v1/empresas/

- Permissão: `AllowAny`
- Body esperado:
```json
{
  "nome": "AutoRent Brasil",
  "cep": "01234-567",
  "telefone": "(11) 99999-9999",
  "email": "contato@autorent.com",
  "cnpj": "12.345.678/0001-90"
}
```

### GET /api/v1/empresas/{id}/

- Permissão: `AllowAny`
- Retorna dados da empresa.

### PUT /api/v1/empresas/{id}/
### PATCH /api/v1/empresas/{id}/
### DELETE /api/v1/empresas/{id}/

- Permissão: `AllowAny`
- Atualiza ou exclui a empresa especificada.

## Rotas de Clientes

- Permissão: `IsAuthenticated`
- Todos os endpoints abaixo exigem cabeçalho `Authorization: Bearer <token>`.

### GET /api/v1/clientes/

- Opções de filtro:
  - `?cpf=<cpf>` - filtra clientes pelo CPF.
- Retorna lista de clientes.
- Exemplo de resposta (200):
```json
[
  {
    "nome": "Maria Silva",
    "cpf": "123.456.789-00",
    "email": "maria@email.com",
    "telefone": "(11) 98888-7777",
    "cep": "01234-567"
  }
]
```

### POST /api/v1/clientes/

- Body esperado:
```json
{
  "nome": "Maria Silva",
  "cpf": "123.456.789-00",
  "email": "maria@email.com",
  "telefone": "(11) 98888-7777",
  "cep": "01234-567"
}
```

### GET /api/v1/clientes/{id}/

- Retorna cliente por ID.

### PUT /api/v1/clientes/{id}/
### PATCH /api/v1/clientes/{id}/
### DELETE /api/v1/clientes/{id}/

- Atualiza ou exclui o cliente especificado.

## Rotas de Empresa Específica

Essas rotas usam o nome da empresa na URL: `/api/v1/{empresa}/...`.
O valor `{empresa}` é buscado por `Empresa.nome` no banco.

> Exemplo: `/api/v1/AutoRent%20Brasil/carros/`

### Carros

- Permissão: `IsAuthenticated`
- Exige `Authorization: Bearer <token>`.

#### GET /api/v1/{empresa}/carros/

- Filtros opcionais:
  - `?status=disponivel`
- Retorna lista de carros da empresa.
- Exemplo de resposta (200):
```json
[
  {
    "marca": "Toyota",
    "modelo": "Corolla",
    "ano": 2024,
    "placa": "ABC-1234",
    "status": "disponivel",
    "preco_base_dia": "150.00"
  }
]
```

#### POST /api/v1/{empresa}/carros/

- Body esperado:
```json
{
  "marca": "Toyota",
  "modelo": "Corolla",
  "ano": 2024,
  "placa": "ABC-1234",
  "status": "disponivel",
  "preco_base_dia": "150.00"
}
```
- O campo `empresa` é inferido pela URL e não deve ser enviado.

#### GET /api/v1/{empresa}/carros/{id}/

- Retorna carro específico.

#### PUT /api/v1/{empresa}/carros/{id}/
### PATCH /api/v1/{empresa}/carros/{id}/

- Atualiza dados do carro.

#### DELETE /api/v1/{empresa}/carros/{id}/

- Remove o carro.

### Vendedores

- Permissão: `IsAuthenticated`
- Exige `Authorization: Bearer <token>`.

#### GET /api/v1/{empresa}/vendedores/

- Retorna lista de vendedores da empresa.
- Exemplo de resposta (200):
```json
[
  {
    "nome": "João Pereira",
    "cpf": "987.654.321-00",
    "email": "joao@autorent.com",
    "telefone": "(11) 97777-6666"
  }
]
```

#### POST /api/v1/{empresa}/vendedores/

- Body esperado:
```json
{
  "nome": "João Pereira",
  "cpf": "987.654.321-00",
  "email": "joao@autorent.com",
  "telefone": "(11) 97777-6666"
}
```
- O campo `empresa` é inferido pela URL.

#### GET /api/v1/{empresa}/vendedores/{id}/

#### PUT /api/v1/{empresa}/vendedores/{id}/
### PATCH /api/v1/{empresa}/vendedores/{id}/

#### DELETE /api/v1/{empresa}/vendedores/{id}/

### Aluguéis

- Permissão: `IsAuthenticated`
- Exige `Authorization: Bearer <token>`.

#### GET /api/v1/{empresa}/alugueis/

- Retorna lista de alugueis da empresa.
- Cada item de aluguel inclui cliente aninhado.
- Exemplo de resposta (200):
```json
[
  {
    "carro": 1,
    "cliente": {
      "nome": "Maria Silva",
      "cpf": "123.456.789-00",
      "email": "maria@email.com",
      "telefone": "(11) 98888-7777",
      "cep": "01234-567"
    },
    "vendedor": 2,
    "data_aluguel": "2026-05-01",
    "data_devolucao_prevista": "2026-05-05",
    "valor_total": "600.00"
  }
]
```

#### POST /api/v1/{empresa}/alugueis/

- Body esperado:
```json
{
  "carro": 1,
  "cliente": {
    "nome": "Maria Silva",
    "cpf": "123.456.789-00",
    "email": "maria@email.com",
    "telefone": "(11) 98888-7777",
    "cep": "01234-567"
  },
  "vendedor": 2,
  "data_aluguel": "2026-05-01",
  "data_devolucao_prevista": "2026-05-05"
}
```
- `valor_total` e `empresa` são calculados / definidos pelo servidor.
- Validação adicional:
  - `carro` deve ter `status = disponivel`.
  - `data_devolucao_prevista` deve ser posterior ou igual a `data_aluguel`.

#### GET /api/v1/{empresa}/alugueis/{id}/

#### PUT /api/v1/{empresa}/alugueis/{id}/
### PATCH /api/v1/{empresa}/alugueis/{id}/

- Atualiza o registro de aluguel.

#### DELETE /api/v1/{empresa}/alugueis/{id}/

- Remove o aluguel.

## Documentação de esquema automática

O projeto também expõe documentação automática via drf-spectacular:

- `/api/schema/`
- `/api/schema/swagger-ui/`
- `/api/schema/redoc/`
