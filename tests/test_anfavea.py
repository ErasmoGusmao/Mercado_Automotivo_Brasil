"""Testes para src/anfavea.py — fetcher dos XLSX da ANFAVEA com snapshots datados.

Decisoes de contrato documentadas (aprovadas em 2026-04-28, antes da implementacao):

- A) Modulo cobre apenas o **fetcher** (download). Parser do XLSX fica no PR #5.
- B) ANOS_COBERTURA e fixo (2016-2026); baixar_todos aceita override via parametro `anos`.
- C) Falha em ano unico nunca aborta o fluxo: baixar_anfavea retorna Resultado(ok=False)
     em qualquer erro de rede/HTTP, e baixar_todos agrega tudo num dict.
- D) Mocks usam pytest monkeypatch sobre `src.anfavea.requests.get` — sem nova dependencia.
- E) Resultado e dataclass com campos `ano`, `ok`, `caminho`, `erro`. Quando ok=True,
     `caminho` e Path e `erro` e None; quando ok=False, `caminho` e None e `erro` e str.

Observacoes operacionais:
- Os arquivos sao salvos em FONTE/ANFAVEA/raw/{mes_coleta}/siteautoveiculos{ano}.xlsx
  conforme convencao "Snapshots datados" do quadro do MVP.
- Cache load-uma-vez: se o arquivo ja existe no caminho de destino, baixar_anfavea NAO
  faz nova requisicao HTTP e retorna ok=True com o caminho existente.
- User-Agent identifica o projeto para a ANFAVEA (cortesia + reduz risco de bloqueio).
"""

from __future__ import annotations

from dataclasses import fields
from pathlib import Path
from typing import Any

import pytest

from src import anfavea


# ---------------------------------------------------------------------------
# Helpers de mock para requests.get
# ---------------------------------------------------------------------------


class _FakeResponse:
    """Mock minimo de requests.Response para os testes do fetcher."""

    def __init__(
        self,
        status_code: int = 200,
        content: bytes = b"FAKE_XLSX_BYTES",
        url: str = "https://anfavea.com.br/docs/siteautoveiculos2024.xlsx",
    ) -> None:
        self.status_code = status_code
        self.content = content
        self.url = url
        self.ok = 200 <= status_code < 300

    def raise_for_status(self) -> None:
        if not self.ok:
            from requests import HTTPError

            raise HTTPError(f"{self.status_code} para {self.url}")


def _fake_get_factory(
    *,
    status_code: int = 200,
    content: bytes = b"FAKE_XLSX_BYTES",
    raise_exc: Exception | None = None,
    capture: dict[str, Any] | None = None,
):
    """Constroi um substituto de requests.get com comportamento configuravel."""

    def _fake_get(url: str, **kwargs: Any) -> _FakeResponse:
        if capture is not None:
            capture["url"] = url
            capture["kwargs"] = kwargs
        if raise_exc is not None:
            raise raise_exc
        return _FakeResponse(status_code=status_code, content=content, url=url)

    return _fake_get


# ---------------------------------------------------------------------------
# 1. Constantes do modulo
# ---------------------------------------------------------------------------


def test_url_template_aponta_para_anfavea_https():
    """URL_TEMPLATE deve ser HTTPS, dominio anfavea.com.br/docs/, com placeholder {ano}."""
    assert isinstance(anfavea.URL_TEMPLATE, str)
    assert anfavea.URL_TEMPLATE.startswith("https://anfavea.com.br/docs/")
    assert "{ano}" in anfavea.URL_TEMPLATE


def test_url_template_usa_padrao_siteautoveiculos_e_nao_o_obsoleto():
    """O padrao correto e siteautoveiculos{ano}.xlsx, nao emplacamentos_nacionais_*."""
    assert "siteautoveiculos" in anfavea.URL_TEMPLATE
    assert "emplacamentos_nacionais" not in anfavea.URL_TEMPLATE
    assert "emplacamentos_importados" not in anfavea.URL_TEMPLATE
    assert anfavea.URL_TEMPLATE.endswith(".xlsx")


def test_anos_cobertura_2016_a_2026_inclusive():
    """ANOS_COBERTURA deve cobrir os 11 anos do periodo historico do MVP."""
    anos = list(anfavea.ANOS_COBERTURA)
    assert anos[0] == 2016
    assert anos[-1] == 2026
    assert len(anos) == 11


# ---------------------------------------------------------------------------
# 2. url_anfavea — formatacao do template
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "ano,esperado",
    [
        (2016, "https://anfavea.com.br/docs/siteautoveiculos2016.xlsx"),
        (2024, "https://anfavea.com.br/docs/siteautoveiculos2024.xlsx"),
        (2026, "https://anfavea.com.br/docs/siteautoveiculos2026.xlsx"),
    ],
)
def test_url_anfavea_formata_url_correta(ano: int, esperado: str):
    """url_anfavea(ano) deve substituir {ano} no template e retornar a URL completa."""
    assert anfavea.url_anfavea(ano) == esperado


def test_url_anfavea_aceita_anos_fora_do_range_de_cobertura():
    """url_anfavea e so um formatador — nao valida o range; validacao e do caller."""
    assert "2012" in anfavea.url_anfavea(2012)
    assert "2030" in anfavea.url_anfavea(2030)


# ---------------------------------------------------------------------------
# 3. Dataclass Resultado
# ---------------------------------------------------------------------------


def test_resultado_tem_campos_ano_ok_caminho_erro():
    """Resultado deve expor exatamente quatro campos: ano, ok, caminho, erro."""
    nomes = {f.name for f in fields(anfavea.Resultado)}
    assert nomes == {"ano", "ok", "caminho", "erro"}


def test_resultado_sucesso_tem_caminho_e_erro_none():
    """Resultado(ok=True) deve carregar caminho e ter erro=None."""
    r = anfavea.Resultado(ano=2024, ok=True, caminho=Path("foo.xlsx"), erro=None)
    assert r.ok is True
    assert r.caminho == Path("foo.xlsx")
    assert r.erro is None


def test_resultado_falha_tem_erro_e_caminho_none():
    """Resultado(ok=False) deve carregar erro e ter caminho=None."""
    r = anfavea.Resultado(ano=2024, ok=False, caminho=None, erro="404 Not Found")
    assert r.ok is False
    assert r.caminho is None
    assert r.erro == "404 Not Found"


# ---------------------------------------------------------------------------
# 4. baixar_anfavea — sucesso, falhas, cache
# ---------------------------------------------------------------------------


def test_baixar_anfavea_sucesso_grava_arquivo_no_caminho_correto(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Em 200 OK, baixar_anfavea grava bytes em FONTE/ANFAVEA/raw/{mes_coleta}/siteautoveiculos{ano}.xlsx."""
    monkeypatch.setattr(
        anfavea.requests, "get", _fake_get_factory(content=b"BYTES_FAKE")
    )

    resultado = anfavea.baixar_anfavea(
        ano=2024, destino_base=tmp_path, mes_coleta="2026-04"
    )

    esperado = tmp_path / "ANFAVEA" / "raw" / "2026-04" / "siteautoveiculos2024.xlsx"
    assert resultado.ok is True
    assert resultado.caminho == esperado
    assert resultado.erro is None
    assert esperado.exists()
    assert esperado.read_bytes() == b"BYTES_FAKE"


def test_baixar_anfavea_chama_url_correta_com_user_agent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """A requisicao HTTP deve usar a URL siteautoveiculos{ano}.xlsx e User-Agent identificando o projeto."""
    capture: dict[str, Any] = {}
    monkeypatch.setattr(
        anfavea.requests, "get", _fake_get_factory(capture=capture)
    )

    anfavea.baixar_anfavea(ano=2025, destino_base=tmp_path, mes_coleta="2026-04")

    assert capture["url"] == "https://anfavea.com.br/docs/siteautoveiculos2025.xlsx"
    headers = capture["kwargs"].get("headers", {})
    assert "User-Agent" in headers
    assert "mercado-automotivo-brasil" in headers["User-Agent"].lower()


@pytest.mark.parametrize("status_code", [404, 500, 503])
def test_baixar_anfavea_erro_http_retorna_ok_false_e_nao_aborta(
    status_code: int, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Erros HTTP (404, 500, 503) NAO devem levantar — devem retornar Resultado(ok=False)."""
    monkeypatch.setattr(
        anfavea.requests, "get", _fake_get_factory(status_code=status_code)
    )

    resultado = anfavea.baixar_anfavea(
        ano=2018, destino_base=tmp_path, mes_coleta="2026-04"
    )

    assert resultado.ok is False
    assert resultado.caminho is None
    assert resultado.erro is not None
    assert str(status_code) in resultado.erro
    # Em falha, NAO deve gravar arquivo no destino.
    destino = tmp_path / "ANFAVEA" / "raw" / "2026-04" / "siteautoveiculos2018.xlsx"
    assert not destino.exists()


def test_baixar_anfavea_excecao_de_rede_retorna_ok_false(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Exceptions de rede (ConnectionError/Timeout) devem virar Resultado(ok=False)."""
    from requests import ConnectionError as RequestsConnectionError

    monkeypatch.setattr(
        anfavea.requests,
        "get",
        _fake_get_factory(raise_exc=RequestsConnectionError("dns down")),
    )

    resultado = anfavea.baixar_anfavea(
        ano=2020, destino_base=tmp_path, mes_coleta="2026-04"
    )

    assert resultado.ok is False
    assert resultado.caminho is None
    assert "dns down" in (resultado.erro or "")


@pytest.mark.parametrize(
    "mes_coleta_invalido",
    # Casos que falham regex de formato AAAA-MM. Nao validamos semantica de
    # calendario (ex: "2026-13" passa pelo regex e e aceito como nome de
    # diretorio); o objetivo e evitar paths quebrados como "abril/2026".
    ["abril/2026", "2026-4", "2026-04-15", "2026/04", "", "abril"],
)
def test_baixar_anfavea_mes_coleta_invalido_levanta_value_error(
    mes_coleta_invalido: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """mes_coleta fora do formato 'AAAA-MM' deve levantar ValueError (input do operador, nao falha de fonte)."""
    monkeypatch.setattr(anfavea.requests, "get", _fake_get_factory())

    with pytest.raises(ValueError, match="mes_coleta"):
        anfavea.baixar_anfavea(
            ano=2024, destino_base=tmp_path, mes_coleta=mes_coleta_invalido
        )


def test_baixar_anfavea_cache_load_uma_vez_pula_download(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Se o arquivo ja existe no caminho de destino, NAO deve fazer requisicao HTTP."""
    destino = tmp_path / "ANFAVEA" / "raw" / "2026-04" / "siteautoveiculos2024.xlsx"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(b"CACHE_PREEXISTENTE")

    chamadas: dict[str, int] = {"count": 0}

    def _get_que_falha_se_chamado(url: str, **kwargs: Any):
        chamadas["count"] += 1
        raise AssertionError(
            f"requests.get nao deveria ter sido chamado (url={url})"
        )

    monkeypatch.setattr(anfavea.requests, "get", _get_que_falha_se_chamado)

    resultado = anfavea.baixar_anfavea(
        ano=2024, destino_base=tmp_path, mes_coleta="2026-04"
    )

    assert resultado.ok is True
    assert resultado.caminho == destino
    assert destino.read_bytes() == b"CACHE_PREEXISTENTE"
    assert chamadas["count"] == 0


# ---------------------------------------------------------------------------
# 5. baixar_todos — delegacao, parcial, override de anos
# ---------------------------------------------------------------------------


def test_baixar_todos_itera_anos_cobertura_por_padrao(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Sem 'anos' explicito, baixar_todos deve iterar ANOS_COBERTURA (11 anos)."""
    monkeypatch.setattr(anfavea.requests, "get", _fake_get_factory())

    resultados = anfavea.baixar_todos(destino_base=tmp_path, mes_coleta="2026-04")

    assert isinstance(resultados, dict)
    assert set(resultados.keys()) == set(anfavea.ANOS_COBERTURA)
    assert all(r.ok for r in resultados.values())


def test_baixar_todos_aceita_override_de_anos(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Quando 'anos' e passado, baixar_todos deve iterar so esses anos."""
    monkeypatch.setattr(anfavea.requests, "get", _fake_get_factory())

    resultados = anfavea.baixar_todos(
        destino_base=tmp_path, mes_coleta="2026-04", anos=[2024, 2025]
    )

    assert set(resultados.keys()) == {2024, 2025}


def test_baixar_todos_continua_mesmo_se_um_ano_falhar(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Se 2018 da 404 mas 2024 da 200, o dict deve conter ambos (parcial-com-warning)."""

    def _fake_get_misto(url: str, **kwargs: Any) -> _FakeResponse:
        if "2018" in url:
            return _FakeResponse(status_code=404, url=url)
        return _FakeResponse(status_code=200, content=b"OK", url=url)

    monkeypatch.setattr(anfavea.requests, "get", _fake_get_misto)

    resultados = anfavea.baixar_todos(
        destino_base=tmp_path, mes_coleta="2026-04", anos=[2018, 2024]
    )

    assert resultados[2018].ok is False
    assert resultados[2018].erro is not None
    assert resultados[2024].ok is True
    assert resultados[2024].caminho is not None


def test_baixar_todos_resultado_ano_bate_com_chave_do_dict(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Cada Resultado.ano deve ser igual a chave correspondente no dict de retorno."""
    monkeypatch.setattr(anfavea.requests, "get", _fake_get_factory())

    resultados = anfavea.baixar_todos(
        destino_base=tmp_path, mes_coleta="2026-04", anos=[2020, 2021, 2022]
    )

    for ano, r in resultados.items():
        assert r.ano == ano
