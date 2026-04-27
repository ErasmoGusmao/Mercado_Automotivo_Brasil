# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Protocolo de Orquestração (LEIA ANTES DE QUALQUER AÇÃO)

Este repositório opera sob o protocolo TDD + revisão dupla descrito em [`docs/protocolo_orquestracao.md`](docs/protocolo_orquestracao.md). Regras-chave:

1. **Triagem obrigatória** — toda tarefa começa classificada em CONSULTA / DOCS / EDIÇÃO PEQUENA / EDIÇÃO GRANDE / REFATORAÇÃO. O hook `UserPromptSubmit` injeta o gate em todo turno.
2. **Nunca editar em `main`** — o hook `PreToolUse` bloqueia `Write|Edit|NotebookEdit` quando a branch corrente é `main`. Crie branch antes (Fase 2).
3. **TDD real** — teste-red commitado **antes** da implementação (`tests/test_*.py` com pytest, schema `pandera` em `src/schemas.py`).
4. **Revisão dupla** — `code-reviewer` interno até 100% limpo, depois `/revisao-codex` para os pontos sensíveis.
5. **Worktree** em EDIÇÃO GRANDE / REFATORAÇÃO; até 3 times paralelos.
6. **Documentação obrigatória** após qualquer mudança de código.
7. **Higiene de Git** — branches só são deletadas com confirmação humana e após verificar `git log <branch> --not main` vazio.

Subagentes ativos: `backend-dev`, `code-reviewer`, `doc-writer`, `test-writer`, `analista-dados` (em `.claude/agents/`).

## Visão geral

Projeto de análise do mercado automotivo brasileiro. Não é uma aplicação — é um pipeline de coleta e consolidação de dados públicos executado em notebooks Jupyter. Não há git, testes, lint, build ou CI configurados.

## Ambiente

- Python via venv local em `.venv_AUTOMOVEL_BR/` (Windows; ativar com `.venv_AUTOMOVEL_BR\Scripts\activate`).
- Dependências instaladas ad-hoc dentro dos notebooks. Pacotes usados: `basedosdados`, `pandas`, `requests`, `openpyxl`, `tqdm`. Não existe `requirements.txt` — ao adicionar libs, instalar no venv ativo e mencionar para o usuário.
- Acesso ao BigQuery via `basedosdados` requer credencial GCP autenticada e o billing project `pequisa-automovel-bd` (definido em `BILLING_ID` no notebook). O nome contém um typo histórico ("pequisa" em vez de "pesquisa") — não "corrigir" sem confirmar com o usuário.

## Notebooks

- `coleta_dados_automotivos.ipynb` — pipeline principal. Coleta DENATRAN (BigQuery via Base dos Dados) e ANFAVEA (download HTTP de XLSX) e grava em `FONTE/`.
- `pesquisa_auto_Brasil.ipynb` — scratch antigo da query DENATRAN; superado pelo notebook de coleta.

Para rodar célula a célula sem abrir o Jupyter: `jupyter nbconvert --to notebook --execute coleta_dados_automotivos.ipynb --inplace`.

## Layout de dados

```
FONTE/
├── DENATRAN/{raw,processed}/     # frota mensal por município × tipo de veículo
└── ANFAVEA/{raw,processed}/      # produção/emplacamento por marca
```

Convenção load-uma-vez: `raw/` é o cache imutável da fonte (parquet do BigQuery, XLSX original da ANFAVEA); `processed/` é derivado e descartável. O notebook detecta o cache em `raw/` e pula o download — para forçar re-fetch, apague o arquivo em `raw/` (não o `processed/`). O CSV DENATRAN consolidado tem ~1,4 GB e ~31M linhas; evite carregá-lo inteiro em memória sem necessidade.

## Coleta ANFAVEA (estado conhecido)

Os URLs `https://anfavea.com.br/docs/{siteautoveiculos,emplacamentos_nacionais,emplacamentos_importados}_{ANO}.xlsx` retornam 404 para todos os anos 2012–2026 quando testados (vide log no notebook). O padrão de URL precisa ser redescoberto inspecionando https://anfavea.com.br/site/edicoes-em-excel/. Ao mexer nessa célula, **não silenciar a falha** — o notebook explicitamente marca `ok=False` para que o usuário veja o que faltou.

## Convenções de código

- Mensagens de output e comentários em português, frequentemente com emojis (`✅`, `⬇️`, `⚠️`). Mantenha esse estilo ao editar células — não troque para inglês nem remova emojis existentes.
- Caminhos via `pathlib.Path` relativos a `BASE_DIR = Path("FONTE")`. CSVs salvos com `encoding="utf-8-sig"` (compatibilidade Excel/BR).
