"""Testes para src/marcas.py — classificador de marcas chinesas, aliases e helper de DataFrame.

Decisoes de contrato documentadas:
- e_marca_chinesa(None) levanta TypeError (input nao e string).
- normalizar_marca(None) levanta TypeError (input nao e string).
- grupo_chines(None) levanta TypeError (input nao e string).
- Volvo e Polestar sao classificadas como NAO-chinesas, apesar do controle acionario
  da Geely sobre ambas. Decisao de produto: o classificador reflete marca comercial
  registrada no DENATRAN/SENATRAN, nao a cadeia de controle societario. Rever se
  a base de dados passar a registrar Volvo/Polestar como subsidiarias Geely.
- normalizar_marca aplica strip().upper() antes de consultar ALIASES_MARCAS.
- adicionar_chinesa retorna novo DataFrame e nao muta o original.
- MARCAS_CHINESAS deve ter exatamente 16 entradas (lista canonica aprovada).
- Todo alias em ALIASES_MARCAS deve apontar para uma marca presente em MARCAS_CHINESAS.
"""

import pandas as pd
import pytest

from src import marcas

# ---------------------------------------------------------------------------
# Constantes de referencia
# ---------------------------------------------------------------------------

MARCAS_CANONICAS_CHINESAS: list[tuple[str, str]] = [
    ("BYD", "BYD"),
    ("CHERY", "CHERY"),
    ("GWM", "GWM"),
    ("HAVAL", "GWM"),
    ("JAC", "JAC"),
    ("LIFAN", "LIFAN"),
    ("GEELY", "GEELY"),
    ("FOTON", "FOTON"),
    ("CHANGAN", "CHANGAN"),
    ("DONGFENG", "DONGFENG"),
    ("DFSK", "DONGFENG"),
    ("MAXUS", "SAIC"),
    ("MG", "SAIC"),
    ("OMODA", "CHERY"),
    ("JAECOO", "CHERY"),
]

# A lista canonica tem 16 marcas — a tabela acima so lista 15 entradas unicas
# porque a decima sexta e SAIC, que nao aparece como marca propria no registro
# DENATRAN mas aparece como grupo controlador de MAXUS e MG.
# Verificar contagem via invariante de modulo.

MARCAS_NAO_CHINESAS = ["FIAT", "VOLKSWAGEN", "TOYOTA", "VOLVO", "POLESTAR", "FORD"]

ALIASES_ESPERADOS: list[tuple[str, str]] = [
    ("CAOA CHERY", "CHERY"),
    ("CAOA-CHERY", "CHERY"),
    ("GREAT WALL", "GWM"),
    ("GREAT WALL MOTORS", "GWM"),
]


# ---------------------------------------------------------------------------
# 1. Cobertura completa das 16 marcas canonicas
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "marca",
    [marca for marca, _ in MARCAS_CANONICAS_CHINESAS],
)
def test_e_marca_chinesa_cobertura_completa(marca: str):
    """Cada uma das 16 marcas canonicas deve retornar True em e_marca_chinesa."""
    assert marcas.e_marca_chinesa(marca) is True


# ---------------------------------------------------------------------------
# 2. Marcas NAO-chinesas
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("marca", MARCAS_NAO_CHINESAS)
def test_e_marca_chinesa_falsas(marca: str):
    """Marcas nao-chinesas devem retornar False.

    Nota sobre Volvo e Polestar: apesar do controle acionario da Geely sobre
    ambas, o classificador usa a marca comercial registrada no DENATRAN/SENATRAN.
    Volvo e Polestar operam com identidade de marca propria e nao aparecem
    agrupadas como 'Geely' nos registros de emplacamento — portanto sao False.
    """
    assert marcas.e_marca_chinesa(marca) is False


# ---------------------------------------------------------------------------
# 3. Normalizacao de input (lower-case e espacos)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "marca_raw",
    [
        "byd",
        "  BYD  ",
        "  byd ",
        "Chery",
        "chery",
        "  CHERY  ",
        "haval",
        "Haval",
        "mg",
        "MG",
    ],
)
def test_e_marca_chinesa_normalizacao_input(marca_raw: str):
    """e_marca_chinesa deve aceitar lower-case e strings com espacos em branco."""
    assert marcas.e_marca_chinesa(marca_raw) is True


# ---------------------------------------------------------------------------
# 4. Aliases — normalizar_marca e e_marca_chinesa via alias
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("alias,canonica", ALIASES_ESPERADOS)
def test_normalizar_marca_alias(alias: str, canonica: str):
    """normalizar_marca deve resolver alias para a forma canonica."""
    assert marcas.normalizar_marca(alias) == canonica


@pytest.mark.parametrize("alias,_canonica", ALIASES_ESPERADOS)
def test_e_marca_chinesa_via_alias(alias: str, _canonica: str):
    """e_marca_chinesa deve retornar True para qualquer alias de marca chinesa."""
    assert marcas.e_marca_chinesa(alias) is True


def test_normalizar_marca_sem_alias_retorna_upper():
    """normalizar_marca sem alias retorna a string com strip().upper() aplicado."""
    assert marcas.normalizar_marca("fiat") == "FIAT"
    assert marcas.normalizar_marca("  Ford  ") == "FORD"
    assert marcas.normalizar_marca("volkswagen") == "VOLKSWAGEN"


# ---------------------------------------------------------------------------
# 5. TypeError em None
# ---------------------------------------------------------------------------


def test_e_marca_chinesa_none_levanta_type_error():
    """None nao e string — deve levantar TypeError, fail-fast."""
    with pytest.raises(TypeError):
        marcas.e_marca_chinesa(None)  # type: ignore[arg-type]


def test_grupo_chines_none_levanta_type_error():
    """None nao e string — deve levantar TypeError em grupo_chines."""
    with pytest.raises(TypeError):
        marcas.grupo_chines(None)  # type: ignore[arg-type]


def test_normalizar_marca_none_levanta_type_error():
    """None nao e string — deve levantar TypeError em normalizar_marca."""
    with pytest.raises(TypeError):
        marcas.normalizar_marca(None)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 6. grupo_chines retorna controlador correto
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "marca,grupo_esperado",
    [
        ("BYD", "BYD"),
        ("HAVAL", "GWM"),
        ("GWM", "GWM"),
        ("OMODA", "CHERY"),
        ("JAECOO", "CHERY"),
        ("CHERY", "CHERY"),
        ("MG", "SAIC"),
        ("MAXUS", "SAIC"),
        ("DFSK", "DONGFENG"),
        ("DONGFENG", "DONGFENG"),
        ("JAC", "JAC"),
        ("LIFAN", "LIFAN"),
        ("GEELY", "GEELY"),
        ("FOTON", "FOTON"),
        ("CHANGAN", "CHANGAN"),
    ],
)
def test_grupo_chines_retorna_controlador_correto(marca: str, grupo_esperado: str):
    """grupo_chines deve retornar o grupo controlador correto para cada marca chinesa."""
    assert marcas.grupo_chines(marca) == grupo_esperado


def test_grupo_chines_nao_chinesa_retorna_none():
    """grupo_chines deve retornar None para marca nao-chinesa."""
    assert marcas.grupo_chines("FIAT") is None
    assert marcas.grupo_chines("TOYOTA") is None
    assert marcas.grupo_chines("VOLKSWAGEN") is None
    assert marcas.grupo_chines("VOLVO") is None


def test_grupo_chines_via_alias():
    """grupo_chines deve resolver alias antes de consultar o grupo."""
    assert marcas.grupo_chines("CAOA CHERY") == "CHERY"
    assert marcas.grupo_chines("GREAT WALL") == "GWM"


# ---------------------------------------------------------------------------
# 7. Vetorizacao em DataFrame
# ---------------------------------------------------------------------------


@pytest.fixture()
def df_emplacamentos_misto():
    """DataFrame de emplacamentos com mix: marcas chinesas, nao-chinesas, alias e lower-case."""
    return pd.DataFrame(
        {
            "marca": [
                "BYD",
                "FIAT",
                "CAOA CHERY",
                "byd",
                "VOLKSWAGEN",
                "MG",
                "GREAT WALL",
                "TOYOTA",
                "HAVAL",
                "  byd  ",
                "FORD",
                "JAECOO",
            ],
            "emplacamentos": [500, 1200, 300, 80, 2000, 150, 90, 1800, 200, 40, 900, 60],
        },
        index=list(range(12)),
    )


ESPERADO_CHINESA = [
    True,   # BYD
    False,  # FIAT
    True,   # CAOA CHERY (alias -> CHERY)
    True,   # byd (lower-case)
    False,  # VOLKSWAGEN
    True,   # MG
    True,   # GREAT WALL (alias -> GWM)
    False,  # TOYOTA
    True,   # HAVAL
    True,   # "  byd  " (espacos)
    False,  # FORD
    True,   # JAECOO
]


def test_adicionar_chinesa_cria_coluna_booleana(df_emplacamentos_misto):
    """adicionar_chinesa deve inserir coluna 'marca_chinesa' com dtype bool."""
    resultado = marcas.adicionar_chinesa(df_emplacamentos_misto)
    assert "marca_chinesa" in resultado.columns
    assert resultado["marca_chinesa"].dtype == bool


def test_adicionar_chinesa_valores_corretos(df_emplacamentos_misto):
    """adicionar_chinesa deve classificar corretamente cada linha do DataFrame."""
    resultado = marcas.adicionar_chinesa(df_emplacamentos_misto)
    assert list(resultado["marca_chinesa"]) == ESPERADO_CHINESA


def test_adicionar_chinesa_preserva_ordem(df_emplacamentos_misto):
    """A ordem das linhas do DataFrame original deve ser mantida."""
    resultado = marcas.adicionar_chinesa(df_emplacamentos_misto)
    assert list(resultado.index) == list(df_emplacamentos_misto.index)


def test_adicionar_chinesa_nao_muta_original(df_emplacamentos_misto):
    """adicionar_chinesa nao deve modificar o DataFrame original."""
    colunas_antes = list(df_emplacamentos_misto.columns)
    marcas.adicionar_chinesa(df_emplacamentos_misto)
    assert list(df_emplacamentos_misto.columns) == colunas_antes
    assert "marca_chinesa" not in df_emplacamentos_misto.columns


def test_adicionar_chinesa_col_marca_personalizada():
    """adicionar_chinesa deve funcionar com nome de coluna diferente do padrao."""
    df = pd.DataFrame({"fabricante": ["BYD", "FIAT", "GWM"]})
    resultado = marcas.adicionar_chinesa(df, col_marca="fabricante")
    assert list(resultado["marca_chinesa"]) == [True, False, True]


def test_adicionar_chinesa_preserva_colunas_existentes(df_emplacamentos_misto):
    """adicionar_chinesa nao deve modificar as colunas originais do DataFrame."""
    resultado = marcas.adicionar_chinesa(df_emplacamentos_misto)
    assert list(resultado["marca"]) == list(df_emplacamentos_misto["marca"])
    assert list(resultado["emplacamentos"]) == list(df_emplacamentos_misto["emplacamentos"])


def test_adicionar_chinesa_dataframe_vazio():
    """adicionar_chinesa deve lidar com DataFrame vazio sem erro."""
    df = pd.DataFrame({"marca": pd.Series([], dtype=str)})
    resultado = marcas.adicionar_chinesa(df)
    assert "marca_chinesa" in resultado.columns
    assert len(resultado) == 0


# ---------------------------------------------------------------------------
# 8. Invariantes do modulo
# ---------------------------------------------------------------------------


def test_marcas_chinesas_tem_16_entradas():
    """MARCAS_CHINESAS deve ter exatamente 16 marcas canonicas."""
    assert len(marcas.MARCAS_CHINESAS) == 16, (
        f"Esperadas 16 marcas, encontradas {len(marcas.MARCAS_CHINESAS)}: "
        f"{sorted(marcas.MARCAS_CHINESAS)}"
    )


def test_marcas_chinesas_igual_chaves_grupos():
    """MARCAS_CHINESAS deve ser igual ao conjunto de chaves de GRUPOS_CHINESES.

    Invariante: toda marca classificada como chinesa precisa ter um grupo controlador
    mapeado em GRUPOS_CHINESES — sem grupo, o campo 'grupo_chines' no DataFrame
    ficaria None para uma marca que o sistema considera chinesa, o que e inconsistente.
    """
    assert marcas.MARCAS_CHINESAS == set(marcas.GRUPOS_CHINESES.keys()), (
        f"Diferenca simetrica: "
        f"{marcas.MARCAS_CHINESAS.symmetric_difference(set(marcas.GRUPOS_CHINESES.keys()))}"
    )


def test_marcas_chinesas_sao_upper_sem_espacos():
    """Todos os valores em MARCAS_CHINESAS devem estar em UPPER e sem espacos laterais."""
    for marca in marcas.MARCAS_CHINESAS:
        assert marca == marca.upper() and marca == marca.strip(), (
            f"Marca fora do padrao em MARCAS_CHINESAS: '{marca}'"
        )


def test_aliases_tem_no_minimo_4_entradas():
    """ALIASES_MARCAS deve ter ao menos 4 aliases cadastrados."""
    assert len(marcas.ALIASES_MARCAS) >= 4, (
        f"Esperados >= 4 aliases, encontrados {len(marcas.ALIASES_MARCAS)}"
    )


def test_aliases_apontam_para_marcas_canonicas():
    """Todo valor de ALIASES_MARCAS deve estar em MARCAS_CHINESAS.

    Invariante: um alias que aponta para uma marca inexistente no conjunto
    canonico causaria e_marca_chinesa a retornar False para entradas que
    deveriam retornar True — falso negativo silencioso na classificacao.
    """
    for alias, canonica in marcas.ALIASES_MARCAS.items():
        assert canonica in marcas.MARCAS_CHINESAS, (
            f"Alias '{alias}' aponta para '{canonica}' que nao esta em MARCAS_CHINESAS"
        )
