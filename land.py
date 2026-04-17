"""Fase 4 - encerramento (land) para tmgit-py.
Este módulo não contém lógica de negócio, somente finalização de execução.
"""

import sys


def land(error_level: int, caller: str, message: str, error_message: str) -> None:
    """Finaliza o programa exibindo as mensagens e saindo com código especificado.

    Esta é a única função que pode chamar sys.exit(). Encerra o programa com as
    informações de contexto coletadas pelas fases preflight → climb → fly.

    **Parâmetros (semântica):**

    - `error_level`: Código de saída (0 = sucesso, >0 = erro). Compatível com shells.
    - `caller`: Rastreio da fase que culminou no encerramento (para debug).
    - `message`: Descrição resumida da ação que estava sendo executada.
    - `error_message`: Detalhes do resultado (sucesso ou erro específico).

    **Exemplo de saída em SUCESSO:**
    ```
    Iniciando aterrissagem chamada por fly
    Encerramento: Fly concluído com sucesso
    Codigo de erro: 0
    ```

    **Exemplo de saída em ERRO:**
    ```
    Iniciando aterrissagem chamada por preflight
    Encerramento: Verificando diretório /home/user
    Erro ou aviso: Diretório não existe
    Codigo de erro: 1
    ```

    Args:
        error_level (int): Código de saída do programa (0 = sucesso, >0 = erro).
        caller (str): Nome da fase que está chamando encerramento.
        message (str): Descrição da ação que estava sendo executada.
        error_message (str): Detalhe do resultado ou mensagem de erro.
    """

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
