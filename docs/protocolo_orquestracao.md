# Protocolo de Orquestração de Agentes — Mercado Automotivo Brasil

> **Status:** ativo a partir de 2026-04-27.
> **Escopo:** este repositório apenas.
> **Objetivo:** padronizar o uso dos subagentes (`backend-dev`, `code-reviewer`, `doc-writer`, `test-writer`, `analista-dados`, `codex:codex-rescue`, `Plan`, `Explore`) num fluxo TDD com branches, worktrees e revisão dupla (interna + Codex).

Este projeto é um **pipeline local de análise de dados** (Python + Jupyter). Onde o protocolo genérico fala em "código de produção", leia "módulo `src/` + células do notebook orquestrador". Onde fala em "API/CLI", leia "schema de dataset processado + dicionário de dados".

---

## 0. Princípios

1. **TDD antes de tudo** — o teste (pytest da função em `src/` ou schema `pandera` do dataset) é escrito e commitado **antes** da implementação.
2. **Isolamento por padrão** — mudanças de médio/grande porte rodam em worktree + branch, nunca direto em `main`.
3. **Revisão dupla** — `code-reviewer` interno até 100% limpo, seguido de revisão externa Codex focada nos pontos sensíveis (`/revisao-codex` pelo modelo, `/codex:review` pelo humano; detalhes na §8).
4. **Documentação é obrigatória** — toda edição de código atualiza `CLAUDE.md`, `README.md`, `docs/dicionario_dados.md`, células markdown do notebook e/ou docstrings.
5. **Higiene de Git** — branches removidas só com confirmação; aborto com aviso se houver commits não-merged.
6. **Máximo 3 times paralelos** — para não virar caos de revisão.

---

## 1. Triagem (Fase 0)

Toda tarefa começa com classificação em uma das 5 categorias:

| Categoria | Critério | Trilha |
|---|---|---|
| **CONSULTA** | Pergunta, leitura, exploração. Sem alteração de arquivos. | Pula o protocolo. Responde direto. |
| **DOCS** | Só edita `.md`, células markdown do notebook, comentários. Sem lógica. | Fase 1 → 6 → 7 → 9 (pula 3/4/5/8). |
| **EDIÇÃO PEQUENA** | 1 arquivo, < 30 linhas, sem lógica nova. Branch só, **sem worktree**. | Fase 1 → 2 (branch) → 3 → 4 → 5 → 6 → 7 → 8 → 9. |
| **EDIÇÃO GRANDE** | Feature nova, múltiplos arquivos, lógica não trivial (ex.: nova fonte de dados, nova análise must-have). | Protocolo completo com **worktree**. Checkpoint humano obrigatório na Fase 1. |
| **REFATORAÇÃO** | Multi-arquivo, reestruturação arquitetural, mudança de schema, migração de formato (parquet → duckdb, etc.). | Protocolo completo com **worktree + times paralelos** quando módulos independentes. Checkpoint humano obrigatório na Fase 1. |

Se houver dúvida de classificação, **assuma a categoria mais alta** (mais cautelosa).

---

## 2. Fase 1 — Plan

- Acionar agente `Plan`.
- Saída obrigatória:
  - Arquivos afetados (caminhos absolutos).
  - Testes necessários: pytest em `tests/` e/ou schema `pandera` em `src/schemas.py` (ver Fase 3).
  - Riscos, dependências externas (BigQuery / Base dos Dados, downloads HTTP de FENABRAVE/ANFAVEA, IBGE).
  - Pontos sensíveis para a revisão externa do Codex (joins UF→Região, filtros temporais, agregações nacionais, performance em datasets grandes).
  - Se REFATORAÇÃO: mapa de paralelização (quais times independentes, até 3).
- O `analista-dados` pode ser consultado nesta fase para validar **qual corte/visualização** responde à pergunta antes de o `backend-dev` codificar.
- **Checkpoint humano obrigatório** em EDIÇÃO GRANDE e REFATORAÇÃO antes de prosseguir.
- EDIÇÃO PEQUENA e DOCS: segue direto.

---

## 3. Fase 2 — Isolamento (worktree + branch)

### 3.1 Escolha do mecanismo

| Categoria | Mecanismo |
|---|---|
| DOCS | branch direto (sem worktree) |
| EDIÇÃO PEQUENA | branch direto (sem worktree) |
| EDIÇÃO GRANDE | worktree + branch |
| REFATORAÇÃO | worktree + branch; 1 worktree por time paralelo (máx 3) |

### 3.2 Convenção de nomes de branch

Base sempre `main`. Formato `<tipo>/<slug-curto-kebab-case>`:

| Tipo | Uso |
|---|---|
| `feat/` | Nova fonte, nova análise, novo gráfico |
| `fix/` | Correção de bug (ex.: URL ANFAVEA quebrada, totais não batendo) |
| `refactor/` | Refatoração sem mudança do dataset processado |
| `docs/` | Só documentação (README, CLAUDE.md, dicionário de dados, células markdown) |
| `test/` | Adicionar/ajustar testes ou schemas pandera |
| `chore/` | Infra, tooling, configuração (`.gitignore`, settings, hooks, agentes) |

### 3.3 Worktree

- Criar via `isolation: "worktree"` ao chamar o agente que vai implementar (`backend-dev`, `test-writer`, `analista-dados` quando edita notebook).
- Um worktree é descartado automaticamente se o agente não fizer mudanças; caso contrário, o path e a branch retornam no resultado.
- Times paralelos: cada um em seu worktree, cada um em sua branch derivada de `main`.

---

## 4. Fase 3 — Red (teste falhando)

Escrever o teste **antes** da implementação. Estratégia em cascata — usar sempre o primeiro nível viável:

### Nível (a) — pytest puro contra função em `src/` (PREFERENCIAL)
- Aplicável a transformações puras: lookup UF→Região, classificação "marca chinesa", agregações, derivações de combustível.
- Teste importa o símbolo real e roda com fixture pequena (5–20 linhas) cobrindo casos reais (27 UFs, marcas de várias origens, combustíveis variados, virada de ano).
- Local: `tests/test_<modulo>.py`.
- Commitar o teste-red com `test(red): <descrição>`.

### Nível (b) — schema pandera + integração com mocks
- Para validação de dataset inteiro (schema, invariantes), use `pandera` em `src/schemas.py` aplicado ao DataFrame.
- Para fetchers que tocam rede (BigQuery, HTTP de FENABRAVE/ANFAVEA): mockar a chamada externa (`requests.get`, `bd.read_sql`) e testar parsing/cache/erro.
- Massa de teste fica em `tests/fixtures/` (XLSX/parquet pequenos versionados).

### Nível (c) — caso manual em plano de testes (ÚLTIMO RECURSO)
- Aplicável a inspeção visual de gráficos Plotly (cores, anotações, ordenação) ou validações que exigem julgamento.
- Adicionar caso numerado a `docs/plano_testes_manuais.md`.
- Requer assinatura humana na Fase 8.
- Antes de cair em (c), tentar gerar o gráfico em ambiente headless e validar dados subjacentes via pytest (assert sobre o `figure.data`).

### Commit
- Teste-red sempre commitado antes da implementação.
- Mensagem: `test(red): <escopo> — <descrição curta>`.

---

## 5. Fase 4 — Green (implementação em times paralelos)

- Agente principal: `backend-dev` para `src/` e células de código do notebook; `analista-dados` para visualizações Plotly e narrativa quando a tarefa é analítica.
- Times: se a Fase 1 identificou módulos independentes (ex.: ingestão FENABRAVE × ingestão ANFAVEA × lookup IBGE), abrir **até 3** worktrees em paralelo (chamadas `Agent` no mesmo turno).
- `doc-writer` pode rodar em paralelo quando o impacto documental é conhecido a priori.
- Objetivo: **todos os testes-red da Fase 3 ficam verdes**. Nada mais.
- Commit: `feat(scope): <descrição>`, `fix(scope): ...`, etc.

---

## 6. Fase 5 — Loop de revisão interna (até 100%)

Loop:
1. `code-reviewer` audita o diff da branch (só aponta, não edita). Devolve veredito `APROVADO` / `RESSALVAS` / `BLOQUEAR`.
2. Se houver apontamentos → `backend-dev` (ou `analista-dados`) corrige → commita → volta ao passo 1.
3. Se `code-reviewer` ficar travado ou ambíguo por **2 rodadas consecutivas** sem convergência → acionar `codex:codex-rescue` como árbitro. O resultado volta para o agente que estava implementando aplicar.
4. Só sai da Fase 5 quando `code-reviewer` reporta zero apontamentos críticos.

---

## 7. Fase 6 — Documentação

**Obrigatória sempre que houver edição de código.** Agente: `doc-writer`.

| Mudou | Atualizar |
|---|---|
| Função em `src/` | Docstring; menção em `CLAUDE.md` se afetar fluxo macro |
| Schema de dataset | `docs/dicionario_dados.md` (campo, tipo, fonte, granularidade, unidade) |
| Nova fonte de dados | `README.md` (tabela de fontes) + `CLAUDE.md` (estado conhecido) + dicionário |
| Célula de análise no notebook | Célula markdown narrativa antes do código + atualização do sumário executivo no fim |
| Configuração / agente / hook / protocolo | `CLAUDE.md` + este arquivo |

O `doc-writer` preserva o estilo PT-BR + emojis já estabelecido. Nunca documentar comportamento não verificado.

---

## 8. Fase 7 — Revisão externa via Codex (até 100%)

Agente: `codex:codex-rescue` via skill `/revisao-codex` (wrapper local) ou `/codex:review` (comando oficial do plugin).

### Como invocar

| Quem dispara | Comando | Notas |
|---|---|---|
| Modelo (auto-invocação) | `/revisao-codex --base main --scope branch` | Wrapper em `.claude/commands/revisao-codex.md` — sem `disable-model-invocation: true`, então o modelo executa via `Skill`. |
| Humano (manual) | `/codex:review --wait --base main --scope branch` | Comando oficial do plugin `openai-codex/codex`. |

Ambos executam o mesmo `codex-companion.mjs review --wait`. O wrapper descobre a versão instalada via glob em `~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs`.

### Regras de uso

- `/codex:review` e `/revisao-codex` **não aceitam focus text customizado**. Para framing adversarial, use `/codex:adversarial-review`.
- Foco da Fase 1: pontos sensíveis devem aparecer na descrição do PR ou nas mensagens de commit — o Codex lê o diff e os metadados.
- Loop: apontamentos críticos → `backend-dev` corrige → nova chamada → até zero críticos.
- Após **3 iterações** sem convergir → pausar e pedir decisão humana.
- Retorno do Codex vem em inglês — traduzir antes de apresentar ao usuário.

### Timeout operacional

**Regra de orçamento:**

- `orçamento = 3 × (tempo do code-reviewer interno da mesma task)`.
- Piso de 5 min, teto de 15 min.

**Execução:**

- Chamada Codex **sempre** com `run_in_background: true`.
- Logo após o disparo, programar `ScheduleWakeup` com o timeout calculado.

**Quando o timeout estoura,** oferecer ao usuário:
- **(a)** Aguardar mais N minutos.
- **(b)** Abortar a Fase 7 e seguir para a Fase 8 com nota "revisão externa pendente" no PR.
- **(c)** Relançar com escopo reduzido (só os arquivos de maior risco).

**Nunca aguardar indefinidamente.** O Codex é segunda opinião, não gate absoluto.

### Template de prompt

```
Contexto: <link ao PR/branch>.
Foco da revisão: <pontos sensíveis da Fase 1 — ex.: join UF→Região, agregação por mês, schema pandera>.
Orçamento de tempo: responda em até <X> minutos — o code-reviewer interno levou <Y>.
Arquivos mudados: <lista>.
Teste-red da Fase 3: <caminho>.
Aponte apenas problemas com impacto real (correctness, performance em datasets de 31M+ linhas, qualidade dos dados).
Ignore estilo que já passou no code-reviewer interno.
```

---

## 9. Fase 8 — Validação automática final

- Rodar `pytest` completo + validações `pandera` em todos os datasets processados, do zero, após a última mudança aceita pela Fase 7.
- Se for tarefa que tocou no notebook, executar smoke-run: `jupyter nbconvert --to notebook --execute coleta_dados_automotivos.ipynb --inplace --ExecutePreprocessor.timeout=600`.
- Se algum teste falhar → volta para Fase 5.
- Se todos passam → segue para Fase 9.
- Para casos de Nível (c): registrar no PR que a validação manual está pendente; pedir assinatura humana antes do merge.

---

## 10. Fase 9 — PR, Merge e higiene

### 10.1 PR
- Sempre abrir via `gh pr create`.
- Título < 70 chars. Corpo com:
  - Summary (1–3 bullets).
  - Link para testes.
  - Pontos revisados pelo Codex.
  - Test plan (checklist).

### 10.2 Merge
- Aguardar **"ok merge" explícito** do usuário.
- Após o ok: `gh pr merge <num> --squash` (ou `--merge` se o histórico da branch for relevante — decidir no plano).
- Nunca `--force`. Nunca `--admin` sem pedido explícito.

### 10.3 Higiene pós-merge
- **Sempre pedir confirmação antes de deletar branch.**
- Antes de deletar:
  ```
  git log <branch> --not main
  ```
  - Se retornar commits → **abortar** e avisar (há trabalho não-merged).
  - Se vazio → deletar local (`git branch -d`) e remota (`git push origin --delete <branch>`).
- Remover worktree associado: `git worktree remove <path>`.
- Confirmar com `git worktree list` e `git branch -a`.

---

## 11. Fallback e escalonamento

- `codex:codex-rescue` faz parte do fluxo normal (Fase 5 passo 3 e Fase 7), **não apenas** último recurso.
- Se o Codex também não resolver após 3 iterações em qualquer fase → **pausa e pede decisão humana**.
- Reportar imediatamente: erro de auth do remote, falha no smoke-run do notebook, schema pandera quebrando em massa, BigQuery sem credencial.

---

## 12. Gatilho automático

O protocolo é consultado **antes de toda tarefa** via:

1. **Base (sempre ativa):** este arquivo referenciado em `CLAUDE.md` + entrada em `memory/project_protocolo_orquestracao.md` (loaded via `MEMORY.md`).
2. **Reforço automatizado:** dois hooks em `.claude/settings.json`:
   - **Camada 1 — `UserPromptSubmit`** → `.claude/hooks/protocolo_gate.sh`: injeta o gate de triagem (CONSULTA / DOCS / EDIÇÃO PEQUENA / EDIÇÃO GRANDE / REFATORAÇÃO + justificativa + trilha) no início de cada turno.
   - **Camada 2 — `PreToolUse` (matcher `Write|Edit|NotebookEdit`)** → `.claude/hooks/bloqueia_edicao_main.sh`: bloqueia com `exit 2` qualquer edição quando a branch corrente é `main`, forçando a Fase 2 antes de qualquer escrita.

   **Caveat:** os hooks só entram em vigor após `/hooks` ou reinício da sessão quando `settings.json` é criado com a sessão já ativa. Em novos clones, executar `/hooks` uma vez após o primeiro `claude` na pasta do repo.

---

## 13. Resumo executivo (fluxograma)

```
[Prompt]
   │
   ▼
 Fase 0 — Triagem ──► CONSULTA? → responde direto (fim)
   │
   ▼
 Fase 1 — Plan
   │   └─ Checkpoint humano se GRANDE/REFATORAÇÃO
   ▼
 Fase 2 — Branch (+worktree se GRANDE/REFATORAÇÃO)
   │
   ▼
 Fase 3 — Teste-red (a→b→c) e commit
   │
   ▼
 Fase 4 — Green (times paralelos, até 3)
   │
   ▼
 Fase 5 — code-reviewer loop até 100%  ──► trava 2x → codex:rescue → volta
   │
   ▼
 Fase 6 — Documentação (obrigatória)
   │
   ▼
 Fase 7 — /revisao-codex focado ──► loop até 100% (ou timeout → opções a/b/c; ver §8)
   │
   ▼
 Fase 8 — pytest + pandera + smoke-run do notebook
   │
   ▼
 Fase 9 — PR → "ok merge" → gh pr merge → limpa branch (com confirmação) → remove worktree
   │
   ▼
 (fim)
```
