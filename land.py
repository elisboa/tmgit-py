"""Fase 4 - encerramento (land) para tmgit-py.
Este módulo não contém lógica de negócio, somente finalização de execução.
"""

import sys


def land(error_level: int, caller: str, message: str, error_message: str) -> None:
    """Finaliza o programa exibindo as mensagens e saindo com código especificado."""

    # Sempre informar a origem da chamada quando fornecida
    if caller:
        print(f"Iniciando aterrissagem chamada por {caller}")

    # Exibir mensagem de encerramento quando houver
    if message:
        print(f"Encerramento: {message}")

    # Exibir erro ou aviso quando houver
    if error_message:
        print(f"Erro ou aviso: {error_message}")

    # Exibir código de erro
    print(f"Codigo de erro: {error_level}")

    # Encerra a aplicação usando o código de erro informado
    sys.exit(error_level)
