"""Testes para a função land() do módulo land.py.
Seguindo a metodologia SDD — cada teste deriva de uma especificação DADO/QUANDO/ENTÃO.
"""

import pytest
import sys
from land import land


class TestLandSuccessful:
    """Testes para encerramento bem-sucedido com error_level=0."""

    def test_land_with_error_level_zero_exits_successfully(self, capsys):
        """DADO error_level=0, caller="preflight", message="ok", error_message=""
        QUANDO land() for chamado
        ENTÃO deve encerrar com sys.exit(0)
        """
        with pytest.raises(SystemExit) as exc_info:
            land(
                error_level=0,
                caller="preflight",
                message="ok",
                error_message=""
            )

        # Verificar que o código de saída é 0
        assert exc_info.value.code == 0


class TestLandWithError:
    """Testes para encerramento com erro (error_level=1)."""

    def test_land_with_error_level_one_exits_with_error(self, capsys):
        """DADO error_level=1, caller="preflight", message="erro", error_message="git não encontrado"
        QUANDO land() for chamado
        ENTÃO deve encerrar com sys.exit(1)
        """
        with pytest.raises(SystemExit) as exc_info:
            land(
                error_level=1,
                caller="preflight",
                message="erro",
                error_message="git não encontrado"
            )

        # Verificar que o código de saída é 1
        assert exc_info.value.code == 1


class TestLandMessageOutput:
    """Testes para as mensagens impressas pelo land()."""

    def test_land_prints_caller_message(self, capsys):
        """DADO caller="preflight"
        QUANDO land() for chamado
        ENTÃO deve imprimir "Iniciando aterrissagem chamada por preflight"
        """
        with pytest.raises(SystemExit):
            land(
                error_level=0,
                caller="preflight",
                message="",
                error_message=""
            )

        captured = capsys.readouterr()
        assert "Iniciando aterrissagem chamada por preflight" in captured.out

    def test_land_prints_encerramento_message(self, capsys):
        """DADO message="Encerramento ok"
        QUANDO land() for chamado
        ENTÃO deve imprimir "Encerramento: Encerramento ok"
        """
        with pytest.raises(SystemExit):
            land(
                error_level=0,
                caller="",
                message="Encerramento ok",
                error_message=""
            )

        captured = capsys.readouterr()
        assert "Encerramento: Encerramento ok" in captured.out

    def test_land_prints_error_message(self, capsys):
        """DADO error_message="git não encontrado"
        QUANDO land() for chamado
        ENTÃO deve imprimir "Erro ou aviso: git não encontrado"
        """
        with pytest.raises(SystemExit):
            land(
                error_level=1,
                caller="",
                message="",
                error_message="git não encontrado"
            )

        captured = capsys.readouterr()
        assert "Erro ou aviso: git não encontrado" in captured.out


class TestLandCompleteFlow:
    """Testes de fluxo completo com múltiplas mensagens."""

    def test_land_with_all_parameters(self, capsys):
        """DADO todos os parâmetros preenchidos (caller, message, error_message)
        QUANDO land() for chamado
        ENTÃO deve imprimir todas as mensagens e encerrar com o código correto
        """
        with pytest.raises(SystemExit) as exc_info:
            land(
                error_level=1,
                caller="preflight",
                message="erro ao validar",
                error_message="git não encontrado"
            )

        captured = capsys.readouterr()

        # Verificar todas as mensagens foram impressas
        assert "Iniciando aterrissagem chamada por preflight" in captured.out
        assert "Encerramento: erro ao validar" in captured.out
        assert "Erro ou aviso: git não encontrado" in captured.out
        assert "Codigo de erro: 1" in captured.out

        # Verificar código de saída
        assert exc_info.value.code == 1

    def test_land_prints_error_code(self, capsys):
        """DADO error_level=42 (código customizado)
        QUANDO land() for chamado
        ENTÃO deve imprimir "Codigo de erro: 42" e encerrar com esse código
        """
        with pytest.raises(SystemExit) as exc_info:
            land(
                error_level=42,
                caller="climb",
                message="falha na criação de branch",
                error_message="branch name inválida"
            )

        captured = capsys.readouterr()
        assert "Codigo de erro: 42" in captured.out
        assert exc_info.value.code == 42


class TestLandEmptyParameters:
    """Testes com parâmetros vazios (strings vazias)."""

    def test_land_with_empty_caller_omits_caller_message(self, capsys):
        """DADO caller=""
        QUANDO land() for chamado
        ENTÃO não deve imprimir mensagem de aterrissagem
        """
        with pytest.raises(SystemExit):
            land(
                error_level=0,
                caller="",
                message="ok",
                error_message=""
            )

        captured = capsys.readouterr()
        assert "Iniciando aterrissagem" not in captured.out

    def test_land_with_empty_message_omits_encerramento_message(self, capsys):
        """DADO message=""
        QUANDO land() for chamado
        ENTÃO não deve imprimir mensagem de encerramento
        """
        with pytest.raises(SystemExit):
            land(
                error_level=0,
                caller="preflight",
                message="",
                error_message=""
            )

        captured = capsys.readouterr()
        assert "Encerramento:" not in captured.out

    def test_land_with_empty_error_message_omits_error_message(self, capsys):
        """DADO error_message=""
        QUANDO land() for chamado
        ENTÃO não deve imprimir mensagem de erro
        """
        with pytest.raises(SystemExit):
            land(
                error_level=0,
                caller="preflight",
                message="ok",
                error_message=""
            )

        captured = capsys.readouterr()
        assert "Erro ou aviso:" not in captured.out
