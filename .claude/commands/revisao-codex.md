---
description: Wrapper local do /codex:review. Executa codex-companion.mjs review --wait. Pode ser auto-invocado pelo modelo via Skill na Fase 7 do protocolo.
argument-hint: [--base <branch>] [--scope branch|staged|working]
allowed-tools: Bash
---

Execute revisão externa via Codex CLI sobre o diff da branch corrente.

```bash
# Descobre o caminho da versão instalada do plugin codex
COMPANION=$(ls ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs 2>/dev/null | sort -V | tail -1)

if [ -z "$COMPANION" ]; then
  echo "[revisao-codex] codex-companion.mjs não encontrado." >&2
  echo "Verifique se o plugin openai-codex/codex está instalado em ~/.claude/plugins/cache/." >&2
  exit 1
fi

# Args default: --wait, --base main, --scope branch.
ARGS=$(echo "$ARGUMENTS" | xargs)
if [ -z "$ARGS" ]; then
  ARGS="--base main --scope branch"
fi

node "$COMPANION" review --wait $ARGS
```

**Notas operacionais (do protocolo §8):**

- O retorno vem em inglês — traduza antes de apresentar ao usuário.
- Sem suporte a focus text customizado. Para framing adversarial, use `/codex:adversarial-review`.
- Os "pontos sensíveis" da Fase 1 devem estar na descrição do PR ou nas mensagens de commit — o Codex lê o diff e os metadados.
- Aplicar timeout: `orçamento = 3 × tempo_code_reviewer_interno`, com piso 5 min e teto 15 min.
- A chamada deve ser feita com `run_in_background: true` e acompanhada de `ScheduleWakeup` no orçamento calculado.
