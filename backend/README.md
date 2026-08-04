# StudyMate AI - Backend

Backend responsável pelo processamento de documentos PDF e execução do agente RAG.

## Tecnologias

- Python
- FastAPI
- LangChain
- ChromaDB
- Poetry
- pyenv

## Funcionalidades

- Upload de arquivos PDF
- Extração de conteúdo dos documentos
- Divisão dos documentos em chunks
- Geração de embeddings
- Armazenamento em banco vetorial
- Busca semântica
- Perguntas e respostas utilizando RAG
- Suporte para múltiplos documentos
- Exclusão de documentos

## Estrutura

```
backend/

├── src/
│   └── backend/
│       ├── agent/
│       ├── core/
│       ├── rag/
│       ├── services/
│       ├── tools/
│       └── main.py
│
├── storage/
│
├── pyproject.toml
├── poetry.lock
└── README.md
```

## Requisitos

- Python instalado
- pyenv instalado
- Poetry instalado

## Configuração do ambiente

### Instalar a versão do Python

Verificar versões disponíveis:

```bash
pyenv versions
```

Instalar uma versão:

```bash
pyenv install 3.12.13
```

Definir a versão do projeto:

```bash
pyenv local 3.12.13
```

Verificar:

```bash
python --version
```

---

## Instalação das dependências

Instalar as dependências utilizando Poetry:

```bash
poetry install
```

O Poetry irá criar e gerenciar o ambiente virtual automaticamente.

Entrar no ambiente:

```bash
poetry shell
```

ou executar comandos diretamente:

```bash
poetry run <comando>
```

---

## Configuração

Criar um arquivo `.env` na raiz do backend.

Exemplo:

```env

GROQ_API_KEY: your_api_key

CHROMA_PATH=storage/chroma
UPLOAD_PATH=storage/uploads

HF_TOKEN=your-api-key
```

---

## Executando

Com o ambiente Poetry ativo:

```bash
uvicorn backend.main:app --reload
```

ou:

```bash
poetry run uvicorn backend.main:app --reload
```

A API estará disponível em:

```
http://localhost:8000
```

Documentação Swagger:

```
http://localhost:8000/docs
```

---

## Endpoints

### Health Check

```
GET /
```

Verifica se a API está funcionando.

---

### Upload de documento

```
POST /upload
```

Recebe um arquivo PDF e realiza:

- Salvamento do arquivo
- Extração do conteúdo
- Criação dos chunks
- Geração dos embeddings
- Armazenamento no banco vetorial
- Cadastro do documento

---

### Listar documentos

```
GET /documents
```

Retorna todos os documentos cadastrados.

Exemplo:

```json
[
  {
    "document_id": "uuid",
    "filename": "documento.pdf",
    "pages": 10,
    "chunks": 30
  }
]
```

---

### Perguntar aos documentos

```
POST /chat
```

Realiza perguntas utilizando os documentos selecionados.

Exemplo:

```json
{
  "message": "Qual o assunto principal do documento?",
  "document_ids": [
    "document-id"
  ]
}
```

Fluxo:

1. Recebe a pergunta
2. Busca contexto relevante no banco vetorial
3. Recupera os trechos relacionados
4. Envia o contexto para a LLM
5. Retorna a resposta baseada nos documentos

---

### Excluir documentos

```
DELETE /documents
```

Remove um ou mais documentos.

Exemplo:

```json
{
  "document_ids": [
    "document-id-1",
    "document-id-2"
  ]
}
```

A exclusão remove:

- Cadastro do documento
- Embeddings do ChromaDB
- Arquivo PDF armazenado

---

## Status

🚧 Em desenvolvimento