# Lysis DB API

API simples em FastAPI para expor estatísticas de processos.

## Instalação
Instale as dependências:

```bash
pip install -r requirements.txt
```

## Execução (modo desenvolvimento)
Use o task definido no `pyproject.toml`:

```bash
task dev
```

Ou execute diretamente com uvicorn:

```bash
uvicorn src.main:app --reload
```

## Endpoints principais
API v1 – Processes

`/api/v1/processes/count`
`/api/v1/processes/by-origin`
`/api/v1/processes/by-status`
`/api/v1/processes/by-matter`
`/api/v1/processes/by-group`
`/api/v1/processes/by-organization`

## Desenvolvimento
Formatação de Código
- lint:check `ruff check .`
- lint:fix `ruff check --fix`

Testes Automatizados
- Rodar testes automatizados `task test`
- Testes no modo Watch `task testWatch`

## Produção
Rodar em produção
- `task prod` executa o script `prod.py` para produção.
