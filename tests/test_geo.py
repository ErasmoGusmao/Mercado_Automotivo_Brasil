"""Testes para src/geo.py — lookup UF -> Regiao IBGE e helper de DataFrame.

Decisoes de contrato documentadas:
- uf_to_regiao(None) levanta TypeError (input nao e string).
- uf_to_regiao("XX") levanta ValueError com a string invalida na mensagem.
- uf_to_regiao aceita lower-case e espacos em branco (strip + upper internamente).
- adicionar_regiao preserva a ordem original das linhas do DataFrame.
- UF_PARA_REGIAO e um dict com exatamente 27 chaves e 5 valores unicos.
"""

import pandas as pd
import pytest

from src import geo

# ---------------------------------------------------------------------------
# Constantes de referencia (divisao oficial IBGE)
# ---------------------------------------------------------------------------

NORTE = "Norte"
NORDESTE = "Nordeste"
CENTRO_OESTE = "Centro-Oeste"
SUDESTE = "Sudeste"
SUL = "Sul"

UFS_NORTE = ["AC", "AP", "AM", "PA", "RO", "RR", "TO"]
UFS_NORDESTE = ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"]
UFS_CENTRO_OESTE = ["DF", "GO", "MT", "MS"]
UFS_SUDESTE = ["ES", "MG", "RJ", "SP"]
UFS_SUL = ["PR", "RS", "SC"]

TODAS_UFS_ESPERADAS: list[tuple[str, str]] = (
    [(uf, NORTE) for uf in UFS_NORTE]
    + [(uf, NORDESTE) for uf in UFS_NORDESTE]
    + [(uf, CENTRO_OESTE) for uf in UFS_CENTRO_OESTE]
    + [(uf, SUDESTE) for uf in UFS_SUDESTE]
    + [(uf, SUL) for uf in UFS_SUL]
)


# ---------------------------------------------------------------------------
# 1. Cobertura completa das 27 UFs
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("uf,regiao_esperada", TODAS_UFS_ESPERADAS)
def test_uf_to_regiao_cobertura_completa(uf: str, regiao_esperada: str):
    """Cada uma das 27 UFs deve retornar a Regiao IBGE correta."""
    assert geo.uf_to_regiao(uf) == regiao_esperada


# ---------------------------------------------------------------------------
# 2. Normalizacao de input (lower-case e espacos)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "uf_raw,regiao_esperada",
    [
        ("sp", SUDESTE),
        ("  SP  ", SUDESTE),
        ("  sp  ", SUDESTE),
        ("rj", SUDESTE),
        ("am", NORTE),
        ("  df  ", CENTRO_OESTE),
    ],
)
def test_uf_to_regiao_normalizacao_input(uf_raw: str, regiao_esperada: str):
    """uf_to_regiao deve aceitar lower-case e strings com espacos em branco."""
    assert geo.uf_to_regiao(uf_raw) == regiao_esperada


# ---------------------------------------------------------------------------
# 3. UF invalida — TypeError para None, ValueError para string invalida
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("uf_invalida", ["XX", "", "BR", "ZZ", "123"])
def test_uf_invalida_levanta_value_error(uf_invalida: str):
    """UF desconhecida deve levantar ValueError contendo o input na mensagem."""
    with pytest.raises(ValueError, match=uf_invalida if uf_invalida else ""):
        geo.uf_to_regiao(uf_invalida)


def test_none_levanta_type_error():
    """None nao e string — deve levantar TypeError, nao ValueError."""
    with pytest.raises(TypeError):
        geo.uf_to_regiao(None)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 4. Vetorizacao via DataFrame
# ---------------------------------------------------------------------------


def test_adicionar_regiao_colunas_e_valores():
    """adicionar_regiao deve inserir coluna 'regiao_ibge' com os valores corretos."""
    df = pd.DataFrame(
        {
            "uf": ["SP", "AM", "BA", "PR", "DF"],
            "quantidade": [1000, 200, 300, 400, 50],
        }
    )
    resultado = geo.adicionar_regiao(df, col_uf="uf")

    assert "regiao_ibge" in resultado.columns
    esperadas = [SUDESTE, NORTE, NORDESTE, SUL, CENTRO_OESTE]
    assert list(resultado["regiao_ibge"]) == esperadas


def test_adicionar_regiao_preserva_ordem_das_linhas():
    """A ordem original das linhas do DataFrame deve ser mantida apos adicionar_regiao."""
    df = pd.DataFrame({"uf": ["SC", "RR", "SE", "MG"]})
    resultado = geo.adicionar_regiao(df, col_uf="uf")

    assert list(resultado["regiao_ibge"]) == [SUL, NORTE, NORDESTE, SUDESTE]
    assert list(resultado.index) == list(df.index)


def test_adicionar_regiao_nao_altera_colunas_existentes():
    """adicionar_regiao nao deve modificar as colunas originais do DataFrame."""
    df = pd.DataFrame({"uf": ["GO", "RS"], "vendas": [100, 200]})
    resultado = geo.adicionar_regiao(df, col_uf="uf")

    assert list(resultado["uf"]) == ["GO", "RS"]
    assert list(resultado["vendas"]) == [100, 200]


def test_adicionar_regiao_col_uf_personalizada():
    """adicionar_regiao deve funcionar com nome de coluna diferente do padrao."""
    df = pd.DataFrame({"estado": ["CE", "SP"]})
    resultado = geo.adicionar_regiao(df, col_uf="estado")

    assert list(resultado["regiao_ibge"]) == [NORDESTE, SUDESTE]


# ---------------------------------------------------------------------------
# 5. Invariante de cardinalidade do dicionario UF_PARA_REGIAO
# ---------------------------------------------------------------------------


def test_uf_para_regiao_tem_27_chaves():
    """UF_PARA_REGIAO deve ter exatamente 27 entradas — uma por UF brasileira."""
    assert len(geo.UF_PARA_REGIAO) == 27, (
        f"Esperadas 27 UFs, encontradas {len(geo.UF_PARA_REGIAO)}: "
        f"{sorted(geo.UF_PARA_REGIAO.keys())}"
    )


def test_uf_para_regiao_tem_5_regioes():
    """UF_PARA_REGIAO deve mapear para exatamente 5 regioes IBGE distintas."""
    regioes = set(geo.UF_PARA_REGIAO.values())
    regioes_esperadas = {NORTE, NORDESTE, CENTRO_OESTE, SUDESTE, SUL}
    assert regioes == regioes_esperadas, (
        f"Regioes encontradas: {regioes} — esperadas: {regioes_esperadas}"
    )


def test_uf_para_regiao_chaves_sao_siglas_maiusculas():
    """Todas as chaves de UF_PARA_REGIAO devem ser siglas em maiusculo com 2 caracteres."""
    for chave in geo.UF_PARA_REGIAO:
        assert len(chave) == 2 and chave == chave.upper(), (
            f"Chave invalida em UF_PARA_REGIAO: '{chave}'"
        )


def test_uf_para_regiao_cobre_todas_as_27_ufs():
    """As 27 UFs oficiais devem estar presentes em UF_PARA_REGIAO."""
    todas_ufs = {uf for uf, _ in TODAS_UFS_ESPERADAS}
    assert set(geo.UF_PARA_REGIAO.keys()) == todas_ufs, (
        f"Diferenca: {set(geo.UF_PARA_REGIAO.keys()).symmetric_difference(todas_ufs)}"
    )
