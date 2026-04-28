# Iniciativa: MVP — Mercado Automotivo Brasil

> **Status:** em andamento desde 2026-04-27.
> **Prazo MVP:** 5 dias úteis.
> **Tag-alvo:** `v0.1.0-mvp`.

Este arquivo é o **quadro de andamento** da iniciativa. Cada PR atualiza a tabela. Use isto + `git log --oneline` + `gh pr list` para retomar trabalho entre sessões.

---

## Perguntas de negócio do MVP

1. Como cresceram as **marcas chinesas** nos últimos 5 anos (2021–2025), no **Brasil (total) e por combustível**?
2. Quais são as **top 10 marcas por emplacamentos** no último ano fechado (2025), no Brasil?
3. Como evoluiu **historicamente (2016–2025) cada uma dessas top 10**, no Brasil (total e por combustível)?

> **Reescopo de 2026-04-27 (Q-A resolvida — Plano C):** o corte por UF/Região IBGE foi removido do MVP porque nenhuma fonte aberta confirmada entrega emplacamentos novos com marca × UF juntos (FENABRAVE só publica em PDF/flipbook; ANFAVEA não tem UF; RENAVAM-diff é proxy de risco). Cortes geográficos só serão exibidos via **frota DENATRAN como proxy declarado**, marcado como nice-to-have e nunca apresentado como "emplacamentos por UF".

## Decisões já tomadas

| Decisão | Valor |
|---|---|
| Métrica primária | Emplacamentos (ANFAVEA) — não frota |
| Fonte primária de emplacamentos | **ANFAVEA `siteautoveiculos{ANO}.xlsx`** — aba IV (marca/empresa) + aba III (combustível); mensal; cobertura 2016-2026-03; URL confirmada em 2026-04-27 |
| Frota DENATRAN | Pano de fundo apenas (já temos parquet); proxy declarado se houver corte regional como nice-to-have |
| Critério "marca chinesa" | Origem da marca (lista canônica em `src/marcas.py`) |
| "Top 10" | Ranqueado por volume de emplacamentos no último ano fechado (2025) |
| Cortes geográficos | **País (Brasil)** apenas — UF/Região IBGE retirados do MVP (Plano C) |
| Granularidade do produto | **marca + combustível** (modelo, versão, motorização: out-of-scope no MVP por indisponibilidade em fonte aberta) |
| Plano B (histórico — não usado) | "Marca × UF × combustível" descartado: marca+UF não disponíveis em fonte aberta sem proxy RENAVAM-diff (risco metodológico) |
| **Plano C aprovado em 2026-04-27** | Brasil × marca × combustível via ANFAVEA. Sem UF/modelo. Para corte regional eventual: frota DENATRAN como proxy explicitamente declarado |
| Período histórico | 2016-01 a 2026-03 |
| Visualização | Plotly + filtros via variáveis no topo das células |
| Testes | pytest (funções) + pandera (datasets) |
| Versionamento de dados | Snapshots datados em `FONTE/<fonte>/raw/AAAA-MM/` (sem Git-LFS, sem DVC) |
| Nice-to-have escolhido (Dia 4) | **Idade média da frota** |
| Out-of-scope formal | Modelo, UF e Região IBGE para emplacamentos; versão/motorização; município; forecasting; dashboard standalone; automação |

## Plano dos 5 dias (PR a PR)

> **Nota sobre numeração:** `PR #N` aqui é a numeração **lógica** do MVP (atribuída quando o quadro foi escrito) e **não corresponde** ao número sequencial do PR no GitHub. Por exemplo, este reescopo é o sexto PR do GitHub mas se refere ao "PR #5" do quadro — que foi reordenado e renomeado abaixo. Para localizar um PR no GitHub, use o nome da branch (`feat/...`, `docs/...`), não o número.

### Dia 1 — Fundação técnica
- [x] PR #1 — `chore/instala-protocolo-orquestracao` — protocolo + agentes + hooks
- [x] PR #2 — `chore/setup-projeto-python` — `src/`, `tests/`, `pyproject.toml`, `requirements.txt`, smoke test, este quadro
- [x] PR #3 — `feat/lookup-uf-regiao` — tabela IBGE UF→Região + função em `src/geo.py` + pytest
- [x] PR #4 — `feat/marcas-chinesas` — lista canônica + classificador + pytest

### Dia 2 — Ingestão de emplacamentos (reordenado em 2026-04-27)
- [ ] PR #11 — `feat/anfavea-redescoberta` — substitui o padrão de URL antigo (`emplacamentos_nacionais_{ANO}.xlsx`) pelo correto (`siteautoveiculos{ANO}.xlsx`); valida cobertura 2016-2026 e abas (IV marca, III combustível). **Movido do Dia 4 para o Dia 2 — virou pré-requisito do PR #5.**
- [ ] PR #5 — `feat/ingestao-anfavea` — fetcher + parser do XLSX ANFAVEA, snapshots datados em `FONTE/ANFAVEA/raw/AAAA-MM/`, schema pandera. (Renomeado de `feat/ingestao-emplacamentos`.)
- [ ] PR #6 — `feat/fato-emplacamentos` — consolidação **mês × marca × combustível** (Brasil). Sem UF, sem modelo. (Escopo reduzido em 2026-04-27.)
- [ ] PR #7 — `docs/dicionario-dados-v1` — dicionário de dados v1

### Dia 3 — Análises must-have
- [ ] PR #8 — `feat/analise-crescimento-chinesas` — Brasil total + por combustível
- [ ] PR #9 — `feat/analise-top-10-marcas` — Brasil
- [ ] PR #10 — `feat/analise-eletrificados-hibridos` — Brasil por combustível

### Dia 4 — Qualidade + nice-to-have
- [ ] PR #12 — `feat/idade-media-frota` (nice-to-have escolhido)
- [ ] PR #13 — `test/cobertura-final`
- [ ] (Liberado pela antecipação do PR #11) — folga para imprevistos ou para um corte regional **opcional via frota DENATRAN como proxy declarado**, se o tempo permitir

### Dia 5 — Empacotamento
- [ ] PR #14 — `docs/readme-e-sumario-executivo`
- [ ] Smoke-run completo do notebook do zero
- [ ] Tag `v0.1.0-mvp`

## Estado atual

- **Último PR mergeado:** #4 (`feat/marcas-chinesas`).
- **PR em andamento:** este (`docs/reescopa-mvp-anfavea-primeiro`) — reescopo do MVP após resolução da Q-A em 2026-04-27.
- **Próxima ação:** após mergear este reescopo, abrir o PR #11 (`feat/anfavea-redescoberta`), agora antecipado para o Dia 2 como pré-requisito do PR #5.

## Open questions ativas

- **Q-A:** **Decisão tomada em 2026-04-27 (implementação pendente no PR #11/PR #5).** Fonte primária escolhida = ANFAVEA `siteautoveiculos{ANO}.xlsx` (granularidade marca × combustível × mês × Brasil). Marca+UF não estão disponíveis em fonte aberta confirmada — FENABRAVE só publica em PDF/flipbook; RENAVAM-diff foi avaliado e descartado por risco metodológico (sucateamento e transferências inter-UF inflam o delta). Plano C: corte por UF/região só como nice-to-have via frota DENATRAN (estoque), explicitamente declarado como proxy.
- **Q-B:** Resolvida no PR #4 — 15 marcas canônicas aprovadas no review; Volvo/Polestar fora (marca comercial registrada, não controle societário); SAIC apenas como valor controlador em `GRUPOS_CHINESES` (Geely é marca canônica desde 2024 no Brasil).

## Bloqueios conhecidos

- ANFAVEA: URLs `https://anfavea.com.br/docs/{emplacamentos_nacionais,emplacamentos_importados}_{ANO}.xlsx` retornam 404. **URL correta descoberta em 2026-04-27** (`https://anfavea.com.br/docs/siteautoveiculos{ANO}.xlsx`), porém **o fetcher do notebook continua quebrado** até que o PR #11 (antecipado para o Dia 2) substitua o padrão antigo. Bloqueio só é fechado no merge do PR #11.

## Como retomar trabalho em nova sessão (Claude)

1. Lê `MEMORY.md` (auto).
2. Lê este arquivo.
3. `gh pr list --state open` + `git log --oneline -10` para validar.
4. Confirma com o usuário em uma frase: *"Última sessão paramos em PR #X; próxima ação seria Y. Confirma?"*
