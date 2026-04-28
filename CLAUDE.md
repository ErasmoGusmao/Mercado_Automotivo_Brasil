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

## Iniciativa ativa

MVP em andamento — quadro de progresso em [`docs/iniciativa_mvp.md`](docs/iniciativa_mvp.md). Sempre consulte este arquivo ao retomar sessão para saber em que PR estamos e qual é a próxima ação.

Para retomar trabalho ao iniciar uma nova sessão (ou quando o usuário disser "continuar", "próximo PR", etc.), use o slash command `/retomar-sessao` (em [`.claude/commands/retomar-sessao.md`](.claude/commands/retomar-sessao.md)). Ele lê o quadro, valida contra `gh pr list` + `git log`, detecta drift e devolve a próxima ação numa frase para confirmação humana.

## Visão geral

Projeto de análise do mercado automotivo brasileiro. Pipeline local de coleta e consolidação de dados públicos, entregue como Jupyter notebook + módulo Python (`src/`).

- `src/geo.py` — lookup canônico UF → Grande Região IBGE (dicionário `UF_PARA_REGIAO` + funções `uf_to_regiao` e `adicionar_regiao`). É a única fonte de verdade para agregações geográficas; não replicar a tabela em outro lugar.
- `src/marcas.py` — classificador de marcas chinesas (`MARCAS_CHINESAS`, `e_marca_chinesa`, `adicionar_chinesa`, `grupo_chines`); 15 marcas canônicas + 4 aliases; Volvo/Polestar excluídas por decisão de produto (marca comercial registrada, não controle societário); SAIC figura apenas como valor controlador em `GRUPOS_CHINESES`.

## Ambiente

- Python 3.10+ via venv local em `.venv_AUTOMOVEL_BR/` (Windows; ativar com `.venv_AUTOMOVEL_BR\Scripts\activate`).
- Dependências em `requirements.txt` (instalar com `.venv_AUTOMOVEL_BR/Scripts/pip.exe install -r requirements.txt`). Metadados do pacote em `pyproject.toml`.
- Acesso ao BigQuery via `basedosdados` requer credencial GCP autenticada e o billing project `pequisa-automovel-bd` (definido em `BILLING_ID` no notebook). O nome contém um typo histórico ("pequisa" em vez de "pesquisa") — não "corrigir" sem confirmar com o usuário.
- Testes: `pytest` (config em `pyproject.toml`, testes em `tests/`). Rodar: `.venv_AUTOMOVEL_BR/Scripts/python.exe -m pytest`.

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

Padrão de URL correto (descoberto em 2026-04-27, **implementação pendente** no PR #11): `https://anfavea.com.br/docs/siteautoveiculos{ANO}.xlsx`. É um arquivo único anual com ~8 abas, incluindo a aba IV ("Emplacamento Empresa", mensal por marca/empresa) e a aba III (mensal por combustível). O padrão antigo do notebook (`emplacamentos_nacionais_{ANO}.xlsx`, `emplacamentos_importados_{ANO}.xlsx`) está obsoleto e retorna 404 — não regredir para ele. Até o PR #11 entrar, o fetcher do notebook continua quebrado; o que mudou foi apenas que a URL nova já está confirmada. Ao mexer nessa célula, **não silenciar a falha** — o notebook deve marcar `ok=False` se a URL nova também falhar, para que o usuário veja o que faltou.

A ANFAVEA agrega por **empresa**, não por marca individual (ex.: Stellantis = Fiat + Jeep + Citroën; GM cobre Chevrolet). Hoje `src/marcas.py` cobre apenas o recorte de marcas chinesas — não existe ainda mapa empresa→marca. Esse mapa será construído num módulo a definir quando o PR #5 (`feat/ingestao-anfavea`) for aberto, e é pré-requisito para responder Q2/Q3 do MVP em nível de marca individual.

## Convenções de código

- Mensagens de output e comentários em português, frequentemente com emojis (`✅`, `⬇️`, `⚠️`). Mantenha esse estilo ao editar células — não troque para inglês nem remova emojis existentes.
- Caminhos via `pathlib.Path` relativos a `BASE_DIR = Path("FONTE")`. CSVs salvos com `encoding="utf-8-sig"` (compatibilidade Excel/BR).
