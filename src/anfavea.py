"""Fetcher dos XLSX anuais da ANFAVEA com snapshots datados.

`URL_TEMPLATE` é o padrão confirmado em 2026-04-27 — substitui o antigo
`emplacamentos_nacionais_{ANO}.xlsx`/`emplacamentos_importados_{ANO}.xlsx` que
retornava 404. `ANOS_COBERTURA` é o range fixo do MVP (2016-2026 inclusive).
`Resultado` é uma dataclass com `ok`/`erro` explícitos: o fetcher nunca levanta
exceção e nunca silencia falhas — quem chama precisa olhar `Resultado.ok`.

Decisões consolidadas (ver `docs/iniciativa_mvp.md`, PR #11):
- Apenas fetcher. Parser do XLSX (abas III combustível e IV marca/empresa)
  é responsabilidade do PR #5 (`feat/ingestao-anfavea`).
- `baixar_anfavea` retorna `Resultado(ok=False)` para qualquer erro de rede ou
  HTTP; `baixar_todos` agrega tudo num dict (parcial-com-warning, nunca aborta).
- Cache load-uma-vez via `FONTE/ANFAVEA/raw/{mes_coleta}/siteautoveiculos{ano}.xlsx`:
  se o arquivo já existe no destino, não refaz a requisição HTTP.
- User-Agent identifica o projeto (cortesia + reduz risco de bloqueio).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import requests

URL_TEMPLATE = "https://anfavea.com.br/docs/siteautoveiculos{ano}.xlsx"
ANOS_COBERTURA = range(2016, 2027)

_USER_AGENT = (
    "mercado-automotivo-brasil/0.1 "
    "(+https://github.com/ErasmoGusmao/Mercado_Automotivo_Brasil)"
)
_TIMEOUT_SEGUNDOS = 30


@dataclass
class Resultado:
    """Resultado de uma tentativa de baixar o XLSX da ANFAVEA para um ano.

    Em sucesso: ok=True, caminho=Path do snapshot, erro=None.
    Em falha:   ok=False, caminho=None, erro=mensagem (str).
    """

    ano: int
    ok: bool
    caminho: Path | None
    erro: str | None


def url_anfavea(ano: int) -> str:
    """Formata a URL do XLSX da ANFAVEA para o ano informado.

    Não valida o ano: é responsabilidade do caller decidir se está dentro de
    `ANOS_COBERTURA`.
    """
    return URL_TEMPLATE.format(ano=ano)


def _caminho_destino(destino_base: Path, mes_coleta: str, ano: int) -> Path:
    """Caminho do snapshot datado para um ano.

    Convenção do MVP: `FONTE/ANFAVEA/raw/{mes_coleta}/siteautoveiculos{ano}.xlsx`,
    onde `mes_coleta` é `AAAA-MM` (ex.: `2026-04`).
    """
    return (
        Path(destino_base)
        / "ANFAVEA"
        / "raw"
        / mes_coleta
        / f"siteautoveiculos{ano}.xlsx"
    )


def baixar_anfavea(
    ano: int,
    destino_base: Path,
    mes_coleta: str,
) -> Resultado:
    """Baixa o XLSX da ANFAVEA para um ano e grava em snapshot datado.

    Idempotente: se o arquivo já existe no caminho de destino, retorna
    `Resultado(ok=True)` sem refazer o download (cache load-uma-vez).

    Nunca levanta exceção — qualquer erro de rede ou HTTP é convertido em
    `Resultado(ok=False)` com a mensagem original em `erro`. Em falha, nenhum
    arquivo é gravado no destino.
    """
    destino = _caminho_destino(destino_base, mes_coleta, ano)

    if destino.exists():
        return Resultado(ano=ano, ok=True, caminho=destino, erro=None)

    url = url_anfavea(ano)
    headers = {"User-Agent": _USER_AGENT}

    try:
        response = requests.get(url, headers=headers, timeout=_TIMEOUT_SEGUNDOS)
        response.raise_for_status()
    except Exception as exc:  # noqa: BLE001 - intencional: qualquer erro vira ok=False
        return Resultado(ano=ano, ok=False, caminho=None, erro=str(exc))

    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(response.content)

    return Resultado(ano=ano, ok=True, caminho=destino, erro=None)


def baixar_todos(
    destino_base: Path,
    mes_coleta: str,
    anos: Iterable[int] | None = None,
) -> dict[int, Resultado]:
    """Baixa o XLSX da ANFAVEA para vários anos, com snapshot datado.

    Sem `anos`, itera `ANOS_COBERTURA` (2016-2026). Sempre retorna um dict
    completo — uma entrada `Resultado` por ano —, mesmo que algum falhe.
    Quem chama precisa filtrar por `r.ok` para identificar o que faltou.
    """
    anos_iter = list(anos) if anos is not None else list(ANOS_COBERTURA)
    return {
        ano: baixar_anfavea(
            ano=ano, destino_base=destino_base, mes_coleta=mes_coleta
        )
        for ano in anos_iter
    }
