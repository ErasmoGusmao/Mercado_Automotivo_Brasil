#!/usr/bin/env bash
# UserPromptSubmit hook — injeta o gate de triagem do protocolo no início de cada turno.
# Documentado em docs/protocolo_orquestracao.md (§12).
set -euo pipefail

cat <<'EOF'
[PROTOCOLO DE ORQUESTRAÇÃO — GATE OBRIGATÓRIO]

Antes de qualquer ação, classifique a tarefa nesta resposta:

  • CATEGORIA: [CONSULTA | DOCS | EDIÇÃO PEQUENA | EDIÇÃO GRANDE | REFATORAÇÃO]
  • JUSTIFICATIVA: 1 frase explicando por que essa categoria.
  • TRILHA: liste as fases que serão executadas.

Regras:
  - CONSULTA pula o protocolo (responde direto).
  - DOCS percorre Fase 1 → 6 → 7 → 9.
  - EDIÇÃO PEQUENA usa branch sem worktree.
  - EDIÇÃO GRANDE / REFATORAÇÃO exigem worktree e checkpoint humano após Fase 1.
  - Em dúvida, escolha a categoria mais alta.

Hook: PreToolUse bloqueia Write|Edit|NotebookEdit em branch=main. Crie branch antes (Fase 2).

Detalhes completos: docs/protocolo_orquestracao.md
EOF
