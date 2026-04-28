# Iniciativa: MVP — Mercado Automotivo Brasil

> **Status:** em andamento desde 2026-04-27.
> **Prazo MVP:** 5 dias úteis.
> **Tag-alvo:** `v0.1.0-mvp`.

Este arquivo é o **quadro de andamento** da iniciativa. Cada PR atualiza a tabela. Use isto + `git log --oneline` + `gh pr list` para retomar trabalho entre sessões.

---

## Perguntas de negócio do MVP

1. Como cresceram as **marcas chinesas** nos últimos 5 anos (2021–2025), por **país, UF e região IBGE**?
2. Quais são as **top 10 marcas por emplacamentos** no último ano fechado (2025)?
3. Como evoluiu **historicamente (2016–2025) cada uma dessas top 10**, no Brasil e por região?

## Decisões já tomadas

| Decisão | Valor |
|---|---|
| Métrica primária | Emplacamentos (FENABRAVE/SENATRAN) — não frota |
| Frota DENATRAN | Pano de fundo apenas (já temos parquet) |
| Critério "marca chinesa" | Origem da marca (lista canônica a definir no Dia 1) |
| "Top 10" | Ranqueado por volume de emplacamentos no último ano fechado (2025) |
| Cortes geográficos | País + UF + Região IBGE (5 macro) |
| Granularidade do produto | marca + modelo + combustível (versão/motorização: out-of-scope) |
| **Plano B aprovado** | Se "modelo" não for viável em fonte aberta, cair para marca × UF × combustível |
| Período histórico | 2016-01 a 2026-03 |
| Visualização | Plotly + filtros via variáveis no topo das células |
| Testes | pytest (funções) + pandera (datasets) |
| Versionamento de dados | Snapshots datados em `FONTE/<fonte>/raw/AAAA-MM/` (sem Git-LFS, sem DVC) |
| Nice-to-have escolhido (Dia 4) | **Idade média da frota** |
| Out-of-scope formal | Versão/motorização, município para emplacamentos, forecasting, dashboard standalone, automação |

## Plano dos 5 dias (PR a PR)

### Dia 1 — Fundação técnica
- [x] PR #1 — `chore/instala-protocolo-orquestracao` — protocolo + agentes + hooks
- [x] PR #2 — `chore/setup-projeto-python` — `src/`, `tests/`, `pyproject.toml`, `requirements.txt`, smoke test, este quadro
- [x] PR #3 — `feat/lookup-uf-regiao` — tabela IBGE UF→Região + função em `src/geo.py` + pytest
- [x] PR #4 — `feat/marcas-chinesas` — lista canônica + classificador + pytest

### Dia 2 — Ingestão de emplacamentos
- [ ] PR #5 — `feat/ingestao-emplacamentos` — fonte aberta, fetcher com snapshots datados, schema pandera
- [ ] PR #6 — `feat/fato-emplacamentos` — consolidação mês × UF × marca × modelo × combustível
- [ ] PR #7 — `docs/dicionario-dados-v1` — dicionário de dados v1

### Dia 3 — Análises must-have
- [ ] PR #8 — `feat/analise-crescimento-chinesas`
- [ ] PR #9 — `feat/analise-top-10-marcas`
- [ ] PR #10 — `feat/analise-eletrificados-hibridos`

### Dia 4 — Qualidade + nice-to-have
- [ ] PR #11 — `feat/anfavea-redescoberta` ou `chore/anfavea-out-of-scope` (time-box 2h)
- [ ] PR #12 — `feat/idade-media-frota` (nice-to-have escolhido)
- [ ] PR #13 — `test/cobertura-final`

### Dia 5 — Empacotamento
- [ ] PR #14 — `docs/readme-e-sumario-executivo`
- [ ] Smoke-run completo do notebook do zero
- [ ] Tag `v0.1.0-mvp`

## Estado atual

- **Último PR mergeado:** #3 (`feat/lookup-uf-regiao`).
- **PR em andamento:** #4 (`feat/marcas-chinesas`) — classificador de marcas chinesas + `src/marcas.py` + 72 testes + invariantes de cardinalidade/grupos.
- **Próxima ação:** revisar e mergear PR #4; em seguida abrir PR #5 (`feat/ingestao-emplacamentos`).

## Open questions ativas

- **Q-A:** Qual fonte aberta cobre emplacamento por marca × modelo × UF × combustível? Investigar Base dos Dados (`br_senatran_*` ou similar) antes de cair em scraping do portal SENATRAN. Decidir no PR #5.
- **Q-B:** Resolvida no PR #4 — 15 marcas canônicas aprovadas no review; Volvo/Polestar fora (marca comercial registrada, não controle societário); SAIC/Geely apenas como valores em `GRUPOS_CHINESES`.

## Bloqueios conhecidos

- ANFAVEA: URLs `https://anfavea.com.br/docs/...` retornam 404. Endereçado no PR #11 com time-box.

## Como retomar trabalho em nova sessão (Claude)

1. Lê `MEMORY.md` (auto).
2. Lê este arquivo.
3. `gh pr list --state open` + `git log --oneline -10` para validar.
4. Confirma com o usuário em uma frase: *"Última sessão paramos em PR #X; próxima ação seria Y. Confirma?"*
