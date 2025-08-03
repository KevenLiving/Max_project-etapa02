# Documentação dos Endpoints da API - ScraperML

## GET /

### Descrição:

Endpoint inicial da API, com instruções básicas de uso.

### Parâmetro:

Nenhum.

### Resposta esperada:

```json
{
  "mensagem": "API de busca Mercado Livre. Use /buscar-produtos?termo=produto&limite=15"
}
```

### Códigos de status:

- `200 OK`

---

## **POST /buscar-produtos/**

### Descrição:

Faz scraping no Mercado Livre e salva os produtos no banco de dados.

### Parâmetros de **query**:

- `termo` (string, obrigatório): termo a ser buscado.
- `limite` (int, opcional, padrão=15): número máximo de produtos a coletar.

### Exemplo de requisição:

```
POST /buscar-produtos/?termo=iphone&limite=10
```

### Resposta esperada:

```json
{
  "mensagem": "Busca por 'iphone' concluída. Produtos salvos no banco (limite: 10)."
}
```

### Códigos de status:

- `200 OK`
- `422 Unprocessable Entity` (parâmetros inválidos)

---

## **GET /produtos/**

### Descrição:

Lista todos os produtos salvos no banco de dados.

### Parâmetros de query:

- `skip` (int, padrão=0): número de registros a pular (paginação).
- `limit` (int, padrão=20): número máximo de registros a retornar.

### Resposta esperada:

```json
[
  {
    "id": 1,
    "nome": "iPhone 13 128GB",
    "preco": 3999.90,
    "link": "https://produto.mercadolivre.com.br/...",
    "avaliacao": 4.8,
    "num_avaliacao": 258,
    "busca_id": 1
  },
  ...
]
```

### Códigos de status:

- `200 OK`

---

## **GET /melhor-preco/**

### Descrição:

Lista os produtos ordenados do menor para o maior preço.

### Parâmetros:

- `limite` (int, opcional, mínimo=1, padrão=10)

### Resposta esperada:

Lista JSON com produtos mais baratos.

### Códigos de status:

- `200 OK`

---

## **GET /melhor-avaliados/**

### Descrição:

Lista os produtos com melhores avaliações e maior número de avaliações.

### Parâmetros:

- `limite` (int, opcional, mínimo=1, padrão=10)

### Resposta esperada:

Lista JSON com produtos ordenados por avaliação e número de avaliações.

### Códigos de status:

- `200 OK`

---

## **GET /buscas/**

### Descrição:

Retorna uma lista de buscas realizadas até agora.

### Parâmetros:

Nenhum.

### Resposta esperada:

```json
[
  {
    "id": 1,
    "termo": "iphone"
  },
  ...
]
```

### Códigos de status:

- `200 OK`

---

## **DELETE /limpar-banco**

### Descrição:

Remove produtos de uma busca específica, ou limpa todo o banco se o termo for `"tudo"`.

### Parâmetros de **query**:

- `termo` (string, obrigatório): termo da busca a ser removida ou `"tudo"` para apagar todos os produtos e buscas órfãs.

### Exemplo de requisição:

```
DELETE /limpar-banco?termo=iphone
DELETE /limpar-banco?termo=tudo
```

### Respostas esperadas:

**Para uma busca específica:**

```
{
  "mensagem": "15 produtos com o termo 'iphone' foram removidos."
}
```

**Caso a busca não exista:**

```
{
  "mensagem": "Nenhuma busca com o termo 'tv' foi encontrada."
}
```

**Para limpeza total:**

```
{
  "mensagem": "120 produtos removidos. 5 buscas órfãs também apagadas."
}
```

### Códigos de status:

- `200 OK`
- `422 Unprocessable Entity` (se parâmetro estiver ausente)

---

#
