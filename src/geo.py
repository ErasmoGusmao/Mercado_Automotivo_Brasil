"""Lookup IBGE: sigla de UF -> nome da Grande Regiao brasileira.

Fornece o dicionario `UF_PARA_REGIAO` (27 entradas) e as funcoes `uf_to_regiao`
e `adicionar_regiao`, usadas nas etapas de agregacao geografica do MVP.
"""

from __future__ import annotations

import pandas as pd

# Agrupamento por regiao facilita auditoria visual contra a tabela IBGE.
_REGIOES: list[tuple[str, list[str]]] = [
    ("Norte",       ["AC", "AP", "AM", "PA", "RO", "RR", "TO"]),
    ("Nordeste",    ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"]),
    ("Centro-Oeste",["DF", "GO", "MT", "MS"]),
    ("Sudeste",     ["ES", "MG", "RJ", "SP"]),
    ("Sul",         ["PR", "RS", "SC"]),
]

UF_PARA_REGIAO: dict[str, str] = {
    uf: regiao
    for regiao, ufs in _REGIOES
    for uf in ufs
}


def uf_to_regiao(uf: str) -> str:
    """Retorna a Grande Regiao IBGE para a sigla de UF informada.

    Normaliza o input com strip() e upper() antes da consulta. Levanta
    TypeError se o argumento nao for string e ValueError se a sigla nao
    estiver na tabela (a mensagem inclui o valor invalido recebido).
    """
    if not isinstance(uf, str):
        raise TypeError(
            f"Esperada string para 'uf', recebido {type(uf).__name__!r}."
        )
    uf_norm = uf.strip().upper()
    if uf_norm not in UF_PARA_REGIAO:
        raise ValueError(
            f"Sigla de UF desconhecida: {uf!r}. "
            f"Valores aceitos: {sorted(UF_PARA_REGIAO)}."
        )
    return UF_PARA_REGIAO[uf_norm]


def adicionar_regiao(df: pd.DataFrame, col_uf: str = "uf") -> pd.DataFrame:
    """Retorna novo DataFrame com coluna 'regiao_ibge' derivada de col_uf.

    Aplica uf_to_regiao linha a linha preservando a ordem e o indice originais.
    O DataFrame de entrada nao e modificado.
    """
    # .apply garante que erros de uf_to_regiao (TypeError/ValueError) se
    # propaguem explicitamente, ao contrario de .map que silenciaria com NaN.
    return df.assign(regiao_ibge=df[col_uf].apply(uf_to_regiao))
