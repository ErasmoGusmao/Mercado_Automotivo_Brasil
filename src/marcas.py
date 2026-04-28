"""Classificador de marcas chinesas para o pipeline de emplacamentos DENATRAN/SENATRAN.

Fornece o conjunto canônico `MARCAS_CHINESAS` (15 entradas), o dicionário
`GRUPOS_CHINESES` (marca -> grupo controlador), o dicionário `ALIASES_MARCAS`
(variações de grafia -> forma canônica) e as funções `normalizar_marca`,
`e_marca_chinesa`, `grupo_chines` e `adicionar_chinesa`, usadas nas etapas
de comparação chinesas vs. demais no DataFrame de emplacamentos do MVP.

Nota de escopo: Volvo e Polestar são classificadas como não-chinesas, pois o
classificador reflete a marca comercial registrada no DENATRAN/SENATRAN, não
a cadeia de controle societário. Rever se a base passar a registrá-las como
subsidiárias Geely. Os grupos controladores SAIC e Geely figuram apenas como
valores em `GRUPOS_CHINESES` — não vendem sob esse nome no Brasil.
"""

from __future__ import annotations

import pandas as pd

# Agrupamento por grupo controlador facilita auditoria visual e gera
# MARCAS_CHINESAS e GRUPOS_CHINESES por comprehension, sem repetição.
_GRUPOS: list[tuple[str, list[str]]] = [
    ("BYD",      ["BYD"]),
    ("CHERY",    ["CHERY", "OMODA", "JAECOO"]),
    ("GWM",      ["GWM", "HAVAL"]),
    ("JAC",      ["JAC"]),
    ("LIFAN",    ["LIFAN"]),
    ("GEELY",    ["GEELY"]),
    ("FOTON",    ["FOTON"]),
    ("CHANGAN",  ["CHANGAN"]),
    ("DONGFENG", ["DONGFENG", "DFSK"]),
    ("SAIC",     ["MAXUS", "MG"]),
]

MARCAS_CHINESAS: frozenset[str] = frozenset(
    marca
    for _grupo, marcas in _GRUPOS
    for marca in marcas
)

GRUPOS_CHINESES: dict[str, str] = {
    marca: grupo
    for grupo, marcas in _GRUPOS
    for marca in marcas
}

ALIASES_MARCAS: dict[str, str] = {
    "CAOA CHERY":        "CHERY",
    "CAOA-CHERY":        "CHERY",
    "GREAT WALL":        "GWM",
    "GREAT WALL MOTORS": "GWM",
}


def normalizar_marca(marca: str) -> str:
    """Normaliza a string de marca: strip().upper() e resolução de alias.

    Levanta TypeError se o argumento não for string.
    Retorna a forma canônica (alias resolvido) ou a string normalizada.
    """
    if not isinstance(marca, str):
        raise TypeError(
            f"Esperada string para 'marca', recebido {type(marca).__name__!r}."
        )
    normalizado = marca.strip().upper()
    return ALIASES_MARCAS.get(normalizado, normalizado)


def e_marca_chinesa(marca: str) -> bool:
    """Retorna True se a marca (normalizada) pertence ao conjunto canônico chinês.

    Levanta TypeError se o argumento não for string.
    """
    return normalizar_marca(marca) in MARCAS_CHINESAS


def grupo_chines(marca: str) -> str | None:
    """Retorna o grupo controlador chinês da marca, ou None se não for chinesa.

    Levanta TypeError se o argumento não for string.
    """
    canonica = normalizar_marca(marca)
    return GRUPOS_CHINESES.get(canonica)


def adicionar_chinesa(df: pd.DataFrame, col_marca: str = "marca") -> pd.DataFrame:
    """Retorna novo DataFrame com coluna booleana 'marca_chinesa'.

    Não modifica o DataFrame original. Preserva ordem e índice.
    """
    return df.assign(marca_chinesa=df[col_marca].apply(e_marca_chinesa))
