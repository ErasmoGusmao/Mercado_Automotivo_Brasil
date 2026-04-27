#!/usr/bin/env bash
# PreToolUse hook — bloqueia Write|Edit|NotebookEdit quando branch corrente é main.
# Força a criação de branch (Fase 2 do protocolo) antes de qualquer escrita.
# Documentado em docs/protocolo_orquestracao.md (§12).
set -euo pipefail

REPO_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# Se o diretório não é repo git, não bloqueia (deixa passar).
if ! git -C "$REPO_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

current_branch="$(git -C "$REPO_DIR" branch --show-current 2>/dev/null || echo '')"

if [ "$current_branch" = "main" ]; then
  cat >&2 <<'EOF'
[PROTOCOLO] Edição bloqueada: a branch corrente é 'main'.

Antes de editar arquivos, execute a Fase 2 do protocolo:
  git checkout -b <tipo>/<slug-curto>

Tipos válidos: feat/, fix/, refactor/, docs/, test/, chore/.

Detalhes: docs/protocolo_orquestracao.md (§3)
EOF
  exit 2
fi

exit 0
