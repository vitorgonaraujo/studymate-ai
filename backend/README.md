# StudyMate AI — Backend

API de estudo com FastAPI, LangChain e ChromaDB para perguntas e respostas baseadas em PDFs.

## Comportamento

- cada navegador recebe uma sessão anônima por cookie, sem cadastro ou login;
- cada sessão pode manter no máximo 3 PDFs;
- um PDF expira após 72 horas sem ser usado no chat;
- a limpeza automática remove o arquivo, o cadastro e seus embeddings;
- sessões diferentes não conseguem listar, consultar ou excluir os documentos umas das outras;
- uploads são limitados a 20 MB e validados antes do processamento.

A sessão é vinculada ao cookie do navegador. Ao limpar os cookies, o navegador perde acesso aos documentos antigos; eles serão apagados automaticamente ao vencerem.

## Executar

Requer Python 3.12 e Poetry.

```bash
cd backend
cp .env.example .env
poetry install
poetry run uvicorn backend.main:app --reload
```

A API ficará disponível em `http://localhost:8000` e o Swagger em `http://localhost:8000/docs`.

Configure no `.env` o provedor compatível com a API da OpenAI:

```env
LLM_API_KEY=sua-chave
LLM_BASE_URL=https://endereco-do-provedor/v1
LLM_MODEL=nome-do-modelo
```

O `HF_TOKEN` é opcional para o download do modelo de embeddings.

## Endpoints

- `GET /`: health check;
- `POST /upload`: envia um PDF para a sessão;
- `GET /documents`: lista os documentos da sessão;
- `POST /chat`: faz uma pergunta usando até 3 documentos da sessão;
- `DELETE /documents`: remove documentos da sessão.

Nas chamadas feitas pelo frontend, habilite o envio de credenciais para que o cookie seja enviado (`withCredentials: true` no Angular ou `credentials: "include"` no Fetch).

## Testes

```bash
poetry run ruff check src tests
poetry run pytest
```

O armazenamento de metadados continua em JSON de propósito, para manter o projeto pequeno e didático. Para múltiplas instâncias da API, o próximo passo seria migrá-lo para PostgreSQL ou outro banco compartilhado.
