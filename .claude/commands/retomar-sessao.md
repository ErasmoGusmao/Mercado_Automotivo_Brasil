---
description: Retoma trabalho do MVP em nova sessão. Lê MEMORY.md + docs/iniciativa_mvp.md, valida com gh+git, detecta drift entre quadro e remote, e apresenta a próxima ação numa frase.
argument-hint: (sem argumentos)
allowed-tools: Read, Bash
---

Use esta skill no **início de uma nova sessão** ou quando o usuário disser "continuar", "próximo PR", "vamos seguir" ou similar. Objetivo: descobrir o estado real do MVP **antes** de tomar qualquer ação, e detectar drift entre o quadro escrito e o git/remote.

## Passos obrigatórios (executar nesta ordem)

1. **Ler `docs/iniciativa_mvp.md`** — em particular as seções "Estado atual", "Plano dos 5 dias (PR a PR)", "Open questions ativas" e "Bloqueios conhecidos". `MEMORY.md` é carregado automaticamente pelo runtime do Claude Code (não precisa `Read` manual); só re-leia se as seções de project memory pedirem ponteiros adicionais.
2. **Rodar em paralelo:**
   - `gh pr list --state open` — PRs ainda abertos.
   - `git log --oneline -10` — últimos commits em `main` (ou na branch corrente).
3. **Cruzar quadro vs realidade do remote.** Procurar especificamente por:
   - **PR marcado como "em andamento"** no Estado atual mas com commit já em `main` (drift de quadro desatualizado — foi exatamente o caso do PR #4 em 2026-04-27).
   - **PR aberto no `gh pr list`** que o quadro não menciona.
   - **Checkbox `[ ]`** num PR que já mergeou (procurar por `Merge pull request #N` ou `(#N)` no `git log`).
   - **"Próxima ação"** que aponta para um PR já mergeado ou para um pré-requisito inexistente.
   - **Open question marcada como ativa** mas com decisão registrada num PR recente.
4. **Se houver drift:** liste cada divergência em bullet curto antes da pergunta final. Sugira que a primeira ação da sessão seja um PR DOCS de ressincronização do quadro.
5. **Output canônico — uma frase no final:**
   > *"Última sessão paramos em PR #X (`branch/Y`); próxima ação seria Z. Confirma?"*

   Substitua X pelo último PR realmente mergeado (validado pelo `git log`), `branch/Y` pelo nome da branch desse PR, e Z pela próxima ação **factível** dado o estado atual (não apenas o que o quadro diz).

## Não fazer

- **Não criar branch, não rodar testes, não invocar subagentes** antes da confirmação humana. Esta skill é puramente de leitura + alinhamento.
- **Não rodar comandos git/gh que mudem estado** — proibido `git commit`, `git push`, `git rebase`, `git checkout -b`, `gh pr merge`, `gh pr create`, `gh pr close`. Use apenas leitura: `git log`, `git status`, `git branch --show-current`, `gh pr list`, `gh pr view`. Embora `allowed-tools` inclua `Bash` sem filtro de subcomando, esta skill é read-only por contrato.
- **Não corrigir o quadro silenciosamente** — sempre reporte o drift ao usuário e proponha um PR explícito de ressincronização (DOCS).
- **Não confiar na memória sozinha** quando ela cita PR/arquivo/flag específico — verifique no `git log` ou `gh pr view`. A memória é frozen-in-time; o git é a verdade do momento.

## Comandos prontos

```bash
# Estado do remote (PRs abertos + últimos 10 commits em qualquer branch)
gh pr list --state open
git log --oneline -10

# Branch corrente (deveria ser main na retomada)
git branch --show-current

# Verifica rapidamente se um PR específico está mergeado
gh pr view <numero> --json state,mergedAt
```

## Exemplo de saída esperada (com drift detectado)

> Drift detectado entre o quadro e o remote:
> - O quadro diz "PR #4 em andamento" mas o commit `0d550a3 feat(marcas): ... (#4)` já está em `main`.
> - "Próxima ação" do quadro aponta para mergear o PR #4, mas isso já aconteceu.
>
> Última sessão paramos em PR #4 (`feat/marcas-chinesas`); próxima ação seria abrir PR #5 (`feat/ingestao-emplacamentos`) **após** um pequeno PR de DOCS para ressincronizar o quadro. Confirma?

## Exemplo de saída esperada (sem drift)

> Última sessão paramos em PR #4 (`feat/marcas-chinesas`); próxima ação seria abrir PR #5 (`feat/ingestao-anfavea`), conforme Dia 2 do plano. Confirma?
